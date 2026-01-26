# ============================================================================
# Ash-Thrash v5.0 Production Dockerfile
# ============================================================================
# FILE VERSION: v5.0-4-2.0-1
# LAST MODIFIED: 2026-01-22
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
#   - Uses python3.12 -m pip (Rule #10)
#   - Pure Python entrypoint for PUID/PGID (Rule #13)
#   - tini for PID 1 signal handling
#
# ============================================================================

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.12-slim AS builder

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

# Create app directory
WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.12-slim AS runtime

# Labels
LABEL maintainer="PapaBearDoes <github.com/PapaBearDoes>"
LABEL org.opencontainers.image.title="Ash-NLP"
LABEL org.opencontainers.image.description="Crisis Detection Testing Suite for The Alphabet Cartel"
LABEL org.opencontainers.image.version="5.0.0"
LABEL org.opencontainers.image.vendor="The Alphabet Cartel"
LABEL org.opencontainers.image.url="https://github.com/the-alphabet-cartel/ash-nlp"
LABEL org.opencontainers.image.source="https://github.com/the-alphabet-cartel/ash-nlp"

# Default user/group IDs (can be overridden at runtime via PUID/PGID)
ARG DEFAULT_UID=1000
ARG DEFAULT_GID=1000

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PATH="/opt/venv/bin:$PATH" \
    # Force ANSI colors in Docker logs (Charter v5.2.1 colorized logging)
    FORCE_COLOR=1 \
    # Default environment
    THRASH_ENVIRONMENT=production \
    # Application settings
    THRASH_LOG_LEVEL=INFO \
    TZ=America/Los_Angeles \
    # Default PUID/PGID (LinuxServer.io style)
    PUID=${DEFAULT_UID} \
    PGID=${DEFAULT_GID}

# Install runtime dependencies
# Note: tini for PID 1 signal handling (Rule #13 - no gosu, pure Python privilege drop)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user (will be modified at runtime by entrypoint if PUID/PGID differ)
RUN groupadd --gid ${PGID} ash-thrash \
    && useradd --uid ${PUID} --gid ash-thrash --shell /bin/bash --create-home ash-thrash \
    && mkdir -p ${APP_HOME}/logs ${APP_HOME}/reports ${APP_HOME}/src/config/phrases \
    && chown -R ${PUID}:${PGID} ${APP_HOME}

# Set working directory
WORKDIR ${APP_HOME}

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . ${APP_HOME}/

# Copy and set up entrypoint script (Rule #13: Pure Python PUID/PGID handling)
COPY docker-entrypoint.py ${APP_HOME}/docker-entrypoint.py
RUN chmod +x ${APP_HOME}/docker-entrypoint.py

# Set ownership of app directory to default user
# (entrypoint will fix this at runtime based on PUID/PGID)
RUN chown -R ${PUID}:${PGID} ${APP_HOME}

# NOTE: We do NOT switch to USER thrash here!
# The entrypoint script handles user switching at runtime after fixing permissions.
# This allows PUID/PGID to work correctly with mounted volumes.

# Expose health check port
EXPOSE 30888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:30888/health || exit 1

# Use tini as init system for proper signal handling
# Then our Python entrypoint for PUID/PGID handling (Rule #13)
ENTRYPOINT ["/usr/bin/tini", "--", "python", "/app/docker-entrypoint.py"]

# Default command (passed to docker-entrypoint.py)
CMD ["python", "main.py"]
