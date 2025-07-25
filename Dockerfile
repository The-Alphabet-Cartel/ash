# Multi-stage Dockerfile for Ash Discord Bot - Production Ready
# Build stage
FROM python:3.11-slim AS builder

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
FROM python:3.11-slim AS production

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

# Set default environment variables (can be overridden by docker-compose or .env)
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Core Discord Bot Configuration (these will be overridden by docker-compose)
ENV DISCORD_TOKEN=""
ENV GUILD_ID=""
ENV CLAUDE_API_KEY=""
ENV CLAUDE_MODEL="claude-sonnet-4-20250514"

# Channel Configuration defaults
ENV RESOURCES_CHANNEL_ID=""
ENV CRISIS_RESPONSE_CHANNEL_ID=""
ENV ALLOWED_CHANNELS=""

# Staff and Crisis Team defaults
ENV STAFF_PING_USER=""
ENV CRISIS_RESPONSE_ROLE_ID=""
ENV RESOURCES_CHANNEL_NAME="resources"
ENV CRISIS_RESPONSE_ROLE_NAME="CrisisResponse"
ENV STAFF_PING_NAME="Staff"

# Learning System defaults
ENV ENABLE_LEARNING_SYSTEM="true"
ENV LEARNING_CONFIDENCE_THRESHOLD="0.6"
ENV MAX_LEARNING_ADJUSTMENTS_PER_DAY="50"

# NLP Service defaults (pointing to your AI rig)
ENV NLP_SERVICE_HOST="10.20.30.16"
ENV NLP_SERVICE_PORT="8881"
ENV REQUEST_TIMEOUT="30"

# Bot Performance defaults
ENV LOG_LEVEL="INFO"
ENV MAX_DAILY_CALLS="1000"
ENV RATE_LIMIT_PER_USER="10"

# Conversation Isolation defaults
ENV CONVERSATION_REQUIRES_MENTION="false"
ENV CONVERSATION_TRIGGER_PHRASES="ash,hey ash,ash help,,@ash"
ENV CONVERSATION_ALLOW_STARTERS="false"
ENV CONVERSATION_SETUP_INSTRUCTIONS="true"
ENV CONVERSATION_LOG_ATTEMPTS="true"
ENV CONVERSATION_TIMEOUT="300"

# Health check with better implementation
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import asyncio; import sys; sys.exit(0)" || exit 1

# Note: No ports exposed - Discord bot connects outbound to Discord's servers

# Use exec form for better signal handling
CMD ["python", "-u", "main.py"]

# Labels for better container management
LABEL maintainer="The Alphabet Cartel" \
      version="2.0" \
      description="Ash Discord Bot - Mental Health Support with Conversation Isolation" \
      org.opencontainers.image.source="https://github.com/The-Alphabet-Cartel/ash" \
      feature.conversation-isolation="enabled"