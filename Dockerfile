# Ash-Thrash Testing Suite Dockerfile
# Repository: https://github.com/the-alphabet-cartel/ash-thrash
# Discord: https://discord.gg/alphabetcartel
# Website: http://alphabetcartel.org

FROM python:3.11-slim

LABEL maintainer="The Alphabet Cartel"
LABEL description="Ash-Thrash Testing Suite"
LABEL repository="https://github.com/The-Alphabet-Cartel/ash-thrash"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create non-root user with matching UID/GID for consistency across containers
RUN groupadd -g 1001 thrash && \
    useradd -g 1001 -u 1001 thrash

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=thrash:thrash . .

# Create directories for results and logs
RUN mkdir -p ./results ./logs ./reports && \
    chown -R thrash:thrash /app  && \
    chmod 755 /app

# Create non-root user for security
USER thrash

# Environmental Variables
ENV TZ="America/Los_Angeles"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8884/health || exit 1

# Expose API port
EXPOSE 8884

# Default command - runs the API server
CMD ["python", "src/ash_thrash_api.py"]