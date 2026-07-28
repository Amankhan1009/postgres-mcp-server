"""
Invoice model.

The most structurally interesting table so far: an invoice can bill
either an Order OR a Project (or both), so order_id and project_id are
both nullable — but a CheckConstraint enforces that at least one is
always set. This models a real-world billing pattern: product sales
and services/consulting are invoiced through different paths.
"""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres_mcp.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        CheckConstraint(
            "order_id IS NOT NULL OR project_id IS NOT NULL",
            name="ck_invoices_has_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="unpaid", index=True)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="invoices")
    order: Mapped["Order | None"] = relationship(back_populates="invoices")
    project: Mapped["Project | None"] = relationship(back_populates="invoices")