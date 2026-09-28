from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsQueryResponse
from app.ai.workflow import analytics_workflow
from app.security.rbac import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["AI Analytics"])

@router.post("/query", response_model=AnalyticsQueryResponse)
def execute_analytics_query(
    request: AnalyticsQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return analytics_workflow.execute_workflow(db, current_user, request)
