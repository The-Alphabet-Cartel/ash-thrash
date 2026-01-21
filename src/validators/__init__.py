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
Ash-Thrash Validators Package
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.2-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 2 - Test Execution Engine
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

This package contains validators for Ash-Thrash test execution:

- ClassificationValidator: Validates Ash-NLP severity against expected priorities
- ResponseValidator: Validates Ash-NLP API response structure

USAGE:
    from src.validators import (
        create_classification_validator,
        create_response_validator,
        ValidationResult,
        ResponseValidationResult,
    )
    
    # Classification validation
    class_validator = create_classification_validator()
    result = class_validator.validate("high", ["high", "critical"])
    
    # Response structure validation
    resp_validator = create_response_validator()
    result = resp_validator.validate(api_response_dict)
"""

__version__ = "5.0.0"
__author__ = "The Alphabet Cartel"
__email__ = "dev@alphabetcartel.org"
__url__ = "https://github.com/the-alphabet-cartel/ash-thrash"

# Import validators for convenient access
from src.validators.classification_validator import (
    ClassificationValidator,
    create_classification_validator,
    ValidationResult,
    PriorityLevel,
    VALID_PRIORITIES,
)

from src.validators.response_validator import (
    ResponseValidator,
    create_response_validator,
    ResponseValidationResult,
    VALID_SEVERITIES,
    VALID_ACTIONS,
    REQUIRED_FIELDS,
)

# Package metadata
__all__ = [
    # Package info
    "__version__",
    "__author__",
    "__email__",
    "__url__",
    # Classification Validator
    "ClassificationValidator",
    "create_classification_validator",
    "ValidationResult",
    "PriorityLevel",
    "VALID_PRIORITIES",
    # Response Validator
    "ResponseValidator",
    "create_response_validator",
    "ResponseValidationResult",
    "VALID_SEVERITIES",
    "VALID_ACTIONS",
    "REQUIRED_FIELDS",
]
