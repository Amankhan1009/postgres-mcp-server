"""
Verifies all models import correctly and register on Base.metadata.
No database writes happen here — that's Alembic's job in Milestone 3.
"""

from postgres_mcp.db.base import Base
from postgres_mcp import models  # noqa: F401  (import triggers registration)

print(f"✅ {len(Base.metadata.tables)} tables registered:")
for table_name in sorted(Base.metadata.tables.keys()):
    print(f"   - {table_name}")