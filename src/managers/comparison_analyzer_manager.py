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
Comparison Analyzer Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-6-6.2-1
LAST MODIFIED: 2026-02-07
PHASE: Phase 6 - A/B Testing Infrastructure (v5.1 Migration Phase 1)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Compare two snapshots (baseline vs candidate) side-by-side
- Calculate per-category accuracy deltas (improvement/regression)
- Track per-phrase changes (which phrases flipped pass/fail)
- Compare false positive/negative rates between snapshots
- Compare latency metrics (mean, p95, p99)
- Apply verdict logic: PASS / WARN / FAIL based on configurable thresholds
- Generate ComparisonResult for report rendering

VERDICT LOGIC:
    PASS: Overall accuracy improved AND no critical category regression > threshold
    WARN: Overall accuracy improved BUT one or more categories regressed > threshold
    FAIL: Overall accuracy decreased OR any critical category regressed

USAGE:
    from src.managers.comparison_analyzer_manager import create_comparison_analyzer_manager

    analyzer = create_comparison_analyzer_manager(
        config_manager=config,
        logging_manager=logging_mgr,
    )

    result = analyzer.compare(
        baseline_snapshot=baseline,
        candidate_snapshot=candidate,
    )

    print(f"Overall verdict: {result.overall_verdict}")
    for cat, delta in result.category_deltas.items():
        print(f"  {cat}: {delta.delta:+.2f}% ({delta.verdict})")
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Module version
__version__ = "v5.0-6-6.2-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default regression thresholds (percentage points)
DEFAULT_OVERALL_FAIL_THRESHOLD = -2.0
DEFAULT_CATEGORY_WARN_THRESHOLD = -5.0
DEFAULT_CRITICAL_CATEGORY_FAIL_THRESHOLD = -3.0

# Categories where regression is unacceptable
DEFAULT_CRITICAL_CATEGORIES = ["specialty_lgbtqia", "lgbtqia_specific"]

# Verdict values
VERDICT_PASS = "PASS"
VERDICT_WARN = "WARN"
VERDICT_FAIL = "FAIL"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PhraseChange:
    """
    Represents a single phrase that changed classification between snapshots.
    """
    phrase_id: str
    text: str
    category: str
    expected_priorities: List[str]
    baseline_severity: Optional[str]
    candidate_severity: Optional[str]
    baseline_passed: bool
    candidate_passed: bool
    baseline_crisis_score: Optional[float]
    candidate_crisis_score: Optional[float]
    change_type: str  # "improved" (fail->pass) or "regressed" (pass->fail)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phrase_id": self.phrase_id,
            "text": self.text,
            "category": self.category,
            "expected_priorities": self.expected_priorities,
            "baseline_severity": self.baseline_severity,
            "candidate_severity": self.candidate_severity,
            "baseline_passed": self.baseline_passed,
            "candidate_passed": self.candidate_passed,
            "baseline_crisis_score": (
                round(self.baseline_crisis_score, 4)
                if self.baseline_crisis_score is not None
                else None
            ),
            "candidate_crisis_score": (
                round(self.candidate_crisis_score, 4)
                if self.candidate_crisis_score is not None
                else None
            ),
            "change_type": self.change_type,
        }


@dataclass
class CategoryDelta:
    """
    Accuracy delta for a single category between baseline and candidate.
    """
    category: str
    baseline_accuracy: float
    candidate_accuracy: float
    delta: float  # candidate - baseline (positive = improvement)
    baseline_total: int
    candidate_total: int
    baseline_passed: int
    candidate_passed: int
    phrases_improved: List[str]  # phrase IDs that went fail->pass
    phrases_regressed: List[str]  # phrase IDs that went pass->fail
    verdict: str  # PASS, WARN, FAIL
    is_critical: bool  # Whether this is a critical category

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category,
            "baseline_accuracy": round(self.baseline_accuracy, 2),
            "candidate_accuracy": round(self.candidate_accuracy, 2),
            "delta": round(self.delta, 2),
            "baseline_total": self.baseline_total,
            "candidate_total": self.candidate_total,
            "baseline_passed": self.baseline_passed,
            "candidate_passed": self.candidate_passed,
            "phrases_improved_count": len(self.phrases_improved),
            "phrases_regressed_count": len(self.phrases_regressed),
            "phrases_improved": self.phrases_improved,
            "phrases_regressed": self.phrases_regressed,
            "verdict": self.verdict,
            "is_critical": self.is_critical,
        }


@dataclass
class LatencyDelta:
    """
    Latency comparison between baseline and candidate.
    """
    baseline_mean_ms: float
    candidate_mean_ms: float
    mean_delta_ms: float
    baseline_p95_ms: float
    candidate_p95_ms: float
    p95_delta_ms: float
    baseline_p99_ms: float
    candidate_p99_ms: float
    p99_delta_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "baseline_mean_ms": round(self.baseline_mean_ms, 2),
            "candidate_mean_ms": round(self.candidate_mean_ms, 2),
            "mean_delta_ms": round(self.mean_delta_ms, 2),
            "baseline_p95_ms": round(self.baseline_p95_ms, 2),
            "candidate_p95_ms": round(self.candidate_p95_ms, 2),
            "p95_delta_ms": round(self.p95_delta_ms, 2),
            "baseline_p99_ms": round(self.baseline_p99_ms, 2),
            "candidate_p99_ms": round(self.candidate_p99_ms, 2),
            "p99_delta_ms": round(self.p99_delta_ms, 2),
        }


@dataclass
class ComparisonResult:
    """
    Complete result of comparing two snapshots.

    This is the primary output of the ComparisonAnalyzerManager and contains
    all deltas, phrase changes, and verdicts for report generation.
    """
    baseline_label: str
    candidate_label: str
    baseline_captured_at: str
    candidate_captured_at: str
    compared_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # Overall metrics
    baseline_overall_accuracy: float = 0.0
    candidate_overall_accuracy: float = 0.0
    overall_delta: float = 0.0

    # Category-level deltas
    category_deltas: Dict[str, CategoryDelta] = field(default_factory=dict)

    # Phrase-level changes
    phrase_changes: List[PhraseChange] = field(default_factory=list)
    total_phrases_improved: int = 0
    total_phrases_regressed: int = 0

    # Latency comparison
    latency_delta: Optional[LatencyDelta] = None

    # Model configuration comparison
    baseline_model_config: Dict[str, Any] = field(default_factory=dict)
    candidate_model_config: Dict[str, Any] = field(default_factory=dict)

    # Verdicts
    overall_verdict: str = VERDICT_PASS
    verdict_reasons: List[str] = field(default_factory=list)
    categories_passed: int = 0
    categories_warned: int = 0
    categories_failed: int = 0

    # Summary
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "baseline_label": self.baseline_label,
            "candidate_label": self.candidate_label,
            "baseline_captured_at": self.baseline_captured_at,
            "candidate_captured_at": self.candidate_captured_at,
            "compared_at": self.compared_at,
            "overall": {
                "baseline_accuracy": round(self.baseline_overall_accuracy, 2),
                "candidate_accuracy": round(self.candidate_overall_accuracy, 2),
                "delta": round(self.overall_delta, 2),
                "verdict": self.overall_verdict,
                "verdict_reasons": self.verdict_reasons,
            },
            "category_deltas": {
                name: delta.to_dict()
                for name, delta in self.category_deltas.items()
            },
            "phrase_changes": {
                "total_improved": self.total_phrases_improved,
                "total_regressed": self.total_phrases_regressed,
                "changes": [c.to_dict() for c in self.phrase_changes],
            },
            "latency": (
                self.latency_delta.to_dict() if self.latency_delta else None
            ),
            "model_configuration": {
                "baseline": self.baseline_model_config,
                "candidate": self.candidate_model_config,
            },
            "verdict_summary": {
                "overall": self.overall_verdict,
                "categories_passed": self.categories_passed,
                "categories_warned": self.categories_warned,
                "categories_failed": self.categories_failed,
            },
            "summary": self.summary,
        }


# =============================================================================
# Comparison Analyzer Manager
# =============================================================================

class ComparisonAnalyzerManager:
    """
    Compares two test run snapshots and calculates comprehensive deltas.

    This manager is the analytical engine of the A/B testing infrastructure.
    It takes a baseline snapshot and a candidate snapshot, then produces
    a ComparisonResult with per-category accuracy deltas, per-phrase
    change tracking, latency comparison, and overall verdicts.

    Attributes:
        config_manager: Configuration manager for threshold settings
        overall_fail_threshold: Overall accuracy drop that triggers FAIL
        category_warn_threshold: Per-category drop that triggers WARN
        critical_category_fail_threshold: Critical category drop for FAIL
        critical_categories: Categories where regression is unacceptable

    Example:
        >>> analyzer = create_comparison_analyzer_manager(config_manager=config)
        >>> result = analyzer.compare(baseline, candidate)
        >>> print(f"Verdict: {result.overall_verdict}")
    """

    def __init__(
        self,
        config_manager: Optional[Any] = None,
        logging_manager: Optional[Any] = None,
    ):
        """
        Initialize the ComparisonAnalyzerManager.

        Args:
            config_manager: Optional ConfigManager for threshold settings
            logging_manager: Optional LoggingConfigManager for custom logger

        Note:
            Use create_comparison_analyzer_manager() factory function instead.
        """
        self._config = config_manager

        # Set up logger
        if logging_manager:
            self._logger = logging_manager.get_logger("comparison_analyzer")
        else:
            self._logger = logger

        # Load thresholds from config
        self._overall_fail = self._get_config_float(
            "comparison", "regression_thresholds.overall_fail",
            DEFAULT_OVERALL_FAIL_THRESHOLD,
        )
        self._category_warn = self._get_config_float(
            "comparison", "regression_thresholds.category_warn",
            DEFAULT_CATEGORY_WARN_THRESHOLD,
        )
        self._critical_fail = self._get_config_float(
            "comparison", "regression_thresholds.critical_category_fail",
            DEFAULT_CRITICAL_CATEGORY_FAIL_THRESHOLD,
        )

        # Load critical categories
        self._critical_categories = set(DEFAULT_CRITICAL_CATEGORIES)
        if self._config:
            try:
                configured = self._config.get(
                    "comparison", "critical_categories"
                )
                if configured and isinstance(configured, list):
                    self._critical_categories = set(configured)
            except Exception:
                pass

        self._logger.info(
            f"✅ ComparisonAnalyzerManager {__version__} initialized "
            f"(overall_fail: {self._overall_fail}%, "
            f"category_warn: {self._category_warn}%, "
            f"critical_fail: {self._critical_fail}%)"
        )

    def _get_config_float(
        self, section: str, key: str, default: float
    ) -> float:
        """Get a float config value with safe fallback."""
        if not self._config:
            return default
        try:
            value = self._config.get(section, key)
            if value is not None:
                return float(value)
        except Exception:
            pass
        return default

    def compare(
        self,
        baseline_snapshot: Any,
        candidate_snapshot: Any,
    ) -> ComparisonResult:
        """
        Compare two snapshots and produce comprehensive deltas.

        Args:
            baseline_snapshot: Snapshot object (the reference/control)
            candidate_snapshot: Snapshot object (the new/experimental)

        Returns:
            ComparisonResult with all deltas, changes, and verdicts

        Example:
            >>> result = analyzer.compare(baseline, candidate)
            >>> print(f"Overall: {result.overall_delta:+.2f}%")
            >>> print(f"Verdict: {result.overall_verdict}")
        """
        self._logger.info(
            f"🔬 Comparing: '{baseline_snapshot.label}' vs "
            f"'{candidate_snapshot.label}'"
        )

        result = ComparisonResult(
            baseline_label=baseline_snapshot.label,
            candidate_label=candidate_snapshot.label,
            baseline_captured_at=baseline_snapshot.captured_at,
            candidate_captured_at=candidate_snapshot.captured_at,
            baseline_overall_accuracy=baseline_snapshot.overall_accuracy,
            candidate_overall_accuracy=candidate_snapshot.overall_accuracy,
            overall_delta=(
                candidate_snapshot.overall_accuracy
                - baseline_snapshot.overall_accuracy
            ),
            baseline_model_config=baseline_snapshot.model_configuration,
            candidate_model_config=candidate_snapshot.model_configuration,
        )

        # Build phrase lookup maps for per-phrase comparison
        baseline_phrases = self._build_phrase_map(
            baseline_snapshot.phrase_results
        )
        candidate_phrases = self._build_phrase_map(
            candidate_snapshot.phrase_results
        )

        # Calculate per-category deltas
        self._calculate_category_deltas(
            baseline_snapshot, candidate_snapshot,
            baseline_phrases, candidate_phrases,
            result,
        )

        # Calculate per-phrase changes
        self._calculate_phrase_changes(
            baseline_phrases, candidate_phrases, result
        )

        # Calculate latency deltas
        self._calculate_latency_delta(
            baseline_snapshot, candidate_snapshot, result
        )

        # Apply verdict logic
        self._apply_verdicts(result)

        # Generate human-readable summary
        result.summary = self._generate_summary(result)

        self._logger.info(
            f"✅ Comparison complete: {result.overall_verdict} "
            f"(delta: {result.overall_delta:+.2f}%, "
            f"{result.total_phrases_improved} improved, "
            f"{result.total_phrases_regressed} regressed)"
        )

        return result

    def _build_phrase_map(
        self, phrase_results: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Build a lookup map from phrase text to phrase result.

        We use the message text as the key since phrase IDs may differ
        between runs (they include indices). This ensures we compare
        the same actual phrases.
        """
        phrase_map = {}
        for phrase in phrase_results:
            text = phrase.get("text", "")
            if text:
                phrase_map[text] = phrase
        return phrase_map

    def _calculate_category_deltas(
        self,
        baseline: Any,
        candidate: Any,
        baseline_phrases: Dict[str, Dict[str, Any]],
        candidate_phrases: Dict[str, Dict[str, Any]],
        result: ComparisonResult,
    ) -> None:
        """Calculate accuracy deltas for each category."""
        all_categories = set(
            list(baseline.category_results.keys())
            + list(candidate.category_results.keys())
        )

        for category in sorted(all_categories):
            baseline_cat = baseline.category_results.get(category, {})
            candidate_cat = candidate.category_results.get(category, {})

            baseline_acc = baseline_cat.get("accuracy", 0.0)
            candidate_acc = candidate_cat.get("accuracy", 0.0)
            delta = candidate_acc - baseline_acc

            is_critical = category in self._critical_categories

            # Find improved and regressed phrases for this category
            improved = []
            regressed = []

            for text, bp in baseline_phrases.items():
                if bp.get("category") != category:
                    continue
                cp = candidate_phrases.get(text)
                if cp is None:
                    continue

                bp_passed = bp.get("passed", False)
                cp_passed = cp.get("passed", False)

                if not bp_passed and cp_passed:
                    improved.append(bp.get("phrase_id", text[:50]))
                elif bp_passed and not cp_passed:
                    regressed.append(bp.get("phrase_id", text[:50]))

            # Determine category verdict
            if delta >= 0:
                cat_verdict = VERDICT_PASS
            elif is_critical and delta < self._critical_fail:
                cat_verdict = VERDICT_FAIL
            elif delta < self._category_warn:
                cat_verdict = VERDICT_WARN
            else:
                cat_verdict = VERDICT_PASS

            result.category_deltas[category] = CategoryDelta(
                category=category,
                baseline_accuracy=baseline_acc,
                candidate_accuracy=candidate_acc,
                delta=delta,
                baseline_total=baseline_cat.get("total", 0),
                candidate_total=candidate_cat.get("total", 0),
                baseline_passed=baseline_cat.get("passed", 0),
                candidate_passed=candidate_cat.get("passed", 0),
                phrases_improved=improved,
                phrases_regressed=regressed,
                verdict=cat_verdict,
                is_critical=is_critical,
            )

    def _calculate_phrase_changes(
        self,
        baseline_phrases: Dict[str, Dict[str, Any]],
        candidate_phrases: Dict[str, Dict[str, Any]],
        result: ComparisonResult,
    ) -> None:
        """Track which individual phrases changed classification."""
        improved_count = 0
        regressed_count = 0

        for text, bp in baseline_phrases.items():
            cp = candidate_phrases.get(text)
            if cp is None:
                continue

            bp_passed = bp.get("passed", False)
            cp_passed = cp.get("passed", False)

            if bp_passed == cp_passed:
                continue

            change_type = "improved" if cp_passed else "regressed"

            if cp_passed:
                improved_count += 1
            else:
                regressed_count += 1

            result.phrase_changes.append(PhraseChange(
                phrase_id=bp.get("phrase_id", ""),
                text=text,
                category=bp.get("category", ""),
                expected_priorities=bp.get("expected_priorities", []),
                baseline_severity=bp.get("actual_severity"),
                candidate_severity=cp.get("actual_severity"),
                baseline_passed=bp_passed,
                candidate_passed=cp_passed,
                baseline_crisis_score=bp.get("crisis_score"),
                candidate_crisis_score=cp.get("crisis_score"),
                change_type=change_type,
            ))

        result.total_phrases_improved = improved_count
        result.total_phrases_regressed = regressed_count

        # Sort: regressions first, then improvements
        result.phrase_changes.sort(
            key=lambda c: (
                0 if c.change_type == "regressed" else 1,
                c.category,
            )
        )

    def _calculate_latency_delta(
        self,
        baseline: Any,
        candidate: Any,
        result: ComparisonResult,
    ) -> None:
        """Calculate latency deltas between snapshots."""
        bp = baseline.performance
        cp = candidate.performance

        b_mean = bp.get("mean_latency_ms", 0.0)
        c_mean = cp.get("mean_latency_ms", 0.0)
        b_p95 = bp.get("p95_latency_ms", 0.0)
        c_p95 = cp.get("p95_latency_ms", 0.0)
        b_p99 = bp.get("p99_latency_ms", 0.0)
        c_p99 = cp.get("p99_latency_ms", 0.0)

        result.latency_delta = LatencyDelta(
            baseline_mean_ms=b_mean,
            candidate_mean_ms=c_mean,
            mean_delta_ms=c_mean - b_mean,
            baseline_p95_ms=b_p95,
            candidate_p95_ms=c_p95,
            p95_delta_ms=c_p95 - b_p95,
            baseline_p99_ms=b_p99,
            candidate_p99_ms=c_p99,
            p99_delta_ms=c_p99 - b_p99,
        )

    def _apply_verdicts(self, result: ComparisonResult) -> None:
        """Apply verdict logic based on thresholds and category results."""
        reasons = []
        passed = 0
        warned = 0
        failed = 0

        # Check overall accuracy
        if result.overall_delta < self._overall_fail:
            reasons.append(
                f"Overall accuracy decreased by "
                f"{abs(result.overall_delta):.2f}% "
                f"(threshold: {abs(self._overall_fail):.1f}%)"
            )

        # Check each category
        for name, delta in result.category_deltas.items():
            if delta.verdict == VERDICT_PASS:
                passed += 1
            elif delta.verdict == VERDICT_WARN:
                warned += 1
                reasons.append(
                    f"Category '{name}' regressed by "
                    f"{abs(delta.delta):.2f}%"
                )
            elif delta.verdict == VERDICT_FAIL:
                failed += 1
                reasons.append(
                    f"Critical category '{name}' regressed by "
                    f"{abs(delta.delta):.2f}%"
                )

        result.categories_passed = passed
        result.categories_warned = warned
        result.categories_failed = failed
        result.verdict_reasons = reasons

        # Determine overall verdict
        if failed > 0 or result.overall_delta < self._overall_fail:
            result.overall_verdict = VERDICT_FAIL
        elif warned > 0:
            result.overall_verdict = VERDICT_WARN
        else:
            result.overall_verdict = VERDICT_PASS

    def _generate_summary(self, result: ComparisonResult) -> str:
        """Generate a human-readable summary of the comparison."""
        lines = []

        direction = "improved" if result.overall_delta >= 0 else "regressed"
        lines.append(
            f"Overall accuracy {direction} by "
            f"{abs(result.overall_delta):.2f}% "
            f"({result.baseline_overall_accuracy:.1f}% -> "
            f"{result.candidate_overall_accuracy:.1f}%)"
        )

        if result.total_phrases_improved or result.total_phrases_regressed:
            lines.append(
                f"Phrases: {result.total_phrases_improved} improved, "
                f"{result.total_phrases_regressed} regressed"
            )

        for name, delta in result.category_deltas.items():
            if delta.verdict != VERDICT_PASS:
                lines.append(
                    f"  Warning: {name}: {delta.delta:+.2f}% "
                    f"({delta.verdict})"
                )

        emoji = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}
        lines.append(
            f"Verdict: {emoji.get(result.overall_verdict, '?')} "
            f"{result.overall_verdict}"
        )

        return "\n".join(lines)

    def get_thresholds(self) -> Dict[str, Any]:
        """Get current threshold configuration."""
        return {
            "overall_fail": self._overall_fail,
            "category_warn": self._category_warn,
            "critical_category_fail": self._critical_fail,
            "critical_categories": list(self._critical_categories),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get analyzer status information."""
        return {
            "version": __version__,
            "thresholds": self.get_thresholds(),
        }


# =============================================================================
# Factory Function - Clean Architecture v5.2.3 Compliance (Rule #1)
# =============================================================================

def create_comparison_analyzer_manager(
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
) -> ComparisonAnalyzerManager:
    """
    Factory function for ComparisonAnalyzerManager (Clean Architecture v5.2.3).

    This is the ONLY way to create a ComparisonAnalyzerManager instance.
    Direct instantiation should be avoided in production code.

    Args:
        config_manager: Optional ConfigManager for threshold settings
        logging_manager: Optional LoggingConfigManager for custom logger

    Returns:
        Configured ComparisonAnalyzerManager instance

    Example:
        >>> analyzer = create_comparison_analyzer_manager(
        ...     config_manager=config,
        ...     logging_manager=logging_mgr,
        ... )
        >>> result = analyzer.compare(baseline, candidate)
    """
    logger.debug("Creating ComparisonAnalyzerManager")

    return ComparisonAnalyzerManager(
        config_manager=config_manager,
        logging_manager=logging_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
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
