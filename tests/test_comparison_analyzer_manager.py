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
Unit Tests: ComparisonAnalyzerManager
----------------------------------------------------------------------------
FILE VERSION: v5.0-6-6.5-1
LAST MODIFIED: 2026-02-07
PHASE: Phase 6 - A/B Testing Infrastructure (v5.1 Migration Phase 1)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

Tests for snapshot comparison, category deltas, phrase change tracking,
latency comparison, and verdict logic. All tests use mock Snapshot objects
with controlled data - no live server or file I/O needed.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.managers.comparison_analyzer_manager import (
    ComparisonAnalyzerManager,
    create_comparison_analyzer_manager,
    ComparisonResult,
    CategoryDelta,
    PhraseChange,
    LatencyDelta,
    VERDICT_PASS,
    VERDICT_WARN,
    VERDICT_FAIL,
)


# Module version
__version__ = "v5.0-6-6.5-1"


# =============================================================================
# Mock Snapshot Class
# =============================================================================

@dataclass
class MockSnapshot:
    """
    Simulates a Snapshot object for comparison testing.

    Provides the same interface that ComparisonAnalyzerManager.compare()
    expects: label, captured_at, overall_accuracy, category_results,
    phrase_results, performance, model_configuration.
    """
    label: str = "v5.0_baseline"
    captured_at: str = "2026-02-07T12:00:00"
    overall_accuracy: float = 95.0
    category_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    phrase_results: List[Dict[str, Any]] = field(default_factory=list)
    performance: Dict[str, float] = field(default_factory=dict)
    model_configuration: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Test Data Builders
# =============================================================================

def _build_phrase(
    phrase_id: str,
    text: str,
    category: str,
    passed: bool,
    crisis_score: float,
    severity: str = "HIGH",
    expected_priorities: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Helper to build a phrase result dict."""
    return {
        "phrase_id": phrase_id,
        "text": text,
        "category": category,
        "subcategory": "general",
        "expected_priorities": expected_priorities or ["HIGH", "CRITICAL"],
        "actual_severity": severity,
        "passed": passed,
        "crisis_score": crisis_score,
        "confidence": 0.90,
        "latency_ms": 45.0,
        "status": "passed" if passed else "failed",
        "failure_reason": None if passed else "Misclassified",
    }


def _build_category(
    accuracy: float,
    total: int,
    passed: int,
) -> Dict[str, Any]:
    """Helper to build a category result dict."""
    return {
        "accuracy": accuracy,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "errors": 0,
        "target_accuracy": 90.0,
        "threshold_status": "met" if accuracy >= 90.0 else "not_met",
    }


def _build_performance(
    mean: float = 48.0,
    p95: float = 120.0,
    p99: float = 185.0,
) -> Dict[str, float]:
    """Helper to build a performance metrics dict."""
    return {
        "mean_latency_ms": mean,
        "p95_latency_ms": p95,
        "p99_latency_ms": p99,
    }


def _build_baseline_snapshot() -> MockSnapshot:
    """Build a standard baseline snapshot for comparison tests."""
    return MockSnapshot(
        label="v5.0_baseline",
        captured_at="2026-02-07T12:00:00",
        overall_accuracy=95.0,
        category_results={
            "crisis_high": _build_category(accuracy=96.0, total=50, passed=48),
            "safe_general": _build_category(accuracy=94.0, total=50, passed=47),
            "edge_case": _build_category(accuracy=85.0, total=20, passed=17),
        },
        phrase_results=[
            _build_phrase("c001", "I want to end it all", "crisis_high", True, 0.92),
            _build_phrase("c002", "Nobody would miss me", "crisis_high", True, 0.88),
            _build_phrase("c003", "I can't go on anymore", "crisis_high", False, 0.45),
            _build_phrase("s001", "Having a great day gaming", "safe_general", True, 0.05),
            _build_phrase("s002", "Anyone up for some Overwatch?", "safe_general", True, 0.03),
            _build_phrase("s003", "This game is killing me", "safe_general", True, 0.08),
            _build_phrase("e001", "I'm dead tired", "edge_case", False, 0.45),
            _build_phrase("e002", "That joke slayed me", "edge_case", True, 0.12),
        ],
        performance=_build_performance(mean=48.0, p95=120.0, p99=185.0),
        model_configuration={
            "bart": {"weight": 0.50, "enabled": True},
            "sentiment": {"weight": 0.25, "enabled": True},
        },
    )


def _build_improved_candidate() -> MockSnapshot:
    """Build a candidate snapshot that improves over baseline."""
    return MockSnapshot(
        label="v5.1_candidate",
        captured_at="2026-02-07T14:00:00",
        overall_accuracy=97.0,
        category_results={
            "crisis_high": _build_category(accuracy=98.0, total=50, passed=49),
            "safe_general": _build_category(accuracy=96.0, total=50, passed=48),
            "edge_case": _build_category(accuracy=90.0, total=20, passed=18),
        },
        phrase_results=[
            _build_phrase("c001", "I want to end it all", "crisis_high", True, 0.95),
            _build_phrase("c002", "Nobody would miss me", "crisis_high", True, 0.91),
            _build_phrase("c003", "I can't go on anymore", "crisis_high", True, 0.82),  # fixed!
            _build_phrase("s001", "Having a great day gaming", "safe_general", True, 0.03),
            _build_phrase("s002", "Anyone up for some Overwatch?", "safe_general", True, 0.02),
            _build_phrase("s003", "This game is killing me", "safe_general", True, 0.06),
            _build_phrase("e001", "I'm dead tired", "edge_case", True, 0.10),  # fixed!
            _build_phrase("e002", "That joke slayed me", "edge_case", True, 0.08),
        ],
        performance=_build_performance(mean=42.0, p95=110.0, p99=170.0),
        model_configuration={
            "bart": {"weight": 0.50, "enabled": True},
            "sentiment": {"weight": 0.25, "enabled": True},
        },
    )


def _build_regressed_candidate() -> MockSnapshot:
    """Build a candidate snapshot that regresses from baseline."""
    return MockSnapshot(
        label="v5.1_regressed",
        captured_at="2026-02-07T14:00:00",
        overall_accuracy=88.0,
        category_results={
            "crisis_high": _build_category(accuracy=90.0, total=50, passed=45),
            "safe_general": _build_category(accuracy=86.0, total=50, passed=43),
            "edge_case": _build_category(accuracy=80.0, total=20, passed=16),
        },
        phrase_results=[
            _build_phrase("c001", "I want to end it all", "crisis_high", True, 0.90),
            _build_phrase("c002", "Nobody would miss me", "crisis_high", False, 0.42),  # regressed!
            _build_phrase("c003", "I can't go on anymore", "crisis_high", False, 0.35),
            _build_phrase("s001", "Having a great day gaming", "safe_general", True, 0.04),
            _build_phrase("s002", "Anyone up for some Overwatch?", "safe_general", False, 0.55),  # regressed!
            _build_phrase("s003", "This game is killing me", "safe_general", False, 0.62),  # regressed!
            _build_phrase("e001", "I'm dead tired", "edge_case", False, 0.50),
            _build_phrase("e002", "That joke slayed me", "edge_case", False, 0.48),  # regressed!
        ],
        performance=_build_performance(mean=55.0, p95=140.0, p99=210.0),
        model_configuration={
            "bart": {"weight": 0.50, "enabled": True},
            "sentiment": {"weight": 0.25, "enabled": True},
        },
    )


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def analyzer():
    """Create a ComparisonAnalyzerManager with defaults (no config)."""
    return create_comparison_analyzer_manager()


@pytest.fixture
def baseline():
    """Standard baseline snapshot."""
    return _build_baseline_snapshot()


@pytest.fixture
def improved_candidate():
    """Candidate snapshot that improves over baseline."""
    return _build_improved_candidate()


@pytest.fixture
def regressed_candidate():
    """Candidate snapshot that regresses from baseline."""
    return _build_regressed_candidate()


@pytest.fixture
def identical_candidate(baseline):
    """Candidate snapshot identical to baseline (zero delta)."""
    snap = _build_baseline_snapshot()
    snap.label = "v5.1_identical"
    snap.captured_at = "2026-02-07T14:00:00"
    return snap


# =============================================================================
# Test: Factory Function
# =============================================================================

class TestComparisonAnalyzerCreation:
    """Tests for ComparisonAnalyzerManager instantiation and factory."""

    @pytest.mark.unit
    def test_factory_returns_instance(self):
        """Factory function returns a valid ComparisonAnalyzerManager."""
        mgr = create_comparison_analyzer_manager()
        assert isinstance(mgr, ComparisonAnalyzerManager)

    @pytest.mark.unit
    def test_factory_with_none_config(self):
        """Factory function works with None config_manager."""
        mgr = create_comparison_analyzer_manager(config_manager=None)
        assert isinstance(mgr, ComparisonAnalyzerManager)

    @pytest.mark.unit
    def test_get_status_keys(self, analyzer):
        """get_status returns expected keys."""
        status = analyzer.get_status()
        assert "version" in status
        assert "thresholds" in status

    @pytest.mark.unit
    def test_get_thresholds_keys(self, analyzer):
        """get_thresholds returns all threshold keys."""
        thresholds = analyzer.get_thresholds()
        assert "overall_fail" in thresholds
        assert "category_warn" in thresholds
        assert "critical_category_fail" in thresholds
        assert "critical_categories" in thresholds

    @pytest.mark.unit
    def test_default_thresholds(self, analyzer):
        """Default thresholds match module constants."""
        thresholds = analyzer.get_thresholds()
        assert thresholds["overall_fail"] == -2.0
        assert thresholds["category_warn"] == -5.0
        assert thresholds["critical_category_fail"] == -3.0


# =============================================================================
# Test: Compare - Result Structure
# =============================================================================

class TestCompareResultStructure:
    """Tests that compare() returns a well-formed ComparisonResult."""

    @pytest.mark.unit
    def test_compare_returns_comparison_result(
        self, analyzer, baseline, improved_candidate
    ):
        """compare() returns a ComparisonResult instance."""
        result = analyzer.compare(baseline, improved_candidate)
        assert isinstance(result, ComparisonResult)

    @pytest.mark.unit
    def test_compare_labels_match(
        self, analyzer, baseline, improved_candidate
    ):
        """Result contains correct baseline and candidate labels."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.baseline_label == "v5.0_baseline"
        assert result.candidate_label == "v5.1_candidate"

    @pytest.mark.unit
    def test_compare_timestamps(
        self, analyzer, baseline, improved_candidate
    ):
        """Result contains snapshot timestamps and comparison timestamp."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.baseline_captured_at == "2026-02-07T12:00:00"
        assert result.candidate_captured_at == "2026-02-07T14:00:00"
        assert result.compared_at  # Non-empty

    @pytest.mark.unit
    def test_compare_has_category_deltas(
        self, analyzer, baseline, improved_candidate
    ):
        """Result contains category deltas for all tested categories."""
        result = analyzer.compare(baseline, improved_candidate)
        assert "crisis_high" in result.category_deltas
        assert "safe_general" in result.category_deltas
        assert "edge_case" in result.category_deltas

    @pytest.mark.unit
    def test_compare_has_latency_delta(
        self, analyzer, baseline, improved_candidate
    ):
        """Result contains latency delta."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.latency_delta is not None
        assert isinstance(result.latency_delta, LatencyDelta)

    @pytest.mark.unit
    def test_compare_has_model_config(
        self, analyzer, baseline, improved_candidate
    ):
        """Result contains model configuration from both snapshots."""
        result = analyzer.compare(baseline, improved_candidate)
        assert "bart" in result.baseline_model_config
        assert "bart" in result.candidate_model_config

    @pytest.mark.unit
    def test_compare_has_summary(
        self, analyzer, baseline, improved_candidate
    ):
        """Result contains a non-empty human-readable summary."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.summary
        assert len(result.summary) > 0


# =============================================================================
# Test: Overall Accuracy Deltas
# =============================================================================

class TestOverallAccuracyDelta:
    """Tests for overall accuracy delta calculation."""

    @pytest.mark.unit
    def test_improved_positive_delta(
        self, analyzer, baseline, improved_candidate
    ):
        """Improved candidate produces positive overall delta."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.overall_delta == pytest.approx(2.0, abs=0.01)
        assert result.baseline_overall_accuracy == 95.0
        assert result.candidate_overall_accuracy == 97.0

    @pytest.mark.unit
    def test_regressed_negative_delta(
        self, analyzer, baseline, regressed_candidate
    ):
        """Regressed candidate produces negative overall delta."""
        result = analyzer.compare(baseline, regressed_candidate)
        assert result.overall_delta == pytest.approx(-7.0, abs=0.01)

    @pytest.mark.unit
    def test_identical_zero_delta(
        self, analyzer, baseline, identical_candidate
    ):
        """Identical snapshots produce zero overall delta."""
        result = analyzer.compare(baseline, identical_candidate)
        assert result.overall_delta == pytest.approx(0.0, abs=0.01)


# =============================================================================
# Test: Category Deltas
# =============================================================================

class TestCategoryDeltas:
    """Tests for per-category accuracy delta calculation."""

    @pytest.mark.unit
    def test_category_delta_values(
        self, analyzer, baseline, improved_candidate
    ):
        """Category deltas are correctly calculated."""
        result = analyzer.compare(baseline, improved_candidate)
        crisis = result.category_deltas["crisis_high"]
        assert crisis.baseline_accuracy == 96.0
        assert crisis.candidate_accuracy == 98.0
        assert crisis.delta == pytest.approx(2.0, abs=0.01)

    @pytest.mark.unit
    def test_category_delta_is_category_delta_type(
        self, analyzer, baseline, improved_candidate
    ):
        """Each category delta is a CategoryDelta instance."""
        result = analyzer.compare(baseline, improved_candidate)
        for delta in result.category_deltas.values():
            assert isinstance(delta, CategoryDelta)

    @pytest.mark.unit
    def test_category_tracks_totals(
        self, analyzer, baseline, improved_candidate
    ):
        """Category deltas track total and passed counts."""
        result = analyzer.compare(baseline, improved_candidate)
        crisis = result.category_deltas["crisis_high"]
        assert crisis.baseline_total == 50
        assert crisis.candidate_total == 50
        assert crisis.baseline_passed == 48
        assert crisis.candidate_passed == 49

    @pytest.mark.unit
    def test_regressed_category_negative_delta(
        self, analyzer, baseline, regressed_candidate
    ):
        """Regressed categories show negative deltas."""
        result = analyzer.compare(baseline, regressed_candidate)
        safe = result.category_deltas["safe_general"]
        assert safe.delta < 0

    @pytest.mark.unit
    def test_all_categories_covered(
        self, analyzer, baseline, improved_candidate
    ):
        """All categories from both snapshots are represented."""
        result = analyzer.compare(baseline, improved_candidate)
        assert len(result.category_deltas) == 3

    @pytest.mark.unit
    def test_category_delta_to_dict(
        self, analyzer, baseline, improved_candidate
    ):
        """CategoryDelta.to_dict() returns expected keys."""
        result = analyzer.compare(baseline, improved_candidate)
        crisis = result.category_deltas["crisis_high"]
        d = crisis.to_dict()
        assert "category" in d
        assert "baseline_accuracy" in d
        assert "candidate_accuracy" in d
        assert "delta" in d
        assert "verdict" in d
        assert "is_critical" in d
        assert "phrases_improved_count" in d
        assert "phrases_regressed_count" in d


# =============================================================================
# Test: Phrase Change Tracking
# =============================================================================

class TestPhraseChangeTracking:
    """Tests for per-phrase change detection between snapshots."""

    @pytest.mark.unit
    def test_improved_phrases_detected(
        self, analyzer, baseline, improved_candidate
    ):
        """Phrases that went fail→pass are detected as improvements."""
        result = analyzer.compare(baseline, improved_candidate)
        improved = [
            c for c in result.phrase_changes if c.change_type == "improved"
        ]
        # "I can't go on anymore" (c003) and "I'm dead tired" (e001) fixed
        assert len(improved) == 2
        improved_texts = {c.text for c in improved}
        assert "I can't go on anymore" in improved_texts
        assert "I'm dead tired" in improved_texts

    @pytest.mark.unit
    def test_regressed_phrases_detected(
        self, analyzer, baseline, regressed_candidate
    ):
        """Phrases that went pass→fail are detected as regressions."""
        result = analyzer.compare(baseline, regressed_candidate)
        regressed = [
            c for c in result.phrase_changes if c.change_type == "regressed"
        ]
        # "Nobody would miss me", "Anyone up for Overwatch?",
        # "This game is killing me", "That joke slayed me" all regressed
        assert len(regressed) == 4

    @pytest.mark.unit
    def test_phrase_change_counts(
        self, analyzer, baseline, improved_candidate
    ):
        """Total improved/regressed counts are correct."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.total_phrases_improved == 2
        assert result.total_phrases_regressed == 0

    @pytest.mark.unit
    def test_regressed_counts(
        self, analyzer, baseline, regressed_candidate
    ):
        """Total regressed count is correct for regression scenario."""
        result = analyzer.compare(baseline, regressed_candidate)
        assert result.total_phrases_regressed == 4

    @pytest.mark.unit
    def test_identical_no_changes(
        self, analyzer, baseline, identical_candidate
    ):
        """Identical snapshots produce no phrase changes."""
        result = analyzer.compare(baseline, identical_candidate)
        assert len(result.phrase_changes) == 0
        assert result.total_phrases_improved == 0
        assert result.total_phrases_regressed == 0

    @pytest.mark.unit
    def test_phrase_change_is_phrase_change_type(
        self, analyzer, baseline, improved_candidate
    ):
        """Each phrase change is a PhraseChange instance."""
        result = analyzer.compare(baseline, improved_candidate)
        for change in result.phrase_changes:
            assert isinstance(change, PhraseChange)

    @pytest.mark.unit
    def test_phrase_change_has_scores(
        self, analyzer, baseline, improved_candidate
    ):
        """Phrase changes include baseline and candidate scores."""
        result = analyzer.compare(baseline, improved_candidate)
        for change in result.phrase_changes:
            assert change.baseline_crisis_score is not None
            assert change.candidate_crisis_score is not None

    @pytest.mark.unit
    def test_phrase_change_to_dict(
        self, analyzer, baseline, improved_candidate
    ):
        """PhraseChange.to_dict() returns expected keys."""
        result = analyzer.compare(baseline, improved_candidate)
        assert len(result.phrase_changes) > 0
        d = result.phrase_changes[0].to_dict()
        assert "phrase_id" in d
        assert "text" in d
        assert "category" in d
        assert "change_type" in d
        assert "baseline_crisis_score" in d
        assert "candidate_crisis_score" in d

    @pytest.mark.unit
    def test_phrase_changes_sorted_regressions_first(
        self, analyzer, baseline, regressed_candidate
    ):
        """Phrase changes are sorted: regressions before improvements."""
        result = analyzer.compare(baseline, regressed_candidate)
        if len(result.phrase_changes) >= 2:
            change_types = [c.change_type for c in result.phrase_changes]
            # All regressions should come before any improvements
            regressed_done = False
            for ct in change_types:
                if ct == "improved":
                    regressed_done = True
                if regressed_done and ct == "regressed":
                    pytest.fail("Regressions not sorted before improvements")


# =============================================================================
# Test: Latency Comparison
# =============================================================================

class TestLatencyComparison:
    """Tests for latency delta calculation."""

    @pytest.mark.unit
    def test_latency_mean_delta(
        self, analyzer, baseline, improved_candidate
    ):
        """Mean latency delta is correctly calculated."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.latency_delta.baseline_mean_ms == 48.0
        assert result.latency_delta.candidate_mean_ms == 42.0
        assert result.latency_delta.mean_delta_ms == pytest.approx(-6.0)

    @pytest.mark.unit
    def test_latency_p95_delta(
        self, analyzer, baseline, improved_candidate
    ):
        """P95 latency delta is correctly calculated."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.latency_delta.p95_delta_ms == pytest.approx(-10.0)

    @pytest.mark.unit
    def test_latency_p99_delta(
        self, analyzer, baseline, improved_candidate
    ):
        """P99 latency delta is correctly calculated."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.latency_delta.p99_delta_ms == pytest.approx(-15.0)

    @pytest.mark.unit
    def test_latency_regression(
        self, analyzer, baseline, regressed_candidate
    ):
        """Regressed candidate shows positive (slower) latency deltas."""
        result = analyzer.compare(baseline, regressed_candidate)
        assert result.latency_delta.mean_delta_ms > 0
        assert result.latency_delta.p95_delta_ms > 0
        assert result.latency_delta.p99_delta_ms > 0

    @pytest.mark.unit
    def test_latency_delta_to_dict(
        self, analyzer, baseline, improved_candidate
    ):
        """LatencyDelta.to_dict() returns all expected keys."""
        result = analyzer.compare(baseline, improved_candidate)
        d = result.latency_delta.to_dict()
        expected_keys = [
            "baseline_mean_ms", "candidate_mean_ms", "mean_delta_ms",
            "baseline_p95_ms", "candidate_p95_ms", "p95_delta_ms",
            "baseline_p99_ms", "candidate_p99_ms", "p99_delta_ms",
        ]
        for key in expected_keys:
            assert key in d


# =============================================================================
# Test: Verdict Logic
# =============================================================================

class TestVerdictLogic:
    """Tests for PASS / WARN / FAIL verdict determination."""

    @pytest.mark.unit
    def test_improved_gets_pass(
        self, analyzer, baseline, improved_candidate
    ):
        """Improved candidate receives PASS verdict."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.overall_verdict == VERDICT_PASS

    @pytest.mark.unit
    def test_regressed_gets_fail(
        self, analyzer, baseline, regressed_candidate
    ):
        """Heavily regressed candidate receives FAIL verdict."""
        result = analyzer.compare(baseline, regressed_candidate)
        assert result.overall_verdict == VERDICT_FAIL

    @pytest.mark.unit
    def test_identical_gets_pass(
        self, analyzer, baseline, identical_candidate
    ):
        """Identical candidate receives PASS verdict."""
        result = analyzer.compare(baseline, identical_candidate)
        assert result.overall_verdict == VERDICT_PASS

    @pytest.mark.unit
    def test_fail_has_reasons(
        self, analyzer, baseline, regressed_candidate
    ):
        """FAIL verdict includes reasons."""
        result = analyzer.compare(baseline, regressed_candidate)
        assert len(result.verdict_reasons) > 0

    @pytest.mark.unit
    def test_pass_no_reasons(
        self, analyzer, baseline, improved_candidate
    ):
        """PASS verdict has no failure reasons."""
        result = analyzer.compare(baseline, improved_candidate)
        assert len(result.verdict_reasons) == 0

    @pytest.mark.unit
    def test_category_verdict_counts(
        self, analyzer, baseline, improved_candidate
    ):
        """Verdict summary tracks pass/warn/fail category counts."""
        result = analyzer.compare(baseline, improved_candidate)
        assert result.categories_passed == 3
        assert result.categories_warned == 0
        assert result.categories_failed == 0

    @pytest.mark.unit
    def test_overall_fail_threshold_triggers(self, analyzer):
        """Overall accuracy drop beyond threshold triggers FAIL."""
        baseline = MockSnapshot(
            label="base", overall_accuracy=95.0,
            category_results={"crisis_high": _build_category(95.0, 50, 47)},
            phrase_results=[], performance=_build_performance(),
        )
        candidate = MockSnapshot(
            label="cand", overall_accuracy=92.0,  # -3.0% > -2.0 threshold
            category_results={"crisis_high": _build_category(92.0, 50, 46)},
            phrase_results=[], performance=_build_performance(),
        )
        result = analyzer.compare(baseline, candidate)
        assert result.overall_verdict == VERDICT_FAIL


    @pytest.mark.unit
    def test_category_warn_threshold_triggers(self, analyzer):
        """Category regression beyond warn threshold triggers WARN."""
        baseline = MockSnapshot(
            label="base", overall_accuracy=95.0,
            category_results={
                "safe_general": _build_category(95.0, 50, 47),
            },
            phrase_results=[], performance=_build_performance(),
        )
        candidate = MockSnapshot(
            label="cand", overall_accuracy=95.0,  # Overall same
            category_results={
                "safe_general": _build_category(89.0, 50, 44),  # -6% > -5 warn
            },
            phrase_results=[], performance=_build_performance(),
        )
        result = analyzer.compare(baseline, candidate)
        assert result.overall_verdict == VERDICT_WARN

    @pytest.mark.unit
    def test_critical_category_fail(self, analyzer):
        """Regression in a critical category triggers FAIL."""
        baseline = MockSnapshot(
            label="base", overall_accuracy=95.0,
            category_results={
                "specialty_lgbtqia": _build_category(96.0, 50, 48),
            },
            phrase_results=[], performance=_build_performance(),
        )
        candidate = MockSnapshot(
            label="cand", overall_accuracy=95.0,
            category_results={
                # -4% > -3 critical threshold
                "specialty_lgbtqia": _build_category(92.0, 50, 46),
            },
            phrase_results=[], performance=_build_performance(),
        )
        result = analyzer.compare(baseline, candidate)
        # specialty_lgbtqia is in DEFAULT_CRITICAL_CATEGORIES
        crisis_delta = result.category_deltas["specialty_lgbtqia"]
        assert crisis_delta.is_critical is True
        assert crisis_delta.verdict == VERDICT_FAIL
        assert result.overall_verdict == VERDICT_FAIL


# =============================================================================
# Test: ComparisonResult Serialization
# =============================================================================

class TestComparisonResultSerialization:
    """Tests for ComparisonResult.to_dict() serialization."""

    @pytest.mark.unit
    def test_to_dict_structure(
        self, analyzer, baseline, improved_candidate
    ):
        """to_dict() returns expected top-level keys."""
        result = analyzer.compare(baseline, improved_candidate)
        d = result.to_dict()
        expected_keys = [
            "baseline_label", "candidate_label",
            "baseline_captured_at", "candidate_captured_at",
            "compared_at", "overall", "category_deltas",
            "phrase_changes", "latency", "model_configuration",
            "verdict_summary", "summary",
        ]
        for key in expected_keys:
            assert key in d, f"Missing key: {key}"

    @pytest.mark.unit
    def test_to_dict_overall_section(
        self, analyzer, baseline, improved_candidate
    ):
        """to_dict() overall section has correct values."""
        result = analyzer.compare(baseline, improved_candidate)
        d = result.to_dict()["overall"]
        assert d["baseline_accuracy"] == 95.0
        assert d["candidate_accuracy"] == 97.0
        assert d["delta"] == pytest.approx(2.0)
        assert d["verdict"] == VERDICT_PASS

    @pytest.mark.unit
    def test_to_dict_phrase_changes_section(
        self, analyzer, baseline, improved_candidate
    ):
        """to_dict() phrase_changes section has counts and list."""
        result = analyzer.compare(baseline, improved_candidate)
        d = result.to_dict()["phrase_changes"]
        assert d["total_improved"] == 2
        assert d["total_regressed"] == 0
        assert isinstance(d["changes"], list)
        assert len(d["changes"]) == 2

    @pytest.mark.unit
    def test_to_dict_verdict_summary(
        self, analyzer, baseline, improved_candidate
    ):
        """to_dict() verdict_summary has all fields."""
        result = analyzer.compare(baseline, improved_candidate)
        d = result.to_dict()["verdict_summary"]
        assert d["overall"] == VERDICT_PASS
        assert d["categories_passed"] == 3
        assert d["categories_warned"] == 0
        assert d["categories_failed"] == 0

    @pytest.mark.unit
    def test_to_dict_latency_present(
        self, analyzer, baseline, improved_candidate
    ):
        """to_dict() latency section is populated."""
        result = analyzer.compare(baseline, improved_candidate)
        d = result.to_dict()["latency"]
        assert d is not None
        assert "mean_delta_ms" in d

