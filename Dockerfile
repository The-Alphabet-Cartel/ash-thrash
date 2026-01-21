# ============================================================================
# Ash-Thrash v5.0 Production Dockerfile
# ============================================================================
# FILE VERSION: v5.0-1-1.7-1
# LAST MODIFIED: 2026-01-20
# Repository: https://github.com/the-alphabet-cartel/ash-thrash
# Community: The Alphabet Cartel - https://discord.gg/alphabetcartel
# ============================================================================
#
# USAGE:
#   # Build the image
#   docker build -t ghcr.io/the-alphabet-cartel/ash-thrash:latest .
#
#   # Run with docker-compose (recommended)
#   docker-compose up -d
#
# MULTI-STAGE BUILD:
#   Stage 1 (builder): Install dependencies
#   Stage 2 (runtime): Minimal production image
#
# CLEAN ARCHITECTURE COMPLIANCE:
#   - Uses python3.11 -m pip (Rule #10)
#   - Non-root user for security
#   - Health check endpoint configured
#
# ============================================================================

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip (Rule #10: version-specific command)
RUN python3.11 -m pip install --upgrade pip setuptools wheel

# Copy requirements and install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN python3.11 -m pip install -r /tmp/requirements.txt


# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim-bookworm AS runtime

# Labels
LABEL org.opencontainers.image.title="Ash-Thrash" \
      org.opencontainers.image.description="Crisis Detection Testing Suite for The Alphabet Cartel" \
      org.opencontainers.image.version="5.0.0" \
      org.opencontainers.image.vendor="The Alphabet Cartel" \
      org.opencontainers.image.url="https://github.com/the-alphabet-cartel/ash-thrash" \
      org.opencontainers.image.source="https://github.com/the-alphabet-cartel/ash-thrash" \
      org.opencontainers.image.licenses="MIT"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # Force ANSI colors in Docker logs (Charter v5.2.1 colorized logging)
    FORCE_COLOR=1 \
    # Default environment
    THRASH_ENVIRONMENT=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 thrash \
    && useradd --uid 1000 --gid thrash --shell /bin/bash --create-home thrash

# Create application directories
RUN mkdir -p /app/logs /app/reports /app/src/config/phrases \
    && chown -R thrash:thrash /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=thrash:thrash . /app/

# Switch to non-root user
USER thrash

# Expose health check port
EXPOSE 30888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:30888/health || exit 1

# Use tini as init system
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command
CMD ["python3.11", "main.py"]
