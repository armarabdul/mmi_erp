from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    city = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)

    users = relationship("User", back_populates="branch")
    customers = relationship("Customer", back_populates="branch")
    sales = relationship("Sale", back_populates="branch")
    purchases = relationship("Purchase", back_populates="branch")
    inventory = relationship("Inventory", back_populates="branch")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    active = Column(Boolean, default=True)

    category = relationship("Category", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    inventory = relationship("Inventory", back_populates="product")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    customer_type = Column(String(50), nullable=False, default="Retail")  # Corporate, Retail, Wholesale
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    branch = relationship("Branch", back_populates="customers")
    sales = relationship("Sale", back_populates="customer")

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)

    purchases = relationship("Purchase", back_populates="supplier")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    sale_date = Column(Date, nullable=False, index=True)
    gross_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False, index=True)
    status = Column(String(50), default="Completed", index=True)  # Completed, Pending, Cancelled

    customer = relationship("Customer", back_populates="sales")
    branch = relationship("Branch", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_sales_branch_date", "branch_id", "sale_date"),
    )

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    purchase_date = Column(Date, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="Completed")  # Completed, Pending, Cancelled

    supplier = relationship("Supplier", back_populates="purchases")
    branch = relationship("Branch", back_populates="purchases")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False, default=10)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    branch = relationship("Branch", back_populates="inventory")
    product = relationship("Product", back_populates="inventory")

    __table_args__ = (
        Index("idx_inventory_branch_product", "branch_id", "product_id", unique=True),
    )
