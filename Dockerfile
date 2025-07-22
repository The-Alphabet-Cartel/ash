# Dockerfile for Ash Discord Bot
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot application code
COPY ./bot .

# Create non-root user for security
RUN useradd -m -u 1001 botuser

# Create logs and data directories with proper ownership
RUN mkdir -p logs data && chown -R botuser:botuser /app

USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import discord; print('Bot modules OK')" || exit 1

# Start the bot
CMD ["python", "main.py"]