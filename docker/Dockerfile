FROM python:3.11-slim

LABEL maintainer="The Alphabet Cartel"
LABEL description="Ash-Thrash Testing Suite"
LABEL repository="https://github.com/The-Alphabet-Cartel/ash-thrash"

WORKDIR /app

# Create non-root user with matching UID/GID for consistency across containers
RUN groupadd -r thrash && useradd -r -g thrash -u 1001 thrash

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
COPY --chown=1001:1001 . .

# Create results directory
RUN mkdir -p ./results && \
    chown -R 1001:1001 /app

# Switch to non-root user
USER thrash
    
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