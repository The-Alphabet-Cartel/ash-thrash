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
Test Runner Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.3-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 2 - Test Execution Engine
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Orchestrate test execution across all phrases
- Integrate with NLPClientManager for API calls
- Integrate with PhraseLoaderManager for test data
- Integrate with validators for classification and response validation
- Track progress and provide real-time status updates
- Capture timing for performance analysis
- Handle errors gracefully (continue on failures)
- Support category filtering and single phrase testing

EXECUTION FLOW:
    1. Load phrases from PhraseLoaderManager
    2. Filter by category (if specified)
    3. For each phrase:
       a. Call NLPClientManager.analyze()
       b. Validate response with ResponseValidator
       c. Validate classification with ClassificationValidator
       d. Record result with timing
       e. Update progress callback
    4. Generate TestRunSummary

USAGE:
    from src.managers.test_runner_manager import create_test_runner_manager
    
    runner = create_test_runner_manager(
        config_manager=config,
        nlp_client=nlp_client,
        phrase_loader=phrase_loader,
        classification_validator=class_validator,
        response_validator=resp_validator,
        logging_manager=logging_mgr,
    )
    
    # Run all tests
    summary = await runner.run_all_tests()
    
    # Run tests for specific category
    summary = await runner.run_all_tests(categories=["critical_high_priority"])
    
    # Run with progress callback
    async def on_progress(current, total, result):
        print(f"Progress: {current}/{total}")
    
    summary = await runner.run_all_tests(progress_callback=on_progress)
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# Module version
__version__ = "v5.0-2-2.3-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default delay between tests (milliseconds)
DEFAULT_TEST_DELAY_MS = 100

# Maximum concurrent tests (for future parallel execution)
MAX_CONCURRENT_TESTS = 1  # Sequential for now


# =============================================================================
# Enums
# =============================================================================

class TestStatus(str, Enum):
    """Status of an individual test."""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class ErrorType(str, Enum):
    """Types of errors that can occur during testing."""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    INVALID_RESPONSE = "invalid_response"
    CLASSIFICATION_FAIL = "classification_fail"
    API_ERROR = "api_error"
    UNKNOWN = "unknown"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class TestResult:
    """
    Result of a single test execution.
    
    Attributes:
        phrase_id: Unique identifier for the test
        category: Category of the test phrase
        subcategory: Subcategory of the test phrase
        message: The message text that was tested
        expected_priorities: List of acceptable priorities
        actual_severity: Severity returned by Ash-NLP
        crisis_score: Crisis score from Ash-NLP
        confidence: Confidence score from Ash-NLP
        status: Test status (passed, failed, error, skipped)
        failure_reason: Explanation if test failed
        error_type: Type of error if status is ERROR
        response_time_ms: API response time in milliseconds
        full_response: Complete Ash-NLP response (for debugging)
        validation_details: Detailed validation results
        timestamp: When the test was executed
    """
    phrase_id: str
    category: str
    subcategory: str
    message: str
    expected_priorities: List[str]
    actual_severity: Optional[str]
    crisis_score: Optional[float]
    confidence: Optional[float]
    status: TestStatus
    failure_reason: Optional[str] = None
    error_type: Optional[ErrorType] = None
    response_time_ms: float = 0.0
    full_response: Optional[Dict[str, Any]] = None
    validation_details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == TestStatus.PASSED
    
    @property
    def failed(self) -> bool:
        """Check if test failed (classification mismatch)."""
        return self.status == TestStatus.FAILED
    
    @property
    def errored(self) -> bool:
        """Check if test had an error (API/connection issues)."""
        return self.status == TestStatus.ERROR
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phrase_id": self.phrase_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "message": self.message,
            "expected_priorities": self.expected_priorities,
            "actual_severity": self.actual_severity,
            "crisis_score": self.crisis_score,
            "confidence": self.confidence,
            "status": self.status.value,
            "failure_reason": self.failure_reason,
            "error_type": self.error_type.value if self.error_type else None,
            "response_time_ms": self.response_time_ms,
            "validation_details": self.validation_details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TestRunSummary:
    """
    Summary of a complete test run.
    
    Attributes:
        run_id: Unique identifier for this test run
        start_time: When the test run started
        end_time: When the test run completed
        total_tests: Total number of tests executed
        passed_tests: Number of tests that passed
        failed_tests: Number of tests that failed
        error_tests: Number of tests with errors
        skipped_tests: Number of tests skipped
        overall_accuracy: Percentage of passed tests (excluding errors)
        accuracy_by_category: Accuracy breakdown by category
        accuracy_by_subcategory: Accuracy breakdown by subcategory
        average_response_time_ms: Mean API response time
        p95_response_time_ms: 95th percentile response time
        results: List of individual test results
        categories_tested: List of categories included in run
        nlp_server_info: Information about Ash-NLP server
    """
    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    skipped_tests: int = 0
    overall_accuracy: float = 0.0
    accuracy_by_category: Dict[str, float] = field(default_factory=dict)
    accuracy_by_subcategory: Dict[str, float] = field(default_factory=dict)
    average_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    results: List[TestResult] = field(default_factory=list)
    categories_tested: List[str] = field(default_factory=list)
    nlp_server_info: Optional[Dict[str, Any]] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate total run duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def tests_per_second(self) -> float:
        """Calculate throughput."""
        duration = self.duration_seconds
        return self.total_tests / duration if duration > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "error_tests": self.error_tests,
            "skipped_tests": self.skipped_tests,
            "overall_accuracy": self.overall_accuracy,
            "accuracy_by_category": self.accuracy_by_category,
            "accuracy_by_subcategory": self.accuracy_by_subcategory,
            "average_response_time_ms": self.average_response_time_ms,
            "p95_response_time_ms": self.p95_response_time_ms,
            "categories_tested": self.categories_tested,
            "nlp_server_info": self.nlp_server_info,
            "tests_per_second": self.tests_per_second,
        }


# Type alias for progress callback
ProgressCallback = Callable[[int, int, TestResult], None]


# =============================================================================
# Test Runner Manager
# =============================================================================

class TestRunnerManager:
    """
    Orchestrates test execution against Ash-NLP.
    
    This manager coordinates the entire test execution pipeline:
    1. Loading test phrases
    2. Making API calls to Ash-NLP
    3. Validating responses and classifications
    4. Collecting and organizing results
    5. Tracking progress and timing
    
    Attributes:
        config_manager: Configuration manager
        nlp_client: NLPClientManager for API calls
        phrase_loader: PhraseLoaderManager for test data
        classification_validator: ClassificationValidator for priority matching
        response_validator: ResponseValidator for API response validation
        test_delay_ms: Delay between tests (milliseconds)
    
    Example:
        >>> runner = create_test_runner_manager(
        ...     config_manager=config,
        ...     nlp_client=nlp_client,
        ...     phrase_loader=phrase_loader,
        ...     classification_validator=class_validator,
        ...     response_validator=resp_validator,
        ... )
        >>> 
        >>> # Run all tests
        >>> summary = await runner.run_all_tests()
        >>> print(f"Accuracy: {summary.overall_accuracy:.1f}%")
    """
    
    def __init__(
        self,
        nlp_client: Any,  # NLPClientManager
        phrase_loader: Any,  # PhraseLoaderManager
        classification_validator: Any,  # ClassificationValidator
        response_validator: Any,  # ResponseValidator
        config_manager: Optional[Any] = None,
        logging_manager: Optional[Any] = None,
        test_delay_ms: int = DEFAULT_TEST_DELAY_MS,
    ):
        """
        Initialize the TestRunnerManager.
        
        Args:
            nlp_client: NLPClientManager instance
            phrase_loader: PhraseLoaderManager instance
            classification_validator: ClassificationValidator instance
            response_validator: ResponseValidator instance
            config_manager: Optional ConfigManager
            logging_manager: Optional LoggingConfigManager
            test_delay_ms: Delay between tests in milliseconds
        
        Note:
            Use create_test_runner_manager() factory function instead.
        """
        self._config = config_manager
        self._nlp_client = nlp_client
        self._phrase_loader = phrase_loader
        self._classification_validator = classification_validator
        self._response_validator = response_validator
        self._test_delay_ms = test_delay_ms
        
        # Set up logger
        if logging_manager:
            self._logger = logging_manager.get_logger("test_runner")
        else:
            self._logger = logger
        
        # Statistics
        self._current_run: Optional[TestRunSummary] = None
        
        self._logger.info(
            f"✅ TestRunnerManager {__version__} initialized "
            f"(delay: {test_delay_ms}ms)"
        )
    
    async def run_all_tests(
        self,
        categories: Optional[List[str]] = None,
        progress_callback: Optional[ProgressCallback] = None,
        include_explanation: bool = False,
    ) -> TestRunSummary:
        """
        Run all tests, optionally filtered by category.
        
        Args:
            categories: List of category names to test (None = all)
            progress_callback: Function called after each test with (current, total, result)
            include_explanation: Whether to request explanations from Ash-NLP
        
        Returns:
            TestRunSummary with complete results
        
        Example:
            >>> # Run all tests
            >>> summary = await runner.run_all_tests()
            >>> 
            >>> # Run specific categories
            >>> summary = await runner.run_all_tests(
            ...     categories=["critical_high_priority", "medium_priority"]
            ... )
            >>> 
            >>> # Run with progress tracking
            >>> async def on_progress(current, total, result):
            ...     print(f"[{current}/{total}] {result.status.value}")
            >>> summary = await runner.run_all_tests(progress_callback=on_progress)
        """
        # Initialize run summary
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        summary = TestRunSummary(
            run_id=run_id,
            start_time=datetime.now(),
        )
        self._current_run = summary
        
        self._logger.info(f"🚀 Starting test run: {run_id}")
        
        # Get phrases to test
        if categories:
            phrases = []
            for cat in categories:
                phrases.extend(self._phrase_loader.get_phrases_by_category(cat))
            summary.categories_tested = categories
        else:
            phrases = self._phrase_loader.get_all_phrases()
            summary.categories_tested = self._phrase_loader.get_all_categories()
        
        summary.total_tests = len(phrases)
        
        if summary.total_tests == 0:
            self._logger.warning("⚠️ No phrases to test")
            summary.end_time = datetime.now()
            return summary
        
        self._logger.info(
            f"📋 Testing {summary.total_tests} phrases across "
            f"{len(summary.categories_tested)} categories"
        )
        
        # Check NLP server availability
        try:
            if await self._nlp_client.is_available():
                server_status = await self._nlp_client.get_status()
                summary.nlp_server_info = server_status
                self._logger.info("✅ Ash-NLP server is available")
            else:
                self._logger.error("❌ Ash-NLP server is not available")
                summary.end_time = datetime.now()
                return summary
        except Exception as e:
            self._logger.error(f"❌ Failed to check Ash-NLP server: {e}")
            summary.end_time = datetime.now()
            return summary
        
        # Run tests
        response_times: List[float] = []
        
        for idx, phrase in enumerate(phrases, 1):
            # Generate unique phrase ID
            phrase_id = f"{phrase.category}_{phrase.subcategory}_{idx}"
            
            # Execute single test
            result = await self._run_single_test(
                phrase=phrase,
                phrase_id=phrase_id,
                include_explanation=include_explanation,
            )
            
            # Record result
            summary.results.append(result)
            
            # Update counters
            if result.status == TestStatus.PASSED:
                summary.passed_tests += 1
            elif result.status == TestStatus.FAILED:
                summary.failed_tests += 1
            elif result.status == TestStatus.ERROR:
                summary.error_tests += 1
            else:
                summary.skipped_tests += 1
            
            # Track response time (only for successful API calls)
            if result.response_time_ms > 0:
                response_times.append(result.response_time_ms)
            
            # Call progress callback
            if progress_callback:
                try:
                    # Support both sync and async callbacks
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(idx, summary.total_tests, result)
                    else:
                        progress_callback(idx, summary.total_tests, result)
                except Exception as e:
                    self._logger.warning(f"Progress callback error: {e}")
            
            # Delay between tests
            if self._test_delay_ms > 0 and idx < summary.total_tests:
                await asyncio.sleep(self._test_delay_ms / 1000)
        
        # Finalize summary
        summary.end_time = datetime.now()
        
        # Calculate accuracy metrics
        self._calculate_accuracy_metrics(summary)
        
        # Calculate response time metrics
        if response_times:
            summary.average_response_time_ms = sum(response_times) / len(response_times)
            sorted_times = sorted(response_times)
            p95_idx = int(len(sorted_times) * 0.95)
            summary.p95_response_time_ms = sorted_times[min(p95_idx, len(sorted_times) - 1)]
        
        self._logger.info(
            f"🏁 Test run complete: {summary.passed_tests}/{summary.total_tests} passed "
            f"({summary.overall_accuracy:.1f}% accuracy) in {summary.duration_seconds:.1f}s"
        )
        
        return summary
    
    async def _run_single_test(
        self,
        phrase: Any,  # TestPhrase
        phrase_id: str,
        include_explanation: bool = False,
    ) -> TestResult:
        """
        Execute a single test phrase.
        
        Args:
            phrase: TestPhrase object to test
            phrase_id: Unique identifier for this test
            include_explanation: Whether to request explanation
        
        Returns:
            TestResult with execution details
        """
        start_time = time.perf_counter()
        
        # Base result (will be updated)
        result = TestResult(
            phrase_id=phrase_id,
            category=phrase.category,
            subcategory=phrase.subcategory,
            message=phrase.message,
            expected_priorities=phrase.expected_priorities,
            actual_severity=None,
            crisis_score=None,
            confidence=None,
            status=TestStatus.ERROR,
            timestamp=datetime.now(),
        )
        
        try:
            # Call Ash-NLP API
            response = await self._nlp_client.analyze(
                message=phrase.message,
                include_explanation=include_explanation,
            )
            
            # Calculate response time
            result.response_time_ms = (time.perf_counter() - start_time) * 1000
            
            # Store raw response
            result.full_response = response.raw_response
            result.actual_severity = response.severity
            result.crisis_score = response.crisis_score
            result.confidence = response.confidence
            
            # Validate response structure
            resp_validation = self._response_validator.validate(response.raw_response)
            if not resp_validation.is_valid:
                result.status = TestStatus.ERROR
                result.error_type = ErrorType.INVALID_RESPONSE
                result.failure_reason = f"Invalid response: {resp_validation.errors[0]}"
                result.validation_details = resp_validation.to_dict()
                return result
            
            # Validate classification
            class_validation = self._classification_validator.validate(
                actual_severity=response.severity,
                **phrase.get_validation_params()
            )
            
            result.validation_details = class_validation.to_dict()
            
            if class_validation.passed:
                result.status = TestStatus.PASSED
                result.failure_reason = None
            else:
                result.status = TestStatus.FAILED
                result.error_type = ErrorType.CLASSIFICATION_FAIL
                result.failure_reason = class_validation.failure_reason
            
        except asyncio.TimeoutError:
            result.response_time_ms = (time.perf_counter() - start_time) * 1000
            result.status = TestStatus.ERROR
            result.error_type = ErrorType.TIMEOUT
            result.failure_reason = "API request timed out"
            self._logger.warning(f"⏱️ Timeout for phrase: {phrase.message[:50]}...")
            
        except ConnectionError as e:
            result.response_time_ms = (time.perf_counter() - start_time) * 1000
            result.status = TestStatus.ERROR
            result.error_type = ErrorType.CONNECTION_ERROR
            result.failure_reason = f"Connection error: {str(e)}"
            self._logger.warning(f"🔌 Connection error: {e}")
            
        except Exception as e:
            result.response_time_ms = (time.perf_counter() - start_time) * 1000
            result.status = TestStatus.ERROR
            result.error_type = ErrorType.UNKNOWN
            result.failure_reason = f"Unexpected error: {str(e)}"
            self._logger.error(f"❌ Unexpected error testing phrase: {e}")
        
        return result
    
    def _calculate_accuracy_metrics(self, summary: TestRunSummary) -> None:
        """Calculate accuracy metrics for the summary."""
        # Overall accuracy (excluding errors)
        testable = summary.passed_tests + summary.failed_tests
        if testable > 0:
            summary.overall_accuracy = (summary.passed_tests / testable) * 100
        
        # Accuracy by category
        category_stats: Dict[str, Dict[str, int]] = {}
        subcategory_stats: Dict[str, Dict[str, int]] = {}
        
        for result in summary.results:
            # Category stats
            if result.category not in category_stats:
                category_stats[result.category] = {"passed": 0, "total": 0}
            
            if result.status in (TestStatus.PASSED, TestStatus.FAILED):
                category_stats[result.category]["total"] += 1
                if result.status == TestStatus.PASSED:
                    category_stats[result.category]["passed"] += 1
            
            # Subcategory stats
            subcat_key = f"{result.category}.{result.subcategory}"
            if subcat_key not in subcategory_stats:
                subcategory_stats[subcat_key] = {"passed": 0, "total": 0}
            
            if result.status in (TestStatus.PASSED, TestStatus.FAILED):
                subcategory_stats[subcat_key]["total"] += 1
                if result.status == TestStatus.PASSED:
                    subcategory_stats[subcat_key]["passed"] += 1
        
        # Calculate percentages
        for cat, stats in category_stats.items():
            if stats["total"] > 0:
                summary.accuracy_by_category[cat] = (
                    stats["passed"] / stats["total"]
                ) * 100
        
        for subcat, stats in subcategory_stats.items():
            if stats["total"] > 0:
                summary.accuracy_by_subcategory[subcat] = (
                    stats["passed"] / stats["total"]
                ) * 100
    
    async def run_single_phrase(
        self,
        message: str,
        expected_priorities: List[str],
        allow_escalation: bool = True,
        allow_deescalation: bool = False,
        include_explanation: bool = True,
    ) -> TestResult:
        """
        Run a single ad-hoc phrase test.
        
        Useful for quick testing without loading phrase files.
        
        Args:
            message: Message text to test
            expected_priorities: List of acceptable priorities
            allow_escalation: Whether higher severity is acceptable
            allow_deescalation: Whether lower severity is acceptable
            include_explanation: Whether to request explanation
        
        Returns:
            TestResult with execution details
        
        Example:
            >>> result = await runner.run_single_phrase(
            ...     message="I'm feeling really down today",
            ...     expected_priorities=["low", "medium"],
            ... )
            >>> print(f"Result: {result.status.value}")
        """
        # Create a pseudo-phrase object
        class AdHocPhrase:
            def __init__(self):
                self.message = message
                self.expected_priorities = expected_priorities
                self.allow_escalation = allow_escalation
                self.allow_deescalation = allow_deescalation
                self.category = "adhoc"
                self.subcategory = "manual"
            
            def get_validation_params(self):
                return {
                    "expected_priorities": self.expected_priorities,
                    "allow_escalation": self.allow_escalation,
                    "allow_deescalation": self.allow_deescalation,
                }
        
        phrase = AdHocPhrase()
        phrase_id = f"adhoc_{uuid.uuid4().hex[:8]}"
        
        return await self._run_single_test(
            phrase=phrase,
            phrase_id=phrase_id,
            include_explanation=include_explanation,
        )
    
    def get_current_run(self) -> Optional[TestRunSummary]:
        """Get the current/most recent test run summary."""
        return self._current_run
    
    def get_status(self) -> Dict[str, Any]:
        """Get runner status information."""
        return {
            "version": __version__,
            "test_delay_ms": self._test_delay_ms,
            "phrases_loaded": len(self._phrase_loader),
            "categories_available": self._phrase_loader.get_all_categories(),
            "has_current_run": self._current_run is not None,
        }


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================

def create_test_runner_manager(
    nlp_client: Any,
    phrase_loader: Any,
    classification_validator: Any,
    response_validator: Any,
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
    test_delay_ms: Optional[int] = None,
) -> TestRunnerManager:
    """
    Factory function for TestRunnerManager (Clean Architecture v5.2.1 Pattern).
    
    This is the ONLY way to create a TestRunnerManager instance.
    Direct instantiation should be avoided in production code.
    
    Args:
        nlp_client: NLPClientManager instance for API calls
        phrase_loader: PhraseLoaderManager instance for test data
        classification_validator: ClassificationValidator instance
        response_validator: ResponseValidator instance
        config_manager: Optional ConfigManager for settings
        logging_manager: Optional LoggingConfigManager for custom logger
        test_delay_ms: Override delay between tests (milliseconds)
    
    Returns:
        Configured TestRunnerManager instance
    
    Example:
        >>> # Create all dependencies first
        >>> config = create_config_manager()
        >>> logging_mgr = create_logging_config_manager(config_manager=config)
        >>> nlp_client = create_nlp_client_manager(config_manager=config)
        >>> phrase_loader = create_phrase_loader_manager(config_manager=config)
        >>> class_validator = create_classification_validator()
        >>> resp_validator = create_response_validator()
        >>> 
        >>> # Create the runner
        >>> runner = create_test_runner_manager(
        ...     nlp_client=nlp_client,
        ...     phrase_loader=phrase_loader,
        ...     classification_validator=class_validator,
        ...     response_validator=resp_validator,
        ...     config_manager=config,
        ...     logging_manager=logging_mgr,
        ... )
    """
    # Resolve test delay
    if test_delay_ms is None:
        if config_manager:
            test_delay_ms = config_manager.get("test_execution", "delay_between_tests_ms")
        if test_delay_ms is None:
            test_delay_ms = DEFAULT_TEST_DELAY_MS
    
    logger.debug(
        f"🏭 Creating TestRunnerManager (delay: {test_delay_ms}ms)"
    )
    
    return TestRunnerManager(
        nlp_client=nlp_client,
        phrase_loader=phrase_loader,
        classification_validator=classification_validator,
        response_validator=response_validator,
        config_manager=config_manager,
        logging_manager=logging_manager,
        test_delay_ms=test_delay_ms,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "TestRunnerManager",
    "create_test_runner_manager",
    "TestResult",
    "TestRunSummary",
    "TestStatus",
    "ErrorType",
    "ProgressCallback",
]
