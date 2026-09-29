from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class AnalyticsQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    language: str = Field(default="en", pattern="^(en|ar)$")
    conversation_id: Optional[str] = None

class ChartMetadata(BaseModel):
    chart_type: str  # bar, line, pie, donut, area, table, kpi, none
    title: str
    subtitle: Optional[str] = None
    x_axis_key: Optional[str] = None
    y_axis_key: Optional[str] = None
    series_keys: Optional[List[str]] = None
    data: List[Dict[str, Any]]

class TechnicalDetails(BaseModel):
    audit_id: int
    execution_time_ms: float
    result_row_count: int
    validated_sql: str
    model_used: str
    ai_provider: str
    branch_restricted: bool
    ai_call_status: Optional[str] = None
    error_category: Optional[str] = None

class AnalyticsQueryResponse(BaseModel):
    question: str
    language: str
    success: bool
    explanation: str
    visualization: ChartMetadata
    table_columns: List[str]
    table_data: List[Dict[str, Any]]
    filters_applied: Dict[str, Any]
    data_source: str = "Demo ERP Analytics Database"
    technical_details: TechnicalDetails
    error_message: Optional[str] = None
    intent: Optional[str] = "ERP_ANALYTICS"
    conversation_id: Optional[str] = None

class ConversationMessageSchema(BaseModel):
    id: int
    conversation_id: str
    user_id: int
    role: str
    user_message: str
    assistant_response: str
    detected_intent: str
    timestamp: datetime
    audit_reference: Optional[int] = None

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    total_messages: int
    messages: List[ConversationMessageSchema]

class ConversationSummaryItem(BaseModel):
    conversation_id: str
    last_message: str
    last_response: str
    last_intent: str
    updated_at: datetime
    message_count: int

class ConversationListResponse(BaseModel):
    conversations: List[ConversationSummaryItem]

class UserPreferenceSchema(BaseModel):
    preferred_language: str = Field(default="en", pattern="^(en|ar)$")
    preferred_response_style: str = Field(default="concise", pattern="^(concise|detailed|executive)$")
    preferred_report_format: str = Field(default="table_and_chart", pattern="^(table_and_chart|chart_only|table_only)$")
    terminology_preference: str = Field(default="standard", pattern="^(standard|formal|technical)$")

class UserPreferenceResponse(UserPreferenceSchema):
    user_id: int
