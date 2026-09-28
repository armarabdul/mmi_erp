from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ReportDefinition(BaseModel):
    id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    category: str

class ReportPreviewResponse(BaseModel):
    report_id: str
    title: str
    title_ar: str
    columns: List[str]
    column_headers: Dict[str, str]
    column_headers_ar: Dict[str, str]
    data: List[Dict[str, Any]]
    total_count: int
    generated_at: str
    branch_restricted: bool
