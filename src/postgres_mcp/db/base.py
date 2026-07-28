"""
SQLAlchemy declarative base.

Why a separate file: every model in models/ needs to inherit from the
same Base for SQLAlchemy's metadata registry and Alembic's autogenerate
to see them all. Keeping Base isolated here (rather than defining it
inside, say, employee.py) avoids circular imports once models start
referencing each other.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass