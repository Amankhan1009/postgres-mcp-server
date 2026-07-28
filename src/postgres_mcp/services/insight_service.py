"""
Insight service — combines schema context from SchemaService with
Groq prompts to power generate_sql, explain_query, and optimize_query.

Why schema context matters here: without it, the LLM would have to
guess table/column names from the question alone, which produces
plausible-looking but wrong SQL. We ground every prompt in the real,
current schema instead.
"""

from postgres_mcp.llm.base import LLMProvider
from postgres_mcp.llm.groq_provider import GroqProvider
from postgres_mcp.services.schema_service import SchemaService


class InsightService:
    def __init__(self, llm: LLMProvider | None = None) -> None:
        self._llm = llm or GroqProvider()
        self._schema_service = SchemaService()

    async def _build_schema_context(self) -> str:
        tables = await self._schema_service.list_tables()
        lines = []
        for table in tables:
            if table == "alembic_version":
                continue
            description = await self._schema_service.describe_table(table)
            columns = ", ".join(
                f"{col['column_name']} ({col['data_type']})" for col in description["columns"]
            )
            fks = ", ".join(
                f"{fk['column']} -> {fk['references_table']}.{fk['references_column']}"
                for fk in description["foreign_keys"]
            )
            line = f"- {table}: {columns}"
            if fks:
                line += f" | foreign keys: {fks}"
            lines.append(line)
        return "\n".join(lines)

    async def generate_sql(self, question: str) -> str:
        schema_context = await self._build_schema_context()
        system_prompt = (
            "You are a PostgreSQL expert. Given a database schema and a "
            "natural-language question, write a single, correct, read-only "
            "SELECT query that answers it. Only output the SQL query, no "
            "explanation, no markdown code fences."
        )
        user_prompt = f"Schema:\n{schema_context}\n\nQuestion: {question}\n\nSQL:"
        return await self._llm.generate(system_prompt, user_prompt)

    async def explain_query(self, query: str) -> str:
        schema_context = await self._build_schema_context()
        system_prompt = (
            "You are a PostgreSQL expert. Explain what the given SQL query "
            "does in plain, concise language a non-technical stakeholder "
            "could understand. Reference the schema context if it helps "
            "clarify relationships being used."
        )
        user_prompt = f"Schema:\n{schema_context}\n\nQuery:\n{query}\n\nExplanation:"
        return await self._llm.generate(system_prompt, user_prompt)

    async def optimize_query(self, query: str) -> str:
        schema_context = await self._build_schema_context()
        system_prompt = (
            "You are a PostgreSQL performance expert. Given a schema and a "
            "SQL query, suggest concrete optimizations: missing indexes, "
            "inefficient joins, unnecessary columns, or better query "
            "structure. Be specific and concise. If the query is already "
            "well-optimized, say so briefly."
        )
        user_prompt = f"Schema:\n{schema_context}\n\nQuery:\n{query}\n\nOptimization suggestions:"
        return await self._llm.generate(system_prompt, user_prompt)

    async def summarize_database(self) -> str:
        schema_context = await self._build_schema_context()
        row_counts = await self._schema_service.summarize_row_counts()
        counts_text = "\n".join(f"- {table}: {count} rows" for table, count in row_counts.items())

        system_prompt = (
            "You are a data analyst writing a concise executive overview "
            "of a company database. Use the schema and row counts to "
            "describe what kind of business this data represents and "
            "highlight anything notable about its scale or structure."
        )
        user_prompt = f"Schema:\n{schema_context}\n\nRow counts:\n{counts_text}\n\nOverview:"
        return await self._llm.generate(system_prompt, user_prompt)

    async def business_insights(self, question: str, query_service) -> str:
        sql_query = await self.generate_sql(question)
        # generate_sql may occasionally wrap output in markdown fences —
        # strip them defensively before execution.
        cleaned_query = sql_query.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()

        rows = await query_service.execute_select(cleaned_query)

        system_prompt = (
            "You are a business analyst. Given a question, the SQL query "
            "used to answer it, and the actual data returned, write a "
            "clear, concise answer for a business stakeholder. Reference "
            "specific numbers from the data. If the data doesn't fully "
            "answer the question, say so."
        )
        user_prompt = (
            f"Question: {question}\n\n"
            f"SQL used: {cleaned_query}\n\n"
            f"Data returned: {rows}\n\n"
            f"Answer:"
        )
        return await self._llm.generate(system_prompt, user_prompt)