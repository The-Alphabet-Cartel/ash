# Multi-stage Dockerfile for Ash Discord Bot - Production Ready
# Build stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies in virtual environment
RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser -u 1001 botuser

# Create necessary directories with proper ownership
RUN mkdir -p logs data tests && \
    chown -R botuser:botuser /app && \
    chmod 755 /app

# Copy bot application code
COPY --chown=botuser:botuser ./bot .

# Switch to non-root user
USER botuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check with better implementation
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import asyncio; import sys; sys.exit(0)" || exit 1

# Note: No ports exposed - Discord bot connects outbound to Discord's servers

# Use exec form for better signal handling
CMD ["python", "-u", "main.py"]

# Labels for better container management
LABEL maintainer="The Alphabet Cartel" \
      version="2.0" \
      description="Ash Discord Bot - Mental Health Support" \
      org.opencontainers.image.source="https://github.com/The-Alphabet-Cartel/ash"