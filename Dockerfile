# Use Python 3.12 slim image
FROM python:3.12-slim-bookworm AS base

# Install system dependencies and UV
RUN apt-get update && apt-get install -y \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

###############################################################################
# BUILDER IMAGE - Install dependencies
###############################################################################
FROM base AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --system -r pyproject.toml

###############################################################################
# RUNTIME IMAGE - Final slim image with dependencies
###############################################################################
FROM base AS runtime

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user with ID 10000 and group ID 10001
RUN groupadd -g 10001 nonroot && \
    useradd -u 10000 -g nonroot -m -s /bin/bash nonroot && \
    chown -R 10000:10001 /app

# Switch to non-root user
USER nonroot

# Expose port
EXPOSE 8632

# Use tini as init system
ENTRYPOINT ["tini", "--"]

# Run the application
CMD ["./docker-entrypoint.sh"]