"""
Schema introspection repository.

Why this file exists: this is the ONLY place that knows the raw SQL
against information_schema. Services call these methods instead of
writing introspection SQL themselves — if we ever need to optimize
these queries or add caching, this is the single place to change.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SchemaRepository:
    async def list_tables(self, session: AsyncSession) -> list[str]:
        result = await session.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
            )
        )
        return [row[0] for row in result]

    async def list_columns(self, session: AsyncSession, table_name: str) -> list[dict]:
        result = await session.execute(
            text(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :table_name
                ORDER BY ordinal_position
                """
            ),
            {"table_name": table_name},
        )
        return [
            {
                "column_name": row.column_name,
                "data_type": row.data_type,
                "is_nullable": row.is_nullable == "YES",
                "default": row.column_default,
            }
            for row in result
        ]

    async def list_foreign_keys(self, session: AsyncSession, table_name: str) -> list[dict]:
        result = await session.execute(
            text(
                """
                SELECT
                    kcu.column_name,
                    ccu.table_name AS referenced_table,
                    ccu.column_name AS referenced_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                    AND tc.table_name = :table_name
                """
            ),
            {"table_name": table_name},
        )
        return [
            {
                "column": row.column_name,
                "references_table": row.referenced_table,
                "references_column": row.referenced_column,
            }
            for row in result
        ]

    async def count_rows(self, session: AsyncSession, table_name: str) -> int:
        # table_name is validated against a whitelist by the service layer
        # before reaching here — see schema_service.py
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar_one()

    async def search_schema(self, session: AsyncSession, keyword: str) -> list[dict]:
        result = await session.execute(
            text(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                    AND (table_name ILIKE :pattern OR column_name ILIKE :pattern)
                ORDER BY table_name, column_name
                """
            ),
            {"pattern": f"%{keyword}%"},
        )
        return [{"table": row.table_name, "column": row.column_name} for row in result]

    async def list_all_foreign_keys(self, session: AsyncSession) -> list[dict]:
            result = await session.execute(
                text(
                    """
                    SELECT
                        tc.table_name AS from_table,
                        kcu.column_name AS from_column,
                        ccu.table_name AS to_table,
                        ccu.column_name AS to_column
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage ccu
                        ON tc.constraint_name = ccu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_schema = 'public'
                    """
                )
            )
            return [
                {
                    "from_table": row.from_table,
                    "from_column": row.from_column,
                    "to_table": row.to_table,
                    "to_column": row.to_column,
                }
                for row in result
            ]