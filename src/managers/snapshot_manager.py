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
Snapshot Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-6-6.1-1
LAST MODIFIED: 2026-02-07
PHASE: Phase 6 - A/B Testing Infrastructure (v5.1 Migration Phase 1)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Capture complete test run results as versioned JSON snapshots
- Include metadata: timestamp, Ash-NLP version, model configuration, git commit
- Load snapshots for comparison by the ComparisonAnalyzerManager
- List available snapshots with metadata summaries
- Validate snapshot integrity and required fields
- Manage snapshot storage directory

SNAPSHOT NAMING:
    snapshot_{label}_{timestamp}.json
    Example: snapshot_v5.0_baseline_20260206T120000.json

USAGE:
    from src.managers.snapshot_manager import create_snapshot_manager

    snapshot_mgr = create_snapshot_manager(
        config_manager=config,
        logging_manager=logging_mgr,
    )

    # Capture a snapshot from a test run
    filepath = snapshot_mgr.capture_snapshot(
        test_run_summary=summary,
        analysis_result=analysis,
        label="v5.0_baseline",
        description="Pre-migration baseline capture",
        nlp_version="v5.0",
        nlp_git_commit="abc123def",
        model_configuration={...},
    )

    # Load a snapshot for comparison
    snapshot = snapshot_mgr.load_snapshot(filepath)

    # List available snapshots
    snapshots = snapshot_mgr.list_snapshots()

    # Validate a snapshot file
    is_valid, errors = snapshot_mgr.validate_snapshot(filepath)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Module version
__version__ = "v5.0-6-6.1-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Snapshot file naming
SNAPSHOT_PREFIX = "snapshot"
SNAPSHOT_EXTENSION = ".json"

# Default snapshot storage directory
DEFAULT_SNAPSHOT_DIR = "/app/reports/snapshots"

# Current snapshot schema version
SNAPSHOT_SCHEMA_VERSION = "1.0"

# Required top-level keys in a valid snapshot
REQUIRED_SNAPSHOT_KEYS = [
    "_metadata",
    "results_summary",
    "category_results",
    "phrase_results",
    "performance",
]

# Required metadata keys
REQUIRED_METADATA_KEYS = [
    "snapshot_version",
    "captured_at",
    "label",
]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SnapshotMetadata:
    """
    Summary metadata for a snapshot file.

    Used by list_snapshots() to provide quick overview without
    loading the full snapshot data.
    """
    filepath: str
    filename: str
    label: str
    description: str
    captured_at: str
    ash_nlp_version: str
    ash_thrash_version: str
    overall_accuracy: float
    total_phrases_tested: int
    total_passed: int
    total_failed: int
    file_size_bytes: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "filepath": self.filepath,
            "filename": self.filename,
            "label": self.label,
            "description": self.description,
            "captured_at": self.captured_at,
            "ash_nlp_version": self.ash_nlp_version,
            "ash_thrash_version": self.ash_thrash_version,
            "overall_accuracy": round(self.overall_accuracy, 2),
            "total_phrases_tested": self.total_phrases_tested,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "file_size_bytes": self.file_size_bytes,
        }


@dataclass
class Snapshot:
    """
    Complete snapshot data loaded from a JSON file.

    Contains all data necessary for A/B comparison analysis.
    """
    metadata: Dict[str, Any] = field(default_factory=dict)
    model_configuration: Dict[str, Any] = field(default_factory=dict)
    results_summary: Dict[str, Any] = field(default_factory=dict)
    category_results: Dict[str, Any] = field(default_factory=dict)
    phrase_results: List[Dict[str, Any]] = field(default_factory=list)
    performance: Dict[str, Any] = field(default_factory=dict)
    analysis_result: Optional[Dict[str, Any]] = None
    filepath: str = ""

    @property
    def label(self) -> str:
        """Get the snapshot label."""
        return self.metadata.get("label", "unknown")

    @property
    def captured_at(self) -> str:
        """Get the capture timestamp."""
        return self.metadata.get("captured_at", "")

    @property
    def overall_accuracy(self) -> float:
        """Get the overall accuracy from results summary."""
        return self.results_summary.get("overall_accuracy", 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            "_metadata": self.metadata,
            "model_configuration": self.model_configuration,
            "results_summary": self.results_summary,
            "category_results": self.category_results,
            "phrase_results": self.phrase_results,
            "performance": self.performance,
        }
        if self.analysis_result:
            data["analysis_result"] = self.analysis_result
        return data


# =============================================================================
# Snapshot Manager
# =============================================================================

class SnapshotManager:
    """
    Captures and manages versioned test run snapshots for A/B comparison.

    This manager is the foundation of the v5.1 A/B testing infrastructure.
    It persists complete test run results as JSON snapshots that can be
    compared by the ComparisonAnalyzerManager.

    Attributes:
        config_manager: Configuration manager for directory settings
        snapshot_dir: Path to snapshot storage directory

    Example:
        >>> mgr = create_snapshot_manager(config_manager=config)
        >>> filepath = mgr.capture_snapshot(
        ...     test_run_summary=summary,
        ...     analysis_result=analysis,
        ...     label="v5.0_baseline",
        ... )
        >>> snapshot = mgr.load_snapshot(filepath)
    """

    def __init__(
        self,
        config_manager: Optional[Any] = None,
        logging_manager: Optional[Any] = None,
        snapshot_dir: Optional[str] = None,
    ):
        """
        Initialize the SnapshotManager.

        Args:
            config_manager: Optional ConfigManager for settings
            logging_manager: Optional LoggingConfigManager for custom logger
            snapshot_dir: Override snapshot storage directory

        Note:
            Use create_snapshot_manager() factory function instead.
        """
        self._config = config_manager
        self._snapshot_dir = self._resolve_snapshot_dir(snapshot_dir)

        # Set up logger
        if logging_manager:
            self._logger = logging_manager.get_logger("snapshot_manager")
        else:
            self._logger = logger

        # Ensure snapshot directory exists
        self._ensure_directory(self._snapshot_dir)

        self._logger.info(
            f"✅ SnapshotManager {__version__} initialized "
            f"(dir: {self._snapshot_dir})"
        )

    def _resolve_snapshot_dir(self, override: Optional[str] = None) -> Path:
        """Resolve snapshot directory from override, config, or default."""
        if override:
            return Path(override)

        if self._config:
            try:
                config_dir = self._config.get("comparison", "snapshot_dir")
                if config_dir:
                    return Path(config_dir)
            except Exception:
                pass

        return Path(DEFAULT_SNAPSHOT_DIR)

    def _ensure_directory(self, path: Path) -> None:
        """Create directory if it doesn't exist."""
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self._logger.warning(
                f"⚠️ Could not create snapshot directory {path}: {e}"
            )

    def _generate_filename(self, label: str) -> str:
        """
        Generate a snapshot filename from label and current timestamp.

        Format: snapshot_{label}_{timestamp}.json
        Example: snapshot_v5.0_baseline_20260206T120000.json
        """
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        # Sanitize label for filename safety
        safe_label = (
            label.replace(" ", "_")
            .replace("/", "-")
            .replace("\\", "-")
            .replace(":", "-")
        )
        return f"{SNAPSHOT_PREFIX}_{safe_label}_{timestamp}{SNAPSHOT_EXTENSION}"

    def capture_snapshot(
        self,
        test_run_summary: Any,
        analysis_result: Any,
        label: str,
        description: str = "",
        nlp_version: str = "",
        nlp_git_commit: str = "",
        thrash_version: str = "",
        model_configuration: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Capture a complete test run as a versioned JSON snapshot.

        Converts the TestRunSummary and AnalysisResult into a standardized
        snapshot format and saves it to the snapshot directory.

        Args:
            test_run_summary: TestRunSummary from TestRunnerManager
            analysis_result: AnalysisResult from ResultAnalyzerManager
            label: Human-readable label (e.g., "v5.0_baseline")
            description: Optional description of what this snapshot represents
            nlp_version: Ash-NLP version string
            nlp_git_commit: Ash-NLP git commit hash
            thrash_version: Ash-Thrash version string
            model_configuration: Optional dict of Ash-NLP model settings

        Returns:
            Filepath of the saved snapshot

        Raises:
            OSError: If the snapshot file cannot be written

        Example:
            >>> filepath = mgr.capture_snapshot(
            ...     test_run_summary=summary,
            ...     analysis_result=analysis,
            ...     label="v5.0_baseline",
            ...     description="Pre-migration baseline",
            ...     nlp_version="v5.0",
            ... )
        """
        self._logger.info(f"📸 Capturing snapshot: {label}")

        # Build snapshot data
        snapshot_data = {
            "_metadata": {
                "snapshot_version": SNAPSHOT_SCHEMA_VERSION,
                "captured_at": datetime.now().isoformat(),
                "ash_nlp_version": nlp_version,
                "ash_nlp_git_commit": nlp_git_commit,
                "ash_thrash_version": thrash_version or __version__,
                "label": label,
                "description": description,
                "run_id": test_run_summary.run_id,
            },
            "model_configuration": model_configuration or {},
            "results_summary": {
                "overall_accuracy": test_run_summary.overall_accuracy,
                "total_phrases_tested": test_run_summary.total_tests,
                "total_passed": test_run_summary.passed_tests,
                "total_failed": test_run_summary.failed_tests,
                "total_errors": test_run_summary.error_tests,
                "total_skipped": getattr(
                    test_run_summary, "skipped_tests", 0
                ),
                "duration_seconds": test_run_summary.duration_seconds,
                "categories_tested": test_run_summary.categories_tested,
            },
            "category_results": self._build_category_results(analysis_result),
            "phrase_results": self._build_phrase_results(
                test_run_summary.results
            ),
            "performance": {
                "mean_latency_ms": test_run_summary.average_response_time_ms,
                "p95_latency_ms": test_run_summary.p95_response_time_ms,
                "p99_latency_ms": getattr(
                    analysis_result.latency_metrics, "p99_ms", 0.0
                ),
            },
            "analysis_result": analysis_result.to_dict(),
        }

        # Populate NLP server info if available
        if test_run_summary.nlp_server_info:
            snapshot_data["_metadata"]["nlp_server_info"] = (
                test_run_summary.nlp_server_info
            )

        # Generate filename and save
        filename = self._generate_filename(label)
        filepath = self._snapshot_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(snapshot_data, f, indent=2, default=str)

            file_size = filepath.stat().st_size
            self._logger.info(
                f"✅ Snapshot saved: {filename} "
                f"({file_size:,} bytes, "
                f"{test_run_summary.total_tests} phrases, "
                f"{test_run_summary.overall_accuracy:.1f}% accuracy)"
            )
            return str(filepath)

        except OSError as e:
            self._logger.error(f"❌ Failed to save snapshot: {e}")
            raise

    def _build_category_results(
        self, analysis_result: Any
    ) -> Dict[str, Any]:
        """Extract category results from AnalysisResult."""
        category_results = {}

        for name, metrics in analysis_result.category_metrics.items():
            category_results[name] = {
                "accuracy": metrics.accuracy,
                "total": metrics.total,
                "passed": metrics.passed,
                "failed": metrics.failed,
                "errors": metrics.errors,
                "target_accuracy": metrics.target_accuracy,
                "threshold_status": metrics.threshold_status.value,
            }

        return category_results

    def _build_phrase_results(
        self, results: List[Any]
    ) -> List[Dict[str, Any]]:
        """Convert TestResult list to serializable phrase results."""
        phrase_results = []

        for result in results:
            phrase_results.append({
                "phrase_id": result.phrase_id,
                "text": result.message,
                "category": result.category,
                "subcategory": result.subcategory,
                "expected_priorities": result.expected_priorities,
                "actual_severity": result.actual_severity,
                "passed": result.passed,
                "crisis_score": result.crisis_score,
                "confidence": result.confidence,
                "latency_ms": round(result.response_time_ms, 2),
                "status": (
                    result.status.value
                    if hasattr(result.status, "value")
                    else str(result.status)
                ),
                "failure_reason": result.failure_reason,
            })

        return phrase_results

    def load_snapshot(self, filepath: str) -> Snapshot:
        """
        Load a snapshot from a JSON file.

        Args:
            filepath: Path to the snapshot JSON file.
                      Can be absolute or relative to snapshot_dir.

        Returns:
            Snapshot object with all data loaded

        Raises:
            FileNotFoundError: If the snapshot file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
            ValueError: If the snapshot is missing required fields

        Example:
            >>> snapshot = mgr.load_snapshot("snapshot_v5.0_baseline_20260206T120000.json")
            >>> print(f"Accuracy: {snapshot.overall_accuracy:.1f}%")
        """
        path = Path(filepath)

        # If not absolute, look in snapshot directory
        if not path.is_absolute():
            path = self._snapshot_dir / path

        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {path}")

        self._logger.info(f"📂 Loading snapshot: {path.name}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate structure
        is_valid, errors = self._validate_snapshot_data(data)
        if not is_valid:
            raise ValueError(
                f"Invalid snapshot {path.name}: {'; '.join(errors)}"
            )

        snapshot = Snapshot(
            metadata=data.get("_metadata", {}),
            model_configuration=data.get("model_configuration", {}),
            results_summary=data.get("results_summary", {}),
            category_results=data.get("category_results", {}),
            phrase_results=data.get("phrase_results", []),
            performance=data.get("performance", {}),
            analysis_result=data.get("analysis_result"),
            filepath=str(path),
        )

        self._logger.info(
            f"✅ Snapshot loaded: {snapshot.label} "
            f"({snapshot.overall_accuracy:.1f}% accuracy, "
            f"{len(snapshot.phrase_results)} phrases)"
        )

        return snapshot

    def list_snapshots(
        self, sort_by: str = "captured_at", reverse: bool = True
    ) -> List[SnapshotMetadata]:
        """
        List all available snapshots with summary metadata.

        Args:
            sort_by: Field to sort by ("captured_at", "label", "accuracy")
            reverse: Sort in descending order if True

        Returns:
            List of SnapshotMetadata objects

        Example:
            >>> snapshots = mgr.list_snapshots()
            >>> for s in snapshots:
            ...     print(f"{s.label}: {s.overall_accuracy:.1f}%")
        """
        snapshots = []

        if not self._snapshot_dir.exists():
            return snapshots

        for path in sorted(self._snapshot_dir.glob(f"{SNAPSHOT_PREFIX}_*{SNAPSHOT_EXTENSION}")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                metadata = data.get("_metadata", {})
                summary = data.get("results_summary", {})

                snapshots.append(SnapshotMetadata(
                    filepath=str(path),
                    filename=path.name,
                    label=metadata.get("label", "unknown"),
                    description=metadata.get("description", ""),
                    captured_at=metadata.get("captured_at", ""),
                    ash_nlp_version=metadata.get("ash_nlp_version", ""),
                    ash_thrash_version=metadata.get(
                        "ash_thrash_version", ""
                    ),
                    overall_accuracy=summary.get("overall_accuracy", 0.0),
                    total_phrases_tested=summary.get(
                        "total_phrases_tested", 0
                    ),
                    total_passed=summary.get("total_passed", 0),
                    total_failed=summary.get("total_failed", 0),
                    file_size_bytes=path.stat().st_size,
                ))

            except (json.JSONDecodeError, OSError) as e:
                self._logger.warning(
                    f"⚠️ Skipping invalid snapshot {path.name}: {e}"
                )
                continue

        # Sort
        sort_key_map = {
            "captured_at": lambda s: s.captured_at,
            "label": lambda s: s.label,
            "accuracy": lambda s: s.overall_accuracy,
        }
        sort_func = sort_key_map.get(sort_by, sort_key_map["captured_at"])
        snapshots.sort(key=sort_func, reverse=reverse)

        self._logger.info(f"📋 Found {len(snapshots)} snapshots")
        return snapshots

    def validate_snapshot(self, filepath: str) -> Tuple[bool, List[str]]:
        """
        Validate a snapshot file for integrity and required fields.

        Args:
            filepath: Path to the snapshot JSON file

        Returns:
            Tuple of (is_valid, list_of_errors)

        Example:
            >>> is_valid, errors = mgr.validate_snapshot("snapshot.json")
            >>> if not is_valid:
            ...     for error in errors:
            ...         print(f"Error: {error}")
        """
        path = Path(filepath)
        if not path.is_absolute():
            path = self._snapshot_dir / path

        errors = []

        # Check file exists
        if not path.exists():
            return False, [f"File not found: {path}"]

        # Check file is readable JSON
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except OSError as e:
            return False, [f"Cannot read file: {e}"]

        # Validate structure
        return self._validate_snapshot_data(data)

    def _validate_snapshot_data(
        self, data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate snapshot data structure."""
        errors = []

        # Check required top-level keys
        for key in REQUIRED_SNAPSHOT_KEYS:
            if key not in data:
                errors.append(f"Missing required key: {key}")

        # Check required metadata keys
        metadata = data.get("_metadata", {})
        for key in REQUIRED_METADATA_KEYS:
            if key not in metadata:
                errors.append(f"Missing metadata key: {key}")

        # Validate results_summary has expected fields
        summary = data.get("results_summary", {})
        if "overall_accuracy" not in summary:
            errors.append(
                "Missing results_summary.overall_accuracy"
            )
        if "total_phrases_tested" not in summary:
            errors.append(
                "Missing results_summary.total_phrases_tested"
            )

        # Validate phrase_results is a list
        phrase_results = data.get("phrase_results", None)
        if phrase_results is not None and not isinstance(
            phrase_results, list
        ):
            errors.append("phrase_results must be a list")

        # Validate category_results is a dict
        category_results = data.get("category_results", None)
        if category_results is not None and not isinstance(
            category_results, dict
        ):
            errors.append("category_results must be a dict")

        return len(errors) == 0, errors

    def delete_snapshot(self, filepath: str) -> bool:
        """
        Delete a snapshot file.

        Args:
            filepath: Path to the snapshot file

        Returns:
            True if deleted successfully, False otherwise
        """
        path = Path(filepath)
        if not path.is_absolute():
            path = self._snapshot_dir / path

        if not path.exists():
            self._logger.warning(
                f"⚠️ Snapshot not found for deletion: {path}"
            )
            return False

        try:
            path.unlink()
            self._logger.info(f"🗑️ Deleted snapshot: {path.name}")
            return True
        except OSError as e:
            self._logger.error(
                f"❌ Failed to delete snapshot {path.name}: {e}"
            )
            return False

    def get_snapshot_dir(self) -> str:
        """Get the snapshot storage directory path."""
        return str(self._snapshot_dir)

    def get_status(self) -> Dict[str, Any]:
        """Get snapshot manager status information."""
        snapshot_count = len(list(
            self._snapshot_dir.glob(
                f"{SNAPSHOT_PREFIX}_*{SNAPSHOT_EXTENSION}"
            )
        )) if self._snapshot_dir.exists() else 0

        return {
            "version": __version__,
            "snapshot_dir": str(self._snapshot_dir),
            "snapshot_count": snapshot_count,
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
        }


# =============================================================================
# Factory Function - Clean Architecture v5.2.3 Compliance (Rule #1)
# =============================================================================

def create_snapshot_manager(
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
    snapshot_dir: Optional[str] = None,
) -> SnapshotManager:
    """
    Factory function for SnapshotManager (Clean Architecture v5.2.3 Pattern).

    This is the ONLY way to create a SnapshotManager instance.
    Direct instantiation should be avoided in production code.

    Args:
        config_manager: Optional ConfigManager for directory settings
        logging_manager: Optional LoggingConfigManager for custom logger
        snapshot_dir: Override snapshot storage directory

    Returns:
        Configured SnapshotManager instance

    Example:
        >>> mgr = create_snapshot_manager(
        ...     config_manager=config,
        ...     logging_manager=logging_mgr,
        ... )
    """
    logger.debug("🏭 Creating SnapshotManager")

    return SnapshotManager(
        config_manager=config_manager,
        logging_manager=logging_manager,
        snapshot_dir=snapshot_dir,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "SnapshotManager",
    "create_snapshot_manager",
    "Snapshot",
    "SnapshotMetadata",
    "SNAPSHOT_SCHEMA_VERSION",
]
