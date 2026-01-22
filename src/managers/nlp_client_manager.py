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
NLP Client Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.4-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 1 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Provide HTTP client for Ash-NLP API communication
- Implement retry logic with exponential backoff
- Handle timeouts gracefully
- Log all requests and responses for debugging
- Validate API responses

SUPPORTED ENDPOINTS:
- POST /analyze        - Analyze single message for crisis signals
- POST /analyze/batch  - Analyze multiple messages in batch
- GET  /health         - Simple health check
- GET  /status         - Detailed server status

CONFIGURATION:
- Host:           THRASH_NLP_HOST (default: 10.20.30.253)
- Port:           THRASH_NLP_PORT (default: 30880)
- Timeout:        THRASH_NLP_TIMEOUT (default: 30 seconds)
- Retry Attempts: THRASH_NLP_RETRY_ATTEMPTS (default: 3)
- Retry Delay:    THRASH_NLP_RETRY_DELAY (default: 1000ms)
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import httpx

# Module version
__version__ = "v5.0-1-1.4-1"

# Initialize logger (will be replaced by LoggingConfigManager logger)
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default configuration
DEFAULT_HOST = "10.20.30.253"
DEFAULT_PORT = 30880
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_MS = 1000

# API endpoints
ENDPOINT_ANALYZE = "/analyze"
ENDPOINT_ANALYZE_BATCH = "/analyze/batch"
ENDPOINT_HEALTH = "/health"
ENDPOINT_STATUS = "/status"


# =============================================================================
# Data Classes
# =============================================================================

class AnalyzeVerbosity(str, Enum):
    """Verbosity levels for analysis explanations."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"


@dataclass
class AnalyzeRequest:
    """Request data for /analyze endpoint."""
    message: str
    user_id: Optional[str] = None
    channel_id: Optional[str] = None
    include_explanation: bool = True
    explanation_verbosity: str = "standard"
    include_context_analysis: bool = False


@dataclass
class AnalyzeResponse:
    """
    Response data from /analyze endpoint.
    
    Attributes:
        crisis_detected: Whether a crisis was detected
        severity: Crisis severity level (none, low, medium, high, critical)
        confidence: Model confidence score (0.0 - 1.0)
        crisis_score: Weighted crisis score (0.0 - 1.0)
        requires_intervention: Whether intervention is recommended
        recommended_action: Suggested action (monitor, check_in, immediate_outreach)
        signals: Per-model signal breakdown
        processing_time_ms: Server processing time
        models_used: List of models that contributed
        is_degraded: Whether server is in degraded mode
        request_id: Unique request identifier
        timestamp: Server timestamp
        explanation: Human-readable explanation (if requested)
        conflict_analysis: Model conflict details (if any)
        consensus: Consensus algorithm results
        context_analysis: Context/escalation analysis (if requested)
        raw_response: Original JSON response for debugging
    """
    crisis_detected: bool
    severity: str
    confidence: float
    crisis_score: float
    requires_intervention: bool
    recommended_action: str
    signals: Dict[str, Any]
    processing_time_ms: float
    models_used: List[str]
    is_degraded: bool
    request_id: str
    timestamp: str
    explanation: Optional[Dict[str, Any]] = None
    conflict_analysis: Optional[Dict[str, Any]] = None
    consensus: Optional[Dict[str, Any]] = None
    context_analysis: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalyzeResponse":
        """Create AnalyzeResponse from API response dictionary."""
        return cls(
            crisis_detected=data.get("crisis_detected", False),
            severity=data.get("severity", "none"),
            confidence=data.get("confidence", 0.0),
            crisis_score=data.get("crisis_score", 0.0),
            requires_intervention=data.get("requires_intervention", False),
            recommended_action=data.get("recommended_action", "monitor"),
            signals=data.get("signals", {}),
            processing_time_ms=data.get("processing_time_ms", 0.0),
            models_used=data.get("models_used", []),
            is_degraded=data.get("is_degraded", False),
            request_id=data.get("request_id", ""),
            timestamp=data.get("timestamp", ""),
            explanation=data.get("explanation"),
            conflict_analysis=data.get("conflict_analysis"),
            consensus=data.get("consensus"),
            context_analysis=data.get("context_analysis"),
            raw_response=data,
        )


@dataclass
class HealthResponse:
    """Response data from /health endpoint."""
    status: str
    healthy: bool
    timestamp: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthResponse":
        """Create HealthResponse from API response dictionary."""
        return cls(
            status=data.get("status", "unknown"),
            healthy=data.get("status", "").lower() in ("ok", "healthy"),
            timestamp=data.get("timestamp"),
        )


# =============================================================================
# Exceptions
# =============================================================================

class NLPClientError(Exception):
    """Base exception for NLP client errors."""
    pass


class NLPConnectionError(NLPClientError):
    """Raised when connection to Ash-NLP fails."""
    pass


class NLPTimeoutError(NLPClientError):
    """Raised when request to Ash-NLP times out."""
    pass


class NLPResponseError(NLPClientError):
    """Raised when Ash-NLP returns an error response."""
    def __init__(self, message: str, status_code: int, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


# =============================================================================
# NLP Client Manager
# =============================================================================

class NLPClientManager:
    """
    HTTP client manager for Ash-NLP API communication.
    
    Provides reliable communication with Ash-NLP including:
    - Automatic retry with exponential backoff
    - Timeout handling
    - Request/response logging
    - Response validation
    
    Attributes:
        base_url: Base URL for Ash-NLP API
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts
        retry_delay_ms: Initial retry delay in milliseconds
    
    Example:
        >>> client = create_nlp_client_manager(config_manager=config)
        >>> 
        >>> # Check health
        >>> health = await client.health_check()
        >>> if health.healthy:
        >>>     # Analyze a message
        >>>     result = await client.analyze("I'm feeling really down today")
        >>>     print(f"Crisis detected: {result.crisis_detected}")
    """
    
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        timeout: int = DEFAULT_TIMEOUT,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        retry_delay_ms: int = DEFAULT_RETRY_DELAY_MS,
        logger_instance: Optional[logging.Logger] = None,
    ):
        """
        Initialize the NLPClientManager.
        
        Args:
            host: Ash-NLP server hostname or IP
            port: Ash-NLP server port
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay_ms: Initial delay between retries (doubles each retry)
            logger_instance: Optional custom logger
        
        Note:
            Use create_nlp_client_manager() factory function instead.
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay_ms = retry_delay_ms
        
        # Use provided logger or module logger
        self._logger = logger_instance or logger
        
        # Internal bypass key (for skipping NLP rate limiting)
        self._bypass_key: Optional[str] = None
        
        # HTTP client (created lazily for async context)
        self._client: Optional[httpx.AsyncClient] = None
        
        # Statistics tracking
        self._stats = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "retries_total": 0,
            "total_latency_ms": 0.0,
        }
        
        self._logger.debug(
            f"NLPClientManager {__version__} initialized "
            f"(base_url: {self.base_url}, timeout: {timeout}s)"
        )
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"Ash-Thrash/{__version__}",
            }
            
            # Add bypass key if available (skip NLP rate limiting)
            if self._bypass_key:
                headers["X-Ash-Internal-Key"] = self._bypass_key
            
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers=headers,
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
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            json_data: Optional JSON body for POST requests
        
        Returns:
            Parsed JSON response
        
        Raises:
            NLPConnectionError: Connection failed after all retries
            NLPTimeoutError: Request timed out after all retries
            NLPResponseError: Server returned an error response
        """
        client = await self._get_client()
        last_exception: Optional[Exception] = None
        
        for attempt in range(self.retry_attempts + 1):
            try:
                self._stats["requests_total"] += 1
                start_time = time.perf_counter()
                
                # Log request
                self._logger.debug(
                    f"📤 {method} {endpoint} (attempt {attempt + 1}/{self.retry_attempts + 1})"
                )
                
                # Make request
                if method.upper() == "GET":
                    response = await client.get(endpoint)
                else:
                    response = await client.post(endpoint, json=json_data)
                
                # Calculate latency
                latency_ms = (time.perf_counter() - start_time) * 1000
                self._stats["total_latency_ms"] += latency_ms
                
                # Check for error responses
                if response.status_code >= 400:
                    error_body = response.text
                    self._logger.warning(
                        f"⚠️ {method} {endpoint} returned {response.status_code}: {error_body[:200]}"
                    )
                    raise NLPResponseError(
                        f"Ash-NLP returned status {response.status_code}",
                        status_code=response.status_code,
                        response_body=error_body,
                    )
                
                # Parse response
                data = response.json()
                
                self._stats["requests_successful"] += 1
                self._logger.debug(
                    f"📥 {method} {endpoint} completed in {latency_ms:.1f}ms"
                )
                
                return data
                
            except httpx.ConnectError as e:
                last_exception = NLPConnectionError(
                    f"Failed to connect to Ash-NLP at {self.base_url}: {e}"
                )
                self._logger.warning(f"🔌 Connection failed: {e}")
                
            except httpx.TimeoutException as e:
                last_exception = NLPTimeoutError(
                    f"Request to Ash-NLP timed out after {self.timeout}s: {e}"
                )
                self._logger.warning(f"⏱️ Request timed out: {e}")
                
            except NLPResponseError:
                # Don't retry on server errors (4xx, 5xx)
                self._stats["requests_failed"] += 1
                raise
                
            except Exception as e:
                last_exception = NLPClientError(f"Unexpected error: {e}")
                self._logger.warning(f"❌ Unexpected error: {e}")
            
            # Retry logic (exponential backoff)
            if attempt < self.retry_attempts:
                delay_ms = self.retry_delay_ms * (2 ** attempt)
                self._stats["retries_total"] += 1
                self._logger.info(
                    f"🔄 Retrying in {delay_ms}ms (attempt {attempt + 2}/{self.retry_attempts + 1})"
                )
                await asyncio.sleep(delay_ms / 1000)
        
        # All retries exhausted
        self._stats["requests_failed"] += 1
        self._logger.error(
            f"❌ {method} {endpoint} failed after {self.retry_attempts + 1} attempts"
        )
        raise last_exception or NLPClientError("Request failed")
    
    # =========================================================================
    # Public API Methods
    # =========================================================================
    
    async def health_check(self) -> HealthResponse:
        """
        Check Ash-NLP server health.
        
        Returns:
            HealthResponse with server status
        
        Raises:
            NLPClientError: If health check fails
        """
        try:
            data = await self._request_with_retry("GET", ENDPOINT_HEALTH)
            return HealthResponse.from_dict(data)
        except Exception as e:
            self._logger.error(f"❌ Health check failed: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed Ash-NLP server status.
        
        Returns:
            Dictionary with detailed server status
        
        Raises:
            NLPClientError: If status request fails
        """
        return await self._request_with_retry("GET", ENDPOINT_STATUS)
    
    async def analyze(
        self,
        message: str,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        include_explanation: bool = True,
        explanation_verbosity: str = "standard",
        include_context_analysis: bool = False,
    ) -> AnalyzeResponse:
        """
        Analyze a single message for crisis signals.
        
        Args:
            message: The message text to analyze
            user_id: Optional Discord user ID for context
            channel_id: Optional Discord channel ID for context
            include_explanation: Whether to include human-readable explanation
            explanation_verbosity: Detail level (minimal, standard, detailed)
            include_context_analysis: Whether to include escalation analysis
        
        Returns:
            AnalyzeResponse with classification results
        
        Raises:
            NLPClientError: If analysis request fails
        
        Example:
            >>> result = await client.analyze("I'm feeling really down today")
            >>> print(f"Severity: {result.severity}, Score: {result.crisis_score:.2f}")
        """
        request_data = {
            "message": message,
            "include_explanation": include_explanation,
            "explanation_verbosity": explanation_verbosity,
            "include_context_analysis": include_context_analysis,
        }
        
        # Add optional fields
        if user_id:
            request_data["user_id"] = user_id
        if channel_id:
            request_data["channel_id"] = channel_id
        
        data = await self._request_with_retry("POST", ENDPOINT_ANALYZE, request_data)
        return AnalyzeResponse.from_dict(data)
    
    async def analyze_batch(
        self,
        messages: List[str],
        include_explanation: bool = False,
        include_context_analysis: bool = False,
    ) -> List[AnalyzeResponse]:
        """
        Analyze multiple messages in a single batch request.
        
        Args:
            messages: List of message texts to analyze
            include_explanation: Whether to include explanations
            include_context_analysis: Whether to include context analysis
        
        Returns:
            List of AnalyzeResponse objects
        
        Raises:
            NLPClientError: If batch request fails
        """
        request_data = {
            "messages": messages,
            "include_explanation": include_explanation,
            "include_context_analysis": include_context_analysis,
        }
        
        data = await self._request_with_retry("POST", ENDPOINT_ANALYZE_BATCH, request_data)
        
        # Parse results
        results = data.get("results", [])
        return [AnalyzeResponse.from_dict(r) for r in results]
    
    async def is_available(self) -> bool:
        """
        Check if Ash-NLP server is available and healthy.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            health = await self.health_check()
            return health.healthy
        except Exception:
            return False
    
    # =========================================================================
    # Statistics and Status
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics.
        
        Returns:
            Dictionary with request statistics
        """
        total = self._stats["requests_total"]
        successful = self._stats["requests_successful"]
        
        return {
            "requests_total": total,
            "requests_successful": successful,
            "requests_failed": self._stats["requests_failed"],
            "retries_total": self._stats["retries_total"],
            "success_rate": (successful / total * 100) if total > 0 else 0.0,
            "average_latency_ms": (
                self._stats["total_latency_ms"] / successful
                if successful > 0 else 0.0
            ),
        }
    
    def reset_stats(self) -> None:
        """Reset client statistics."""
        self._stats = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "retries_total": 0,
            "total_latency_ms": 0.0,
        }
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        Get client configuration and status.
        
        Returns:
            Dictionary with client configuration and statistics
        """
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay_ms": self.retry_delay_ms,
            "client_open": self._client is not None and not self._client.is_closed,
            "stats": self.get_stats(),
        }
    
    # =========================================================================
    # Context Manager Support
    # =========================================================================
    
    async def __aenter__(self) -> "NLPClientManager":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================

def create_nlp_client_manager(
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout: Optional[int] = None,
    retry_attempts: Optional[int] = None,
    retry_delay_ms: Optional[int] = None,
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
) -> NLPClientManager:
    """
    Factory function for NLPClientManager (Clean Architecture v5.2.1 Pattern).
    
    This is the ONLY way to create an NLPClientManager instance.
    Direct instantiation should be avoided in production code.
    
    Resolution order for each setting:
    1. Explicit parameter (if provided)
    2. ConfigManager value (if config_manager provided)
    3. Environment variable (THRASH_NLP_*)
    4. Default value
    
    Args:
        host: Ash-NLP server hostname override
        port: Ash-NLP server port override
        timeout: Request timeout override (seconds)
        retry_attempts: Retry attempts override
        retry_delay_ms: Retry delay override (milliseconds)
        config_manager: Optional ConfigManager for loading settings
        logging_manager: Optional LoggingConfigManager for custom logger
    
    Returns:
        Configured NLPClientManager instance
    
    Example:
        >>> # Simple usage
        >>> client = create_nlp_client_manager()
        
        >>> # With ConfigManager integration
        >>> config = create_config_manager()
        >>> client = create_nlp_client_manager(config_manager=config)
        
        >>> # With full dependency injection
        >>> client = create_nlp_client_manager(
        ...     config_manager=config,
        ...     logging_manager=logging_mgr,
        ... )
    """
    import os
    
    # Resolve host
    if host is None:
        if config_manager:
            host = config_manager.get("nlp_server", "host")
        if host is None:
            host = os.environ.get("THRASH_NLP_HOST", DEFAULT_HOST)
    
    # Resolve port
    if port is None:
        if config_manager:
            port = config_manager.get("nlp_server", "port")
        if port is None:
            port_str = os.environ.get("THRASH_NLP_PORT", str(DEFAULT_PORT))
            try:
                port = int(port_str)
            except ValueError:
                port = DEFAULT_PORT
    
    # Resolve timeout
    if timeout is None:
        if config_manager:
            timeout = config_manager.get("nlp_server", "timeout")
        if timeout is None:
            timeout_str = os.environ.get("THRASH_NLP_TIMEOUT", str(DEFAULT_TIMEOUT))
            try:
                timeout = int(timeout_str)
            except ValueError:
                timeout = DEFAULT_TIMEOUT
    
    # Resolve retry_attempts
    if retry_attempts is None:
        if config_manager:
            retry_attempts = config_manager.get("nlp_server", "retry_attempts")
        if retry_attempts is None:
            retry_str = os.environ.get("THRASH_NLP_RETRY_ATTEMPTS", str(DEFAULT_RETRY_ATTEMPTS))
            try:
                retry_attempts = int(retry_str)
            except ValueError:
                retry_attempts = DEFAULT_RETRY_ATTEMPTS
    
    # Resolve retry_delay_ms
    if retry_delay_ms is None:
        if config_manager:
            retry_delay_ms = config_manager.get("nlp_server", "retry_delay_ms")
        if retry_delay_ms is None:
            delay_str = os.environ.get("THRASH_NLP_RETRY_DELAY", str(DEFAULT_RETRY_DELAY_MS))
            try:
                retry_delay_ms = int(delay_str)
            except ValueError:
                retry_delay_ms = DEFAULT_RETRY_DELAY_MS
    
    # Get logger if logging_manager provided
    logger_instance = None
    if logging_manager:
        logger_instance = logging_manager.get_logger("nlp_client")
    
    # Load bypass key from secrets (for skipping NLP rate limiting)
    from src.managers import create_secrets_manager
    secrets = create_secrets_manager()
    bypass_key = secrets.get("ash_internal_bypass_key")
    
    logger.debug(
        f"🏭 Creating NLPClientManager (host: {host}, port: {port}, bypass_key={'configured' if bypass_key else 'none'})"
    )
    
    client = NLPClientManager(
        host=host,
        port=port,
        timeout=timeout,
        retry_attempts=retry_attempts,
        retry_delay_ms=retry_delay_ms,
        logger_instance=logger_instance,
    )
    
    # Set bypass key after creation
    client._bypass_key = bypass_key
    
    if bypass_key:
        logger.info("🔑 NLP rate limit bypass key loaded")
    
    return client


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
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
]
