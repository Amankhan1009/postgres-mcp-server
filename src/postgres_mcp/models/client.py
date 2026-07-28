"""
Client model.

Represents a company Orbitals does business with. This is a central
"hub" table — projects, orders, invoices, and support tickets all
reference it, mirroring how a real CRM/ERP schema is usually organized
around a Client or Account entity.
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres_mcp.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(150), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    projects: Mapped[list["Project"]] = relationship(back_populates="client")
    orders: Mapped[list["Order"]] = relationship(back_populates="client")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="client")
    support_tickets: Mapped[list["SupportTicket"]] = relationship(back_populates="client")
    meetings: Mapped[list["Meeting"]] = relationship(back_populates="client")