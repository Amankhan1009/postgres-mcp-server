"""
ProjectAssignment model — the many-to-many join between Employee and
Project.

Unlike a simple lookup table, this join carries its own data (role,
assigned_at), so it's modeled as a full entity with its own primary
key rather than a bare association Table. A UniqueConstraint prevents
the same employee being assigned to the same project twice.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres_mcp.db.base import Base


class ProjectAssignment(Base):
    __tablename__ = "project_assignments"
    __table_args__ = (
        UniqueConstraint("project_id", "employee_id", name="uq_project_employee"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)

    project: Mapped["Project"] = relationship(back_populates="assignments")
    employee: Mapped["Employee"] = relationship(back_populates="project_assignments")