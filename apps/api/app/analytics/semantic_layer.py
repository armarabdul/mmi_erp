from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MetricMetadata(BaseModel):
    id: str
    name: str
    name_ar: str
    definition: str
    definition_ar: str
    sql_expression: str
    table: str
    allowed_dimensions: List[str]
    synonyms_en: List[str]
    synonyms_ar: List[str]

class DimensionMetadata(BaseModel):
    id: str
    name: str
    name_ar: str
    sql_field: str
    table: str
    join_clause: str
    synonyms_en: List[str]
    synonyms_ar: List[str]

class SemanticLayer:
    def __init__(self):
        self.metrics: Dict[str, MetricMetadata] = {
            "total_sales": MetricMetadata(
                id="total_sales",
                name="Total Sales",
                name_ar="إجمالي المبيعات",
                definition="Sum of net sales revenue for completed transactions",
                definition_ar="مجموع صافي الإيرادات للمبيعات المكتملة",
                sql_expression="SUM(s.net_amount)",
                table="sales s",
                allowed_dimensions=["branch", "product", "category", "customer", "date"],
                synonyms_en=["sales", "revenue", "turnover", "total sales", "net sales", "earnings"],
                synonyms_ar=["المبيعات", "إجمالي المبيعات", "الايرادات", "صافي المبيعات", "الدخل", "مبيعات"],
            ),
            "average_order_value": MetricMetadata(
                id="average_order_value",
                name="Average Order Value",
                name_ar="متوسط قيمة الطلب",
                definition="Average net invoice amount per completed sale",
                definition_ar="متوسط قيمة الفاتورة لكل عملية بيع مكتملة",
                sql_expression="AVG(s.net_amount)",
                table="sales s",
                allowed_dimensions=["branch", "customer", "date"],
                synonyms_en=["aov", "average order value", "average sale", "basket size", "avg order"],
                synonyms_ar=["متوسط الطلب", "متوسط قيمة الطلب", "متوسط الفاتورة", "معدل السلة"],
            ),
            "order_count": MetricMetadata(
                id="order_count",
                name="Order Count",
                name_ar="عدد الطلبات",
                definition="Total number of completed sales orders",
                definition_ar="إجمالي عدد فواتير المبيعات المكتملة",
                sql_expression="COUNT(s.id)",
                table="sales s",
                allowed_dimensions=["branch", "customer", "date"],
                synonyms_en=["orders", "order count", "transactions", "number of orders", "invoices"],
                synonyms_ar=["عدد الطلبات", "عدد الفواتير", "الطلبات", "المعاملات", "الفواتير"],
            ),
            "purchase_value": MetricMetadata(
                id="purchase_value",
                name="Purchase Value",
                name_ar="قيمة المشتريات",
                definition="Sum of procurement and purchase expenditure",
                definition_ar="إجمالي نفقات المشتريات والتوريد",
                sql_expression="SUM(p.total_amount)",
                table="purchases p",
                allowed_dimensions=["branch", "supplier", "date"],
                synonyms_en=["purchases", "purchase value", "procurement", "supplier spend", "buying"],
                synonyms_ar=["المشتريات", "قيمة المشتريات", "التوريد", "نفقات التوريد"],
            ),
            "inventory_value": MetricMetadata(
                id="inventory_value",
                name="Inventory Value",
                name_ar="قيمة المخزون",
                definition="Total current valuation of stock on hand at cost price",
                definition_ar="القيمة المالية الإجمالية للبضاعة بالمخازن بسعر التكلفة",
                sql_expression="SUM(i.quantity * pr.cost)",
                table="inventory i",
                allowed_dimensions=["branch", "product", "category"],
                synonyms_en=["inventory", "inventory value", "stock", "stock value", "warehouse value"],
                synonyms_ar=["المخزون", "قيمة المخزون", "البضاعة", "المستودع", "المخازن"],
            ),
            "customer_count": MetricMetadata(
                id="customer_count",
                name="Customer Count",
                name_ar="عدد العملاء",
                definition="Total count of registered customer accounts",
                definition_ar="إجمالي عدد حسابات العملاء المسجلين",
                sql_expression="COUNT(c.id)",
                table="customers c",
                allowed_dimensions=["branch", "customer_type"],
                synonyms_en=["customers", "customer count", "clients", "accounts"],
                synonyms_ar=["عدد العملاء", "العملاء", "الزبائن", "قاعدة العملاء"],
            ),
        }

        self.dimensions: Dict[str, DimensionMetadata] = {
            "branch": DimensionMetadata(
                id="branch",
                name="Branch",
                name_ar="الفرع",
                sql_field="b.name",
                table="branches b",
                join_clause="JOIN branches b ON s.branch_id = b.id",
                synonyms_en=["branch", "branches", "location", "store", "city", "muscat", "salalah", "sohar", "nizwa"],
                synonyms_ar=["الفرع", "الفروع", "فرع", "فروع", "المدينة", "مسقط", "صلالة", "صحار", "نزوى"],
            ),
            "product": DimensionMetadata(
                id="product",
                name="Product",
                name_ar="المنتج",
                sql_field="pr.name",
                table="products pr",
                join_clause="JOIN sale_items si ON s.id = si.sale_id JOIN products pr ON si.product_id = pr.id",
                synonyms_en=["product", "products", "item", "items", "sku", "materials"],
                synonyms_ar=["المنتج", "المنتجات", "منتج", "سلعة", "بضائع", "أصناف", "مواد"],
            ),
            "category": DimensionMetadata(
                id="category",
                name="Product Category",
                name_ar="فئة المنتج",
                sql_field="cat.name",
                table="categories cat",
                join_clause="JOIN sale_items si ON s.id = si.sale_id JOIN products pr ON si.product_id = pr.id JOIN categories cat ON pr.category_id = cat.id",
                synonyms_en=["category", "categories", "product category", "department", "type"],
                synonyms_ar=["الفئة", "الفئات", "تصنيف", "تصنيفات", "قسم", "نوع"],
            ),
            "customer": DimensionMetadata(
                id="customer",
                name="Customer",
                name_ar="العميل",
                sql_field="c.name",
                table="customers c",
                join_clause="JOIN customers c ON s.customer_id = c.id",
                synonyms_en=["customer", "customers", "client", "clients", "company"],
                synonyms_ar=["العميل", "العملاء", "زبون", "زبائن", "شركات"],
            ),
            "date": DimensionMetadata(
                id="date",
                name="Date",
                name_ar="التاريخ",
                sql_field="s.sale_date",
                table="sales s",
                join_clause="",
                synonyms_en=["date", "month", "monthly", "year", "trend", "daily", "timeline", "period"],
                synonyms_ar=["تاريخ", "شهر", "شهري", "شهريا", "سنة", "سنوي", "فترة", "اتجاه"],
            ),
        }

    def get_semantic_context_prompt(self) -> str:
        """Returns structured metadata documentation for LLM prompt injection."""
        lines = ["=== ENTERPRISE ERP SEMANTIC LAYER ==="]
        lines.append("METRICS:")
        for m in self.metrics.values():
            lines.append(f"- {m.id}: {m.name} ({m.name_ar}) | SQL: {m.sql_expression} from {m.table} | Dimensions: {', '.join(m.allowed_dimensions)}")
        lines.append("\nDIMENSIONS:")
        for d in self.dimensions.values():
            lines.append(f"- {d.id}: {d.name} ({d.name_ar}) | Field: {d.sql_field} | Join: {d.join_clause}")
        lines.append("\nDATABASE SCHEMA:")
        lines.append("- branches (id, name, city, region)")
        lines.append("- categories (id, name, description)")
        lines.append("- products (id, name, category_id, sku, price, cost, active)")
        lines.append("- customers (id, name, email, branch_id, customer_type, created_at)")
        lines.append("- suppliers (id, name, contact, city)")
        lines.append("- sales (id, invoice_number, customer_id, branch_id, sale_date, gross_amount, discount, tax, net_amount, status)")
        lines.append("- sale_items (id, sale_id, product_id, quantity, unit_price, discount, total_amount)")
        lines.append("- purchases (id, supplier_id, branch_id, purchase_date, total_amount, status)")
        lines.append("- inventory (id, branch_id, product_id, quantity, reorder_level, updated_at)")
        return "\n".join(lines)

semantic_layer = SemanticLayer()
