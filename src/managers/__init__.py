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
FILE VERSION: v5.0-6-6.3-3
LAST MODIFIED: 2026-02-07
PHASE: Phase 6 - A/B Testing Infrastructure (v5.1 Migration Phase 1)
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

MANAGERS (Phase 3 - Analysis & Reporting):
- ResultAnalyzerManager: Metrics calculation and threshold comparison
- ReportManager:         JSON/HTML reports, baselines, Discord notifications

MANAGERS (Phase 6 - A/B Testing Infrastructure):
- SnapshotManager:           Versioned test run snapshot capture and loading
- ComparisonAnalyzerManager: Side-by-side snapshot comparison with verdicts

USAGE:
    from src.managers import (
        create_config_manager,
        create_secrets_manager,
        create_logging_config_manager,
        create_nlp_client_manager,
        create_phrase_loader_manager,
        create_test_runner_manager,
        create_result_analyzer_manager,
        create_report_manager,
        create_snapshot_manager,
        create_comparison_analyzer_manager,
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
    
    # Analyze results (Phase 3)
    analyzer = create_result_analyzer_manager(config_manager=config, logging_manager=logging_mgr)
    analysis = analyzer.analyze(summary)
    print(f"Overall accuracy: {analysis.overall_accuracy:.1f}%")
    
    # Generate reports (Phase 3)
    reporter = create_report_manager(config_manager=config, secrets_manager=secrets, logging_manager=logging_mgr)
    json_path = reporter.generate_json_report(analysis)
    html_path = reporter.generate_html_report(analysis)
    
    # Capture snapshot for A/B comparison (Phase 6)
    snapshot_mgr = create_snapshot_manager(config_manager=config, logging_manager=logging_mgr)
    filepath = snapshot_mgr.capture_snapshot(
        test_run_summary=summary, analysis_result=analysis, label="v5.0_baseline",
    )
    
    # Compare two snapshots (Phase 6)
    comparator = create_comparison_analyzer_manager(config_manager=config, logging_manager=logging_mgr)
    baseline = snapshot_mgr.load_snapshot("snapshot_v5.0_baseline_20260206T120000.json")
    candidate = snapshot_mgr.load_snapshot("snapshot_v5.1_candidate_20260207T120000.json")
    comparison = comparator.compare(baseline, candidate)
    print(f"Verdict: {comparison.overall_verdict}")
"""

# Module version
__version__ = "v5.0-6-6.3-3"

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
# Result Analyzer Manager (Phase 3)
# =============================================================================

from .result_analyzer_manager import (
    ResultAnalyzerManager,
    create_result_analyzer_manager,
    AnalysisResult,
    CategoryMetrics,
    SubcategoryMetrics,
    LatencyMetrics,
    FailedTestDetail,
    ThresholdResult,
    ThresholdStatus,
    RegressionSeverity,
)

# =============================================================================
# Report Manager (Phase 3)
# =============================================================================

from .report_manager import (
    ReportManager,
    create_report_manager,
    BaselineComparison,
    RegressionDetail,
    ImprovementDetail,
    ComparisonVerdict,
)

# =============================================================================
# Snapshot Manager (Phase 6 - A/B Testing)
# =============================================================================

from .snapshot_manager import (
    SnapshotManager,
    create_snapshot_manager,
    Snapshot,
    SnapshotMetadata,
    SNAPSHOT_SCHEMA_VERSION,
)

# =============================================================================
# Comparison Analyzer Manager (Phase 6 - A/B Testing)
# =============================================================================

from .comparison_analyzer_manager import (
    ComparisonAnalyzerManager,
    create_comparison_analyzer_manager,
    ComparisonResult,
    CategoryDelta,
    PhraseChange,
    LatencyDelta,
    VERDICT_PASS,
    VERDICT_WARN,
    VERDICT_FAIL,
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
    # Result Analyzer (Phase 3)
    "ResultAnalyzerManager",
    "create_result_analyzer_manager",
    "AnalysisResult",
    "CategoryMetrics",
    "SubcategoryMetrics",
    "LatencyMetrics",
    "FailedTestDetail",
    "ThresholdResult",
    "ThresholdStatus",
    "RegressionSeverity",
    # Report Manager (Phase 3)
    "ReportManager",
    "create_report_manager",
    "BaselineComparison",
    "RegressionDetail",
    "ImprovementDetail",
    "ComparisonVerdict",
    # Snapshot Manager (Phase 6)
    "SnapshotManager",
    "create_snapshot_manager",
    "Snapshot",
    "SnapshotMetadata",
    "SNAPSHOT_SCHEMA_VERSION",
    # Comparison Analyzer Manager (Phase 6)
    "ComparisonAnalyzerManager",
    "create_comparison_analyzer_manager",
    "ComparisonResult",
    "CategoryDelta",
    "PhraseChange",
    "LatencyDelta",
    "VERDICT_PASS",
    "VERDICT_WARN",
    "VERDICT_FAIL",
]
