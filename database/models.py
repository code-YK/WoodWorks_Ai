from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")
    memories = relationship("WorkflowMemory", back_populates="user")


class ProductCatalog(Base):
    __tablename__ = "product_catalog"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Float, nullable=False)
    material = Column(String(100), nullable=True)
    finish_options = Column(String(200), nullable=True)
    dimensions_guide = Column(String(200), nullable=True)
    customizable = Column(Integer, default=1)  # 1=True, 0=False

    items = relationship("ProductItem", back_populates="product")
    orders = relationship("Order", back_populates="product")


class ProductItem(Base):
    __tablename__ = "product_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product_catalog.id"), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    stock_quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("ProductCatalog", back_populates="items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product_catalog.id"), nullable=False)
    human_spec = Column(Text, nullable=True)
    technical_spec = Column(Text, nullable=True)
    final_price = Column(Float, nullable=False)
    status = Column(String(50), default="confirmed")
    receipt_path = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    product = relationship("ProductCatalog", back_populates="orders")


class WorkflowMemory(Base):
    __tablename__ = "workflow_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("product_catalog.id"), nullable=True)
    session_type = Column(String(20), default="workflow")  # workflow | chat
    agent_summary = Column(Text, nullable=True)
    final_state = Column(JSON, nullable=True)
    pricing = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")
