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
Response Validator for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-4-4.0-3
LAST MODIFIED: 2026-01-22
PHASE: Phase 2 - Test Execution Engine
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Validate Ash-NLP API response structure
- Ensure required fields are present
- Validate data types and value ranges
- Provide detailed validation errors for debugging

REQUIRED RESPONSE FIELDS:
    - crisis_detected: bool
    - severity: str (enum: none, low, medium, high, critical)
    - confidence: float (0.0 - 1.0)
    - crisis_score: float (0.0 - 1.0)
    - requires_intervention: bool
    - recommended_action: str (enum: monitor, check_in, immediate_outreach)
    - signals: dict
    - processing_time_ms: float (>= 0)
    - models_used: list
    - is_degraded: bool
    - request_id: str
    - timestamp: str

USAGE:
    from src.validators.response_validator import create_response_validator
    
    validator = create_response_validator()
    result = validator.validate(response_dict)
    
    if result.is_valid:
        print("✅ Response structure is valid")
    else:
        for error in result.errors:
            print(f"❌ {error}")
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

# Module version
__version__ = "v5.0-4-4.0-3"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Valid severity values (includes 'safe' returned by Ash-NLP)
VALID_SEVERITIES: Set[str] = {"safe", "none", "low", "medium", "high", "critical"}

# Valid recommended actions (includes all values returned by Ash-NLP)
VALID_ACTIONS: Set[str] = {"none", "passive_monitoring", "standard_monitoring", "monitor", "check_in", "priority_response", "immediate_outreach"}

# Required top-level fields with expected types
REQUIRED_FIELDS: Dict[str, type] = {
    "crisis_detected": bool,
    "severity": str,
    "confidence": (int, float),
    "crisis_score": (int, float),
    "requires_intervention": bool,
    "recommended_action": str,
    "signals": dict,
    "processing_time_ms": (int, float),
    "models_used": list,
    "is_degraded": bool,
    "request_id": str,
    "timestamp": str,
}

# Optional fields (presence checked but not required)
OPTIONAL_FIELDS: Dict[str, type] = {
    "explanation": (dict, type(None)),
    "conflict_analysis": (dict, type(None)),
    "consensus": (dict, type(None)),
    "context_analysis": (dict, type(None)),
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ResponseValidationResult:
    """
    Result of response validation.
    
    Attributes:
        is_valid: Whether the response passed all validations
        errors: List of validation error messages
        warnings: List of validation warning messages
        fields_present: Set of fields found in response
        fields_missing: Set of required fields not found
        field_type_errors: Dict of field names to type error descriptions
        value_errors: Dict of field names to value error descriptions
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fields_present: Set[str] = field(default_factory=set)
    fields_missing: Set[str] = field(default_factory=set)
    field_type_errors: Dict[str, str] = field(default_factory=dict)
    value_errors: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "fields_present": list(self.fields_present),
            "fields_missing": list(self.fields_missing),
            "field_type_errors": self.field_type_errors,
            "value_errors": self.value_errors,
        }
    
    @property
    def error_count(self) -> int:
        """Get total number of errors."""
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        """Get total number of warnings."""
        return len(self.warnings)


# =============================================================================
# Response Validator
# =============================================================================

class ResponseValidator:
    """
    Validates Ash-NLP API response structure and data.
    
    This validator ensures that responses from Ash-NLP conform to the
    expected schema, have valid data types, and contain values within
    expected ranges.
    
    Attributes:
        strict_mode: If True, treat warnings as errors
    
    Example:
        >>> validator = create_response_validator()
        >>> 
        >>> # Validate a response
        >>> result = validator.validate(response_dict)
        >>> if result.is_valid:
        ...     print("Response is valid")
        ... else:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """
    
    def __init__(
        self,
        strict_mode: bool = False,
        logger_instance: Optional[logging.Logger] = None,
    ):
        """
        Initialize the ResponseValidator.
        
        Args:
            strict_mode: If True, warnings become errors
            logger_instance: Optional custom logger
        
        Note:
            Use create_response_validator() factory function instead.
        """
        self.strict_mode = strict_mode
        self._logger = logger_instance or logger
        
        self._logger.debug(
            f"ResponseValidator {__version__} initialized "
            f"(strict_mode: {strict_mode})"
        )
    
    def validate(self, response: Dict[str, Any]) -> ResponseValidationResult:
        """
        Validate an Ash-NLP API response.
        
        Args:
            response: Dictionary containing the API response
        
        Returns:
            ResponseValidationResult with validation details
        
        Example:
            >>> result = validator.validate({
            ...     "crisis_detected": True,
            ...     "severity": "high",
            ...     "confidence": 0.85,
            ...     ...
            ... })
        """
        errors: List[str] = []
        warnings: List[str] = []
        fields_present: Set[str] = set()
        fields_missing: Set[str] = set()
        field_type_errors: Dict[str, str] = {}
        value_errors: Dict[str, str] = {}
        
        # Check if response is a dictionary
        if not isinstance(response, dict):
            errors.append(f"Response must be a dictionary, got {type(response).__name__}")
            return ResponseValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                fields_present=fields_present,
                fields_missing=fields_missing,
                field_type_errors=field_type_errors,
                value_errors=value_errors,
            )
        
        # Check required fields
        for field_name, expected_type in REQUIRED_FIELDS.items():
            if field_name not in response:
                fields_missing.add(field_name)
                errors.append(f"Missing required field: '{field_name}'")
            else:
                fields_present.add(field_name)
                value = response[field_name]
                
                # Check type
                if not isinstance(value, expected_type):
                    type_name = (
                        expected_type.__name__ 
                        if not isinstance(expected_type, tuple) 
                        else "/".join(t.__name__ for t in expected_type)
                    )
                    field_type_errors[field_name] = (
                        f"Expected {type_name}, got {type(value).__name__}"
                    )
                    errors.append(
                        f"Field '{field_name}' has wrong type: "
                        f"expected {type_name}, got {type(value).__name__}"
                    )
        
        # Check optional fields (note presence but don't error if missing)
        for field_name, expected_type in OPTIONAL_FIELDS.items():
            if field_name in response:
                fields_present.add(field_name)
                value = response[field_name]
                
                # Check type (None is allowed for optional fields)
                if value is not None and not isinstance(value, expected_type):
                    type_name = (
                        expected_type.__name__
                        if not isinstance(expected_type, tuple)
                        else "/".join(t.__name__ for t in expected_type if t != type(None))
                    )
                    field_type_errors[field_name] = (
                        f"Expected {type_name} or null, got {type(value).__name__}"
                    )
                    warnings.append(
                        f"Optional field '{field_name}' has unexpected type: "
                        f"expected {type_name} or null, got {type(value).__name__}"
                    )
        
        # Validate specific field values
        self._validate_severity(response, errors, value_errors)
        self._validate_confidence(response, errors, value_errors)
        self._validate_crisis_score(response, errors, value_errors)
        self._validate_recommended_action(response, errors, value_errors)
        self._validate_processing_time(response, warnings, value_errors)
        self._validate_signals(response, warnings, value_errors)
        self._validate_models_used(response, warnings, value_errors)
        
        # In strict mode, warnings become errors
        if self.strict_mode:
            errors.extend(warnings)
            warnings = []
        
        is_valid = len(errors) == 0
        
        # Log result
        if is_valid:
            self._logger.debug("✅ Response validation passed")
        else:
            self._logger.debug(f"❌ Response validation failed: {len(errors)} errors")
        
        return ResponseValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            fields_present=fields_present,
            fields_missing=fields_missing,
            field_type_errors=field_type_errors,
            value_errors=value_errors,
        )
    
    def _validate_severity(
        self,
        response: Dict[str, Any],
        errors: List[str],
        value_errors: Dict[str, str],
    ) -> None:
        """Validate severity field value."""
        if "severity" not in response:
            return
        
        severity = response["severity"]
        if isinstance(severity, str):
            severity_lower = severity.lower()
            if severity_lower not in VALID_SEVERITIES:
                value_errors["severity"] = (
                    f"Invalid severity '{severity}'. "
                    f"Valid values: {sorted(VALID_SEVERITIES)}"
                )
                errors.append(
                    f"Invalid severity value: '{severity}'. "
                    f"Expected one of: {sorted(VALID_SEVERITIES)}"
                )
    
    def _validate_confidence(
        self,
        response: Dict[str, Any],
        errors: List[str],
        value_errors: Dict[str, str],
    ) -> None:
        """Validate confidence field value is in range [0, 1]."""
        if "confidence" not in response:
            return
        
        confidence = response["confidence"]
        if isinstance(confidence, (int, float)):
            if not (0.0 <= confidence <= 1.0):
                value_errors["confidence"] = (
                    f"Confidence {confidence} out of range [0.0, 1.0]"
                )
                errors.append(
                    f"Confidence value {confidence} is out of range. "
                    f"Expected 0.0 <= confidence <= 1.0"
                )
    
    def _validate_crisis_score(
        self,
        response: Dict[str, Any],
        errors: List[str],
        value_errors: Dict[str, str],
    ) -> None:
        """Validate crisis_score field value is in range [0, 1]."""
        if "crisis_score" not in response:
            return
        
        crisis_score = response["crisis_score"]
        if isinstance(crisis_score, (int, float)):
            if not (0.0 <= crisis_score <= 1.0):
                value_errors["crisis_score"] = (
                    f"Crisis score {crisis_score} out of range [0.0, 1.0]"
                )
                errors.append(
                    f"Crisis score value {crisis_score} is out of range. "
                    f"Expected 0.0 <= crisis_score <= 1.0"
                )
    
    def _validate_recommended_action(
        self,
        response: Dict[str, Any],
        errors: List[str],
        value_errors: Dict[str, str],
    ) -> None:
        """Validate recommended_action field value."""
        if "recommended_action" not in response:
            return
        
        action = response["recommended_action"]
        if isinstance(action, str):
            action_lower = action.lower()
            if action_lower not in VALID_ACTIONS:
                value_errors["recommended_action"] = (
                    f"Invalid action '{action}'. "
                    f"Valid values: {sorted(VALID_ACTIONS)}"
                )
                errors.append(
                    f"Invalid recommended_action value: '{action}'. "
                    f"Expected one of: {sorted(VALID_ACTIONS)}"
                )
    
    def _validate_processing_time(
        self,
        response: Dict[str, Any],
        warnings: List[str],
        value_errors: Dict[str, str],
    ) -> None:
        """Validate processing_time_ms is non-negative."""
        if "processing_time_ms" not in response:
            return
        
        processing_time = response["processing_time_ms"]
        if isinstance(processing_time, (int, float)):
            if processing_time < 0:
                value_errors["processing_time_ms"] = (
                    f"Processing time {processing_time}ms is negative"
                )
                warnings.append(
                    f"Processing time {processing_time}ms is negative, "
                    f"which is unexpected"
                )
    
    def _validate_signals(
        self,
        response: Dict[str, Any],
        warnings: List[str],
        value_errors: Dict[str, str],
    ) -> None:
        """Validate signals dictionary structure."""
        if "signals" not in response:
            return
        
        signals = response["signals"]
        if not isinstance(signals, dict):
            return
        
        # Check each model's signal structure
        for model_name, signal_data in signals.items():
            if not isinstance(signal_data, dict):
                warnings.append(
                    f"Signal data for model '{model_name}' is not a dictionary"
                )
                continue
            
            # Expected signal fields
            expected_signal_fields = {"label", "score", "crisis_signal"}
            missing_signal_fields = expected_signal_fields - set(signal_data.keys())
            
            if missing_signal_fields:
                warnings.append(
                    f"Signal for model '{model_name}' missing fields: "
                    f"{sorted(missing_signal_fields)}"
                )
    
    def _validate_models_used(
        self,
        response: Dict[str, Any],
        warnings: List[str],
        value_errors: Dict[str, str],
    ) -> None:
        """Validate models_used list."""
        if "models_used" not in response:
            return
        
        models_used = response["models_used"]
        if not isinstance(models_used, list):
            return
        
        if len(models_used) == 0:
            warnings.append("models_used list is empty")
        
        # Check that models_used matches signals keys
        if "signals" in response and isinstance(response["signals"], dict):
            signal_models = set(response["signals"].keys())
            listed_models = set(models_used)
            
            if signal_models != listed_models:
                missing_in_signals = listed_models - signal_models
                missing_in_list = signal_models - listed_models
                
                if missing_in_signals:
                    warnings.append(
                        f"Models in models_used but not in signals: "
                        f"{sorted(missing_in_signals)}"
                    )
                if missing_in_list:
                    warnings.append(
                        f"Models in signals but not in models_used: "
                        f"{sorted(missing_in_list)}"
                    )
    
    def is_valid_response(self, response: Dict[str, Any]) -> bool:
        """
        Quick check if response is valid.
        
        Args:
            response: Dictionary containing the API response
        
        Returns:
            True if valid, False otherwise
        """
        return self.validate(response).is_valid


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================

def create_response_validator(
    strict_mode: bool = False,
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
) -> ResponseValidator:
    """
    Factory function for ResponseValidator (Clean Architecture v5.2.1 Pattern).
    
    This is the ONLY way to create a ResponseValidator instance.
    Direct instantiation should be avoided in production code.
    
    Args:
        strict_mode: If True, warnings become errors
        config_manager: Optional ConfigManager (for future configuration)
        logging_manager: Optional LoggingConfigManager for custom logger
    
    Returns:
        Configured ResponseValidator instance
    
    Example:
        >>> # Simple usage
        >>> validator = create_response_validator()
        
        >>> # With strict mode
        >>> validator = create_response_validator(strict_mode=True)
        
        >>> # With logging integration
        >>> validator = create_response_validator(logging_manager=logging_mgr)
    """
    # Get logger if logging_manager provided
    logger_instance = None
    if logging_manager:
        logger_instance = logging_manager.get_logger("response_validator")
    
    # Future: Could load strict_mode from config_manager
    if config_manager:
        configured_strict = config_manager.get("validation", "strict_response_mode")
        if configured_strict is not None:
            strict_mode = bool(configured_strict)
    
    logger.debug(f"🏭 Creating ResponseValidator (strict_mode: {strict_mode})")
    
    return ResponseValidator(
        strict_mode=strict_mode,
        logger_instance=logger_instance,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "ResponseValidator",
    "create_response_validator",
    "ResponseValidationResult",
    "VALID_SEVERITIES",
    "VALID_ACTIONS",
    "REQUIRED_FIELDS",
]
