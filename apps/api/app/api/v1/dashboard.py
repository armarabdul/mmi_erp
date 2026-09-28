from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.dashboard import DashboardDataResponse
from app.services.dashboard_service import dashboard_service
from app.security.rbac import get_current_user, get_user_branch_filter
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardDataResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    branch_id = get_user_branch_filter(current_user)
    return dashboard_service.get_dashboard_data(db, branch_id=branch_id)
