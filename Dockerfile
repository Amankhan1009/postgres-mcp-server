# ---- Stage 1: builder ----
# Installs dependencies in a full-featured image with build tools.
# This stage is discarded after building — only its output (installed
# packages) gets copied into the final image.
FROM python:3.13-slim AS builder

WORKDIR /app

# Build tools needed to compile any C-extension dependencies
# (asyncpg has some). Removed automatically since this stage is discarded.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
# Install into a local directory we can copy wholesale into stage 2,
# rather than polluting the system Python of the builder stage.
RUN pip install --no-cache-dir --target=/install .

# ---- Stage 2: runtime ----
# Slim final image — no compilers, no build tools, just Python +
# our installed packages + our source code.
FROM python:3.13-slim

# Create a non-root user. Running containers as root is a real
# security risk: if an attacker escapes the container, root inside
# maps to meaningful privilege on the host in some configurations.
RUN groupadd --system app && useradd --system --gid app app

WORKDIR /app

COPY --from=builder /install /usr/local/lib/python3.13/site-packages
COPY src/ ./src/

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

USER app

# stdio transport — no EXPOSE needed, this isn't a network server.
# The MCP client pipes stdin/stdout into this process directly.
CMD ["python", "-m", "postgres_mcp.server"]