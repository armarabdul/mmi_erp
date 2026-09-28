from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AuditLogItem(BaseModel):
    id: int
    user_id: Optional[int]
    user_role: Optional[str]
    branch_id: Optional[int]
    timestamp: datetime
    language: str
    user_question: str
    conversation_id: Optional[str]
    ai_provider: Optional[str]
    model: Optional[str]
    generated_sql: Optional[str]
    validated_sql: Optional[str]
    execution_time_ms: Optional[float]
    result_row_count: Optional[int]
    chart_type: Optional[str]
    success: bool
    error_message: Optional[str]
    final_response: Optional[str]
    token_count: Optional[int]

    model_config = ConfigDict(from_attributes=True)

class AuditListResponse(BaseModel):
    items: List[AuditLogItem]
    total_count: int
    page: int
    page_size: int
