"""
MeetingAttendee model — many-to-many join between Meeting and Employee.

Unlike ProjectAssignment, this join carries no extra data, so instead
of a surrogate `id` primary key, we use a composite primary key
(meeting_id + employee_id together). This is a common pattern for
"pure" join tables versus join tables that carry attributes.
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres_mcp.db.base import Base


class MeetingAttendee(Base):
    __tablename__ = "meeting_attendees"

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), primary_key=True)

    meeting: Mapped["Meeting"] = relationship(back_populates="attendees")
    employee: Mapped["Employee"] = relationship(back_populates="meeting_attendances")