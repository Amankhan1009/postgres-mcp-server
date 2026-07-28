<div align="center">

# 🐘 Postgres MCP Server
### An AI Database Assistant, built on the Model Context Protocol

*Connects an AI client to a real PostgreSQL database — schema exploration, safe querying, and LLM-powered reasoning, all through MCP tools.*

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x%20Async-red)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen)

[Docker Hub](https://hub.docker.com/r/amankhan1009/postgres-mcp-server) · [Architecture](#architecture) · [Installation](#installation) · [Example Tool Calls](#example-tool-calls)

</div>

---

## What is this?

A production-grade Model Context Protocol (MCP) server that connects an AI client (like Claude) to a real PostgreSQL database, combining direct schema/data access with LLM-powered reasoning (via Groq) for SQL generation, query explanation, optimization, and business insight generation.

Built on a fictional company database ("Orbitals Inc.") — a software consultancy with employees, departments, clients, projects, orders, invoices, support tickets, and meetings — to exercise realistic relational queries and multi-hop relationships.

## What makes this an "AI Database Assistant," not just a SQL executor

| Capability | Tool |
|---|---|
| Schema exploration | `list_tables`, `describe_table`, `list_columns`, `search_schema` |
| Safe, validated querying | `execute_select` (SELECT-only, injection-hardened, row-limited) |
| Relationship discovery | `find_related_tables` (BFS over the FK graph, direct + indirect) |
| AI-assisted SQL | `generate_sql`, `explain_query`, `optimize_query` |
| Business reasoning | `summarize_database`, `business_insights` (generates SQL, executes it, interprets results in plain language) |

The database is the source of truth for all facts; the LLM is used for reasoning, translation, and interpretation — never as a substitute for real query execution.

## Architecture

```
MCP Layer (tools/)        → thin, declares tools only
Service Layer (services/) → business logic, orchestration
Repository Layer (repositories/) → raw SQL / SQLAlchemy queries
Database Layer (db/)      → async engine, connection pooling
LLM Client Layer (llm/)   → Groq abstraction, provider-agnostic
```

Each layer only knows about the one below it — MCP tools never touch the database directly, and the LLM provider is swappable behind an interface (`llm/base.py`) without touching services.

## Folder Structure

```
postgres-mcp-server/
├── src/postgres_mcp/
│   ├── config.py, server.py, logging_config.py, exceptions.py
│   ├── db/               # async engine, session management
│   ├── models/            # SQLAlchemy models (11 tables)
│   ├── repositories/       # raw SQL against Postgres
│   ├── services/           # business logic
│   ├── llm/                # Groq provider (swappable interface)
│   ├── tools/               # MCP tool registration
│   └── utils/                # SQL injection defenses (sql_guard.py)
├── scripts/               # check_connection, check_llm, seed_database
├── alembic/                # schema migrations
├── tests/
│   ├── unit/                # sql_guard, schema_service, insight_service
│   └── integration/          # real Neon queries
├── Dockerfile, docker-compose.yml
└── alembic.ini
```

## Database Schema

11 tables modeling a software consultancy: `departments`, `employees` (self-referencing manager hierarchy), `clients`, `projects`, `project_assignments` (many-to-many), `products`, `orders`, `invoices`, `support_tickets`, `meetings`, `meeting_attendees` (many-to-many). Full relational integrity via foreign keys, check constraints (e.g., positive order quantities, valid status enums), and indexes on frequently-filtered columns.

## Installation

### Prerequisites
- Python 3.12+
- A [Neon](https://neon.tech) PostgreSQL database (free tier works)
- A [Groq](https://console.groq.com) API key (free tier works)
- Docker (optional, for containerized runs)

### Setup

```bash
git clone <your-repo-url>
cd postgres-mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# fill in .env with your real Neon connection string and Groq API key
```

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Neon connection string, async form: `postgresql+asyncpg://user:pass@host/db?ssl=require` |
| `GROQ_API_KEY` | Your Groq API key |
| `GROQ_MODEL` | Model name (default: `llama-3.3-70b-versatile`) |
| `LOG_LEVEL` | Logging verbosity (default: `INFO`) |
| `ENVIRONMENT` | `development` or `production` |

## Neon Setup

1. Create a free account and project at [neon.tech](https://neon.tech)
2. Copy the connection string from your project dashboard
3. Convert it to async form: change `postgresql://` to `postgresql+asyncpg://`, and `sslmode=require` to `ssl=require`, dropping any `channel_binding` param

## Database Setup

```bash
alembic upgrade head              # creates all 11 tables
python scripts/seed_database.py   # populates realistic fictional data
```

## Running Locally

```bash
python -m postgres_mcp.server
```

This starts the MCP server over stdio transport. To test it interactively:

```bash
npx @modelcontextprotocol/inspector@latest python -m postgres_mcp.server
```

## Running with Docker

```bash
docker build -t postgres-mcp-server:latest .
docker run -i --env-file .env postgres-mcp-server:latest
```

Or via Docker Compose:
```bash
docker compose up --build
```

Pre-built image available on Docker Hub:
```bash
docker pull amankhan1009/postgres-mcp-server:latest
```

## Testing

```bash
pytest -m "not integration" -v   # unit + mocked tests (fast, no DB needed)
pytest -m integration -v          # integration tests (hits real Neon)
pytest -v                          # everything
```

22 tests passing: 20 unit/mocked (including full `sql_guard` injection-defense coverage) + 2 integration tests against real seeded data.

## Example Tool Calls

**`list_tables()`**
```json
["clients", "departments", "employees", "invoices", "meeting_attendees",
 "meetings", "orders", "products", "project_assignments", "projects", "support_tickets"]
```

**`business_insights("which department has the highest average employee salary?")`**
> The department with the highest average employee salary is **Engineering**, with an average salary of **$101,125**.

**`find_related_tables("employees", max_depth=2)`**
```json
{
  "table_name": "employees",
  "related_tables": {
    "departments": 1, "project_assignments": 1, "meeting_attendees": 1, "support_tickets": 1,
    "projects": 2, "clients": 2, "meetings": 2
  }
}
```

## Security

- All user/LLM-supplied SQL passes through `sql_guard.py`: single-statement enforcement, forbidden keyword/function blocking, and a hard row limit
- Every query runs inside a `READ ONLY` Postgres transaction as a final safety net
- Table names from tool inputs are validated against a live whitelist (`list_tables()`) before being used in any query, since identifiers can't be parameterized like values
- Secrets are never baked into the Docker image — passed only at runtime via `--env-file`
- Container runs as a non-root user

## Future Improvements

- Optional, separately-hardened write capability (structured `insert_row`-style tools with strict table/column whitelisting, audit logging, and confirmation steps) — deliberately out of scope for this version, which is read-only by design
- Support for a second LLM provider (OpenAI/Anthropic) via the existing `LLMProvider` interface
- Query result caching for repeated `describe_table`/`list_tables` calls
- Rate limiting on `execute_select` and LLM-powered tools

---

<div align="center">

Built as a portfolio project to demonstrate production-grade backend architecture, PostgreSQL fluency, and safe AI-database integration via MCP.

</div>