"""
Ash-Thrash: Testing Suite for the Ash-NLP Server
CORE PRINCIPLE:
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Thrash is a TESTING SUITE for the Ash-NLP Server that:
1. **PRIMARY**:
2. **SECONDARY**:
3. **TERTIARY**:
4. **PURPOSE**:
********************************************************************************
Managers Package for Ash-Thrash Service
---
FILE VERSION: v5.0
LAST MODIFIED: 2026-01-03
PHASE: Phase 1
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

This package contains resource managers for Ash-Thrash:

MANAGERS:
- ConfigManager: Configuration loading and validation

USAGE:
    from src.managers import create_config_manager, create_secrets_manager

    config = create_config_manager(environment="production")
    secrets = create_secrets_manager(environment="production")
"""

# Module version
__version__ = "v5.0-6-3.0-1"

# =============================================================================
# Configuration Manager
# =============================================================================

from .config_manager import (
    ConfigManager,
    create_config_manager,
)

# =============================================================================
# Secrets Manager
# =============================================================================

from .secrets_manager import (
    SecretsManager,
    create_secrets_manager,
    get_secrets_manager,
    get_secret,
    SecretNotFoundError,
    KNOWN_SECRETS,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # Config
    "ConfigManager",
    "create_config_manager",
    # Secrets
    "SecretsManager",
    "create_secrets_manager",
    "get_secrets_manager",
    "get_secret",
    "SecretNotFoundError",
    "KNOWN_SECRETS",
]
