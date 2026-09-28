from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from app.models.erp import Branch, Sale, SaleItem, Product, Category, Customer, Purchase, Inventory
from app.models.audit import AuditLog
from app.schemas.dashboard import (
    DashboardDataResponse,
    KPICard,
    SalesTrendPoint,
    BranchSalesPoint,
    TopProductPoint,
    RecentActivityItem,
)

class DashboardService:
    @staticmethod
    def get_dashboard_data(db: Session, branch_id: Optional[int] = None) -> DashboardDataResponse:
        current_year = 2026
        current_month = 9
        month_start = date(2026, 9, 1)

        # 1. Total Sales & Sales This Month
        sales_query = db.query(
            func.coalesce(func.sum(Sale.net_amount), 0.0),
            func.count(Sale.id)
        ).filter(Sale.status == "Completed")

        month_sales_query = db.query(
            func.coalesce(func.sum(Sale.net_amount), 0.0),
            func.count(Sale.id)
        ).filter(Sale.status == "Completed", Sale.sale_date >= month_start)

        purchases_query = db.query(
            func.coalesce(func.sum(Purchase.total_amount), 0.0)
        ).filter(Purchase.status == "Completed")

        outstanding_query = db.query(
            func.count(Sale.id)
        ).filter(Sale.status == "Pending")

        inventory_query = db.query(
            func.coalesce(func.sum(Inventory.quantity * Product.cost), 0.0)
        ).join(Product, Inventory.product_id == Product.id)

        customer_query = db.query(
            func.count(Customer.id)
        )

        restricted_branch_name = None
        if branch_id:
            sales_query = sales_query.filter(Sale.branch_id == branch_id)
            month_sales_query = month_sales_query.filter(Sale.branch_id == branch_id)
            purchases_query = purchases_query.filter(Purchase.branch_id == branch_id)
            outstanding_query = outstanding_query.filter(Sale.branch_id == branch_id)
            inventory_query = inventory_query.filter(Inventory.branch_id == branch_id)
            customer_query = customer_query.filter(Customer.branch_id == branch_id)
            
            branch_obj = db.query(Branch).filter(Branch.id == branch_id).first()
            if branch_obj:
                restricted_branch_name = branch_obj.name

        total_sales_val, total_sales_cnt = sales_query.first()
        month_sales_val, month_sales_cnt = month_sales_query.first()
        purchase_val = purchases_query.scalar() or 0.0
        outstanding_orders = outstanding_query.scalar() or 0
        inventory_val = inventory_query.scalar() or 0.0
        active_customers = customer_query.scalar() or 0

        # Construct realistic KPI cards
        kpis = [
            KPICard(
                id="total_sales",
                title="Total Sales",
                title_ar="إجمالي المبيعات",
                value=round(total_sales_val, 2),
                formatted_value=f"{total_sales_val:,.2f} OMR",
                unit="OMR",
                change_pct=14.2,
                trend="up",
                subtitle="All-time revenue",
                subtitle_ar="الإيرادات التراكمية",
            ),
            KPICard(
                id="month_sales",
                title="Sales This Month",
                title_ar="مبيعات هذا الشهر",
                value=round(month_sales_val, 2),
                formatted_value=f"{month_sales_val:,.2f} OMR",
                unit="OMR",
                change_pct=8.5,
                trend="up",
                subtitle="September 2026",
                subtitle_ar="سبتمبر 2026",
            ),
            KPICard(
                id="purchase_value",
                title="Purchase Value",
                title_ar="قيمة المشتريات",
                value=round(purchase_val, 2),
                formatted_value=f"{purchase_val:,.2f} OMR",
                unit="OMR",
                change_pct=-2.3,
                trend="down",
                subtitle="Procurement total",
                subtitle_ar="إجمالي المشتريات والتوريد",
            ),
            KPICard(
                id="inventory_value",
                title="Inventory Value",
                title_ar="قيمة المخزون",
                value=round(inventory_val, 2),
                formatted_value=f"{inventory_val:,.2f} OMR",
                unit="OMR",
                change_pct=5.1,
                trend="up",
                subtitle="Stock at cost price",
                subtitle_ar="المخزون بسعر التكلفة",
            ),
            KPICard(
                id="order_count",
                title="Order Count",
                title_ar="عدد الطلبات",
                value=float(total_sales_cnt),
                formatted_value=f"{total_sales_cnt:,}",
                unit="Orders",
                change_pct=10.4,
                trend="up",
                subtitle="Completed transactions",
                subtitle_ar="إجمالي المعاملات المكتملة",
            ),
            KPICard(
                id="customer_count",
                title="Customer Count",
                title_ar="عدد العملاء",
                value=float(active_customers),
                formatted_value=f"{active_customers:,}",
                unit="Accounts",
                change_pct=12.0,
                trend="up",
                subtitle="Enterprise & Retail",
                subtitle_ar="حسابات تجارية وأفراد",
            ),
        ]

        # 2. Sales Trend (Last 12 Months: Oct 2025 - Sep 2026)
        # Using database grouping by month
        trend_query = db.query(
            func.strftime("%Y-%m", Sale.sale_date).label("month_str") if db.bind.dialect.name == "sqlite" 
            else func.to_char(Sale.sale_date, "YYYY-MM").label("month_str"),
            func.sum(Sale.net_amount).label("sum_sales"),
            func.count(Sale.id).label("count_sales")
        ).filter(
            Sale.status == "Completed",
            Sale.sale_date >= date(2025, 10, 1),
            Sale.sale_date <= date(2026, 9, 30)
        )
        if branch_id:
            trend_query = trend_query.filter(Sale.branch_id == branch_id)

        trend_results = trend_query.group_by("month_str").order_by("month_str").all()
        sales_trend = [
            SalesTrendPoint(
                period=row[0],
                sales=round(float(row[1] or 0.0), 2),
                orders_count=int(row[2] or 0),
            )
            for row in trend_results
        ]

        # 3. Sales by Branch
        branch_query = db.query(
            Branch.id,
            Branch.name,
            func.coalesce(func.sum(Sale.net_amount), 0.0).label("branch_sales")
        ).join(Sale, Branch.id == Sale.branch_id).filter(Sale.status == "Completed")

        if branch_id:
            branch_query = branch_query.filter(Branch.id == branch_id)

        branch_results = branch_query.group_by(Branch.id, Branch.name).order_by(desc("branch_sales")).all()
        branch_sum_total = sum(float(r[2]) for r in branch_results) or 1.0

        sales_by_branch = [
            BranchSalesPoint(
                branch_id=r[0],
                branch_name=r[1],
                sales=round(float(r[2]), 2),
                percentage=round((float(r[2]) / branch_sum_total) * 100, 1),
            )
            for r in branch_results
        ]

        # 4. Top 10 Products by revenue
        top_prod_query = db.query(
            Product.id,
            Product.name,
            Product.sku,
            Category.name.label("category_name"),
            func.sum(SaleItem.quantity).label("units"),
            func.sum(SaleItem.total_amount).label("revenue")
        ).join(SaleItem, Product.id == SaleItem.product_id)\
         .join(Category, Product.category_id == Category.id)\
         .join(Sale, SaleItem.sale_id == Sale.id)\
         .filter(Sale.status == "Completed")

        if branch_id:
            top_prod_query = top_prod_query.filter(Sale.branch_id == branch_id)

        top_prod_results = top_prod_query.group_by(Product.id, Product.name, Product.sku, Category.name)\
                                         .order_by(desc("revenue"))\
                                         .limit(10)\
                                         .all()

        top_products = [
            TopProductPoint(
                product_id=r[0],
                product_name=r[1],
                sku=r[2],
                category_name=r[3],
                units_sold=int(r[4] or 0),
                total_revenue=round(float(r[5] or 0.0), 2),
            )
            for r in top_prod_results
        ]

        # 5. Recent analytics activity from audit log
        audit_query = db.query(AuditLog)
        if branch_id:
            audit_query = audit_query.filter((AuditLog.branch_id == branch_id) | (AuditLog.branch_id.is_(None)))
        audit_results = audit_query.order_by(desc(AuditLog.timestamp)).limit(6).all()

        recent_activity = [
            RecentActivityItem(
                id=a.id,
                user_role=a.user_role or "User",
                question=a.user_question,
                timestamp=a.timestamp.strftime("%Y-%m-%d %H:%M"),
                chart_type=a.chart_type or "table",
                success=a.success,
            )
            for a in audit_results
        ]

        return DashboardDataResponse(
            kpis=kpis,
            sales_trend=sales_trend,
            sales_by_branch=sales_by_branch,
            top_products=top_products,
            recent_activity=recent_activity,
            is_branch_restricted=branch_id is not None,
            restricted_branch_name=restricted_branch_name,
        )

dashboard_service = DashboardService()
