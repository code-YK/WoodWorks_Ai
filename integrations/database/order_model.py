from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from integrations.database.engine import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    total_price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)

    # Relationships
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    # Snapshotted spec (JSON-safe)
    technical_spec = Column(JSON, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
