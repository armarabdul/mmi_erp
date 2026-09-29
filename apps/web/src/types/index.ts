export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'Admin' | 'Branch Manager' | 'Analyst';
  branch_id?: number | null;
  branch_name?: string | null;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface KPICardData {
  id: string;
  title: string;
  title_ar: string;
  value: number;
  formatted_value: string;
  unit: string;
  change_pct: number;
  trend: 'up' | 'down' | 'neutral';
  subtitle: string;
  subtitle_ar: string;
}

export interface SalesTrendPoint {
  period: string;
  sales: number;
  orders_count: number;
}

export interface BranchSalesPoint {
  branch_id: number;
  branch_name: string;
  sales: number;
  percentage: number;
}

export interface TopProductPoint {
  product_id: number;
  product_name: string;
  sku: string;
  category_name: string;
  units_sold: number;
  total_revenue: number;
}

export interface RecentActivityItem {
  id: number;
  user_role: string;
  question: string;
  timestamp: string;
  chart_type: string;
  success: boolean;
}

export interface DashboardData {
  kpis: KPICardData[];
  sales_trend: SalesTrendPoint[];
  sales_by_branch: BranchSalesPoint[];
  top_products: TopProductPoint[];
  recent_activity: RecentActivityItem[];
  is_branch_restricted: boolean;
  restricted_branch_name?: string | null;
}

export interface ChartMetadata {
  chart_type: 'bar' | 'line' | 'pie' | 'donut' | 'area' | 'table' | 'kpi' | 'none';
  title: string;
  subtitle?: string | null;
  x_axis_key?: string | null;
  y_axis_key?: string | null;
  series_keys?: string[] | null;
  data: Record<string, any>[];
}

export interface TechnicalDetails {
  audit_id: number;
  execution_time_ms: number;
  result_row_count: number;
  validated_sql: string;
  model_used: string;
  ai_provider: string;
  branch_restricted: boolean;
}

export interface AnalyticsQueryResponse {
  question: string;
  language: string;
  success: boolean;
  explanation: string;
  visualization: ChartMetadata;
  table_columns: string[];
  table_data: Record<string, any>[];
  filters_applied: Record<string, any>;
  data_source: string;
  technical_details: TechnicalDetails;
  error_message?: string | null;
  intent?: 'GENERAL_CONVERSATION' | 'ERP_ANALYTICS' | 'CONTEXTUAL' | string;
  conversation_id?: string | null;
}

export interface ReportDefinition {
  id: string;
  name: string;
  name_ar: string;
  description: string;
  description_ar: string;
  category: string;
}

export interface ReportPreviewResponse {
  report_id: string;
  title: string;
  title_ar: string;
  columns: string[];
  column_headers: Record<string, string>;
  column_headers_ar: Record<string, string>;
  data: Record<string, any>[];
  total_count: number;
  generated_at: string;
  branch_restricted: boolean;
}

export interface AuditLogItem {
  id: number;
  user_id?: number | null;
  user_role?: string | null;
  branch_id?: number | null;
  timestamp: string;
  language: string;
  user_question: string;
  conversation_id?: string | null;
  ai_provider?: string | null;
  model?: string | null;
  generated_sql?: string | null;
  validated_sql?: string | null;
  execution_time_ms?: number | null;
  result_row_count?: number | null;
  chart_type?: string | null;
  success: boolean;
  error_message?: string | null;
  final_response?: string | null;
  token_count?: number | null;
}

export interface AuditListResponse {
  items: AuditLogItem[];
  total_count: number;
  page: number;
  page_size: number;
}
