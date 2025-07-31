FROM python:3.11-slim

LABEL maintainer="The Alphabet Cartel"
LABEL description="Ash-Thrash Testing Suite"
LABEL repository="https://github.com/The-Alphabet-Cartel/ash-thrash"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Create results directory
RUN mkdir -p /app/results

# Copy and setup cron
COPY docker/crontab /etc/cron.d/ash-thrash
RUN chmod 0644 /etc/cron.d/ash-thrash && \
    crontab /etc/cron.d/ash-thrash

# Environmental Variables
ENV TZ="America/Los_Angeles"

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8884/health', timeout=5)"

EXPOSE 8884

ENTRYPOINT ["/entrypoint.sh"]
CMD ["testing"]