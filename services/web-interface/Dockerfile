# Atrium Grounds - Web Interface Dockerfile
# Multi-stage build for minimal production image

FROM python:3.11-slim AS base

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files and README (needed by pyproject.toml)
COPY pyproject.toml README.md ./

# Install dependencies (production only)
RUN uv sync --no-dev

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Expose port
EXPOSE 8080

# Set environment variables
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8080
ENV OBSERVATORY_URL=http://observatory:8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/ping || exit 1

# Run application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
