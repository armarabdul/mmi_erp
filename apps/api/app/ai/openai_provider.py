import time
import json
import httpx
from typing import Dict, Any, Optional
from app.ai.provider import AIProvider
from app.core.config import settings
from app.core.logging import logger

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = "https://api.openai.com/v1"

    def has_api_key(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2, max_tokens: int = 800) -> str:
        """
        Calls OpenAI Chat Completions API with safe sanitized structured logging.
        Never logs API keys, bearer tokens, or sensitive credentials.
        Clearly categorizes failures (missing key, invalid key, quota, network, etc.).
        Provides safe conversational fallbacks when offline or unconfigured.
        """
        start_time = time.perf_counter()

        if not self.has_api_key():
            logger.warning(
                f"OpenAI API call skipped: OPENAI_API_KEY is not configured [provider=openai, model={self.model}, duration_ms=0, status=failure, error_category=missing_key]"
            )
            return self._fallback_response(system_prompt, user_prompt)

        logger.info(
            f"OpenAI API call initiated [provider=openai, model={self.model}, prompt_len={len(user_prompt)}, status=in_progress]"
        )

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            with httpx.Client(timeout=25.0) as client:
                res = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.info(
                    f"OpenAI API call successful in {duration_ms}ms [provider=openai, model={self.model}, status=success]"
                )
                return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as http_err:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            status_code = http_err.response.status_code
            error_cat = "other_api_error"
            if status_code == 401:
                error_cat = "invalid_key"
            elif status_code == 429:
                error_cat = "insufficient_quota_or_billing"
            elif status_code >= 500:
                error_cat = "server_error"

            logger.error(
                f"OpenAI API HTTP error in {duration_ms}ms [provider=openai, model={self.model}, status=failure, error_category={error_cat}, status_code={status_code}]"
            )
            return self._fallback_response(system_prompt, user_prompt)
        except httpx.ConnectError:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"OpenAI API network connection error in {duration_ms}ms [provider=openai, model={self.model}, status=failure, error_category=network_failure]"
            )
            return self._fallback_response(system_prompt, user_prompt)
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"OpenAI API unexpected failure in {duration_ms}ms [provider=openai, model={self.model}, status=failure, error_category=other_api_error, exception={type(e).__name__}]"
            )
            return self._fallback_response(system_prompt, user_prompt)

    def generate_structured(self, system_prompt: str, user_prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.perf_counter()

        if not self.has_api_key():
            logger.warning(
                f"OpenAI structured call skipped: OPENAI_API_KEY missing [provider=openai, model={self.model}, status=failure, error_category=missing_key]"
            )
            return {}

        logger.info(
            f"OpenAI structured call initiated [provider=openai, model={self.model}, prompt_len={len(user_prompt)}]"
        )

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt + "\nYou MUST return valid JSON ONLY with no backticks."},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "max_tokens": 1000,
            }
            with httpx.Client(timeout=25.0) as client:
                res = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.warning(f"OpenAI structured call failed ({type(e).__name__}). Falling back.")
            return {}

    def _fallback_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Intelligent local fallback for general conversation and SQL generation
        when OpenAI is unconfigured or temporarily unavailable.
        """
        q = user_prompt.lower()
        is_ar = any(c in user_prompt for c in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي")

        # Check if prompt is for exploratory SQL generation
        if "sql" in system_prompt.lower() or "enterprise sql" in system_prompt.lower():
            for bad in ["drop ", "delete ", "update ", "insert ", "truncate ", "alter ", "exec "]:
                if bad in q:
                    raw_q = user_prompt.split("User Question:")[-1].split("\n")[0].strip()
                    return raw_q
            if "product" in q or "منتج" in q:
                return "SELECT pr.name AS product, ROUND(CAST(SUM(si.total_amount) AS NUMERIC), 2) AS total_sales FROM sales s JOIN sale_items si ON s.id = si.sale_id JOIN products pr ON si.product_id = pr.id WHERE s.status = 'Completed' GROUP BY pr.id, pr.name ORDER BY total_sales DESC LIMIT 10;"
            return "SELECT b.name AS branch, ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_sales FROM sales s JOIN branches b ON s.branch_id = b.id WHERE s.status = 'Completed' GROUP BY b.id, b.name ORDER BY total_sales DESC LIMIT 10;"

        # 1. Difference between invoice and purchase order
        if ("invoice" in q and "purchase order" in q) or ("فاتورة" in q and "أمر شراء" in q) or ("الفرق" in q and ("فاتورة" in q or "شراء" in q)):
            if is_ar:
                return "الفرق الأساسي بين أمر الشراء والفاتورة:\n• **أمر الشراء (Purchase Order)**: مستند يصدره المشتري أولاً للالتزام بشراء سلع أو خدمات معينة قبل تسليمها.\n• **الفاتورة (Invoice)**: وثيقة يصدرها البائع لاحقاً بعد التسليم للمطالبة بالسداد وتعد سنداً مالياً لإثبات المديونية في النظام المحاسبي."
            return "Key differences between a Purchase Order and an Invoice:\n• **Purchase Order (PO)**: Issued by the buyer to authorize and confirm an order before delivery.\n• **Invoice**: Issued by the seller after delivery to request payment and record revenue in the accounts."

        # 2. Motivational quote
        if any(w in q for w in ["quote", "motivational", "حكمة", "اقتباس", "inspire", "inspiration"]):
            if is_ar:
                return "«النجاح في إدارة الأعمال ليس ضربة حظ، بل ثمرة التخطيط الدقيق، والبيانات الموثوقة، والعمل المنضبط والمستمر.»"
            return '"Success in business is the result of continuous preparation, disciplined execution, and learning from experience."'

        # 3. Greetings
        if any(w in q for w in ["hello", "hi", "hey", "good morning", "good afternoon", "greetings"]):
            return "Hello! How can I help you today? You can ask me general questions about ERP concepts or request real-time sales and inventory analytics."
        if any(w in q for w in ["مرحبا", "أهلا", "اهلا", "السلام عليكم", "صباح الخير", "مساء الخير"]):
            return "أهلاً بك! كيف يمكنني مساعدتك اليوم؟ يمكنك سؤالي عن المفاهيم العامة للـ ERP أو طلب تحليلات فورية للمبيعات والمخزون."

        # 4. Capabilities
        if any(w in q for w in ["what can you do", "what can you help me with", "help me", "capabilities", "features", "who are you"]):
            return (
                "I am your MMI ERP Assistant. Here is what I can do:\n\n"
                "1. **ERP Analytics**: Query sales trends, branch comparisons, top products, and inventory valuation.\n"
                "2. **Business Concepts**: Explain ERP terms such as purchase orders, invoices, chart of accounts, and supply chain.\n"
                "3. **Contextual Analysis**: Answer follow-ups like 'Which branch performed better?' or 'What about last month?'.\n\n"
                "How can I assist you right now?"
            )
        if any(w in q for w in ["ماذا يمكنك", "ما هي قدراتك", "كيف تساعدني", "من أنت", "من انت"]):
            return (
                "أنا مساعد نظام MMI للـ ERP. إليك ما يمكنني تقديمه:\n\n"
                "1. **تحليلات الـ ERP**: استعراض اتجاهات المبيعات، ومقارنة أداء الفروع، والمنتجات الأكثر مبيعاً، وتقييم المخزون.\n"
                "2. **المفاهيم الإدارية**: شرح مصطلحات الأعمال مثل أوامر الشراء، والفواتير، وسلسلة الإمداد.\n"
                "3. **تحليل المحادثة المتتابع**: الإجابة عن الأسئلة المترابطة مثل 'أي فرع كان أفضل؟' أو 'ماذا عن الشهر الماضي؟'.\n\n"
                "كيف ترغب أن أساعدك اليوم؟"
            )

        # 5. Invoice definition
        if "invoice" in q or "فاتورة" in q or "الفاتورة" in q:
            if is_ar:
                return "الفاتورة (Invoice) هي وثيقة تجارية ملزمة يصدرها البائع للمشتري توضح المنتجات أو الخدمات المقدمة وكمياتها وأسعارها المتفق عليها وشروط السداد، وتعد سنداً قانونياً لإثبات المعاملة في النظام المحاسبي."
            return "An invoice is a formal commercial document issued by a seller to a buyer. It itemizes the products or services delivered, quantities, agreed prices, applicable taxes, and payment terms, serving as a legally binding record for financial accounting."

        # 6. Purchase order definition
        if "purchase order" in q or "امر الشراء" in q or "أمر الشراء" in q or "po" in q:
            if is_ar:
                return "أمر الشراء (Purchase Order - PO) هو مستند رسمي يصدره المشتري إلى المورد يعبر فيه عن التزامه بشراء كميات محددة من السلع بأسعار وشروط تسليم محددة مسبقاً قبل استلام البضاعة أو الفاتورة."
            return "A Purchase Order (PO) is an official commercial document issued by a buyer committing to pay the seller for specific quantities of goods or services at agreed prices and delivery terms before fulfillment."

        # 7. ERP definition
        if "erp" in q or "تخطيط موارد" in q:
            if is_ar:
                return "نظام تخطيط موارد المؤسسات (ERP) هو برنامج متكامل يربط ويدير كافة العمليات والبيانات الأساسية للمنشأة، بما في ذلك المالية والمبيعات والمشتريات والمخزون والموارد البشرية في قاعدة بيانات موحدة."
            return "Enterprise Resource Planning (ERP) is an integrated business management software that unifies core corporate operations—including finance, sales, procurement, inventory, and supply chain—into a single centralized database and workflow."

        # 8. Thanks / Politeness
        if any(w in q for w in ["thank", "thanks", "appreciate", "شكرا", "مشكور"]):
            return "You are very welcome! Let me know if you need anything else." if not is_ar else "على الرحب والسعة! أنا في خدمتك دائماً لأي استفسار آخر."

        # 9. Goodbye
        if any(w in q for w in ["bye", "goodbye", "see you", "مع السلامة", "وداعا"]):
            return "Goodbye! Have a great day ahead." if not is_ar else "مع السلامة! نتمنى لك يوماً موفقاً ومثمراً."

        # Default general response
        if is_ar:
            return "أنا هنا للإجابة عن أسئلتك الإدارية ومساعدتك في استعراض بيانات الـ ERP. يمكنك سؤالي عن المبيعات، المخزون، أو المفاهيم المحاسبية."
        return "I am here to answer your enterprise questions and assist with ERP analytics. You can ask about sales trends, inventory, branch comparisons, or general business concepts."

def get_ai_provider() -> AIProvider:
    if settings.AI_PROVIDER.lower() == "openai":
        return OpenAIProvider()
    return OpenAIProvider()
