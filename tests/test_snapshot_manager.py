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
Unit Tests: SnapshotManager
----------------------------------------------------------------------------
FILE VERSION: v5.0-6-6.4-1
LAST MODIFIED: 2026-02-07
PHASE: Phase 6 - A/B Testing Infrastructure (v5.1 Migration Phase 1)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

Tests for snapshot capture, loading, listing, validation, and deletion.
All tests use temporary directories and mock objects - no live server needed.
"""

import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.managers.snapshot_manager import (
    SnapshotManager,
    create_snapshot_manager,
    Snapshot,
    SnapshotMetadata,
    SNAPSHOT_SCHEMA_VERSION,
    REQUIRED_SNAPSHOT_KEYS,
    REQUIRED_METADATA_KEYS,
)


# Module version
__version__ = "v5.0-6-6.4-1"


# =============================================================================
# Mock Data Classes
# =============================================================================

@dataclass
class MockTestResult:
    """Simulates a TestResult for snapshot capture."""
    phrase_id: str = "test_001"
    message: str = "I need help right now"
    category: str = "crisis_high"
    subcategory: str = "suicidal_ideation"
    expected_priorities: List[str] = field(default_factory=lambda: ["HIGH", "CRITICAL"])
    actual_severity: str = "HIGH"
    passed: bool = True
    failed: bool = False
    crisis_score: float = 0.85
    confidence: float = 0.92
    response_time_ms: float = 45.2
    status: str = "passed"
    failure_reason: Optional[str] = None


@dataclass
class MockTestRunSummary:
    """Simulates a TestRunSummary for snapshot capture."""
    run_id: str = "test-run-001"
    overall_accuracy: float = 95.5
    total_tests: int = 100
    passed_tests: int = 95
    failed_tests: int = 4
    error_tests: int = 1
    skipped_tests: int = 0
    duration_seconds: float = 12.5
    categories_tested: List[str] = field(
        default_factory=lambda: ["crisis_high", "safe_general", "edge_case"]
    )
    average_response_time_ms: float = 48.3
    p95_response_time_ms: float = 120.5
    nlp_server_info: Optional[Dict[str, Any]] = None
    results: List[MockTestResult] = field(default_factory=list)


@dataclass
class MockLatencyMetrics:
    """Simulates latency metrics from AnalysisResult."""
    p99_ms: float = 185.0


@dataclass
class MockCategoryMetrics:
    """Simulates per-category metrics from AnalysisResult."""
    accuracy: float = 96.0
    total: int = 50
    passed: int = 48
    failed: int = 2
    errors: int = 0
    target_accuracy: float = 90.0
    threshold_status: str = "met"

    def __post_init__(self):
        """Ensure threshold_status has a .value for enum compat."""
        if isinstance(self.threshold_status, str):
            self.threshold_status = type(
                "MockEnum", (), {"value": self.threshold_status}
            )()


@dataclass
class MockAnalysisResult:
    """Simulates an AnalysisResult for snapshot capture."""
    category_metrics: Dict[str, MockCategoryMetrics] = field(
        default_factory=lambda: {
            "crisis_high": MockCategoryMetrics(accuracy=96.0, total=50, passed=48, failed=2),
            "safe_general": MockCategoryMetrics(accuracy=98.0, total=30, passed=29, failed=1),
            "edge_case": MockCategoryMetrics(accuracy=85.0, total=20, passed=17, failed=3),
        }
    )
    latency_metrics: MockLatencyMetrics = field(default_factory=MockLatencyMetrics)

    def to_dict(self) -> Dict[str, Any]:
        """Serialization stub."""
        return {
            "overall_accuracy": 95.5,
            "category_count": len(self.category_metrics),
        }


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    """Create a temporary snapshot directory."""
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()
    return snapshot_dir


@pytest.fixture
def snapshot_manager(tmp_snapshot_dir):
    """Create a SnapshotManager with temporary directory."""
    return create_snapshot_manager(snapshot_dir=str(tmp_snapshot_dir))


@pytest.fixture
def mock_test_run():
    """Create a mock TestRunSummary with sample results."""
    results = [
        MockTestResult(
            phrase_id="crisis_001", message="I want to end it all",
            category="crisis_high", passed=True, crisis_score=0.92,
        ),
        MockTestResult(
            phrase_id="crisis_002", message="Nobody would miss me",
            category="crisis_high", passed=True, crisis_score=0.88,
        ),
        MockTestResult(
            phrase_id="safe_001", message="Having a great day gaming",
            category="safe_general", passed=True, crisis_score=0.05,
        ),
        MockTestResult(
            phrase_id="edge_001", message="I'm dead tired",
            category="edge_case", passed=False, crisis_score=0.45,
            failed=True, failure_reason="False positive: colloquial expression",
        ),
    ]
    return MockTestRunSummary(
        total_tests=4, passed_tests=3, failed_tests=1, error_tests=0,
        overall_accuracy=75.0, results=results,
    )


@pytest.fixture
def mock_analysis():
    """Create a mock AnalysisResult."""
    return MockAnalysisResult()


def _create_sample_snapshot_data(
    label: str = "v5.0_baseline",
    accuracy: float = 95.5,
) -> Dict[str, Any]:
    """Helper to create valid snapshot JSON data."""
    return {
        "_metadata": {
            "snapshot_version": SNAPSHOT_SCHEMA_VERSION,
            "captured_at": "2026-02-07T12:00:00",
            "ash_nlp_version": "v5.0",
            "ash_nlp_git_commit": "abc123",
            "ash_thrash_version": "v5.0-6-6.1-1",
            "label": label,
            "description": "Test snapshot",
            "run_id": "test-run-001",
        },
        "model_configuration": {
            "bart": {"weight": 0.50, "enabled": True},
            "sentiment": {"weight": 0.25, "enabled": True},
        },
        "results_summary": {
            "overall_accuracy": accuracy,
            "total_phrases_tested": 100,
            "total_passed": int(accuracy),
            "total_failed": 100 - int(accuracy),
            "total_errors": 0,
            "total_skipped": 0,
            "duration_seconds": 12.5,
            "categories_tested": ["crisis_high", "safe_general"],
        },
        "category_results": {
            "crisis_high": {
                "accuracy": 96.0, "total": 50, "passed": 48,
                "failed": 2, "errors": 0, "target_accuracy": 90.0,
                "threshold_status": "met",
            },
            "safe_general": {
                "accuracy": 95.0, "total": 50, "passed": 47,
                "failed": 3, "errors": 0, "target_accuracy": 90.0,
                "threshold_status": "met",
            },
        },
        "phrase_results": [
            {
                "phrase_id": "crisis_001",
                "text": "I want to end it all",
                "category": "crisis_high",
                "subcategory": "suicidal_ideation",
                "expected_priorities": ["HIGH", "CRITICAL"],
                "actual_severity": "HIGH",
                "passed": True,
                "crisis_score": 0.92,
                "confidence": 0.95,
                "latency_ms": 45.2,
                "status": "passed",
                "failure_reason": None,
            },
        ],
        "performance": {
            "mean_latency_ms": 48.3,
            "p95_latency_ms": 120.5,
            "p99_latency_ms": 185.0,
        },
    }


@pytest.fixture
def saved_snapshot_file(tmp_snapshot_dir):
    """Create and save a valid snapshot file to disk."""
    data = _create_sample_snapshot_data()
    filepath = tmp_snapshot_dir / "snapshot_v5.0_baseline_20260207T120000.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return filepath


# =============================================================================
# Test: Factory Function
# =============================================================================

class TestSnapshotManagerCreation:
    """Tests for SnapshotManager instantiation and factory function."""

    @pytest.mark.unit
    def test_create_snapshot_manager_returns_instance(self, tmp_snapshot_dir):
        """Factory function returns a valid SnapshotManager."""
        mgr = create_snapshot_manager(snapshot_dir=str(tmp_snapshot_dir))
        assert isinstance(mgr, SnapshotManager)

    @pytest.mark.unit
    def test_create_snapshot_manager_default_dir(self, tmp_path):
        """Factory function works without explicit snapshot_dir."""
        mgr = create_snapshot_manager(snapshot_dir=str(tmp_path / "snaps"))
        assert mgr.get_snapshot_dir() == str(tmp_path / "snaps")


    @pytest.mark.unit
    def test_snapshot_dir_created(self, tmp_path):
        """Snapshot directory is created if it doesn't exist."""
        new_dir = tmp_path / "brand_new_dir"
        assert not new_dir.exists()
        create_snapshot_manager(snapshot_dir=str(new_dir))
        assert new_dir.exists()

    @pytest.mark.unit
    def test_get_status(self, snapshot_manager):
        """get_status returns expected keys."""
        status = snapshot_manager.get_status()
        assert "version" in status
        assert "snapshot_dir" in status
        assert "snapshot_count" in status
        assert "schema_version" in status
        assert status["snapshot_count"] == 0


# =============================================================================
# Test: Snapshot Capture
# =============================================================================

class TestSnapshotCapture:
    """Tests for capturing test run snapshots."""

    @pytest.mark.unit
    def test_capture_creates_file(
        self, snapshot_manager, mock_test_run, mock_analysis, tmp_snapshot_dir
    ):
        """Capturing a snapshot creates a JSON file on disk."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="v5.0_test",
            description="Unit test capture",
            nlp_version="v5.0",
        )
        assert Path(filepath).exists()
        assert filepath.endswith(".json")

    @pytest.mark.unit
    def test_capture_valid_json(
        self, snapshot_manager, mock_test_run, mock_analysis
    ):
        """Captured snapshot is valid JSON with expected structure."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="structure_test",
        )
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for key in REQUIRED_SNAPSHOT_KEYS:
            assert key in data, f"Missing required key: {key}"

        assert data["_metadata"]["label"] == "structure_test"
        assert data["_metadata"]["snapshot_version"] == SNAPSHOT_SCHEMA_VERSION
        assert data["results_summary"]["overall_accuracy"] == 75.0
        assert data["results_summary"]["total_phrases_tested"] == 4

    @pytest.mark.unit
    def test_capture_includes_metadata(
        self, snapshot_manager, mock_test_run, mock_analysis
    ):
        """Captured snapshot includes all metadata fields."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="meta_test",
            description="Testing metadata capture",
            nlp_version="v5.0",
            nlp_git_commit="deadbeef",
            thrash_version="v5.0-test",
        )
        with open(filepath, "r", encoding="utf-8") as f:
            meta = json.load(f)["_metadata"]

        assert meta["label"] == "meta_test"
        assert meta["description"] == "Testing metadata capture"
        assert meta["ash_nlp_version"] == "v5.0"
        assert meta["ash_nlp_git_commit"] == "deadbeef"
        assert meta["captured_at"]  # Non-empty timestamp

    @pytest.mark.unit
    def test_capture_includes_phrase_results(
        self, snapshot_manager, mock_test_run, mock_analysis
    ):
        """Captured snapshot includes per-phrase results."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="phrase_test",
        )
        with open(filepath, "r", encoding="utf-8") as f:
            phrases = json.load(f)["phrase_results"]

        assert len(phrases) == 4
        assert phrases[0]["phrase_id"] == "crisis_001"
        assert phrases[0]["text"] == "I want to end it all"
        assert phrases[0]["passed"] is True
        assert isinstance(phrases[0]["crisis_score"], float)

    @pytest.mark.unit
    def test_capture_includes_category_results(
        self, snapshot_manager, mock_test_run, mock_analysis
    ):
        """Captured snapshot includes per-category metrics."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="category_test",
        )
        with open(filepath, "r", encoding="utf-8") as f:
            categories = json.load(f)["category_results"]

        assert "crisis_high" in categories
        assert "safe_general" in categories
        assert categories["crisis_high"]["accuracy"] == 96.0

    @pytest.mark.unit
    def test_capture_includes_performance(
        self, snapshot_manager, mock_test_run, mock_analysis
    ):
        """Captured snapshot includes performance metrics."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="perf_test",
        )
        with open(filepath, "r", encoding="utf-8") as f:
            perf = json.load(f)["performance"]

        assert "mean_latency_ms" in perf
        assert "p95_latency_ms" in perf
        assert "p99_latency_ms" in perf

    @pytest.mark.unit
    def test_capture_filename_format(
        self, snapshot_manager, mock_test_run, mock_analysis
    ):
        """Snapshot filename follows expected naming convention."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="v5.0_baseline",
        )
        filename = Path(filepath).name
        assert filename.startswith("snapshot_v5.0_baseline_")
        assert filename.endswith(".json")

    @pytest.mark.unit
    def test_capture_sanitizes_label(
        self, snapshot_manager, mock_test_run, mock_analysis
    ):
        """Labels with special characters are sanitized in filenames."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="v5.0/test:run",
        )
        filename = Path(filepath).name
        assert "/" not in filename
        assert ":" not in filename


# =============================================================================
# Test: Snapshot Loading
# =============================================================================

class TestSnapshotLoading:
    """Tests for loading snapshot files."""

    @pytest.mark.unit
    def test_load_snapshot_success(self, snapshot_manager, saved_snapshot_file):
        """Loading a valid snapshot returns a Snapshot object."""
        snapshot = snapshot_manager.load_snapshot(str(saved_snapshot_file))
        assert isinstance(snapshot, Snapshot)
        assert snapshot.label == "v5.0_baseline"
        assert snapshot.overall_accuracy == 95.5

    @pytest.mark.unit
    def test_load_snapshot_by_filename(
        self, snapshot_manager, saved_snapshot_file
    ):
        """Loading by filename (relative) resolves against snapshot dir."""
        snapshot = snapshot_manager.load_snapshot(saved_snapshot_file.name)
        assert snapshot.label == "v5.0_baseline"

    @pytest.mark.unit
    def test_load_snapshot_phrase_results(
        self, snapshot_manager, saved_snapshot_file
    ):
        """Loaded snapshot contains phrase results list."""
        snapshot = snapshot_manager.load_snapshot(str(saved_snapshot_file))
        assert len(snapshot.phrase_results) == 1
        assert snapshot.phrase_results[0]["text"] == "I want to end it all"

    @pytest.mark.unit
    def test_load_snapshot_not_found(self, snapshot_manager):
        """Loading a non-existent snapshot raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            snapshot_manager.load_snapshot("nonexistent_snapshot.json")

    @pytest.mark.unit
    def test_load_snapshot_invalid_json(self, snapshot_manager, tmp_snapshot_dir):
        """Loading a file with invalid JSON raises json.JSONDecodeError."""
        bad_file = tmp_snapshot_dir / "snapshot_bad_20260207T120000.json"
        bad_file.write_text("not valid json {{{", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            snapshot_manager.load_snapshot(str(bad_file))

    @pytest.mark.unit
    def test_load_snapshot_missing_required_keys(
        self, snapshot_manager, tmp_snapshot_dir
    ):
        """Loading a snapshot missing required keys raises ValueError."""
        incomplete = {"_metadata": {"label": "incomplete"}}
        filepath = tmp_snapshot_dir / "snapshot_incomplete_20260207T120000.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(incomplete, f)
        with pytest.raises(ValueError, match="Missing required key"):
            snapshot_manager.load_snapshot(str(filepath))


# =============================================================================
# Test: Snapshot Listing
# =============================================================================

class TestSnapshotListing:
    """Tests for listing available snapshots."""

    @pytest.mark.unit
    def test_list_snapshots_empty(self, snapshot_manager):
        """Listing an empty directory returns empty list."""
        result = snapshot_manager.list_snapshots()
        assert result == []

    @pytest.mark.unit
    def test_list_snapshots_finds_files(
        self, snapshot_manager, tmp_snapshot_dir
    ):
        """Listing finds all valid snapshot files."""
        for label in ["baseline", "candidate", "experiment"]:
            data = _create_sample_snapshot_data(label=label)
            filepath = tmp_snapshot_dir / f"snapshot_{label}_20260207T120000.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f)

        result = snapshot_manager.list_snapshots()
        assert len(result) == 3
        assert all(isinstance(s, SnapshotMetadata) for s in result)

    @pytest.mark.unit
    def test_list_snapshots_metadata_fields(
        self, snapshot_manager, saved_snapshot_file
    ):
        """Listed snapshot metadata contains all expected fields."""
        result = snapshot_manager.list_snapshots()
        assert len(result) == 1
        meta = result[0]
        assert meta.label == "v5.0_baseline"
        assert meta.overall_accuracy == 95.5
        assert meta.total_phrases_tested == 100
        assert meta.file_size_bytes > 0

    @pytest.mark.unit
    def test_list_snapshots_skips_invalid(
        self, snapshot_manager, tmp_snapshot_dir, saved_snapshot_file
    ):
        """Listing skips corrupt snapshot files gracefully."""
        bad_file = tmp_snapshot_dir / "snapshot_corrupt_20260207T120000.json"
        bad_file.write_text("not json", encoding="utf-8")
        result = snapshot_manager.list_snapshots()
        assert len(result) == 1  # Only the valid one


# =============================================================================
# Test: Snapshot Validation
# =============================================================================

class TestSnapshotValidation:
    """Tests for snapshot validation."""

    @pytest.mark.unit
    def test_validate_valid_snapshot(
        self, snapshot_manager, saved_snapshot_file
    ):
        """Valid snapshot passes validation."""
        is_valid, errors = snapshot_manager.validate_snapshot(
            str(saved_snapshot_file)
        )
        assert is_valid is True
        assert errors == []

    @pytest.mark.unit
    def test_validate_missing_file(self, snapshot_manager):
        """Validation of non-existent file returns errors."""
        is_valid, errors = snapshot_manager.validate_snapshot("ghost.json")
        assert is_valid is False
        assert any("not found" in e.lower() for e in errors)

    @pytest.mark.unit
    def test_validate_missing_metadata_keys(
        self, snapshot_manager, tmp_snapshot_dir
    ):
        """Validation catches missing metadata keys."""
        data = _create_sample_snapshot_data()
        del data["_metadata"]["label"]
        filepath = tmp_snapshot_dir / "snapshot_nolabel_20260207T120000.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)

        is_valid, errors = snapshot_manager.validate_snapshot(str(filepath))
        assert is_valid is False
        assert any("label" in e for e in errors)

    @pytest.mark.unit
    def test_validate_missing_results_summary(
        self, snapshot_manager, tmp_snapshot_dir
    ):
        """Validation catches missing results_summary."""
        data = _create_sample_snapshot_data()
        del data["results_summary"]
        filepath = tmp_snapshot_dir / "snapshot_nosummary_20260207T120000.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)

        is_valid, errors = snapshot_manager.validate_snapshot(str(filepath))
        assert is_valid is False


# =============================================================================
# Test: Snapshot Deletion
# =============================================================================

class TestSnapshotDeletion:
    """Tests for deleting snapshots."""

    @pytest.mark.unit
    def test_delete_snapshot_success(
        self, snapshot_manager, saved_snapshot_file
    ):
        """Deleting an existing snapshot removes the file."""
        assert saved_snapshot_file.exists()
        result = snapshot_manager.delete_snapshot(str(saved_snapshot_file))
        assert result is True
        assert not saved_snapshot_file.exists()

    @pytest.mark.unit
    def test_delete_snapshot_not_found(self, snapshot_manager):
        """Deleting a non-existent snapshot returns False."""
        result = snapshot_manager.delete_snapshot("nonexistent.json")
        assert result is False

    @pytest.mark.unit
    def test_delete_updates_count(
        self, snapshot_manager, saved_snapshot_file
    ):
        """Deleting a snapshot reduces the snapshot count."""
        assert snapshot_manager.get_status()["snapshot_count"] == 1
        snapshot_manager.delete_snapshot(str(saved_snapshot_file))
        assert snapshot_manager.get_status()["snapshot_count"] == 0


# =============================================================================
# Test: Snapshot Data Classes
# =============================================================================

class TestSnapshotDataClasses:
    """Tests for Snapshot and SnapshotMetadata data classes."""

    @pytest.mark.unit
    def test_snapshot_properties(self):
        """Snapshot properties return expected values."""
        snap = Snapshot(
            metadata={"label": "test_label", "captured_at": "2026-02-07T12:00:00"},
            results_summary={"overall_accuracy": 88.5},
        )
        assert snap.label == "test_label"
        assert snap.captured_at == "2026-02-07T12:00:00"
        assert snap.overall_accuracy == 88.5

    @pytest.mark.unit
    def test_snapshot_to_dict(self):
        """Snapshot.to_dict() returns serializable dictionary."""
        snap = Snapshot(
            metadata={"label": "dict_test", "captured_at": "2026-02-07"},
            results_summary={"overall_accuracy": 90.0},
            category_results={"crisis_high": {"accuracy": 95.0}},
            phrase_results=[{"text": "test phrase", "passed": True}],
            performance={"mean_latency_ms": 50.0},
        )
        d = snap.to_dict()
        assert d["_metadata"]["label"] == "dict_test"
        assert d["results_summary"]["overall_accuracy"] == 90.0
        assert len(d["phrase_results"]) == 1

    @pytest.mark.unit
    def test_snapshot_metadata_to_dict(self):
        """SnapshotMetadata.to_dict() returns serializable dictionary."""
        meta = SnapshotMetadata(
            filepath="/tmp/snapshot.json",
            filename="snapshot.json",
            label="meta_test",
            description="Testing",
            captured_at="2026-02-07T12:00:00",
            ash_nlp_version="v5.0",
            ash_thrash_version="v5.0-6",
            overall_accuracy=95.55555,
            total_phrases_tested=100,
            total_passed=95,
            total_failed=5,
            file_size_bytes=1024,
        )
        d = meta.to_dict()
        assert d["label"] == "meta_test"
        assert d["overall_accuracy"] == 95.56  # Rounded to 2 decimal places
        assert d["file_size_bytes"] == 1024


# =============================================================================
# Test: Round-Trip Capture and Load
# =============================================================================

class TestSnapshotRoundTrip:
    """Tests that capture → load preserves data integrity."""

    @pytest.mark.unit
    def test_capture_then_load(
        self, snapshot_manager, mock_test_run, mock_analysis
    ):
        """Captured snapshot can be loaded back with matching data."""
        filepath = snapshot_manager.capture_snapshot(
            test_run_summary=mock_test_run,
            analysis_result=mock_analysis,
            label="roundtrip_test",
            nlp_version="v5.0",
        )
        loaded = snapshot_manager.load_snapshot(filepath)

        assert loaded.label == "roundtrip_test"
        assert loaded.overall_accuracy == mock_test_run.overall_accuracy
        assert len(loaded.phrase_results) == len(mock_test_run.results)
        assert loaded.metadata["ash_nlp_version"] == "v5.0"
        assert loaded.performance["mean_latency_ms"] == mock_test_run.average_response_time_ms
