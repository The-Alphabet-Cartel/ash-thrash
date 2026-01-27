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
FILE VERSION: v5.0-2-2.1-1
LAST MODIFIED: 2026-01-26
PHASE: Phase 2 - Ash-Thrash Evaluation Infrastructure
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
__version__ = "v5.0-2-2.1-1"

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
]
