from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class KPICard(BaseModel):
    id: str
    title: str
    title_ar: str
    value: float
    formatted_value: str
    unit: str
    change_pct: float
    trend: str  # up, down, neutral
    subtitle: str
    subtitle_ar: str

class SalesTrendPoint(BaseModel):
    period: str
    sales: float
    orders_count: int

class BranchSalesPoint(BaseModel):
    branch_id: int
    branch_name: str
    sales: float
    percentage: float

class TopProductPoint(BaseModel):
    product_id: int
    product_name: str
    sku: str
    category_name: str
    units_sold: int
    total_revenue: float

class RecentActivityItem(BaseModel):
    id: int
    user_role: str
    question: str
    timestamp: str
    chart_type: str
    success: bool

class DashboardDataResponse(BaseModel):
    kpis: List[KPICard]
    sales_trend: List[SalesTrendPoint]
    sales_by_branch: List[BranchSalesPoint]
    top_products: List[TopProductPoint]
    recent_activity: List[RecentActivityItem]
    is_branch_restricted: bool
    restricted_branch_name: Optional[str] = None
