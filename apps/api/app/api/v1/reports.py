from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.reports import ReportDefinition, ReportPreviewResponse
from app.services.reports_service import reports_service
from app.services.export_service import export_service
from app.security.rbac import get_current_user, get_user_branch_filter
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", response_model=List[ReportDefinition])
def get_reports_catalog(current_user: User = Depends(get_current_user)):
    return reports_service.get_catalog()

@router.get("/{report_id}/preview", response_model=ReportPreviewResponse)
def get_report_preview(
    report_id: str,
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    branch_id = get_user_branch_filter(current_user)
    try:
        return reports_service.generate_report_data(db, report_id, branch_id=branch_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{report_id}/export")
def export_report(
    report_id: str,
    format: str = Query("xlsx", pattern="^(xlsx|pdf|docx|csv)$"),
    lang: str = Query("en", pattern="^(en|ar)$"),
    limit: int = Query(500, ge=1, le=2000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    branch_id = get_user_branch_filter(current_user)
    try:
        report_data = reports_service.generate_report_data(db, report_id, branch_id=branch_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    title = report_data.title_ar if lang == "ar" else report_data.title
    headers = report_data.column_headers_ar if lang == "ar" else report_data.column_headers

    if format == "xlsx":
        content = export_service.export_excel(title, report_data.columns, headers, report_data.data)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{report_id}_{lang}.xlsx"
    elif format == "pdf":
        content = export_service.export_pdf(title, report_data.columns, headers, report_data.data)
        media_type = "application/pdf"
        filename = f"{report_id}_{lang}.pdf"
    elif format == "docx":
        content = export_service.export_word(title, report_data.columns, headers, report_data.data)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{report_id}_{lang}.docx"
    elif format == "csv":
        content = export_service.export_csv(report_data.columns, headers, report_data.data)
        media_type = "text/csv; charset=utf-8"
        filename = f"{report_id}_{lang}.csv"
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
