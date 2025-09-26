# Multi-stage build for optimization
# Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /code

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files first for better caching
COPY uv.lock pyproject.toml ./

# Install dependencies only (no source code yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Production stage
FROM python:3.12-slim AS production

WORKDIR /code

# Install uv in production stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy virtual environment from builder
COPY --from=builder /code/.venv /code/.venv

# Copy source code
COPY . .

# Place executables in the environment at the front of the path
ENV PATH="/code/.venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r adventurer && useradd -r -g adventurer adventurer -m
RUN chown -R adventurer:adventurer /code
RUN mkdir -p /home/adventurer/.cache && chown -R adventurer:adventurer /home/adventurer/.cache
USER adventurer

# Run the FastAPI application
CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "app/main.py"]