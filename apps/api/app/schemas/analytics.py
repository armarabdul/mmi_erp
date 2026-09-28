from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AnalyticsQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    language: str = Field(default="en", pattern="^(en|ar)$")
    conversation_id: Optional[str] = None

class ChartMetadata(BaseModel):
    chart_type: str  # bar, line, pie, donut, area, table, kpi
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
