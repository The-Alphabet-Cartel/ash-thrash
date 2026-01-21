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
Classification Validator for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.1-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 2 - Test Execution Engine
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Validate Ash-NLP severity classifications against expected priorities
- Implement tolerance logic for escalation and de-escalation
- Provide detailed validation results with failure reasons
- Support multiple acceptable priorities (for edge cases)

PRIORITY HIERARCHY:
    none (0) → low (1) → medium (2) → high (3) → critical (4)

TOLERANCE LOGIC:
    - Exact Match: actual_severity in expected_priorities → PASS
    - Escalation: actual > expected AND allow_escalation → PASS
    - De-escalation: actual < expected AND allow_deescalation → PASS
    - Otherwise → FAIL

USAGE:
    from src.validators.classification_validator import create_classification_validator
    
    validator = create_classification_validator()
    result = validator.validate(
        actual_severity="medium",
        expected_priorities=["high"],
        allow_escalation=True,
        allow_deescalation=False
    )
    
    if result.passed:
        print("✅ Classification matches expectations")
    else:
        print(f"❌ {result.failure_reason}")
"""

import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional

# Module version
__version__ = "v5.0-2-2.1-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

class PriorityLevel(IntEnum):
    """
    Priority/severity levels in hierarchical order.
    
    Higher values indicate more severe crisis levels.
    """
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# String to enum mapping
PRIORITY_MAP: Dict[str, PriorityLevel] = {
    "none": PriorityLevel.NONE,
    "low": PriorityLevel.LOW,
    "medium": PriorityLevel.MEDIUM,
    "high": PriorityLevel.HIGH,
    "critical": PriorityLevel.CRITICAL,
}

# Valid priority strings
VALID_PRIORITIES = list(PRIORITY_MAP.keys())


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ValidationResult:
    """
    Result of a classification validation.
    
    Attributes:
        passed: Whether the classification passed validation
        actual_severity: The severity returned by Ash-NLP
        expected_priorities: List of acceptable priorities
        match_type: How the classification matched (exact, escalation, deescalation, none)
        failure_reason: Human-readable explanation if failed
        actual_level: Numeric level of actual severity
        expected_levels: Numeric levels of expected priorities
        details: Additional validation details for debugging
    """
    passed: bool
    actual_severity: str
    expected_priorities: List[str]
    match_type: str  # "exact", "escalation", "deescalation", "none"
    failure_reason: Optional[str] = None
    actual_level: Optional[int] = None
    expected_levels: List[int] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "passed": self.passed,
            "actual_severity": self.actual_severity,
            "expected_priorities": self.expected_priorities,
            "match_type": self.match_type,
            "failure_reason": self.failure_reason,
            "actual_level": self.actual_level,
            "expected_levels": self.expected_levels,
            "details": self.details,
        }


# =============================================================================
# Classification Validator
# =============================================================================

class ClassificationValidator:
    """
    Validates Ash-NLP severity classifications against expected priorities.
    
    This is the single source of truth for priority validation logic in Ash-Thrash.
    It handles exact matches, escalation tolerance, and de-escalation tolerance.
    
    Attributes:
        strict_mode: If True, only exact matches pass (ignore tolerance settings)
    
    Example:
        >>> validator = create_classification_validator()
        >>> 
        >>> # Exact match
        >>> result = validator.validate("high", ["high"])
        >>> assert result.passed and result.match_type == "exact"
        >>> 
        >>> # Escalation allowed
        >>> result = validator.validate("critical", ["high"], allow_escalation=True)
        >>> assert result.passed and result.match_type == "escalation"
        >>> 
        >>> # De-escalation not allowed
        >>> result = validator.validate("medium", ["high"], allow_deescalation=False)
        >>> assert not result.passed
    """
    
    def __init__(
        self,
        strict_mode: bool = False,
        logger_instance: Optional[logging.Logger] = None,
    ):
        """
        Initialize the ClassificationValidator.
        
        Args:
            strict_mode: If True, only exact matches pass
            logger_instance: Optional custom logger
        
        Note:
            Use create_classification_validator() factory function instead.
        """
        self.strict_mode = strict_mode
        self._logger = logger_instance or logger
        
        self._logger.debug(
            f"ClassificationValidator {__version__} initialized "
            f"(strict_mode: {strict_mode})"
        )
    
    def _normalize_priority(self, priority: str) -> str:
        """
        Normalize priority string to lowercase.
        
        Args:
            priority: Priority string to normalize
        
        Returns:
            Lowercase priority string
        """
        return priority.lower().strip()
    
    def _get_priority_level(self, priority: str) -> Optional[PriorityLevel]:
        """
        Get numeric level for a priority string.
        
        Args:
            priority: Priority string
        
        Returns:
            PriorityLevel enum value, or None if invalid
        """
        normalized = self._normalize_priority(priority)
        return PRIORITY_MAP.get(normalized)
    
    def is_valid_priority(self, priority: str) -> bool:
        """
        Check if a priority string is valid.
        
        Args:
            priority: Priority string to check
        
        Returns:
            True if valid, False otherwise
        """
        return self._normalize_priority(priority) in VALID_PRIORITIES
    
    def validate(
        self,
        actual_severity: str,
        expected_priorities: List[str],
        allow_escalation: bool = True,
        allow_deescalation: bool = False,
    ) -> ValidationResult:
        """
        Validate a classification against expected priorities.
        
        This method implements the tolerance logic:
        1. Check for exact match in expected_priorities
        2. If escalation allowed, check if actual > all expected
        3. If de-escalation allowed, check if actual < any expected
        
        Args:
            actual_severity: The severity returned by Ash-NLP
            expected_priorities: List of acceptable priority values
            allow_escalation: Whether higher severity is acceptable
            allow_deescalation: Whether lower severity is acceptable
        
        Returns:
            ValidationResult with pass/fail status and details
        
        Example:
            >>> result = validator.validate(
            ...     actual_severity="medium",
            ...     expected_priorities=["high"],
            ...     allow_escalation=True,
            ...     allow_deescalation=False
            ... )
            >>> print(f"Passed: {result.passed}, Reason: {result.failure_reason}")
        """
        # Normalize inputs
        actual_norm = self._normalize_priority(actual_severity)
        expected_norm = [self._normalize_priority(p) for p in expected_priorities]
        
        # Build base result
        details: Dict[str, Any] = {
            "allow_escalation": allow_escalation,
            "allow_deescalation": allow_deescalation,
            "strict_mode": self.strict_mode,
        }
        
        # Validate actual severity is recognized
        actual_level = self._get_priority_level(actual_norm)
        if actual_level is None:
            return ValidationResult(
                passed=False,
                actual_severity=actual_severity,
                expected_priorities=expected_priorities,
                match_type="none",
                failure_reason=f"Unknown severity '{actual_severity}'. Valid values: {VALID_PRIORITIES}",
                actual_level=None,
                expected_levels=[],
                details=details,
            )
        
        # Validate expected priorities are recognized
        expected_levels: List[int] = []
        for exp in expected_norm:
            level = self._get_priority_level(exp)
            if level is None:
                return ValidationResult(
                    passed=False,
                    actual_severity=actual_severity,
                    expected_priorities=expected_priorities,
                    match_type="none",
                    failure_reason=f"Unknown expected priority '{exp}'. Valid values: {VALID_PRIORITIES}",
                    actual_level=int(actual_level),
                    expected_levels=[],
                    details=details,
                )
            expected_levels.append(int(level))
        
        # Check for exact match
        if actual_norm in expected_norm:
            self._logger.debug(
                f"✅ Exact match: '{actual_severity}' in {expected_priorities}"
            )
            return ValidationResult(
                passed=True,
                actual_severity=actual_severity,
                expected_priorities=expected_priorities,
                match_type="exact",
                failure_reason=None,
                actual_level=int(actual_level),
                expected_levels=expected_levels,
                details=details,
            )
        
        # In strict mode, only exact matches pass
        if self.strict_mode:
            return ValidationResult(
                passed=False,
                actual_severity=actual_severity,
                expected_priorities=expected_priorities,
                match_type="none",
                failure_reason=(
                    f"Strict mode: expected {expected_priorities}, got '{actual_severity}'"
                ),
                actual_level=int(actual_level),
                expected_levels=expected_levels,
                details=details,
            )
        
        # Calculate min and max expected levels
        min_expected = min(expected_levels)
        max_expected = max(expected_levels)
        
        # Check escalation (actual is higher than all expected)
        if allow_escalation and int(actual_level) > max_expected:
            max_priority = VALID_PRIORITIES[max_expected]
            self._logger.debug(
                f"✅ Escalation accepted: '{actual_severity}' > '{max_priority}'"
            )
            return ValidationResult(
                passed=True,
                actual_severity=actual_severity,
                expected_priorities=expected_priorities,
                match_type="escalation",
                failure_reason=None,
                actual_level=int(actual_level),
                expected_levels=expected_levels,
                details={
                    **details,
                    "escalation_from": max_priority,
                    "escalation_to": actual_severity,
                },
            )
        
        # Check de-escalation (actual is lower than any expected)
        if allow_deescalation and int(actual_level) < min_expected:
            min_priority = VALID_PRIORITIES[min_expected]
            self._logger.debug(
                f"✅ De-escalation accepted: '{actual_severity}' < '{min_priority}'"
            )
            return ValidationResult(
                passed=True,
                actual_severity=actual_severity,
                expected_priorities=expected_priorities,
                match_type="deescalation",
                failure_reason=None,
                actual_level=int(actual_level),
                expected_levels=expected_levels,
                details={
                    **details,
                    "deescalation_from": min_priority,
                    "deescalation_to": actual_severity,
                },
            )
        
        # Determine failure reason
        if int(actual_level) > max_expected:
            # Escalation not allowed
            max_priority = VALID_PRIORITIES[max_expected]
            failure_reason = (
                f"Escalation not allowed: expected at most '{max_priority}', "
                f"got '{actual_severity}'"
            )
        elif int(actual_level) < min_expected:
            # De-escalation not allowed
            min_priority = VALID_PRIORITIES[min_expected]
            failure_reason = (
                f"De-escalation not allowed: expected at least '{min_priority}', "
                f"got '{actual_severity}'"
            )
        else:
            # Actual is between expected values but not in the list
            failure_reason = (
                f"Classification mismatch: expected {expected_priorities}, "
                f"got '{actual_severity}'"
            )
        
        self._logger.debug(f"❌ Validation failed: {failure_reason}")
        
        return ValidationResult(
            passed=False,
            actual_severity=actual_severity,
            expected_priorities=expected_priorities,
            match_type="none",
            failure_reason=failure_reason,
            actual_level=int(actual_level),
            expected_levels=expected_levels,
            details=details,
        )
    
    def validate_batch(
        self,
        validations: List[Dict[str, Any]],
    ) -> List[ValidationResult]:
        """
        Validate multiple classifications at once.
        
        Args:
            validations: List of dicts with keys:
                - actual_severity: str
                - expected_priorities: List[str]
                - allow_escalation: bool (optional, default True)
                - allow_deescalation: bool (optional, default False)
        
        Returns:
            List of ValidationResult objects
        
        Example:
            >>> results = validator.validate_batch([
            ...     {"actual_severity": "high", "expected_priorities": ["high"]},
            ...     {"actual_severity": "low", "expected_priorities": ["medium"]},
            ... ])
        """
        results = []
        for v in validations:
            result = self.validate(
                actual_severity=v["actual_severity"],
                expected_priorities=v["expected_priorities"],
                allow_escalation=v.get("allow_escalation", True),
                allow_deescalation=v.get("allow_deescalation", False),
            )
            results.append(result)
        return results
    
    def get_priority_level(self, priority: str) -> int:
        """
        Get the numeric level for a priority (public interface).
        
        Args:
            priority: Priority string
        
        Returns:
            Integer level (0-4), or -1 if invalid
        """
        level = self._get_priority_level(priority)
        return int(level) if level is not None else -1
    
    def compare_priorities(self, priority_a: str, priority_b: str) -> int:
        """
        Compare two priorities.
        
        Args:
            priority_a: First priority
            priority_b: Second priority
        
        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        
        Raises:
            ValueError: If either priority is invalid
        """
        level_a = self._get_priority_level(priority_a)
        level_b = self._get_priority_level(priority_b)
        
        if level_a is None:
            raise ValueError(f"Invalid priority: '{priority_a}'")
        if level_b is None:
            raise ValueError(f"Invalid priority: '{priority_b}'")
        
        if level_a < level_b:
            return -1
        elif level_a > level_b:
            return 1
        else:
            return 0


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================

def create_classification_validator(
    strict_mode: bool = False,
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
) -> ClassificationValidator:
    """
    Factory function for ClassificationValidator (Clean Architecture v5.2.1 Pattern).
    
    This is the ONLY way to create a ClassificationValidator instance.
    Direct instantiation should be avoided in production code.
    
    Args:
        strict_mode: If True, only exact matches pass (no tolerance)
        config_manager: Optional ConfigManager (for future configuration)
        logging_manager: Optional LoggingConfigManager for custom logger
    
    Returns:
        Configured ClassificationValidator instance
    
    Example:
        >>> # Simple usage
        >>> validator = create_classification_validator()
        
        >>> # With strict mode
        >>> validator = create_classification_validator(strict_mode=True)
        
        >>> # With logging integration
        >>> validator = create_classification_validator(logging_manager=logging_mgr)
    """
    # Get logger if logging_manager provided
    logger_instance = None
    if logging_manager:
        logger_instance = logging_manager.get_logger("classification_validator")
    
    # Future: Could load strict_mode from config_manager
    if config_manager:
        configured_strict = config_manager.get("validation", "strict_mode")
        if configured_strict is not None:
            strict_mode = bool(configured_strict)
    
    logger.debug(f"🏭 Creating ClassificationValidator (strict_mode: {strict_mode})")
    
    return ClassificationValidator(
        strict_mode=strict_mode,
        logger_instance=logger_instance,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "ClassificationValidator",
    "create_classification_validator",
    "ValidationResult",
    "PriorityLevel",
    "VALID_PRIORITIES",
]
