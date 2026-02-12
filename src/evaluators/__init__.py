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
Evaluators Module - Model Evaluation Framework for Ash-Vigil
----------------------------------------------------------------------------
FILE VERSION: v5.1-1-1.8-1
LAST MODIFIED: 2026-02-12
PHASE: Phase 1 - Unified Vigil Evaluation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

This module provides the evaluation framework for testing mental health risk
detection models via Ash-Vigil's /evaluate endpoint.

COMPONENTS:
- VigilEvaluator: HTTP client for evaluating models via Ash-Vigil
- EvaluationReportGenerator: Generates comparison reports (HTML/JSON)

USAGE:
    from src.evaluators import create_vigil_evaluator, create_evaluation_report_generator

    evaluator = create_vigil_evaluator(config_manager=config)
    results = await evaluator.evaluate_model("ourafla/mental-health-bert-finetuned")

    reporter = create_evaluation_report_generator(config_manager=config)
    reporter.generate_comparison_report([results])
"""

# Module version
__version__ = "v5.1-1-1.8-1"

# Import public interfaces (will be added as files are created)
from .vigil_evaluator import (
    VigilEvaluator,
    create_vigil_evaluator,
    EvaluationResult,
    CategoryAccuracy,
    PhraseResult,
    VigilEvaluatorError,
    VigilConnectionError,
    VigilTimeoutError,
    STANDARD_PHRASE_FILES,
    EDGE_CASE_PHRASE_FILES,
    SPECIALTY_PHRASE_FILES,
    ALL_PHRASE_FILES,
    VALID_PHRASE_SETS,
)

from .evaluation_report_generator import (
    EvaluationReportGenerator,
    create_evaluation_report_generator,
    ModelComparison,
)

__all__ = [
    # Core classes
    "VigilEvaluator",
    "EvaluationReportGenerator",
    # Factory functions
    "create_vigil_evaluator",
    "create_evaluation_report_generator",
    # Data classes
    "EvaluationResult",
    "CategoryAccuracy",
    "PhraseResult",
    "ModelComparison",
    # Exceptions
    "VigilEvaluatorError",
    "VigilConnectionError",
    "VigilTimeoutError",
    # Phrase file registries
    "STANDARD_PHRASE_FILES",
    "EDGE_CASE_PHRASE_FILES",
    "SPECIALTY_PHRASE_FILES",
    "ALL_PHRASE_FILES",
    "VALID_PHRASE_SETS",
]
