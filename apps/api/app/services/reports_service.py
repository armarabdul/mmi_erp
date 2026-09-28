from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.erp import Branch, Product, Category, Sale, SaleItem, Inventory
from app.schemas.reports import ReportDefinition, ReportPreviewResponse

REPORTS_CATALOG = [
    ReportDefinition(
        id="sales-summary",
        name="Sales Summary Report",
        name_ar="تقرير ملخص المبيعات",
        description="Comprehensive breakdown of completed transactions, VAT, discounts and net revenue.",
        description_ar="تحليل شامل للمبيعات المكتملة، ضريبة القيمة المضافة، والخصومات وصافي الإيرادات.",
        category="Sales",
    ),
    ReportDefinition(
        id="sales-by-branch",
        name="Sales by Branch Report",
        name_ar="تقرير المبيعات حسب الفروع",
        description="Branch revenue comparison, order volumes, and average ticket size.",
        description_ar="مقارنة إيرادات الفروع، أحجام الطلبات، ومتوسط قيمة الفاتورة.",
        category="Sales",
    ),
    ReportDefinition(
        id="product-performance",
        name="Product Performance Report",
        name_ar="تقرير أداء المنتجات",
        description="Units moved, revenue generated, and category ranking across catalog items.",
        description_ar="حجم الكميات المباعة، الإيرادات المحققة، وترتيب الأصناف حسب الفئات.",
        category="Inventory & Sales",
    ),
    ReportDefinition(
        id="inventory-summary",
        name="Inventory Valuation Summary",
        name_ar="تقرير تقييم المخزون والمستودعات",
        description="Stock quantities on hand, reorder thresholds, unit costs, and inventory asset valuation.",
        description_ar="كميات البضائع المتاحة، حدود إعادة الطلب، تكلفة الوحدة، وإجمالي قيمة المخزون.",
        category="Inventory",
    ),
]

class ReportsService:
    @staticmethod
    def get_catalog() -> List[ReportDefinition]:
        return REPORTS_CATALOG

    @staticmethod
    def generate_report_data(
        db: Session,
        report_id: str,
        branch_id: Optional[int] = None,
        limit: int = 200,
    ) -> ReportPreviewResponse:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        if report_id == "sales-summary":
            query = db.query(
                Sale.invoice_number,
                Sale.sale_date,
                Branch.name.label("branch_name"),
                Sale.gross_amount,
                Sale.discount,
                Sale.tax,
                Sale.net_amount,
                Sale.status,
            ).join(Branch, Sale.branch_id == Branch.id)
            if branch_id:
                query = query.filter(Sale.branch_id == branch_id)
            records = query.order_by(desc(Sale.sale_date)).limit(limit).all()

            data = [
                {
                    "invoice_number": r[0],
                    "sale_date": str(r[1]),
                    "branch": r[2],
                    "gross_amount": round(float(r[3]), 2),
                    "discount": round(float(r[4]), 2),
                    "tax": round(float(r[5]), 2),
                    "net_amount": round(float(r[6]), 2),
                    "status": r[7],
                }
                for r in records
            ]
            return ReportPreviewResponse(
                report_id=report_id,
                title="Sales Summary Report",
                title_ar="تقرير ملخص المبيعات",
                columns=["invoice_number", "sale_date", "branch", "gross_amount", "discount", "tax", "net_amount", "status"],
                column_headers={
                    "invoice_number": "Invoice #",
                    "sale_date": "Date",
                    "branch": "Branch",
                    "gross_amount": "Gross (OMR)",
                    "discount": "Discount (OMR)",
                    "tax": "VAT (OMR)",
                    "net_amount": "Net Amount (OMR)",
                    "status": "Status",
                },
                column_headers_ar={
                    "invoice_number": "رقم الفاتورة",
                    "sale_date": "التاريخ",
                    "branch": "الفرع",
                    "gross_amount": "الإجمالي (ر.ع)",
                    "discount": "الخصم (ر.ع)",
                    "tax": "الضريبة (ر.ع)",
                    "net_amount": "الصافي (ر.ع)",
                    "status": "الحالة",
                },
                data=data,
                total_count=len(data),
                generated_at=now_str,
                branch_restricted=branch_id is not None,
            )

        elif report_id == "sales-by-branch":
            query = db.query(
                Branch.name.label("branch_name"),
                Branch.city,
                Branch.region,
                func.count(Sale.id).label("orders_count"),
                func.sum(Sale.net_amount).label("total_sales"),
                func.avg(Sale.net_amount).label("avg_order_value"),
            ).join(Sale, Branch.id == Sale.branch_id).filter(Sale.status == "Completed")
            if branch_id:
                query = query.filter(Branch.id == branch_id)
            records = query.group_by(Branch.id, Branch.name, Branch.city, Branch.region).order_by(desc("total_sales")).all()

            data = [
                {
                    "branch": r[0],
                    "city": r[1],
                    "region": r[2],
                    "orders_count": int(r[3]),
                    "total_sales": round(float(r[4] or 0.0), 2),
                    "avg_order_value": round(float(r[5] or 0.0), 2),
                }
                for r in records
            ]
            return ReportPreviewResponse(
                report_id=report_id,
                title="Sales by Branch Report",
                title_ar="تقرير المبيعات حسب الفروع",
                columns=["branch", "city", "region", "orders_count", "total_sales", "avg_order_value"],
                column_headers={
                    "branch": "Branch Name",
                    "city": "City",
                    "region": "Region",
                    "orders_count": "Orders Count",
                    "total_sales": "Total Sales (OMR)",
                    "avg_order_value": "Avg Order (OMR)",
                },
                column_headers_ar={
                    "branch": "اسم الفرع",
                    "city": "المدينة",
                    "region": "المنطقة",
                    "orders_count": "عدد الطلبات",
                    "total_sales": "إجمالي المبيعات (ر.ع)",
                    "avg_order_value": "متوسط الطلب (ر.ع)",
                },
                data=data,
                total_count=len(data),
                generated_at=now_str,
                branch_restricted=branch_id is not None,
            )

        elif report_id == "product-performance":
            query = db.query(
                Product.sku,
                Product.name.label("product_name"),
                Category.name.label("category_name"),
                Product.price,
                Product.cost,
                func.sum(SaleItem.quantity).label("units_sold"),
                func.sum(SaleItem.total_amount).label("total_revenue"),
            ).join(SaleItem, Product.id == SaleItem.product_id)\
             .join(Category, Product.category_id == Category.id)\
             .join(Sale, SaleItem.sale_id == Sale.id)\
             .filter(Sale.status == "Completed")
            if branch_id:
                query = query.filter(Sale.branch_id == branch_id)
            records = query.group_by(Product.id, Product.sku, Product.name, Category.name, Product.price, Product.cost)\
                           .order_by(desc("total_revenue")).limit(limit).all()

            data = [
                {
                    "sku": r[0],
                    "product": r[1],
                    "category": r[2],
                    "unit_price": round(float(r[3]), 2),
                    "unit_cost": round(float(r[4]), 2),
                    "units_sold": int(r[5] or 0),
                    "total_revenue": round(float(r[6] or 0.0), 2),
                }
                for r in records
            ]
            return ReportPreviewResponse(
                report_id=report_id,
                title="Product Performance Report",
                title_ar="تقرير أداء المنتجات",
                columns=["sku", "product", "category", "unit_price", "unit_cost", "units_sold", "total_revenue"],
                column_headers={
                    "sku": "SKU",
                    "product": "Product Name",
                    "category": "Category",
                    "unit_price": "Unit Price (OMR)",
                    "unit_cost": "Unit Cost (OMR)",
                    "units_sold": "Units Sold",
                    "total_revenue": "Total Revenue (OMR)",
                },
                column_headers_ar={
                    "sku": "رمز الصنف (SKU)",
                    "product": "اسم المنتج",
                    "category": "الفئة",
                    "unit_price": "سعر البيع (ر.ع)",
                    "unit_cost": "سعر التكلفة (ر.ع)",
                    "units_sold": "الكمية المباعة",
                    "total_revenue": "إجمالي الإيرادات (ر.ع)",
                },
                data=data,
                total_count=len(data),
                generated_at=now_str,
                branch_restricted=branch_id is not None,
            )

        elif report_id == "inventory-summary":
            query = db.query(
                Branch.name.label("branch_name"),
                Product.sku,
                Product.name.label("product_name"),
                Category.name.label("category_name"),
                Inventory.quantity,
                Inventory.reorder_level,
                Product.cost,
                (Inventory.quantity * Product.cost).label("stock_val"),
            ).join(Branch, Inventory.branch_id == Branch.id)\
             .join(Product, Inventory.product_id == Product.id)\
             .join(Category, Product.category_id == Category.id)
            if branch_id:
                query = query.filter(Inventory.branch_id == branch_id)
            records = query.order_by(desc("stock_val")).limit(limit).all()

            data = [
                {
                    "branch": r[0],
                    "sku": r[1],
                    "product": r[2],
                    "category": r[3],
                    "quantity": int(r[4]),
                    "reorder_level": int(r[5]),
                    "unit_cost": round(float(r[6]), 2),
                    "inventory_value": round(float(r[7]), 2),
                }
                for r in records
            ]
            return ReportPreviewResponse(
                report_id=report_id,
                title="Inventory Valuation Summary",
                title_ar="تقرير تقييم المخزون والمستودعات",
                columns=["branch", "sku", "product", "category", "quantity", "reorder_level", "unit_cost", "inventory_value"],
                column_headers={
                    "branch": "Branch",
                    "sku": "SKU",
                    "product": "Product Name",
                    "category": "Category",
                    "quantity": "In Stock",
                    "reorder_level": "Reorder Level",
                    "unit_cost": "Cost (OMR)",
                    "inventory_value": "Stock Value (OMR)",
                },
                column_headers_ar={
                    "branch": "الفرع",
                    "sku": "رمز الصنف (SKU)",
                    "product": "اسم المنتج",
                    "category": "الفئة",
                    "quantity": "المتوفر بالمخزن",
                    "reorder_level": "حد إعادة الطلب",
                    "unit_cost": "التكلفة (ر.ع)",
                    "inventory_value": "قيمة المخزون (ر.ع)",
                },
                data=data,
                total_count=len(data),
                generated_at=now_str,
                branch_restricted=branch_id is not None,
            )

        raise ValueError(f"Unknown report ID: {report_id}")

reports_service = ReportsService()
