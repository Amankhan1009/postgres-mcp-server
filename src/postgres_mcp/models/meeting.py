"""
Meeting model.

client_id is nullable because meetings can be purely internal
(no client involved) or client-facing.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from postgres_mcp.db.base import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True)

    client: Mapped["Client | None"] = relationship(back_populates="meetings")
    attendees: Mapped[list["MeetingAttendee"]] = relationship(back_populates="meeting")