from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditListResponse, AuditLogItem
from app.security.rbac import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("", response_model=AuditListResponse)
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    success: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["Admin", "Analyst"])),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)

    if success is not None:
        query = query.filter(AuditLog.success == success)
    if search:
        query = query.filter(AuditLog.user_question.ilike(f"%{search}%"))

    total_count = query.count()
    items = (
        query.order_by(desc(AuditLog.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AuditListResponse(
        items=items,
        total_count=total_count,
        page=page,
        page_size=page_size,
    )

@router.get("/{audit_id}", response_model=AuditLogItem)
def get_audit_detail(
    audit_id: int,
    current_user: User = Depends(require_role(["Admin", "Analyst"])),
    db: Session = Depends(get_db),
):
    item = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Audit log entry not found")
    return item
