"""
Employee model.

Introduces two new patterns:
  1. A self-referencing foreign key (manager_id -> employees.id) to
     model the org chart — an employee's manager is another employee.
  2. remote_side= on the self-referential relationship, which tells
     SQLAlchemy which side of the FK is the "one" in this one-to-many
     (without it, SQLAlchemy can't tell direction on a self-join).
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres_mcp.db.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), nullable=True)

    department: Mapped["Department"] = relationship(back_populates="employees")
    manager: Mapped["Employee | None"] = relationship(remote_side=[id], back_populates="direct_reports")
    direct_reports: Mapped[list["Employee"]] = relationship(back_populates="manager")

    project_assignments: Mapped[list["ProjectAssignment"]] = relationship(back_populates="employee")
    assigned_tickets: Mapped[list["SupportTicket"]] = relationship(back_populates="assigned_employee")
    meeting_attendances: Mapped[list["MeetingAttendee"]] = relationship(back_populates="employee")