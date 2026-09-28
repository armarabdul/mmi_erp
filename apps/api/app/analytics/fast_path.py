import re
from typing import Optional, Dict, Any, Tuple
from datetime import date
from app.analytics.semantic_layer import semantic_layer

class FastPathResult:
    def __init__(
        self,
        intent: str,
        kpi: str,
        dimension: Optional[str],
        date_filter: Optional[str],
        limit: int,
        generated_sql: str,
        chart_type: str,
        chart_title: str,
        chart_title_ar: str,
        x_axis_key: str,
        y_axis_key: str,
    ):
        self.intent = intent
        self.kpi = kpi
        self.dimension = dimension
        self.date_filter = date_filter
        self.limit = limit
        self.generated_sql = generated_sql
        self.chart_type = chart_type
        self.chart_title = chart_title
        self.chart_title_ar = chart_title_ar
        self.x_axis_key = x_axis_key
        self.y_axis_key = y_axis_key

class FastPathAnalyzer:
    @staticmethod
    def match(question: str, language: str = "en") -> Optional[FastPathResult]:
        q = question.strip().lower()

        # 1. Check for unsafe keywords early
        for bad in ["drop ", "delete ", "update ", "insert ", "truncate ", "alter ", "exec "]:
            if bad in q:
                # Let SQL guard handle rejection
                return None

        # Scenario 1 & 2: Sales by branch this month / المبيعات حسب الفرع هذا الشهر
        is_branch_sales = (
            ("sales by branch" in q or "branch sales" in q or "sales per branch" in q or "by branch" in q) or
            ("المبيعات حسب الفرع" in q or "مبيعات الفروع" in q or "حسب الفرع" in q or "لكل فرع" in q)
        )
        is_this_month = (
            ("this month" in q or "current month" in q or "september" in q) or
            ("هذا الشهر" in q or "الشهر الحالي" in q or "سبتمبر" in q)
        )

        # Highest sales branch
        is_highest_branch = (
            ("highest sales" in q and "branch" in q) or
            ("top branch" in q or "best branch" in q or "best performing branch" in q) or
            ("أعلى مبيعات" in q and "فرع" in q) or
            ("اعلى مبيعات" in q and "فرع" in q) or
            ("أفضل فرع" in q or "افضل فرع" in q)
        )
        if is_highest_branch:
            sql = """SELECT b.name AS branch, 
       ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_sales,
       COUNT(s.id) AS order_count
FROM sales s
JOIN branches b ON s.branch_id = b.id
WHERE s.status = 'Completed'
GROUP BY b.id, b.name
ORDER BY total_sales DESC
LIMIT 1"""
            return FastPathResult(
                intent="kpi_highest_sales_branch",
                kpi="total_sales",
                dimension="branch",
                date_filter=None,
                limit=1,
                generated_sql=sql,
                chart_type="bar",
                chart_title="Highest Performing Branch by Sales",
                chart_title_ar="الفرع الأعلى مبيعات",
                x_axis_key="branch",
                y_axis_key="total_sales",
            )

        # Total sales value this month
        is_total_month_sales = (
            (("total sales" in q or "sales value" in q) and ("this month" in q or "current month" in q or "september" in q)) or
            ("إجمالي المبيعات هذا الشهر" in q or "اجمالي المبيعات هذا الشهر" in q or "مبيعات الشهر الحالي" in q)
        )
        if is_total_month_sales:
            sql = """SELECT 'September 2026' AS period,
       ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_sales,
       COUNT(s.id) AS order_count
FROM sales s
WHERE s.status = 'Completed' AND s.sale_date >= '2026-09-01' AND s.sale_date <= '2026-09-30'"""
            return FastPathResult(
                intent="kpi_total_sales_this_month",
                kpi="total_sales",
                dimension="date",
                date_filter="2026-09",
                limit=1,
                generated_sql=sql,
                chart_type="bar",
                chart_title="Total Sales Value — September 2026",
                chart_title_ar="إجمالي قيمة المبيعات — سبتمبر 2026",
                x_axis_key="period",
                y_axis_key="total_sales",
            )

        if is_branch_sales:
            date_where = "WHERE s.status = 'Completed'"
            title = "Sales by Branch"
            title_ar = "المبيعات حسب الفرع"
            if is_this_month:
                date_where += " AND s.sale_date >= '2026-09-01' AND s.sale_date <= '2026-09-30'"
                title = "Sales by Branch — September 2026"
                title_ar = "المبيعات حسب الفرع — سبتمبر 2026"

            sql = f"""SELECT b.name AS branch, 
       ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_sales,
       COUNT(s.id) AS order_count
FROM sales s
JOIN branches b ON s.branch_id = b.id
{date_where}
GROUP BY b.id, b.name
ORDER BY total_sales DESC"""

            return FastPathResult(
                intent="kpi_sales_by_branch",
                kpi="total_sales",
                dimension="branch",
                date_filter="2026-09" if is_this_month else None,
                limit=10,
                generated_sql=sql,
                chart_type="bar",
                chart_title=title,
                chart_title_ar=title_ar,
                x_axis_key="branch",
                y_axis_key="total_sales",
            )

        # Scenario 3: Top products / أفضل المنتجات
        is_top_products = (
            ("top" in q and "product" in q) or
            ("best selling" in q or "highest selling" in q) or
            ("أفضل المنتجات" in q or "اعلى المنتجات" in q or "أكثر المنتجات مبيعا" in q or "افضل 10 منتجات" in q or "أفضل 10 منتجات" in q)
        )
        if is_top_products:
            limit = 10
            limit_match = re.search(r"\b(\d+)\b", q)
            if limit_match:
                limit = min(int(limit_match.group(1)), 50)

            sql = f"""SELECT pr.name AS product,
       cat.name AS category,
       SUM(si.quantity) AS units_sold,
       ROUND(CAST(SUM(si.total_amount) AS NUMERIC), 2) AS total_sales
FROM sales s
JOIN sale_items si ON s.id = si.sale_id
JOIN products pr ON si.product_id = pr.id
JOIN categories cat ON pr.category_id = cat.id
WHERE s.status = 'Completed'
GROUP BY pr.id, pr.name, cat.name
ORDER BY total_sales DESC
LIMIT {limit}"""

            return FastPathResult(
                intent="kpi_top_products",
                kpi="total_sales",
                dimension="product",
                date_filter=None,
                limit=limit,
                generated_sql=sql,
                chart_type="bar",
                chart_title=f"Top {limit} Products by Sales Revenue",
                chart_title_ar=f"أفضل {limit} منتجات من حيث إيرادات المبيعات",
                x_axis_key="product",
                y_axis_key="total_sales",
            )

        # Scenario 4: Trend / Monthly sales for last 12 months / المبيعات الشهرية لآخر 12 شهرا
        is_monthly_trend = (
            ("monthly sales" in q or "sales trend" in q or "sales for the last 12 months" in q or "last 12 months" in q or "monthly trend" in q) or
            ("المبيعات الشهرية" in q or "اتجاه المبيعات" in q or "آخر 12 شهر" in q or "اخر 12 شهر" in q)
        )
        if is_monthly_trend:
            from app.core.database import engine
            period_expr = "to_char(s.sale_date, 'YYYY-MM')" if engine.dialect.name == "postgresql" else "strftime('%Y-%m', s.sale_date)"
            sql = f"""SELECT {period_expr} AS period,
       ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_sales,
       COUNT(s.id) AS order_count
FROM sales s
WHERE s.status = 'Completed' AND s.sale_date >= '2025-10-01' AND s.sale_date <= '2026-09-30'
GROUP BY period
ORDER BY period ASC"""

            return FastPathResult(
                intent="kpi_monthly_sales_trend",
                kpi="total_sales",
                dimension="date",
                date_filter="last_12_months",
                limit=12,
                generated_sql=sql,
                chart_type="line",
                chart_title="Monthly Sales Trend (Last 12 Months)",
                chart_title_ar="اتجاه المبيعات الشهرية (آخر 12 شهراً)",
                x_axis_key="period",
                y_axis_key="total_sales",
            )

        # Outstanding orders
        is_outstanding = (
            ("outstanding orders" in q or "pending orders" in q or "unfulfilled" in q) or
            ("الطلبات المعلقة" in q or "طلبات قيد الانتظار" in q)
        )
        if is_outstanding:
            sql = """SELECT b.name AS branch,
       COUNT(s.id) AS order_count,
       ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_sales
FROM sales s
JOIN branches b ON s.branch_id = b.id
WHERE s.status = 'Pending'
GROUP BY b.id, b.name
ORDER BY order_count DESC"""

            return FastPathResult(
                intent="kpi_outstanding_orders",
                kpi="order_count",
                dimension="branch",
                date_filter=None,
                limit=10,
                generated_sql=sql,
                chart_type="bar",
                chart_title="Outstanding Pending Orders by Branch",
                chart_title_ar="الطلبات المعلقة حسب الفرع",
                x_axis_key="branch",
                y_axis_key="order_count",
            )

        # Inventory by branch
        is_inventory_branch = (
            ("inventory by branch" in q or "stock by branch" in q or "inventory value" in q) or
            ("المخزون حسب الفرع" in q or "قيمة المخزون" in q or "المستودع حسب الفرع" in q)
        )
        if is_inventory_branch:
            sql = """SELECT b.name AS branch,
       ROUND(CAST(SUM(i.quantity * pr.cost) AS NUMERIC), 2) AS inventory_value,
       SUM(i.quantity) AS total_units
FROM inventory i
JOIN branches b ON i.branch_id = b.id
JOIN products pr ON i.product_id = pr.id
GROUP BY b.id, b.name
ORDER BY inventory_value DESC"""

            return FastPathResult(
                intent="kpi_inventory_by_branch",
                kpi="inventory_value",
                dimension="branch",
                date_filter=None,
                limit=10,
                generated_sql=sql,
                chart_type="pie",
                chart_title="Inventory Valuation by Branch",
                chart_title_ar="تقييم المخزون المالي حسب الفرع",
                x_axis_key="branch",
                y_axis_key="inventory_value",
            )

        # Sales by Category
        is_cat_sales = (
            ("sales by category" in q or "revenue by category" in q) or
            ("المبيعات حسب الفئة" in q or "المبيعات حسب التصنيف" in q)
        )
        if is_cat_sales:
            sql = """SELECT cat.name AS category,
       ROUND(CAST(SUM(si.total_amount) AS NUMERIC), 2) AS total_sales,
       SUM(si.quantity) AS units_sold
FROM sales s
JOIN sale_items si ON s.id = si.sale_id
JOIN products pr ON si.product_id = pr.id
JOIN categories cat ON pr.category_id = cat.id
WHERE s.status = 'Completed'
GROUP BY cat.id, cat.name
ORDER BY total_sales DESC"""

            return FastPathResult(
                intent="kpi_sales_by_category",
                kpi="total_sales",
                dimension="category",
                date_filter=None,
                limit=10,
                generated_sql=sql,
                chart_type="pie",
                chart_title="Sales Distribution by Product Category",
                chart_title_ar="توزيع المبيعات حسب فئة المنتجات",
                x_axis_key="category",
                y_axis_key="total_sales",
            )

        return None

fast_path_analyzer = FastPathAnalyzer()
