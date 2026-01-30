# Multi-stage build for smaller final image
# Stage 1: Build - install dependencies
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /code

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies (cached if pyproject.toml/uv.lock unchanged)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev


# Stage 2: Production - run the app
FROM python:3.12-slim AS production

WORKDIR /code

# Copy uv binary for potential future use
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy virtual environment from builder stage
COPY --from=builder /code/.venv /code/.venv

# Copy application code
COPY . .

# Add virtual environment to PATH
ENV PATH="/code/.venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=config.settings

# Collect static files for whitenoise
RUN python manage.py collectstatic --noinput

# Create non-root user for security
RUN groupadd -r adventurer && useradd -r -g adventurer adventurer -m
RUN chown -R adventurer:adventurer /code
USER adventurer

# Railway provides PORT env var; default to 8000 for local Docker
ENV PORT=8000
EXPOSE 8000

# Production server options:
# granian - Rust-based, fast, low memory (recommended)
# hypercorn - Pure Python, supports HTTP/2 and HTTP/3
#
# Using sh -c to allow $PORT substitution at runtime
CMD ["sh", "-c", "granian --interface wsgi --host 0.0.0.0 --port $PORT --workers 2 config.wsgi:application"]
# CMD ["sh", "-c", "hypercorn config.asgi:application --bind 0.0.0.0:$PORT --workers 2"]
