from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    document: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="admin")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class MarketplaceAccount(Base):
    __tablename__ = "marketplace_accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    marketplace: Mapped[str] = mapped_column(String(50), default="mercado_livre")
    seller_id: Mapped[str] = mapped_column(String(80), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(120))
    access_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ERPConnection(Base):
    __tablename__ = "erp_connections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    erp_name: Mapped[str] = mapped_column(String(80), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(255))
    api_key_enc: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    marketplace_item_id: Mapped[str | None] = mapped_column(String(80))
    sku: Mapped[str | None] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    cost: Mapped[float | None] = mapped_column(Numeric(14, 2))
    raw_payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    marketplace_order_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    status: Mapped[str | None] = mapped_column(String(80))
    buyer_id: Mapped[str | None] = mapped_column(String(80))
    buyer_nickname: Mapped[str | None] = mapped_column(String(120))
    total_amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    paid_amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    currency_id: Mapped[str | None] = mapped_column(String(10))
    shipping_id: Mapped[str | None] = mapped_column(String(80))
    date_created: Mapped[datetime | None] = mapped_column(DateTime)
    date_closed: Mapped[datetime | None] = mapped_column(DateTime)
    raw_payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    marketplace_item_id: Mapped[str | None] = mapped_column(String(80))
    sku: Mapped[str | None] = mapped_column(String(120))
    title: Mapped[str | None] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    sale_fee: Mapped[float | None] = mapped_column(Numeric(14, 2))
    raw_payload: Mapped[dict | None] = mapped_column(JSON)
    order = relationship("Order", back_populates="items")

class FinancialEntry(Base):
    __tablename__ = "financial_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    due_date: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    raw_payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SyncLog(Base):
    __tablename__ = "sync_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(80))
    entity: Mapped[str] = mapped_column(String(80))
    external_id: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(50))
    message: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AIInsight(Base):
    __tablename__ = "ai_insights"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    insight_type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(40), default="info")
    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
