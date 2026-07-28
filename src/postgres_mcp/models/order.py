"""
Order model.

Introduces a numeric CheckConstraint: quantity must be positive.
This is a good example of "the database as a safety net" — even a bug
in application logic can't insert an invalid quantity.
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres_mcp.db.base import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_orders_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)

    client: Mapped["Client"] = relationship(back_populates="orders")
    product: Mapped["Product"] = relationship(back_populates="orders")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="order")