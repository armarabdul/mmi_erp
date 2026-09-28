import time
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.user import User
from app.models.audit import AuditLog
from app.models.erp import Branch
from app.security.rbac import get_user_branch_filter
from app.security.sql_guard import SQLGuard, SQLGuardError
from app.analytics.semantic_layer import semantic_layer
from app.analytics.fast_path import fast_path_analyzer
from app.ai.openai_provider import get_ai_provider
from app.core.config import settings
from app.core.logging import logger
from app.schemas.analytics import (
    AnalyticsQueryRequest,
    AnalyticsQueryResponse,
    ChartMetadata,
    TechnicalDetails,
)

class AnalyticsWorkflow:
    def __init__(self):
        self.ai_provider = get_ai_provider()

    def execute_workflow(
        self,
        db: Session,
        user: User,
        request: AnalyticsQueryRequest,
    ) -> AnalyticsQueryResponse:
        start_time = time.perf_counter()
        language = request.language if request.language in ("en", "ar") else "en"
        question = request.question.strip()
        user_branch_id = get_user_branch_filter(user)

        generated_sql = ""
        validated_sql = ""
        chart_type = "table"
        chart_title = "Analytics Result"
        x_axis_key = "dimension"
        y_axis_key = "metric"
        explanation = ""
        rows_data: List[Dict[str, Any]] = []
        columns: List[str] = []
        filters_applied: Dict[str, Any] = {}
        error_msg = None
        success = True

        if user_branch_id:
            branch_rec = db.query(Branch).filter(Branch.id == user_branch_id).first()
            branch_name = branch_rec.name if branch_rec else f"Branch {user_branch_id}"
            filters_applied["branch_restriction"] = branch_name

        try:
            # 1. Intent Detection & Fast-Path Checking
            fast_match = fast_path_analyzer.match(question, language=language)

            if fast_match:
                generated_sql = fast_match.generated_sql
                chart_type = fast_match.chart_type
                chart_title = fast_match.chart_title_ar if language == "ar" else fast_match.chart_title
                x_axis_key = fast_match.x_axis_key
                y_axis_key = fast_match.y_axis_key
                if fast_match.date_filter:
                    filters_applied["period"] = fast_match.date_filter
            else:
                # Exploratory AI Mode: generate SQL using LLM + Semantic Context
                generated_sql = self._generate_sql_with_ai(question, language, user_branch_id)
                chart_type, chart_title, x_axis_key, y_axis_key = self._infer_chart_type(question, generated_sql, language)

            # 2. SQL Validation / Security Guard
            is_valid, sanitized_sql, guard_error = SQLGuard.validate_and_sanitize(
                generated_sql, 
                branch_restriction_id=user_branch_id
            )
            validated_sql = sanitized_sql

            if not is_valid:
                raise SQLGuardError(guard_error or "Query violated SQL security policy")

            # 3. Read-only Database Execution
            cursor = db.execute(text(validated_sql))
            raw_columns = list(cursor.keys())
            columns = [str(c) for c in raw_columns]
            raw_rows = cursor.fetchall()

            for r in raw_rows:
                row_dict = {}
                for idx, col in enumerate(columns):
                    val = r[idx]
                    if isinstance(val, (float, Decimal)):
                        val = round(float(val), 2)
                    row_dict[col] = val
                rows_data.append(row_dict)

            # Fix axis keys if inferred keys are missing in actual columns
            if columns:
                if x_axis_key not in columns:
                    x_axis_key = columns[0]
                if y_axis_key not in columns:
                    y_axis_key = columns[1] if len(columns) > 1 else columns[0]

            # 4. Generate Business Explanation
            explanation = self._generate_explanation(question, rows_data, language, user_branch_id)

        except SQLGuardError as sge:
            db.rollback()
            success = False
            error_msg = str(sge)
            explanation = (
                f"تنبيه أمني: تم رفض الاستعلام ({error_msg})"
                if language == "ar"
                else f"Security Guard Alert: Query was rejected. {error_msg}"
            )
            chart_type = "table"
            chart_title = "Security Alert" if language == "en" else "تنبيه أمني"
        except Exception as ex:
            db.rollback()
            success = False
            logger.error(f"Error executing analytics workflow: {ex}", exc_info=True)
            error_msg = "An error occurred while executing the analytics query."
            explanation = (
                "تعذر استخراج البيانات المطلوبة. يرجى التحقق من صياغة السؤال."
                if language == "ar"
                else "Unable to process the analytics request. Please refine your query."
            )

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 5. Persistent Enterprise Audit Logging (Section 22)
        audit_entry = AuditLog(
            user_id=user.id,
            user_role=user.role,
            branch_id=user_branch_id,
            timestamp=datetime.now(timezone.utc),
            language=language,
            user_question=question,
            conversation_id=request.conversation_id,
            ai_provider=settings.AI_PROVIDER,
            model=settings.OPENAI_MODEL,
            generated_sql=generated_sql,
            validated_sql=validated_sql,
            execution_time_ms=duration_ms,
            result_row_count=len(rows_data),
            chart_type=chart_type,
            success=success,
            error_message=error_msg,
            final_response=explanation,
            token_count=180 + len(question.split()) * 2,
        )
        audit_id = 0
        try:
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            audit_id = audit_entry.id
        except Exception as audit_ex:
            logger.error(f"Failed to persist audit log: {audit_ex}", exc_info=True)
            db.rollback()

        # 6. Build Structured Result
        return AnalyticsQueryResponse(
            question=question,
            language=language,
            success=success,
            explanation=explanation,
            visualization=ChartMetadata(
                chart_type=chart_type,
                title=chart_title,
                x_axis_key=x_axis_key,
                y_axis_key=y_axis_key,
                data=rows_data,
            ),
            table_columns=columns,
            table_data=rows_data,
            filters_applied=filters_applied,
            data_source="Demo ERP Analytics Database",
            technical_details=TechnicalDetails(
                audit_id=audit_id,
                execution_time_ms=duration_ms,
                result_row_count=len(rows_data),
                validated_sql=validated_sql,
                model_used=settings.OPENAI_MODEL,
                ai_provider=settings.AI_PROVIDER,
                branch_restricted=user_branch_id is not None,
            ),
            error_message=error_msg,
        )

    def _generate_sql_with_ai(self, question: str, language: str, branch_id: Optional[int]) -> str:
        """Exploratory AI mode: prompts LLM with semantic metadata."""
        system_prompt = f"""You are a professional Enterprise SQL Analytics engineer for MMI ERP.
Your task is to generate a SINGLE standard ANSI SQL SELECT query based on the user's natural language question.

CRITICAL RULES:
1. Output RAW SQL ONLY. Do NOT include markdown ticks, explanation, or commentary.
2. Only use SELECT queries. Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
3. Tables available: branches, categories, products, customers, suppliers, sales, sale_items, purchases, inventory.
4. Always filter completed sales using `status = 'Completed'`.
5. Group by relevant dimensions and order by aggregate metric descending.
6. Limit results to 20 rows unless specified.
7. For rounding aggregate functions, cast to NUMERIC first: ROUND(CAST(SUM(...) AS NUMERIC), 2).

{semantic_layer.get_semantic_context_prompt()}
"""
        user_prompt = f"User Question: {question}\nLanguage: {language}"
        raw_sql = self.ai_provider.generate_text(system_prompt, user_prompt)
        # Clean potential markdown fences
        cleaned = re.sub(r"^```(sql)?", "", raw_sql.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"```$", "", cleaned.strip()).strip()
        return cleaned

    def _infer_chart_type(self, question: str, sql: str, language: str) -> Tuple[str, str, str, str]:
        q = question.lower()
        title = "Analytics Visualization" if language == "en" else "الرسم البياني التحليلي"
        if any(w in q for w in ["trend", "monthly", "date", "over time", "timeline", "شهري", "تاريخ", "اتجاه"]):
            return "line", title, "period", "total_sales"
        if any(w in q for w in ["share", "distribution", "category", "proportion", "فئة", "توزيع", "نسبة"]):
            return "pie", title, "category", "total_sales"
        return "bar", title, "name", "total_sales"

    def _generate_explanation(
        self,
        question: str,
        rows: List[Dict[str, Any]],
        language: str,
        branch_id: Optional[int],
    ) -> str:
        if not rows:
            return (
                "لم يتم العثور على سجلات مطابقة لمعايير البحث في قاعدة البيانات."
                if language == "ar"
                else "No matching records found in the analytics database for this criteria."
            )

        row_count = len(rows)
        first_row = rows[0]
        
        # Identify metric key and label key
        numeric_key = None
        label_key = None
        for k, v in first_row.items():
            if isinstance(v, (int, float)) and numeric_key is None:
                numeric_key = k
            elif isinstance(v, str) and label_key is None:
                label_key = k

        top_val = float(first_row.get(numeric_key, 0.0)) if numeric_key else 0.0
        top_name = str(first_row.get(label_key, "")) if label_key else ""
        
        # Sum of metric across available rows
        total_val = sum(float(r.get(numeric_key, 0.0)) for r in rows if numeric_key and isinstance(r.get(numeric_key), (int, float)))

        # Specific formatting for sales by branch
        is_branch_context = any("branch" in str(k).lower() for k in first_row.keys()) or "branch" in question.lower() or "فرع" in question
        
        if is_branch_context and row_count > 1:
            second_name = str(rows[1].get(label_key, "")) if row_count > 1 and label_key else ""
            second_val = float(rows[1].get(numeric_key, 0.0)) if row_count > 1 and numeric_key else 0.0
            
            if language == "ar":
                return f"سجل فرع {top_name} أعلى مبيعات بقيمة {top_val:,.2f} ر.ع.، يليه فرع {second_name} بقيمة {second_val:,.2f} ر.ع. وبلغ إجمالي المبيعات عبر الفروع المتاحة {total_val:,.2f} ر.ع."
            else:
                return f"{top_name} recorded the highest sales this period ({top_val:,.2f} OMR), followed by {second_name}. Total sales across the available branches were {total_val:,.2f} OMR."
        
        elif branch_id is not None or row_count == 1:
            if language == "ar":
                return f"سجل فرع {top_name} مبيعات بقيمة {top_val:,.2f} ر.ع. ضمن نطاق الصلاحيات المعتمدة للفرع."
            else:
                return f"{top_name} recorded {top_val:,.2f} OMR across {row_count} verified record(s) within authorized access."

        # Default multi-record explanation
        if language == "ar":
            return f"استناداً إلى سجلات قاعدة البيانات، تم استرجاع {row_count} نتائج تحليلية. تصدرت النتيجة '{top_name}' بقيمة بلغت {top_val:,.2f} ر.ع. من إجمالي قدره {total_val:,.2f} ر.ع."
        else:
            return f"Based on enterprise database records, {row_count} analytical records were retrieved. Top result is '{top_name}' with {top_val:,.2f} OMR from a total of {total_val:,.2f} OMR."

analytics_workflow = AnalyticsWorkflow()
