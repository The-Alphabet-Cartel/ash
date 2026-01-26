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
#   - Rule #10: Environment Version Specificity (python3.12 -m pip)
#   - Rule #13: Pure Python entrypoint for PUID/PGID
#
# ============================================================================

# =============================================================================
# Stage 1: Python Builder - Install Python dependencies
# =============================================================================
FROM python:3.12-slim AS builder

# Set build-time environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# =============================================================================
# Stage 2: Runtime - Production image
# =============================================================================
FROM python:3.12-slim AS runtime

# Labels
LABEL maintainer="PapaBearDoes <github.com/PapaBearDoes>"
LABEL org.opencontainers.image.title="Ash-NLP"
LABEL org.opencontainers.image.description="Crisis Detection for the Alphabet Cartel Discord Community"
LABEL org.opencontainers.image.version="5.0.0"
LABEL org.opencontainers.image.vendor="The Alphabet Cartel"
LABEL org.opencontainers.image.url="https://github.com/the-alphabet-cartel/ash-nlp"
LABEL org.opencontainers.image.source="https://github.com/the-alphabet-cartel/ash-nlp"

# Default user/group IDs (can be overridden at runtime via PUID/PGID)
ARG DEFAULT_UID=1000
ARG DEFAULT_GID=1000

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PATH="/opt/venv/bin:$PATH" \
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

# Install runtime dependencies
# tini: PID 1 signal handling (Rule #13)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR ${APP_HOME}

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user (will be modified at runtime by entrypoint if PUID/PGID differ)
RUN groupadd -g ${DEFAULT_GID} ashgroup && \
    useradd -m -u ${DEFAULT_UID} -g ashgroup ashuser && \
    mkdir -p ${APP_HOME}/logs ${APP_HOME}/data && \
    chown -R ${DEFAULT_UID}:${DEFAULT_GID} ${APP_HOME}

# Copy application code
COPY --chown=${DEFAULT_UID}:${DEFAULT_GID} . .

# Copy and set up entrypoint script
COPY docker-entrypoint.py ${APP_HOME}/docker-entrypoint.py
RUN chmod +x ${APP_HOME}/docker-entrypoint.py

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
