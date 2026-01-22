#!/bin/bash
# ============================================================================
# Ash-Thrash v5.0 Docker Entrypoint Script
# ============================================================================
# FILE VERSION: v5.0-4-1.0-1
# LAST MODIFIED: 2026-01-22
# Repository: https://github.com/the-alphabet-cartel/ash-thrash
# Community: The Alphabet Cartel - https://discord.gg/alphabetcartel
# ============================================================================
#
# PURPOSE:
#   LinuxServer.io-style entrypoint that handles PUID/PGID at runtime,
#   ensuring mounted volumes have correct permissions regardless of host
#   user configuration.
#
# ENVIRONMENT VARIABLES:
#   PUID - User ID to run as (default: 1000)
#   PGID - Group ID to run as (default: 1000)
#
# ============================================================================

set -e

# Default values
PUID=${PUID:-1000}
PGID=${PGID:-1000}

# Colors for output
GREEN='\033[92m'
CYAN='\033[96m'
YELLOW='\033[93m'
RESET='\033[0m'

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${CYAN}  Ash-Thrash Container Initialization${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

# =============================================================================
# Step 1: Configure User/Group
# =============================================================================

echo -e "${GREEN}▶${RESET} Configuring user/group..."
echo -e "  PUID: ${YELLOW}${PUID}${RESET}"
echo -e "  PGID: ${YELLOW}${PGID}${RESET}"

# Modify the thrash group's GID
groupmod -o -g "${PGID}" thrash 2>/dev/null || true

# Modify the thrash user's UID
usermod -o -u "${PUID}" thrash 2>/dev/null || true

# =============================================================================
# Step 2: Fix Ownership of Application Directories
# =============================================================================

echo -e "${GREEN}▶${RESET} Setting directory ownership..."

# Directories that need write access
WRITABLE_DIRS=(
    "/app/logs"
    "/app/reports"
)

for dir in "${WRITABLE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        chown -R thrash:thrash "$dir"
        echo -e "  ✓ ${dir}"
    fi
done

# =============================================================================
# Step 3: Drop Privileges and Execute Command
# =============================================================================

echo -e "${GREEN}▶${RESET} Starting application as user ${YELLOW}thrash${RESET} (${PUID}:${PGID})"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# Use gosu to drop privileges and run the command
# gosu is the recommended tool for this (better than su or sudo)
exec gosu thrash:thrash "$@"
