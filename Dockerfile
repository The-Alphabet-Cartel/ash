# ============================================================================
# Ash v5.0 Production Dockerfile (Multi-Stage Build)
# ============================================================================
# FILE VERSION: v5.0-6-1.0-1
# LAST MODIFIED: 2026-01-22
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
# CLEAN ARCHITECTURE COMPLIANCE:
#   - Rule #10: Environment Version Specificity (python3.11 -m pip)
#   - Rule #13: Pure Python entrypoint for PUID/PGID
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
# Rule #10: Use python3.11 -m pip for version specificity
RUN python3.11 -m pip install --upgrade pip && \
    python3.11 -m pip install --no-cache-dir -r requirements.txt


# =============================================================================
# Stage 2: Runtime - Production image
# =============================================================================
FROM python:3.11-slim AS runtime

# Default user/group IDs (can be overridden at runtime via PUID/PGID)
ARG DEFAULT_UID=1000
ARG DEFAULT_GID=1000

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
    TZ=America/Los_Angeles \
    # Force ANSI colors in Docker logs (Charter v5.2.1)
    FORCE_COLOR=1 \
    # Default PUID/PGID (LinuxServer.io style)
    PUID=${DEFAULT_UID} \
    PGID=${DEFAULT_GID}

WORKDIR /app

# Install runtime dependencies
# tini: PID 1 signal handling (Rule #13)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user (will be modified at runtime by entrypoint if PUID/PGID differ)
RUN groupadd -g ${DEFAULT_GID} ashgroup && \
    useradd -m -u ${DEFAULT_UID} -g ashgroup ashuser && \
    mkdir -p /app/logs /app/data && \
    chown -R ${DEFAULT_UID}:${DEFAULT_GID} /app

# Copy application code
COPY --chown=${DEFAULT_UID}:${DEFAULT_GID} . .

# Copy and set up entrypoint script (Rule #13: Pure Python PUID/PGID handling)
COPY docker-entrypoint.py /app/docker-entrypoint.py
RUN chmod +x /app/docker-entrypoint.py

# NOTE: We do NOT switch to USER ashuser here!
# The entrypoint script handles user switching at runtime after fixing permissions.
# This allows PUID/PGID to work correctly with mounted volumes.

# Expose the application port
EXPOSE 30887

# Health check using curl
# Interval: Check every 30 seconds
# Timeout: Wait up to 10 seconds for response
# Start-period: Give the app 60 seconds to start
# Retries: Fail after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:30887/health || exit 1

# Use tini as init system for proper signal handling
# Then our Python entrypoint for PUID/PGID handling (Rule #13)
ENTRYPOINT ["/usr/bin/tini", "--", "python", "/app/docker-entrypoint.py"]

# Default command - run with uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "30887"]
