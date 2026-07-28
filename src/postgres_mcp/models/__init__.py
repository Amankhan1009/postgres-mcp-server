"""
Central import point for all models.

Why this matters: SQLAlchemy's Base.metadata only knows about a model
once its class has been imported/executed at least once. If Alembic's
env.py only imports, say, `Employee`, autogenerate would silently miss
every other table. Importing everything here and having env.py import
*this* module guarantees nothing gets left out.
"""

from postgres_mcp.models.client import Client
from postgres_mcp.models.department import Department
from postgres_mcp.models.employee import Employee
from postgres_mcp.models.invoice import Invoice
from postgres_mcp.models.meeting import Meeting
from postgres_mcp.models.meeting_attendee import MeetingAttendee
from postgres_mcp.models.order import Order
from postgres_mcp.models.product import Product
from postgres_mcp.models.project import Project
from postgres_mcp.models.project_assignment import ProjectAssignment
from postgres_mcp.models.support_ticket import SupportTicket

__all__ = [
    "Client",
    "Department",
    "Employee",
    "Invoice",
    "Meeting",
    "MeetingAttendee",
    "Order",
    "Product",
    "Project",
    "ProjectAssignment",
    "SupportTicket",
]