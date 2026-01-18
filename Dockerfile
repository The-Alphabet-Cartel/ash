# ============================================================================
# Ash v5.0 Production Dockerfile (Multi-Stage Build)
# ============================================================================
# FILE VERSION: v5.0-1-1.1-1
# LAST MODIFIED: 2026-01-15
# Repository: https://github.com/the-alphabet-cartel/ash
# Community: The Alphabet Cartel - https://discord.gg/alphabetcartel
# ============================================================================
#
# USAGE:
#   # Build the image
#   docker build -t ghcr.io/the-alphabet-cartel/ash:latest .
#
#   # Run with docker-compose (recommended)
#   docker-compose up -d
#
# MULTI-STAGE BUILD:
#   Stage 1 (builder): Install Python dependencies
#   Stage 2 (runtime): Minimal production image
#
# CLEAN ARCHITECTURE: Rule #12 - Environment Version Specificity
#   All pip commands use python3.11 -m pip for version consistency
#
# ============================================================================

# =============================================================================
# Stage 1: Python Builder - Install Python dependencies
# =============================================================================
FROM python:3.11-slim AS builder

# Set build-time environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
# Rule #12: Use python3.11 -m pip for version specificity
RUN python3.11 -m pip install --upgrade pip && \
    python3.11 -m pip install --no-cache-dir -r requirements.txt


# =============================================================================
# Stage 2: Runtime - Production image
# =============================================================================
FROM python:3.11-slim AS runtime

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Application defaults
    ASH_HOST=0.0.0.0 \
    ASH_PORT=30887 \
    ASH_ENVIRONMENT=production \
    ASH_LOG_LEVEL=INFO \
    ASH_LOG_FORMAT=human \
    TZ=America/Los_Angeles

WORKDIR /app

# Install runtime dependencies (minimal - just curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN groupadd -g 1001 ashgroup && \
    useradd -m -u 1001 -g ashgroup ashuser && \
    mkdir -p /app/logs && \
    chown -R ashuser:ashgroup /app

# Copy application code
COPY --chown=ashuser:ashgroup . .

# Switch to non-root user
USER ashuser

# Expose the application port
EXPOSE 30887

# Health check using curl
# Interval: Check every 30 seconds
# Timeout: Wait up to 10 seconds for response
# Start-period: Give the app 60 seconds to start
# Retries: Fail after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:30887/health || exit 1

# Default command - run with uvicorn
# Using python -m uvicorn for proper module resolution
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "30887"]
