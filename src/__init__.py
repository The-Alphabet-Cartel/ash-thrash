"""
============================================================================
Ash-Thrash: Discord Crisis Detection Testing Suite
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Validate  → Verify crisis detection accuracy through live Ash-NLP integration testing
    Challenge → Stress test the system with edge cases and adversarial scenarios
    Guard     → Prevent regressions that could compromise detection reliability
    Protect   → Safeguard our LGBTQIA+ community through rigorous quality assurance

============================================================================
Ash-Thrash Source Package
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.7-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 1 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

This is the main source package for Ash-Thrash containing:

PACKAGES:
- managers:   Configuration and resource management
- config:     JSON configuration files
- validators: Response and classification validation (Phase 2)

MANAGERS (Phase 1):
- ConfigManager:        Configuration loading and validation
- SecretsManager:       Docker secrets and credential management  
- LoggingConfigManager: Colorized logging with SUCCESS level
- NLPClientManager:     HTTP client for Ash-NLP API communication
- PhraseLoaderManager:  Test phrase loading and validation

USAGE:
    from src.managers import (
        create_config_manager,
        create_secrets_manager,
        create_logging_config_manager,
        create_nlp_client_manager,
        create_phrase_loader_manager,
    )
"""

__version__ = "5.0.0"
__author__ = "The Alphabet Cartel"
__email__ = "dev@alphabetcartel.org"
__url__ = "https://github.com/the-alphabet-cartel/ash-thrash"

# Package metadata
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__url__",
]
