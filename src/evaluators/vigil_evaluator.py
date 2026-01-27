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
Vigil Evaluator - Model Evaluation via Ash-Vigil /evaluate Endpoint
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.2-1
LAST MODIFIED: 2026-01-26
PHASE: Phase 2 - Ash-Thrash Evaluation Infrastructure
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Connect to Ash-Vigil's /evaluate endpoint for batch phrase evaluation
- Load test phrases from Ash-Thrash specialty phrase files
- Calculate per-category accuracy metrics
- Support configurable model selection via environment variable
- Track timing metrics for performance comparison

DESIGN NOTE:
Ash-Vigil is an AMPLIFIER for specialty edge cases, not a standalone classifier.
This evaluator tests Ash-Vigil's ability to detect risk patterns that generic
models miss - specifically LGBTQIA+ minority stress, gaming false positives,
and planning signals.

ENDPOINTS USED:
- GET  /health    - Verify Ash-Vigil availability
- POST /evaluate  - Bulk phrase evaluation

USAGE:
    from src.evaluators import create_vigil_evaluator
    
    evaluator = create_vigil_evaluator(config_manager=config)
    
    # Evaluate current model against specialty phrases
    result = await evaluator.evaluate_model()
    
    # Evaluate specific categories only
    result = await evaluator.evaluate_model(
        categories=["specialty_lgbtqia", "specialty_gaming"]
    )
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

# Module version
__version__ = "v5.0-2-2.2-1"

# Initialize logger (will be replaced by LoggingConfigManager logger)
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default Ash-Vigil configuration
DEFAULT_VIGIL_HOST = "10.20.30.14"
DEFAULT_VIGIL_PORT = 30882
DEFAULT_TIMEOUT = 120  # Seconds - batch evaluation can take time
DEFAULT_RETRY_ATTEMPTS = 2
DEFAULT_RETRY_DELAY_MS = 2000
DEFAULT_BATCH_SIZE = 50

# API endpoints
ENDPOINT_HEALTH = "/health"
ENDPOINT_EVALUATE = "/evaluate"

# Phrase file paths (relative to Ash-Thrash src/config/phrases/)
SPECIALTY_PHRASE_FILES = {
    "specialty_lgbtqia": "specialty/lgbtqia_specific.json",
    "specialty_gaming": "specialty/gaming_context.json",
    "specialty_slang": "specialty/cultural_slang.json",
    "specialty_irony": "specialty/irony_sarcasm.json",
    "specialty_multilang": "specialty/language_hints.json",
    "specialty_quotes": "specialty/songs_quotes.json",
}

# Risk level mapping from Ash-Vigil labels
RISK_LEVEL_MAP = {
    "high_risk": ["high", "critical"],      # Suicidal
    "moderate_risk": ["medium", "high"],    # Anxiety, Depression
    "safe": ["none", "low"],                # Normal
}

# Expected priority mapping for evaluation
EXPECTED_PRIORITY_TO_VIGIL = {
    "critical": "high_risk",
    "high": "high_risk",
    "medium": "moderate_risk",
    "low": "safe",
    "none": "safe",
}


# =============================================================================
# Enums
# =============================================================================

class EvaluationStatus(str, Enum):
    """Status of an evaluation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some phrases failed


class PassStatus(str, Enum):
    """Pass/fail status for individual phrase evaluation."""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    ESCALATED = "escalated"  # Higher risk than expected (acceptable)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class TestPhrase:
    """A single test phrase for evaluation."""
    phrase_id: str
    message: str
    category: str
    subcategory: str
    expected_priorities: List[str]
    description: str = ""
    
    @property
    def expected_risk_levels(self) -> List[str]:
        """Convert expected priorities to Vigil risk levels."""
        risk_levels = set()
        for priority in self.expected_priorities:
            if priority in EXPECTED_PRIORITY_TO_VIGIL:
                risk_levels.add(EXPECTED_PRIORITY_TO_VIGIL[priority])
        return list(risk_levels)


@dataclass
class PhraseResult:
    """Result of evaluating a single phrase."""
    phrase_id: str
    message: str
    category: str
    subcategory: str
    expected_priorities: List[str]
    expected_risk_levels: List[str]
    
    # Vigil response
    vigil_label: str = ""
    vigil_risk_level: str = ""
    vigil_confidence: float = 0.0
    vigil_scores: Dict[str, float] = field(default_factory=dict)
    
    # Evaluation result
    status: PassStatus = PassStatus.ERROR
    inference_time_ms: float = 0.0
    error_message: str = ""
    
    @property
    def passed(self) -> bool:
        """Check if phrase evaluation passed."""
        return self.status in (PassStatus.PASS, PassStatus.ESCALATED)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phrase_id": self.phrase_id,
            "message": self.message[:100] + "..." if len(self.message) > 100 else self.message,
            "category": self.category,
            "subcategory": self.subcategory,
            "expected_priorities": self.expected_priorities,
            "expected_risk_levels": self.expected_risk_levels,
            "vigil_label": self.vigil_label,
            "vigil_risk_level": self.vigil_risk_level,
            "vigil_confidence": round(self.vigil_confidence, 4),
            "vigil_scores": {k: round(v, 4) for k, v in self.vigil_scores.items()},
            "status": self.status.value,
            "passed": self.passed,
            "inference_time_ms": round(self.inference_time_ms, 2),
            "error_message": self.error_message,
        }


@dataclass
class CategoryAccuracy:
    """Accuracy metrics for a single category."""
    category: str
    total_phrases: int
    passed: int
    failed: int
    errors: int
    escalated: int
    accuracy: float
    
    # Per-subcategory breakdown
    subcategory_breakdown: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # Timing
    total_inference_time_ms: float = 0.0
    average_inference_time_ms: float = 0.0
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate including escalations."""
        if self.total_phrases == 0:
            return 0.0
        return ((self.passed + self.escalated) / self.total_phrases) * 100
    
    @property
    def strict_accuracy(self) -> float:
        """Calculate strict accuracy (passes only, no escalations)."""
        if self.total_phrases == 0:
            return 0.0
        return (self.passed / self.total_phrases) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category,
            "total_phrases": self.total_phrases,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "escalated": self.escalated,
            "accuracy": round(self.accuracy, 2),
            "pass_rate": round(self.pass_rate, 2),
            "strict_accuracy": round(self.strict_accuracy, 2),
            "subcategory_breakdown": self.subcategory_breakdown,
            "total_inference_time_ms": round(self.total_inference_time_ms, 2),
            "average_inference_time_ms": round(self.average_inference_time_ms, 2),
        }


@dataclass
class EvaluationResult:
    """Complete result of a model evaluation."""
    # Identification
    evaluation_id: str
    model_name: str
    timestamp: datetime
    
    # Overall metrics
    total_phrases: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_errors: int = 0
    total_escalated: int = 0
    overall_accuracy: float = 0.0
    overall_pass_rate: float = 0.0
    
    # Per-category metrics
    category_accuracies: Dict[str, CategoryAccuracy] = field(default_factory=dict)
    
    # All phrase results
    phrase_results: List[PhraseResult] = field(default_factory=list)
    
    # Timing
    total_evaluation_time_seconds: float = 0.0
    total_inference_time_ms: float = 0.0
    average_inference_time_ms: float = 0.0
    
    # Status
    status: EvaluationStatus = EvaluationStatus.PENDING
    status_message: str = ""
    
    # Vigil info
    vigil_host: str = ""
    vigil_version: str = ""
    
    @property
    def failed_phrase_results(self) -> List[PhraseResult]:
        """Get only failed phrase results."""
        return [r for r in self.phrase_results if r.status == PassStatus.FAIL]
    
    @property
    def categories_evaluated(self) -> List[str]:
        """Get list of categories that were evaluated."""
        return list(self.category_accuracies.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "evaluation_id": self.evaluation_id,
            "model_name": self.model_name,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "status_message": self.status_message,
            "total_phrases": self.total_phrases,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "total_errors": self.total_errors,
            "total_escalated": self.total_escalated,
            "overall_accuracy": round(self.overall_accuracy, 2),
            "overall_pass_rate": round(self.overall_pass_rate, 2),
            "total_evaluation_time_seconds": round(self.total_evaluation_time_seconds, 2),
            "total_inference_time_ms": round(self.total_inference_time_ms, 2),
            "average_inference_time_ms": round(self.average_inference_time_ms, 2),
            "vigil_host": self.vigil_host,
            "vigil_version": self.vigil_version,
            "category_accuracies": {
                k: v.to_dict() for k, v in self.category_accuracies.items()
            },
            "categories_evaluated": self.categories_evaluated,
            "failed_count": len(self.failed_phrase_results),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationResult":
        """Create EvaluationResult from dictionary."""
        result = cls(
            evaluation_id=data.get("evaluation_id", ""),
            model_name=data.get("model_name", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
        )
        result.status = EvaluationStatus(data.get("status", "pending"))
        result.status_message = data.get("status_message", "")
        result.total_phrases = data.get("total_phrases", 0)
        result.total_passed = data.get("total_passed", 0)
        result.total_failed = data.get("total_failed", 0)
        result.total_errors = data.get("total_errors", 0)
        result.total_escalated = data.get("total_escalated", 0)
        result.overall_accuracy = data.get("overall_accuracy", 0.0)
        result.overall_pass_rate = data.get("overall_pass_rate", 0.0)
        result.total_evaluation_time_seconds = data.get("total_evaluation_time_seconds", 0.0)
        result.total_inference_time_ms = data.get("total_inference_time_ms", 0.0)
        result.average_inference_time_ms = data.get("average_inference_time_ms", 0.0)
        result.vigil_host = data.get("vigil_host", "")
        result.vigil_version = data.get("vigil_version", "")
        return result


# =============================================================================
# Exceptions
# =============================================================================

class VigilEvaluatorError(Exception):
    """Base exception for Vigil evaluator errors."""
    pass


class VigilConnectionError(VigilEvaluatorError):
    """Raised when connection to Ash-Vigil fails."""
    pass


class VigilTimeoutError(VigilEvaluatorError):
    """Raised when request to Ash-Vigil times out."""
    pass


class VigilResponseError(VigilEvaluatorError):
    """Raised when Ash-Vigil returns an error response."""
    def __init__(self, message: str, status_code: int, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


# =============================================================================
# Vigil Evaluator Manager
# =============================================================================

class VigilEvaluator:
    """
    Evaluates mental health risk detection models via Ash-Vigil's /evaluate endpoint.
    
    This evaluator is specifically designed to test Ash-Vigil's specialty detection
    capabilities - the edge cases that generic models miss:
    - LGBTQIA+ minority stress patterns
    - Gaming context false positive reduction
    - Planning signals and passive ideation
    - Cultural slang and code-switching
    
    Attributes:
        vigil_host: Ash-Vigil server hostname
        vigil_port: Ash-Vigil server port
        timeout: Request timeout in seconds
        batch_size: Number of phrases per batch request
    
    Example:
        >>> evaluator = create_vigil_evaluator(config_manager=config)
        >>> 
        >>> # Check Vigil availability
        >>> if await evaluator.is_available():
        >>>     # Run full evaluation
        >>>     result = await evaluator.evaluate_model()
        >>>     print(f"Overall accuracy: {result.overall_accuracy}%")
    """
    
    def __init__(
        self,
        vigil_host: str = DEFAULT_VIGIL_HOST,
        vigil_port: int = DEFAULT_VIGIL_PORT,
        timeout: int = DEFAULT_TIMEOUT,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        retry_delay_ms: int = DEFAULT_RETRY_DELAY_MS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        phrases_base_path: Optional[str] = None,
        logger_instance: Optional[logging.Logger] = None,
    ):
        """
        Initialize the VigilEvaluator.
        
        Args:
            vigil_host: Ash-Vigil server hostname or IP
            vigil_port: Ash-Vigil server port
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay_ms: Initial delay between retries
            batch_size: Number of phrases per batch request
            phrases_base_path: Base path to phrase files (default: auto-detect)
            logger_instance: Optional custom logger
        
        Note:
            Use create_vigil_evaluator() factory function instead.
        """
        self.vigil_host = vigil_host
        self.vigil_port = vigil_port
        self.base_url = f"http://{vigil_host}:{vigil_port}"
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay_ms = retry_delay_ms
        self.batch_size = batch_size
        
        # Resolve phrases base path
        self._phrases_base_path = self._resolve_phrases_path(phrases_base_path)
        
        # Use provided logger or module logger
        self._logger = logger_instance or logger
        
        # HTTP client (created lazily for async context)
        self._client: Optional[httpx.AsyncClient] = None
        
        # Cache for loaded phrases
        self._phrase_cache: Dict[str, List[TestPhrase]] = {}
        
        self._logger.debug(
            f"VigilEvaluator {__version__} initialized "
            f"(base_url: {self.base_url}, timeout: {timeout}s, batch_size: {batch_size})"
        )
    
    def _resolve_phrases_path(self, override: Optional[str]) -> Path:
        """Resolve the base path for phrase files."""
        if override:
            return Path(override)
        
        # Try common locations
        candidates = [
            Path("/app/src/config/phrases"),
            Path("src/config/phrases"),
            Path(__file__).parent.parent / "config" / "phrases",
        ]
        
        for path in candidates:
            if path.exists():
                return path
        
        # Default to first candidate
        return candidates[0]
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"Ash-Thrash-Evaluator/{__version__}",
                },
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            self._logger.debug("HTTP client connection closed")
    
    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request with retry logic."""
        client = await self._get_client()
        last_exception: Optional[Exception] = None
        
        for attempt in range(self.retry_attempts + 1):
            try:
                start_time = time.perf_counter()
                
                self._logger.debug(
                    f"📤 {method} {endpoint} (attempt {attempt + 1}/{self.retry_attempts + 1})"
                )
                
                if method.upper() == "GET":
                    response = await client.get(endpoint)
                else:
                    response = await client.post(endpoint, json=json_data)
                
                latency_ms = (time.perf_counter() - start_time) * 1000
                
                if response.status_code >= 400:
                    error_body = response.text
                    self._logger.warning(
                        f"⚠️ {method} {endpoint} returned {response.status_code}: {error_body[:200]}"
                    )
                    raise VigilResponseError(
                        f"Ash-Vigil returned status {response.status_code}",
                        status_code=response.status_code,
                        response_body=error_body,
                    )
                
                data = response.json()
                self._logger.debug(f"📥 {method} {endpoint} completed in {latency_ms:.1f}ms")
                return data
                
            except httpx.ConnectError as e:
                last_exception = VigilConnectionError(
                    f"Failed to connect to Ash-Vigil at {self.base_url}: {e}"
                )
                self._logger.warning(f"🔌 Connection failed: {e}")
                
            except httpx.TimeoutException as e:
                last_exception = VigilTimeoutError(
                    f"Request to Ash-Vigil timed out after {self.timeout}s: {e}"
                )
                self._logger.warning(f"⏱️ Request timed out: {e}")
                
            except VigilResponseError:
                raise
                
            except Exception as e:
                last_exception = VigilEvaluatorError(f"Unexpected error: {e}")
                self._logger.warning(f"❌ Unexpected error: {e}")
            
            if attempt < self.retry_attempts:
                delay_ms = self.retry_delay_ms * (2 ** attempt)
                self._logger.info(
                    f"🔄 Retrying in {delay_ms}ms (attempt {attempt + 2}/{self.retry_attempts + 1})"
                )
                await asyncio.sleep(delay_ms / 1000)
        
        self._logger.error(
            f"❌ {method} {endpoint} failed after {self.retry_attempts + 1} attempts"
        )
        raise last_exception or VigilEvaluatorError("Request failed")
    
    # =========================================================================
    # Health & Status
    # =========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check Ash-Vigil server health.
        
        Returns:
            Health response dictionary
        
        Raises:
            VigilEvaluatorError: If health check fails
        """
        return await self._request_with_retry("GET", ENDPOINT_HEALTH)
    
    async def is_available(self) -> bool:
        """
        Check if Ash-Vigil server is available.
        
        Returns:
            True if server is healthy
        """
        try:
            health = await self.health_check()
            return health.get("status", "").lower() in ("ok", "healthy")
        except Exception:
            return False
    
    async def get_vigil_info(self) -> Tuple[str, str]:
        """
        Get Ash-Vigil version and model info.
        
        Returns:
            Tuple of (version, model_name)
        """
        try:
            health = await self.health_check()
            return (
                health.get("version", "unknown"),
                health.get("model", health.get("model_name", "unknown")),
            )
        except Exception:
            return ("unknown", "unknown")
    
    # =========================================================================
    # Phrase Loading
    # =========================================================================
    
    def _load_phrases_from_file(self, category: str, filepath: str) -> List[TestPhrase]:
        """Load test phrases from a JSON file."""
        full_path = self._phrases_base_path / filepath
        
        if not full_path.exists():
            self._logger.warning(f"⚠️ Phrase file not found: {full_path}")
            return []
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            phrases = []
            phrase_index = 0
            
            # Get expected priorities from category info
            category_info = data.get("category_info", {})
            category_defaults = data.get("category", {}).get("defaults", {})
            default_priorities = category_defaults.get("expected_priority", ["medium", "high"])
            
            # Parse subcategories
            subcategories = data.get("category", {}).get("subcategories", {})
            
            for subcategory_name, subcategory_phrases in subcategories.items():
                for phrase_data in subcategory_phrases:
                    phrase_index += 1
                    
                    # Get message
                    message = phrase_data.get("message", "")
                    if not message:
                        continue
                    
                    # Get expected priorities (per-phrase or category default)
                    expected = phrase_data.get("expected_priorities", default_priorities)
                    if isinstance(expected, str):
                        expected = [expected]
                    
                    phrases.append(TestPhrase(
                        phrase_id=f"{category}_{subcategory_name}_{phrase_index}",
                        message=message,
                        category=category,
                        subcategory=subcategory_name,
                        expected_priorities=expected,
                        description=phrase_data.get("description", ""),
                    ))
            
            self._logger.info(
                f"📂 Loaded {len(phrases)} phrases from {category} ({filepath})"
            )
            return phrases
            
        except Exception as e:
            self._logger.error(f"❌ Failed to load phrases from {filepath}: {e}")
            return []
    
    def load_phrases(
        self,
        categories: Optional[List[str]] = None,
    ) -> Dict[str, List[TestPhrase]]:
        """
        Load test phrases for evaluation.
        
        Args:
            categories: List of category names to load (default: all specialty)
        
        Returns:
            Dictionary mapping category names to phrase lists
        """
        # Default to all specialty categories
        if categories is None:
            categories = list(SPECIALTY_PHRASE_FILES.keys())
        
        result = {}
        
        for category in categories:
            # Check cache first
            if category in self._phrase_cache:
                result[category] = self._phrase_cache[category]
                continue
            
            # Load from file
            filepath = SPECIALTY_PHRASE_FILES.get(category)
            if not filepath:
                self._logger.warning(f"⚠️ Unknown category: {category}")
                continue
            
            phrases = self._load_phrases_from_file(category, filepath)
            if phrases:
                self._phrase_cache[category] = phrases
                result[category] = phrases
        
        return result
    
    # =========================================================================
    # Evaluation Logic
    # =========================================================================
    
    def _determine_pass_status(
        self,
        expected_risk_levels: List[str],
        actual_risk_level: str,
        allow_escalation: bool = True,
    ) -> PassStatus:
        """
        Determine if a phrase evaluation passed.
        
        Args:
            expected_risk_levels: Expected risk levels (from phrase)
            actual_risk_level: Actual risk level from Vigil
            allow_escalation: Whether escalation (higher risk) counts as pass
        
        Returns:
            PassStatus enum value
        """
        if not actual_risk_level:
            return PassStatus.ERROR
        
        # Direct match
        if actual_risk_level in expected_risk_levels:
            return PassStatus.PASS
        
        # Check for escalation (higher risk than expected)
        if allow_escalation:
            risk_order = ["safe", "moderate_risk", "high_risk"]
            
            try:
                actual_idx = risk_order.index(actual_risk_level)
                max_expected_idx = max(
                    risk_order.index(r) for r in expected_risk_levels
                    if r in risk_order
                )
                
                if actual_idx > max_expected_idx:
                    return PassStatus.ESCALATED
            except ValueError:
                pass
        
        return PassStatus.FAIL
    
    async def _evaluate_batch(
        self,
        phrases: List[TestPhrase],
    ) -> List[PhraseResult]:
        """
        Evaluate a batch of phrases via Ash-Vigil.
        
        Args:
            phrases: List of phrases to evaluate
        
        Returns:
            List of phrase results
        """
        # Prepare request - Ash-Vigil expects {"phrases": [{"id": "...", "text": "..."}, ...]}
        request_data = {
            "phrases": [
                {"id": p.phrase_id, "text": p.message}
                for p in phrases
            ],
            "include_timing": True,
        }
        
        try:
            start_time = time.perf_counter()
            response = await self._request_with_retry("POST", ENDPOINT_EVALUATE, request_data)
            total_time_ms = (time.perf_counter() - start_time) * 1000
            
        except Exception as e:
            # Return error results for all phrases
            return [
                PhraseResult(
                    phrase_id=p.phrase_id,
                    message=p.message,
                    category=p.category,
                    subcategory=p.subcategory,
                    expected_priorities=p.expected_priorities,
                    expected_risk_levels=p.expected_risk_levels,
                    status=PassStatus.ERROR,
                    error_message=str(e),
                )
                for p in phrases
            ]
        
        # Parse results
        results = []
        vigil_results = response.get("results", [])
        
        # Build a lookup by ID for matching results
        vigil_by_id = {r.get("id", ""): r for r in vigil_results}
        
        # Calculate per-phrase timing (approximate if not provided)
        per_phrase_time_ms = total_time_ms / len(phrases) if phrases else 0
        
        for phrase in phrases:
            vigil_data = vigil_by_id.get(phrase.phrase_id, {})
            
            if vigil_data:
                # Extract Vigil response fields
                # API returns: risk_score, risk_label, confidence, inference_time_ms
                risk_label = vigil_data.get("risk_label", "")
                risk_score = vigil_data.get("risk_score", 0.0)
                confidence = vigil_data.get("confidence", 0.0)
                inference_time = vigil_data.get("inference_time_ms", per_phrase_time_ms)
                error = vigil_data.get("error")
                
                if error:
                    results.append(PhraseResult(
                        phrase_id=phrase.phrase_id,
                        message=phrase.message,
                        category=phrase.category,
                        subcategory=phrase.subcategory,
                        expected_priorities=phrase.expected_priorities,
                        expected_risk_levels=phrase.expected_risk_levels,
                        status=PassStatus.ERROR,
                        error_message=error,
                    ))
                else:
                    # Determine pass/fail
                    status = self._determine_pass_status(
                        expected_risk_levels=phrase.expected_risk_levels,
                        actual_risk_level=risk_label,
                        allow_escalation=True,
                    )
                    
                    results.append(PhraseResult(
                        phrase_id=phrase.phrase_id,
                        message=phrase.message,
                        category=phrase.category,
                        subcategory=phrase.subcategory,
                        expected_priorities=phrase.expected_priorities,
                        expected_risk_levels=phrase.expected_risk_levels,
                        vigil_label=risk_label,
                        vigil_risk_level=risk_label,
                        vigil_confidence=confidence,
                        vigil_scores={"risk_score": risk_score},
                        status=status,
                        inference_time_ms=inference_time,
                    ))
            else:
                results.append(PhraseResult(
                    phrase_id=phrase.phrase_id,
                    message=phrase.message,
                    category=phrase.category,
                    subcategory=phrase.subcategory,
                    expected_priorities=phrase.expected_priorities,
                    expected_risk_levels=phrase.expected_risk_levels,
                    status=PassStatus.ERROR,
                    error_message="No result from Vigil for this phrase",
                ))
        
        return results
    
    def _calculate_category_accuracy(
        self,
        category: str,
        results: List[PhraseResult],
    ) -> CategoryAccuracy:
        """
        Calculate accuracy metrics for a category.
        
        Args:
            category: Category name
            results: Phrase results for this category
        
        Returns:
            CategoryAccuracy with calculated metrics
        """
        passed = sum(1 for r in results if r.status == PassStatus.PASS)
        failed = sum(1 for r in results if r.status == PassStatus.FAIL)
        errors = sum(1 for r in results if r.status == PassStatus.ERROR)
        escalated = sum(1 for r in results if r.status == PassStatus.ESCALATED)
        
        total = len(results)
        accuracy = ((passed + escalated) / total * 100) if total > 0 else 0.0
        
        # Calculate subcategory breakdown
        subcategory_breakdown: Dict[str, Dict[str, int]] = {}
        for result in results:
            if result.subcategory not in subcategory_breakdown:
                subcategory_breakdown[result.subcategory] = {
                    "total": 0, "passed": 0, "failed": 0, "errors": 0, "escalated": 0
                }
            
            subcategory_breakdown[result.subcategory]["total"] += 1
            if result.status == PassStatus.PASS:
                subcategory_breakdown[result.subcategory]["passed"] += 1
            elif result.status == PassStatus.FAIL:
                subcategory_breakdown[result.subcategory]["failed"] += 1
            elif result.status == PassStatus.ERROR:
                subcategory_breakdown[result.subcategory]["errors"] += 1
            elif result.status == PassStatus.ESCALATED:
                subcategory_breakdown[result.subcategory]["escalated"] += 1
        
        # Calculate timing
        total_time = sum(r.inference_time_ms for r in results)
        avg_time = total_time / total if total > 0 else 0.0
        
        return CategoryAccuracy(
            category=category,
            total_phrases=total,
            passed=passed,
            failed=failed,
            errors=errors,
            escalated=escalated,
            accuracy=accuracy,
            subcategory_breakdown=subcategory_breakdown,
            total_inference_time_ms=total_time,
            average_inference_time_ms=avg_time,
        )
    
    async def evaluate_model(
        self,
        model_name: Optional[str] = None,
        categories: Optional[List[str]] = None,
    ) -> EvaluationResult:
        """
        Run a full model evaluation.
        
        Args:
            model_name: Model name for identification (default: fetch from Vigil)
            categories: List of categories to evaluate (default: all specialty)
        
        Returns:
            EvaluationResult with complete metrics
        
        Example:
            >>> result = await evaluator.evaluate_model()
            >>> print(f"Overall accuracy: {result.overall_accuracy}%")
            >>> for cat, acc in result.category_accuracies.items():
            ...     print(f"  {cat}: {acc.accuracy}%")
        """
        import uuid
        
        evaluation_start = time.perf_counter()
        evaluation_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # Get Vigil info
        vigil_version, detected_model = await self.get_vigil_info()
        if model_name is None:
            model_name = detected_model
        
        self._logger.info(
            f"🚀 Starting evaluation {evaluation_id} "
            f"(model: {model_name}, vigil: {vigil_version})"
        )
        
        # Initialize result
        result = EvaluationResult(
            evaluation_id=evaluation_id,
            model_name=model_name,
            timestamp=datetime.now(),
            vigil_host=self.base_url,
            vigil_version=vigil_version,
            status=EvaluationStatus.RUNNING,
        )
        
        try:
            # Load phrases
            phrases_by_category = self.load_phrases(categories)
            
            if not phrases_by_category:
                result.status = EvaluationStatus.FAILED
                result.status_message = "No phrases loaded"
                return result
            
            all_results: List[PhraseResult] = []
            
            # Evaluate each category
            for category, phrases in phrases_by_category.items():
                self._logger.info(f"📊 Evaluating category: {category} ({len(phrases)} phrases)")
                
                # Process in batches
                for i in range(0, len(phrases), self.batch_size):
                    batch = phrases[i:i + self.batch_size]
                    batch_results = await self._evaluate_batch(batch)
                    all_results.extend(batch_results)
                    
                    # Log progress
                    progress = min(i + self.batch_size, len(phrases))
                    self._logger.debug(f"  Processed {progress}/{len(phrases)} phrases")
                
                # Calculate category accuracy
                category_results = [r for r in all_results if r.category == category]
                result.category_accuracies[category] = self._calculate_category_accuracy(
                    category, category_results
                )
            
            # Store all results
            result.phrase_results = all_results
            
            # Calculate overall metrics
            result.total_phrases = len(all_results)
            result.total_passed = sum(1 for r in all_results if r.status == PassStatus.PASS)
            result.total_failed = sum(1 for r in all_results if r.status == PassStatus.FAIL)
            result.total_errors = sum(1 for r in all_results if r.status == PassStatus.ERROR)
            result.total_escalated = sum(1 for r in all_results if r.status == PassStatus.ESCALATED)
            
            if result.total_phrases > 0:
                result.overall_accuracy = (
                    (result.total_passed + result.total_escalated) / result.total_phrases * 100
                )
                result.overall_pass_rate = result.overall_accuracy
            
            # Calculate timing
            result.total_inference_time_ms = sum(r.inference_time_ms for r in all_results)
            result.average_inference_time_ms = (
                result.total_inference_time_ms / result.total_phrases
                if result.total_phrases > 0 else 0.0
            )
            result.total_evaluation_time_seconds = time.perf_counter() - evaluation_start
            
            # Set final status
            if result.total_errors > 0:
                result.status = EvaluationStatus.PARTIAL
                result.status_message = f"{result.total_errors} phrases had errors"
            else:
                result.status = EvaluationStatus.COMPLETED
                result.status_message = "Evaluation completed successfully"
            
            self._logger.info(
                f"✅ Evaluation complete: {result.overall_accuracy:.1f}% accuracy "
                f"({result.total_passed + result.total_escalated}/{result.total_phrases} passed, "
                f"{result.total_failed} failed, {result.total_errors} errors) "
                f"in {result.total_evaluation_time_seconds:.1f}s"
            )
            
        except Exception as e:
            result.status = EvaluationStatus.FAILED
            result.status_message = f"Evaluation failed: {e}"
            result.total_evaluation_time_seconds = time.perf_counter() - evaluation_start
            self._logger.error(f"❌ Evaluation failed: {e}")
        
        return result
    
    async def evaluate_phrases(
        self,
        phrases: List[TestPhrase],
    ) -> List[PhraseResult]:
        """
        Evaluate a specific list of phrases.
        
        Args:
            phrases: List of TestPhrase objects to evaluate
        
        Returns:
            List of PhraseResult objects
        """
        all_results = []
        
        for i in range(0, len(phrases), self.batch_size):
            batch = phrases[i:i + self.batch_size]
            batch_results = await self._evaluate_batch(batch)
            all_results.extend(batch_results)
        
        return all_results
    
    # =========================================================================
    # Context Manager
    # =========================================================================
    
    async def __aenter__(self) -> "VigilEvaluator":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    # =========================================================================
    # Status
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get evaluator status information."""
        return {
            "version": __version__,
            "vigil_url": self.base_url,
            "timeout": self.timeout,
            "batch_size": self.batch_size,
            "phrases_path": str(self._phrases_base_path),
            "cached_categories": list(self._phrase_cache.keys()),
            "client_open": self._client is not None and not self._client.is_closed,
        }


# =============================================================================
# Factory Function - Clean Architecture v5.2.3 Compliance (Rule #1)
# =============================================================================

def create_vigil_evaluator(
    vigil_host: Optional[str] = None,
    vigil_port: Optional[int] = None,
    timeout: Optional[int] = None,
    retry_attempts: Optional[int] = None,
    retry_delay_ms: Optional[int] = None,
    batch_size: Optional[int] = None,
    phrases_base_path: Optional[str] = None,
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
) -> VigilEvaluator:
    """
    Factory function for VigilEvaluator (Clean Architecture v5.2.3 Pattern).
    
    This is the ONLY way to create a VigilEvaluator instance.
    Direct instantiation should be avoided in production code.
    
    Resolution order for each setting:
    1. Explicit parameter (if provided)
    2. ConfigManager value (if config_manager provided)
    3. Environment variable (THRASH_VIGIL_*)
    4. Default value
    
    Args:
        vigil_host: Ash-Vigil server hostname override
        vigil_port: Ash-Vigil server port override
        timeout: Request timeout override (seconds)
        retry_attempts: Retry attempts override
        retry_delay_ms: Retry delay override (milliseconds)
        batch_size: Batch size override
        phrases_base_path: Override path to phrase files
        config_manager: Optional ConfigManager for loading settings
        logging_manager: Optional LoggingConfigManager for custom logger
    
    Returns:
        Configured VigilEvaluator instance
    
    Example:
        >>> # Simple usage
        >>> evaluator = create_vigil_evaluator()
        
        >>> # With ConfigManager integration
        >>> config = create_config_manager()
        >>> evaluator = create_vigil_evaluator(config_manager=config)
        
        >>> # With explicit overrides
        >>> evaluator = create_vigil_evaluator(
        ...     vigil_host="10.20.30.14",
        ...     vigil_port=30882,
        ...     timeout=120,
        ... )
    """
    import os
    
    # Resolve vigil_host
    if vigil_host is None:
        if config_manager:
            vigil_host = config_manager.get("vigil", "host")
        if vigil_host is None:
            vigil_host = os.environ.get("THRASH_VIGIL_HOST", DEFAULT_VIGIL_HOST)
    
    # Resolve vigil_port
    if vigil_port is None:
        if config_manager:
            vigil_port = config_manager.get("vigil", "port")
        if vigil_port is None:
            port_str = os.environ.get("THRASH_VIGIL_PORT", str(DEFAULT_VIGIL_PORT))
            try:
                vigil_port = int(port_str)
            except ValueError:
                vigil_port = DEFAULT_VIGIL_PORT
    
    # Resolve timeout
    if timeout is None:
        if config_manager:
            timeout = config_manager.get("vigil", "timeout")
        if timeout is None:
            timeout_str = os.environ.get("THRASH_VIGIL_TIMEOUT", str(DEFAULT_TIMEOUT))
            try:
                timeout = int(timeout_str)
            except ValueError:
                timeout = DEFAULT_TIMEOUT
    
    # Resolve retry_attempts
    if retry_attempts is None:
        if config_manager:
            retry_attempts = config_manager.get("vigil", "retry_attempts")
        if retry_attempts is None:
            retry_str = os.environ.get("THRASH_VIGIL_RETRY_ATTEMPTS", str(DEFAULT_RETRY_ATTEMPTS))
            try:
                retry_attempts = int(retry_str)
            except ValueError:
                retry_attempts = DEFAULT_RETRY_ATTEMPTS
    
    # Resolve retry_delay_ms
    if retry_delay_ms is None:
        if config_manager:
            retry_delay_ms = config_manager.get("vigil", "retry_delay_ms")
        if retry_delay_ms is None:
            delay_str = os.environ.get("THRASH_VIGIL_RETRY_DELAY", str(DEFAULT_RETRY_DELAY_MS))
            try:
                retry_delay_ms = int(delay_str)
            except ValueError:
                retry_delay_ms = DEFAULT_RETRY_DELAY_MS
    
    # Resolve batch_size
    if batch_size is None:
        if config_manager:
            batch_size = config_manager.get("vigil", "batch_size")
        if batch_size is None:
            batch_str = os.environ.get("THRASH_VIGIL_BATCH_SIZE", str(DEFAULT_BATCH_SIZE))
            try:
                batch_size = int(batch_str)
            except ValueError:
                batch_size = DEFAULT_BATCH_SIZE
    
    # Resolve phrases_base_path
    if phrases_base_path is None:
        if config_manager:
            phrases_base_path = config_manager.get("vigil", "phrases_path")
        if phrases_base_path is None:
            phrases_base_path = os.environ.get("THRASH_VIGIL_PHRASES_PATH")
    
    # Get logger if logging_manager provided
    logger_instance = None
    if logging_manager:
        logger_instance = logging_manager.get_logger("vigil_evaluator")
    
    # Use appropriate logger for factory function messages
    log = logger_instance or logger
    log.debug(
        f"🏭 Creating VigilEvaluator (host: {vigil_host}, port: {vigil_port})"
    )
    
    return VigilEvaluator(
        vigil_host=vigil_host,
        vigil_port=vigil_port,
        timeout=timeout,
        retry_attempts=retry_attempts,
        retry_delay_ms=retry_delay_ms,
        batch_size=batch_size,
        phrases_base_path=phrases_base_path,
        logger_instance=logger_instance,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "VigilEvaluator",
    "create_vigil_evaluator",
    "TestPhrase",
    "PhraseResult",
    "CategoryAccuracy",
    "EvaluationResult",
    "EvaluationStatus",
    "PassStatus",
    "VigilEvaluatorError",
    "VigilConnectionError",
    "VigilTimeoutError",
    "VigilResponseError",
]
