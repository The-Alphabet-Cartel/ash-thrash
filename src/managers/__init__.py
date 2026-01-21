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
Managers Package for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.3-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 2 - Test Execution Engine
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

This package contains resource managers for Ash-Thrash:

MANAGERS (Phase 1 - Foundation):
- ConfigManager:        Configuration loading and validation
- SecretsManager:       Docker secrets and credential management
- LoggingConfigManager: Colorized logging with SUCCESS level
- NLPClientManager:     HTTP client for Ash-NLP API communication
- PhraseLoaderManager:  Test phrase loading and validation

MANAGERS (Phase 2 - Test Execution):
- TestRunnerManager:    Test orchestration and execution

USAGE:
    from src.managers import (
        create_config_manager,
        create_secrets_manager,
        create_logging_config_manager,
        create_nlp_client_manager,
        create_phrase_loader_manager,
        create_test_runner_manager,
    )
    from src.validators import (
        create_classification_validator,
        create_response_validator,
    )

    # Initialize managers with dependency injection
    config = create_config_manager()
    secrets = create_secrets_manager()
    logging_mgr = create_logging_config_manager(config_manager=config)
    nlp_client = create_nlp_client_manager(config_manager=config, logging_manager=logging_mgr)
    phrase_loader = create_phrase_loader_manager(config_manager=config, logging_manager=logging_mgr)
    class_validator = create_classification_validator(logging_manager=logging_mgr)
    resp_validator = create_response_validator(logging_manager=logging_mgr)
    
    # Create test runner
    runner = create_test_runner_manager(
        nlp_client=nlp_client,
        phrase_loader=phrase_loader,
        classification_validator=class_validator,
        response_validator=resp_validator,
        config_manager=config,
        logging_manager=logging_mgr,
    )
    
    # Run tests
    summary = await runner.run_all_tests()
"""

# Module version
__version__ = "v5.0-2-2.3-1"

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
# Logging Configuration Manager
# =============================================================================

from .logging_config_manager import (
    LoggingConfigManager,
    create_logging_config_manager,
    SUCCESS_LEVEL,
    Colors,
    Symbols,
)

# =============================================================================
# NLP Client Manager
# =============================================================================

from .nlp_client_manager import (
    NLPClientManager,
    create_nlp_client_manager,
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    AnalyzeVerbosity,
    NLPClientError,
    NLPConnectionError,
    NLPTimeoutError,
    NLPResponseError,
)

# =============================================================================
# Phrase Loader Manager
# =============================================================================

from .phrase_loader_manager import (
    PhraseLoaderManager,
    create_phrase_loader_manager,
    TestPhrase,
    CategoryInfo,
    PhraseStatistics,
    CATEGORY_DEFINITE,
    CATEGORY_EDGE_CASE,
    CATEGORY_SPECIALTY,
)

# =============================================================================
# Test Runner Manager (Phase 2)
# =============================================================================

from .test_runner_manager import (
    TestRunnerManager,
    create_test_runner_manager,
    TestResult,
    TestRunSummary,
    TestStatus,
    ErrorType,
    ProgressCallback,
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
    # Logging
    "LoggingConfigManager",
    "create_logging_config_manager",
    "SUCCESS_LEVEL",
    "Colors",
    "Symbols",
    # NLP Client
    "NLPClientManager",
    "create_nlp_client_manager",
    "AnalyzeRequest",
    "AnalyzeResponse",
    "HealthResponse",
    "AnalyzeVerbosity",
    "NLPClientError",
    "NLPConnectionError",
    "NLPTimeoutError",
    "NLPResponseError",
    # Phrase Loader
    "PhraseLoaderManager",
    "create_phrase_loader_manager",
    "TestPhrase",
    "CategoryInfo",
    "PhraseStatistics",
    "CATEGORY_DEFINITE",
    "CATEGORY_EDGE_CASE",
    "CATEGORY_SPECIALTY",
    # Test Runner (Phase 2)
    "TestRunnerManager",
    "create_test_runner_manager",
    "TestResult",
    "TestRunSummary",
    "TestStatus",
    "ErrorType",
    "ProgressCallback",
]
