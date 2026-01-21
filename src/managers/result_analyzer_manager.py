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
Result Analyzer Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-3-3.1-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 3 - Analysis & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Analyze test results from TestRunSummary
- Calculate overall accuracy metrics
- Calculate per-category and per-subcategory breakdown
- Calculate false positive/negative rates
- Calculate latency percentiles (p50, p95, p99)
- Compare results against accuracy thresholds
- Identify failed tests with detailed context
- Provide serialization for reporting

METRICS CALCULATED:
- Overall accuracy (passed / testable)
- Category accuracy with threshold comparison
- Subcategory accuracy breakdown
- False positive rate (non-crisis flagged as crisis)
- False negative rate (crisis flagged as non-crisis)
- Latency statistics (min, max, mean, median, p95, p99)

USAGE:
    from src.managers.result_analyzer_manager import create_result_analyzer_manager
    
    analyzer = create_result_analyzer_manager(
        config_manager=config,
        logging_manager=logging_mgr,
    )
    
    # Analyze a test run
    analysis = analyzer.analyze(test_run_summary)
    
    # Get analysis as dictionary for reporting
    report_data = analysis.to_dict()
"""

import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Module version
__version__ = "v5.0-3-3.1-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Priority levels considered "crisis" for false positive/negative calculations
CRISIS_PRIORITIES = {"critical", "high", "medium"}

# Priority levels considered "non-crisis"
NON_CRISIS_PRIORITIES = {"low", "none"}

# Category to threshold mapping (matches config thresholds section)
CATEGORY_THRESHOLD_MAP = {
    "critical_high_priority": "high_target_accuracy",
    "high_priority": "high_target_accuracy",
    "medium_priority": "medium_target_accuracy",
    "low_priority": "low_target_accuracy",
    "none_priority": "none_target_accuracy",
    # Edge cases and specialty use their own thresholds
    "edge_cases": "edge_case_target_accuracy",
    "maybe_high_medium": "edge_case_target_accuracy",
    "maybe_medium_low": "edge_case_target_accuracy",
    "maybe_low_none": "edge_case_target_accuracy",
    "specialty": "specialty_target_accuracy",
    "irony_sarcasm": "specialty_target_accuracy",
    "gaming_context": "specialty_target_accuracy",
    "songs_quotes": "specialty_target_accuracy",
    "lgbtqia_specific": "specialty_target_accuracy",
    "cultural_slang": "specialty_target_accuracy",
    "language_hints": "specialty_target_accuracy",
}


# =============================================================================
# Enums
# =============================================================================

class ThresholdStatus(str, Enum):
    """Status of threshold comparison."""
    MET = "met"
    NOT_MET = "not_met"
    WARNING = "warning"  # Within 2% of threshold
    NO_THRESHOLD = "no_threshold"


class RegressionSeverity(str, Enum):
    """Severity of detected regression."""
    NONE = "none"
    WARNING = "warning"
    ALERT = "alert"
    CRITICAL = "critical"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LatencyMetrics:
    """
    Latency statistics from test execution.
    
    All values in milliseconds.
    """
    min_ms: float = 0.0
    max_ms: float = 0.0
    mean_ms: float = 0.0
    median_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    std_dev_ms: float = 0.0
    sample_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "mean_ms": round(self.mean_ms, 2),
            "median_ms": round(self.median_ms, 2),
            "p50_ms": round(self.p50_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "p99_ms": round(self.p99_ms, 2),
            "std_dev_ms": round(self.std_dev_ms, 2),
            "sample_count": self.sample_count,
        }


@dataclass
class CategoryMetrics:
    """
    Metrics for a single test category.
    """
    category: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    accuracy: float = 0.0
    target_accuracy: float = 0.0
    threshold_status: ThresholdStatus = ThresholdStatus.NO_THRESHOLD
    delta_from_target: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "accuracy": round(self.accuracy, 2),
            "target_accuracy": round(self.target_accuracy, 2),
            "threshold_status": self.threshold_status.value,
            "delta_from_target": round(self.delta_from_target, 2),
        }


@dataclass
class SubcategoryMetrics:
    """
    Metrics for a test subcategory.
    """
    category: str
    subcategory: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    accuracy: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category,
            "subcategory": self.subcategory,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "accuracy": round(self.accuracy, 2),
        }


@dataclass
class FailedTestDetail:
    """
    Detailed information about a failed test.
    """
    phrase_id: str
    category: str
    subcategory: str
    message: str
    expected_priorities: List[str]
    actual_severity: Optional[str]
    crisis_score: Optional[float]
    confidence: Optional[float]
    failure_reason: Optional[str]
    response_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phrase_id": self.phrase_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "message": self.message,
            "expected_priorities": self.expected_priorities,
            "actual_severity": self.actual_severity,
            "crisis_score": round(self.crisis_score, 4) if self.crisis_score else None,
            "confidence": round(self.confidence, 4) if self.confidence else None,
            "failure_reason": self.failure_reason,
            "response_time_ms": round(self.response_time_ms, 2),
        }


@dataclass
class ThresholdResult:
    """
    Result of comparing a metric against its threshold.
    """
    metric_name: str
    actual_value: float
    target_value: float
    status: ThresholdStatus
    delta: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "actual_value": round(self.actual_value, 2),
            "target_value": round(self.target_value, 2),
            "status": self.status.value,
            "delta": round(self.delta, 2),
        }


@dataclass
class AnalysisResult:
    """
    Complete analysis of a test run.
    
    This is the primary output of the ResultAnalyzerManager and contains
    all metrics calculated from a TestRunSummary.
    
    Attributes:
        run_id: Unique identifier from the test run
        timestamp: When the analysis was performed
        test_run_start: When the test run started
        test_run_end: When the test run ended
        test_run_duration_seconds: Total run duration
        
        overall_accuracy: Percentage of tests passed (excluding errors)
        total_tests: Total number of tests executed
        passed_tests: Tests that passed
        failed_tests: Tests that failed (classification mismatch)
        error_tests: Tests with errors (API/connection issues)
        
        category_metrics: Detailed metrics per category
        subcategory_metrics: Detailed metrics per subcategory
        
        false_positive_rate: Non-crisis messages flagged as crisis
        false_negative_rate: Crisis messages flagged as non-crisis
        
        latency_metrics: Response time statistics
        
        threshold_results: Comparison of each category against targets
        all_thresholds_met: Whether all required thresholds passed
        
        failed_test_details: List of all failed tests with context
    """
    run_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    test_run_start: Optional[datetime] = None
    test_run_end: Optional[datetime] = None
    test_run_duration_seconds: float = 0.0
    
    # Overall metrics
    overall_accuracy: float = 0.0
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    skipped_tests: int = 0
    
    # Category breakdown
    category_metrics: Dict[str, CategoryMetrics] = field(default_factory=dict)
    
    # Subcategory breakdown
    subcategory_metrics: Dict[str, SubcategoryMetrics] = field(default_factory=dict)
    
    # False positive/negative rates
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    true_positive_count: int = 0
    true_negative_count: int = 0
    false_positive_count: int = 0
    false_negative_count: int = 0
    
    # Performance metrics
    latency_metrics: LatencyMetrics = field(default_factory=LatencyMetrics)
    
    # Threshold comparison
    threshold_results: Dict[str, ThresholdResult] = field(default_factory=dict)
    all_thresholds_met: bool = False
    thresholds_met_count: int = 0
    thresholds_total_count: int = 0
    
    # Failed test details
    failed_test_details: List[FailedTestDetail] = field(default_factory=list)
    
    # NLP server info (from test run)
    nlp_server_info: Optional[Dict[str, Any]] = None
    
    # Categories included in analysis
    categories_analyzed: List[str] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as decimal (0.0-1.0)."""
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.error_tests / self.total_tests) * 100
    
    @property
    def tests_per_second(self) -> float:
        """Calculate throughput."""
        if self.test_run_duration_seconds > 0:
            return self.total_tests / self.test_run_duration_seconds
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        This format is used for JSON reports and baseline storage.
        """
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "test_run_start": self.test_run_start.isoformat() if self.test_run_start else None,
            "test_run_end": self.test_run_end.isoformat() if self.test_run_end else None,
            "test_run_duration_seconds": round(self.test_run_duration_seconds, 2),
            
            "summary": {
                "overall_accuracy": round(self.overall_accuracy, 2),
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "error_tests": self.error_tests,
                "skipped_tests": self.skipped_tests,
                "pass_rate": round(self.pass_rate, 4),
                "error_rate": round(self.error_rate, 2),
                "tests_per_second": round(self.tests_per_second, 2),
            },
            
            "false_positive_negative": {
                "false_positive_rate": round(self.false_positive_rate, 2),
                "false_negative_rate": round(self.false_negative_rate, 2),
                "true_positive_count": self.true_positive_count,
                "true_negative_count": self.true_negative_count,
                "false_positive_count": self.false_positive_count,
                "false_negative_count": self.false_negative_count,
            },
            
            "category_metrics": {
                name: metrics.to_dict() 
                for name, metrics in self.category_metrics.items()
            },
            
            "subcategory_metrics": {
                key: metrics.to_dict()
                for key, metrics in self.subcategory_metrics.items()
            },
            
            "latency_metrics": self.latency_metrics.to_dict(),
            
            "thresholds": {
                "all_met": self.all_thresholds_met,
                "met_count": self.thresholds_met_count,
                "total_count": self.thresholds_total_count,
                "results": {
                    name: result.to_dict()
                    for name, result in self.threshold_results.items()
                },
            },
            
            "failed_tests": [
                detail.to_dict() for detail in self.failed_test_details
            ],
            
            "categories_analyzed": self.categories_analyzed,
            "nlp_server_info": self.nlp_server_info,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """
        Create AnalysisResult from dictionary.
        
        Used for loading baselines.
        """
        result = cls(run_id=data["run_id"])
        
        # Parse timestamps
        result.timestamp = datetime.fromisoformat(data["timestamp"])
        if data.get("test_run_start"):
            result.test_run_start = datetime.fromisoformat(data["test_run_start"])
        if data.get("test_run_end"):
            result.test_run_end = datetime.fromisoformat(data["test_run_end"])
        result.test_run_duration_seconds = data.get("test_run_duration_seconds", 0.0)
        
        # Summary metrics
        summary = data.get("summary", {})
        result.overall_accuracy = summary.get("overall_accuracy", 0.0)
        result.total_tests = summary.get("total_tests", 0)
        result.passed_tests = summary.get("passed_tests", 0)
        result.failed_tests = summary.get("failed_tests", 0)
        result.error_tests = summary.get("error_tests", 0)
        result.skipped_tests = summary.get("skipped_tests", 0)
        
        # False positive/negative
        fp_fn = data.get("false_positive_negative", {})
        result.false_positive_rate = fp_fn.get("false_positive_rate", 0.0)
        result.false_negative_rate = fp_fn.get("false_negative_rate", 0.0)
        result.true_positive_count = fp_fn.get("true_positive_count", 0)
        result.true_negative_count = fp_fn.get("true_negative_count", 0)
        result.false_positive_count = fp_fn.get("false_positive_count", 0)
        result.false_negative_count = fp_fn.get("false_negative_count", 0)
        
        # Category metrics
        for name, cat_data in data.get("category_metrics", {}).items():
            result.category_metrics[name] = CategoryMetrics(
                category=cat_data["category"],
                total=cat_data.get("total", 0),
                passed=cat_data.get("passed", 0),
                failed=cat_data.get("failed", 0),
                errors=cat_data.get("errors", 0),
                accuracy=cat_data.get("accuracy", 0.0),
                target_accuracy=cat_data.get("target_accuracy", 0.0),
                threshold_status=ThresholdStatus(cat_data.get("threshold_status", "no_threshold")),
                delta_from_target=cat_data.get("delta_from_target", 0.0),
            )
        
        # Subcategory metrics
        for key, sub_data in data.get("subcategory_metrics", {}).items():
            result.subcategory_metrics[key] = SubcategoryMetrics(
                category=sub_data["category"],
                subcategory=sub_data["subcategory"],
                total=sub_data.get("total", 0),
                passed=sub_data.get("passed", 0),
                failed=sub_data.get("failed", 0),
                errors=sub_data.get("errors", 0),
                accuracy=sub_data.get("accuracy", 0.0),
            )
        
        # Latency metrics
        latency_data = data.get("latency_metrics", {})
        result.latency_metrics = LatencyMetrics(
            min_ms=latency_data.get("min_ms", 0.0),
            max_ms=latency_data.get("max_ms", 0.0),
            mean_ms=latency_data.get("mean_ms", 0.0),
            median_ms=latency_data.get("median_ms", 0.0),
            p50_ms=latency_data.get("p50_ms", 0.0),
            p95_ms=latency_data.get("p95_ms", 0.0),
            p99_ms=latency_data.get("p99_ms", 0.0),
            std_dev_ms=latency_data.get("std_dev_ms", 0.0),
            sample_count=latency_data.get("sample_count", 0),
        )
        
        # Thresholds
        thresholds_data = data.get("thresholds", {})
        result.all_thresholds_met = thresholds_data.get("all_met", False)
        result.thresholds_met_count = thresholds_data.get("met_count", 0)
        result.thresholds_total_count = thresholds_data.get("total_count", 0)
        
        for name, thresh_data in thresholds_data.get("results", {}).items():
            result.threshold_results[name] = ThresholdResult(
                metric_name=thresh_data["metric_name"],
                actual_value=thresh_data.get("actual_value", 0.0),
                target_value=thresh_data.get("target_value", 0.0),
                status=ThresholdStatus(thresh_data.get("status", "no_threshold")),
                delta=thresh_data.get("delta", 0.0),
            )
        
        # Failed tests (minimal reconstruction)
        for failed_data in data.get("failed_tests", []):
            result.failed_test_details.append(FailedTestDetail(
                phrase_id=failed_data["phrase_id"],
                category=failed_data["category"],
                subcategory=failed_data["subcategory"],
                message=failed_data["message"],
                expected_priorities=failed_data.get("expected_priorities", []),
                actual_severity=failed_data.get("actual_severity"),
                crisis_score=failed_data.get("crisis_score"),
                confidence=failed_data.get("confidence"),
                failure_reason=failed_data.get("failure_reason"),
                response_time_ms=failed_data.get("response_time_ms", 0.0),
            ))
        
        result.categories_analyzed = data.get("categories_analyzed", [])
        result.nlp_server_info = data.get("nlp_server_info")
        
        return result


# =============================================================================
# Result Analyzer Manager
# =============================================================================

class ResultAnalyzerManager:
    """
    Analyzes test results and calculates comprehensive metrics.
    
    This manager transforms raw TestRunSummary data into detailed
    AnalysisResult objects with accuracy metrics, latency statistics,
    threshold comparisons, and failed test details.
    
    Attributes:
        config_manager: Configuration manager for thresholds
        thresholds: Cached accuracy thresholds from config
    
    Example:
        >>> analyzer = create_result_analyzer_manager(config_manager=config)
        >>> analysis = analyzer.analyze(test_run_summary)
        >>> print(f"Overall accuracy: {analysis.overall_accuracy:.1f}%")
        >>> print(f"All thresholds met: {analysis.all_thresholds_met}")
    """
    
    def __init__(
        self,
        config_manager: Optional[Any] = None,
        logging_manager: Optional[Any] = None,
    ):
        """
        Initialize the ResultAnalyzerManager.
        
        Args:
            config_manager: Optional ConfigManager for threshold configuration
            logging_manager: Optional LoggingConfigManager for custom logging
        
        Note:
            Use create_result_analyzer_manager() factory function instead.
        """
        self._config = config_manager
        
        # Set up logger
        if logging_manager:
            self._logger = logging_manager.get_logger("result_analyzer")
        else:
            self._logger = logger
        
        # Load thresholds from config
        self._thresholds = self._load_thresholds()
        
        self._logger.info(f"✅ ResultAnalyzerManager {__version__} initialized")
    
    def _load_thresholds(self) -> Dict[str, float]:
        """Load accuracy thresholds from configuration."""
        thresholds = {}
        
        if self._config:
            try:
                thresholds = {
                    "high_target_accuracy": self._config.get(
                        "thresholds", "high_target_accuracy"
                    ) or 95.0,
                    "medium_target_accuracy": self._config.get(
                        "thresholds", "medium_target_accuracy"
                    ) or 85.0,
                    "low_target_accuracy": self._config.get(
                        "thresholds", "low_target_accuracy"
                    ) or 85.0,
                    "none_target_accuracy": self._config.get(
                        "thresholds", "none_target_accuracy"
                    ) or 95.0,
                    "edge_case_target_accuracy": self._config.get(
                        "thresholds", "edge_case_target_accuracy"
                    ) or 70.0,
                    "specialty_target_accuracy": self._config.get(
                        "thresholds", "specialty_target_accuracy"
                    ) or 75.0,
                }
            except Exception as e:
                self._logger.warning(f"⚠️ Failed to load thresholds from config: {e}")
        
        # Apply defaults for any missing thresholds
        defaults = {
            "high_target_accuracy": 95.0,
            "medium_target_accuracy": 85.0,
            "low_target_accuracy": 85.0,
            "none_target_accuracy": 95.0,
            "edge_case_target_accuracy": 70.0,
            "specialty_target_accuracy": 75.0,
        }
        
        for key, default in defaults.items():
            if key not in thresholds or thresholds[key] is None:
                thresholds[key] = default
        
        return thresholds
    
    def analyze(self, test_run: Any) -> AnalysisResult:
        """
        Analyze a test run and generate comprehensive metrics.
        
        Args:
            test_run: TestRunSummary from TestRunnerManager
        
        Returns:
            AnalysisResult with all calculated metrics
        
        Example:
            >>> analysis = analyzer.analyze(test_run_summary)
            >>> print(f"Accuracy: {analysis.overall_accuracy:.1f}%")
            >>> for cat, metrics in analysis.category_metrics.items():
            ...     print(f"  {cat}: {metrics.accuracy:.1f}%")
        """
        self._logger.info(f"📊 Analyzing test run: {test_run.run_id}")
        
        # Initialize result
        analysis = AnalysisResult(
            run_id=test_run.run_id,
            timestamp=datetime.now(),
            test_run_start=test_run.start_time,
            test_run_end=test_run.end_time,
            test_run_duration_seconds=test_run.duration_seconds,
            total_tests=test_run.total_tests,
            passed_tests=test_run.passed_tests,
            failed_tests=test_run.failed_tests,
            error_tests=test_run.error_tests,
            skipped_tests=getattr(test_run, 'skipped_tests', 0),
            categories_analyzed=test_run.categories_tested,
            nlp_server_info=test_run.nlp_server_info,
        )
        
        # Calculate overall accuracy (excluding errors)
        testable = analysis.passed_tests + analysis.failed_tests
        if testable > 0:
            analysis.overall_accuracy = (analysis.passed_tests / testable) * 100
        
        # Calculate category and subcategory metrics
        self._calculate_category_metrics(test_run.results, analysis)
        
        # Calculate false positive/negative rates
        self._calculate_fp_fn_rates(test_run.results, analysis)
        
        # Calculate latency metrics
        self._calculate_latency_metrics(test_run.results, analysis)
        
        # Compare against thresholds
        self._evaluate_thresholds(analysis)
        
        # Collect failed test details
        self._collect_failed_details(test_run.results, analysis)
        
        self._logger.info(
            f"✅ Analysis complete: {analysis.overall_accuracy:.1f}% accuracy, "
            f"{analysis.thresholds_met_count}/{analysis.thresholds_total_count} thresholds met"
        )
        
        return analysis
    
    def _calculate_category_metrics(
        self, 
        results: List[Any], 
        analysis: AnalysisResult
    ) -> None:
        """Calculate accuracy metrics by category and subcategory."""
        # Category aggregation
        category_stats: Dict[str, Dict[str, int]] = {}
        # Subcategory aggregation
        subcategory_stats: Dict[str, Dict[str, int]] = {}
        
        for result in results:
            category = result.category
            subcategory = result.subcategory
            status = result.status.value if hasattr(result.status, 'value') else str(result.status)
            
            # Initialize category stats
            if category not in category_stats:
                category_stats[category] = {
                    "total": 0, "passed": 0, "failed": 0, "errors": 0
                }
            
            # Initialize subcategory stats
            subcat_key = f"{category}.{subcategory}"
            if subcat_key not in subcategory_stats:
                subcategory_stats[subcat_key] = {
                    "category": category,
                    "subcategory": subcategory,
                    "total": 0, "passed": 0, "failed": 0, "errors": 0
                }
            
            # Count based on status (only passed/failed count toward accuracy)
            if status == "passed":
                category_stats[category]["total"] += 1
                category_stats[category]["passed"] += 1
                subcategory_stats[subcat_key]["total"] += 1
                subcategory_stats[subcat_key]["passed"] += 1
            elif status == "failed":
                category_stats[category]["total"] += 1
                category_stats[category]["failed"] += 1
                subcategory_stats[subcat_key]["total"] += 1
                subcategory_stats[subcat_key]["failed"] += 1
            elif status == "error":
                category_stats[category]["errors"] += 1
                subcategory_stats[subcat_key]["errors"] += 1
        
        # Create CategoryMetrics objects
        for category, stats in category_stats.items():
            accuracy = 0.0
            if stats["total"] > 0:
                accuracy = (stats["passed"] / stats["total"]) * 100
            
            # Get target threshold for this category
            threshold_key = CATEGORY_THRESHOLD_MAP.get(
                category, "specialty_target_accuracy"
            )
            target = self._thresholds.get(threshold_key, 75.0)
            
            analysis.category_metrics[category] = CategoryMetrics(
                category=category,
                total=stats["total"],
                passed=stats["passed"],
                failed=stats["failed"],
                errors=stats["errors"],
                accuracy=accuracy,
                target_accuracy=target,
                delta_from_target=accuracy - target,
            )
        
        # Create SubcategoryMetrics objects
        for subcat_key, stats in subcategory_stats.items():
            accuracy = 0.0
            if stats["total"] > 0:
                accuracy = (stats["passed"] / stats["total"]) * 100
            
            analysis.subcategory_metrics[subcat_key] = SubcategoryMetrics(
                category=stats["category"],
                subcategory=stats["subcategory"],
                total=stats["total"],
                passed=stats["passed"],
                failed=stats["failed"],
                errors=stats["errors"],
                accuracy=accuracy,
            )
    
    def _calculate_fp_fn_rates(
        self, 
        results: List[Any], 
        analysis: AnalysisResult
    ) -> None:
        """
        Calculate false positive and false negative rates.
        
        For crisis detection:
        - True Positive (TP): Crisis message correctly identified as crisis
        - True Negative (TN): Non-crisis message correctly identified as non-crisis
        - False Positive (FP): Non-crisis message incorrectly flagged as crisis
        - False Negative (FN): Crisis message incorrectly marked as non-crisis
        
        Note: FN is more dangerous than FP - missing a real crisis is worse
        than a false alarm.
        """
        tp, tn, fp, fn = 0, 0, 0, 0
        
        for result in results:
            # Skip errors - we can't determine FP/FN for failed API calls
            status = result.status.value if hasattr(result.status, 'value') else str(result.status)
            if status == "error":
                continue
            
            # Determine expected category (crisis vs non-crisis)
            expected_priorities = result.expected_priorities
            expected_is_crisis = any(
                p.lower() in CRISIS_PRIORITIES 
                for p in expected_priorities
            )
            
            # Determine actual classification
            actual_severity = result.actual_severity
            actual_is_crisis = (
                actual_severity and 
                actual_severity.lower() in CRISIS_PRIORITIES
            )
            
            # Classify into TP/TN/FP/FN
            if expected_is_crisis and actual_is_crisis:
                tp += 1
            elif not expected_is_crisis and not actual_is_crisis:
                tn += 1
            elif not expected_is_crisis and actual_is_crisis:
                fp += 1
            elif expected_is_crisis and not actual_is_crisis:
                fn += 1
        
        # Store counts
        analysis.true_positive_count = tp
        analysis.true_negative_count = tn
        analysis.false_positive_count = fp
        analysis.false_negative_count = fn
        
        # Calculate rates
        # FP rate = FP / (FP + TN) - of all non-crisis messages, how many were flagged
        if (fp + tn) > 0:
            analysis.false_positive_rate = (fp / (fp + tn)) * 100
        
        # FN rate = FN / (FN + TP) - of all crisis messages, how many were missed
        if (fn + tp) > 0:
            analysis.false_negative_rate = (fn / (fn + tp)) * 100
    
    def _calculate_latency_metrics(
        self, 
        results: List[Any], 
        analysis: AnalysisResult
    ) -> None:
        """Calculate latency statistics from response times."""
        # Collect valid response times (skip zeros/missing)
        response_times = [
            r.response_time_ms 
            for r in results 
            if r.response_time_ms > 0
        ]
        
        if not response_times:
            return
        
        sorted_times = sorted(response_times)
        count = len(sorted_times)
        
        # Calculate percentile indices
        def percentile(data: List[float], p: float) -> float:
            """Calculate percentile value."""
            idx = int(len(data) * p / 100)
            return data[min(idx, len(data) - 1)]
        
        analysis.latency_metrics = LatencyMetrics(
            min_ms=min(sorted_times),
            max_ms=max(sorted_times),
            mean_ms=statistics.mean(sorted_times),
            median_ms=statistics.median(sorted_times),
            p50_ms=percentile(sorted_times, 50),
            p95_ms=percentile(sorted_times, 95),
            p99_ms=percentile(sorted_times, 99),
            std_dev_ms=statistics.stdev(sorted_times) if count > 1 else 0.0,
            sample_count=count,
        )
    
    def _evaluate_thresholds(self, analysis: AnalysisResult) -> None:
        """Compare category accuracy against configured thresholds."""
        met_count = 0
        total_count = 0
        
        for category, metrics in analysis.category_metrics.items():
            target = metrics.target_accuracy
            actual = metrics.accuracy
            delta = actual - target
            
            # Determine status
            if actual >= target:
                status = ThresholdStatus.MET
                met_count += 1
            elif actual >= (target - 2.0):  # Within 2% is warning
                status = ThresholdStatus.WARNING
            else:
                status = ThresholdStatus.NOT_MET
            
            # Update category metrics
            metrics.threshold_status = status
            
            # Create threshold result
            analysis.threshold_results[category] = ThresholdResult(
                metric_name=category,
                actual_value=actual,
                target_value=target,
                status=status,
                delta=delta,
            )
            
            total_count += 1
        
        analysis.thresholds_met_count = met_count
        analysis.thresholds_total_count = total_count
        analysis.all_thresholds_met = (met_count == total_count)
    
    def _collect_failed_details(
        self, 
        results: List[Any], 
        analysis: AnalysisResult
    ) -> None:
        """Collect detailed information about failed tests."""
        for result in results:
            status = result.status.value if hasattr(result.status, 'value') else str(result.status)
            
            if status == "failed":
                analysis.failed_test_details.append(FailedTestDetail(
                    phrase_id=result.phrase_id,
                    category=result.category,
                    subcategory=result.subcategory,
                    message=result.message,
                    expected_priorities=result.expected_priorities,
                    actual_severity=result.actual_severity,
                    crisis_score=result.crisis_score,
                    confidence=result.confidence,
                    failure_reason=result.failure_reason,
                    response_time_ms=result.response_time_ms,
                ))
    
    def get_threshold(self, category: str) -> float:
        """
        Get the accuracy threshold for a category.
        
        Args:
            category: Category name
        
        Returns:
            Target accuracy percentage
        """
        threshold_key = CATEGORY_THRESHOLD_MAP.get(
            category, "specialty_target_accuracy"
        )
        return self._thresholds.get(threshold_key, 75.0)
    
    def get_all_thresholds(self) -> Dict[str, float]:
        """Get all configured thresholds."""
        return self._thresholds.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get analyzer status information."""
        return {
            "version": __version__,
            "thresholds": self._thresholds,
            "crisis_priorities": list(CRISIS_PRIORITIES),
            "non_crisis_priorities": list(NON_CRISIS_PRIORITIES),
        }


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================

def create_result_analyzer_manager(
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
) -> ResultAnalyzerManager:
    """
    Factory function for ResultAnalyzerManager (Clean Architecture v5.2.1 Pattern).
    
    This is the ONLY way to create a ResultAnalyzerManager instance.
    Direct instantiation should be avoided in production code.
    
    Args:
        config_manager: Optional ConfigManager for threshold configuration
        logging_manager: Optional LoggingConfigManager for custom logging
    
    Returns:
        Configured ResultAnalyzerManager instance
    
    Example:
        >>> analyzer = create_result_analyzer_manager(config_manager=config)
        >>> analysis = analyzer.analyze(test_run_summary)
    """
    logger.debug("🏭 Creating ResultAnalyzerManager")
    
    return ResultAnalyzerManager(
        config_manager=config_manager,
        logging_manager=logging_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
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
]
