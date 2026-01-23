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
Report Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-3-3.2-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 3 - Analysis & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Generate JSON reports from AnalysisResult
- Generate HTML reports using Jinja2 templates
- Save and load baselines for regression comparison
- Compare analysis results against baselines
- Send Discord webhook notifications
- Manage report storage directories

REPORT FORMATS:
- JSON: Machine-readable format for CI/CD and programmatic access
- HTML: Human-readable format with visual indicators

BASELINE FEATURES:
- Save analysis as named baseline (e.g., "main", "pre-release")
- Load baseline by name
- Compare current analysis to baseline
- Detect regressions based on configurable thresholds

USAGE:
    from src.managers.report_manager import create_report_manager
    
    reporter = create_report_manager(
        config_manager=config,
        secrets_manager=secrets,
        logging_manager=logging_mgr,
    )
    
    # Generate reports
    json_path = reporter.generate_json_report(analysis)
    html_path = reporter.generate_html_report(analysis)
    
    # Baseline operations
    reporter.save_baseline(analysis, name="main")
    baseline = reporter.load_baseline(name="main")
    comparison = reporter.compare_to_baseline(analysis, baseline)
    
    # Discord notification
    await reporter.send_discord_notification(analysis, comparison)
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

# Import Phase 3 types
from .result_analyzer_manager import (
    AnalysisResult,
    CategoryMetrics,
    LatencyMetrics,
    ThresholdResult,
    ThresholdStatus,
    RegressionSeverity,
)

# Module version
__version__ = "v5.0-3-3.2-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default report output directory
DEFAULT_REPORT_DIR = "/app/reports"

# Default baseline directory
DEFAULT_BASELINE_DIR = "/app/reports/baselines"

# Report filename patterns
JSON_REPORT_PATTERN = "report_{run_id}_{timestamp}.json"
HTML_REPORT_PATTERN = "report_{run_id}_{timestamp}.html"
BASELINE_PATTERN = "baseline_{name}.json"

# Discord webhook timeout
DISCORD_TIMEOUT = 30

# Discord embed colors (decimal)
DISCORD_COLOR_SUCCESS = 3066993    # Green
DISCORD_COLOR_WARNING = 15105570   # Orange
DISCORD_COLOR_FAILURE = 15158332   # Red
DISCORD_COLOR_INFO = 3447003       # Blue


# =============================================================================
# Enums
# =============================================================================

class ComparisonVerdict(str, Enum):
    """Overall verdict from baseline comparison."""
    PASS = "pass"           # No regressions detected
    WARNING = "warning"     # Minor regressions detected
    FAIL = "fail"           # Significant regressions detected
    NO_BASELINE = "no_baseline"  # No baseline to compare


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class RegressionDetail:
    """Details about a detected regression."""
    metric_name: str
    baseline_value: float
    current_value: float
    delta: float
    threshold: float
    severity: RegressionSeverity
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "baseline_value": round(self.baseline_value, 2),
            "current_value": round(self.current_value, 2),
            "delta": round(self.delta, 2),
            "threshold": round(self.threshold, 2),
            "severity": self.severity.value,
            "description": self.description,
        }


@dataclass
class ImprovementDetail:
    """Details about a detected improvement."""
    metric_name: str
    baseline_value: float
    current_value: float
    delta: float
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "baseline_value": round(self.baseline_value, 2),
            "current_value": round(self.current_value, 2),
            "delta": round(self.delta, 2),
            "description": self.description,
        }


@dataclass
class BaselineComparison:
    """
    Result of comparing analysis against a baseline.
    """
    baseline_name: str
    baseline_run_id: str
    baseline_timestamp: datetime
    current_run_id: str
    current_timestamp: datetime
    
    # Overall changes
    overall_accuracy_delta: float = 0.0
    
    # Category-level deltas
    category_deltas: Dict[str, float] = field(default_factory=dict)
    
    # Detected issues
    regressions: List[RegressionDetail] = field(default_factory=list)
    improvements: List[ImprovementDetail] = field(default_factory=list)
    
    # Verdict
    verdict: ComparisonVerdict = ComparisonVerdict.PASS
    verdict_reason: str = ""
    
    @property
    def has_regressions(self) -> bool:
        """Check if any regressions were detected."""
        return len(self.regressions) > 0
    
    @property
    def has_improvements(self) -> bool:
        """Check if any improvements were detected."""
        return len(self.improvements) > 0
    
    @property
    def critical_regressions(self) -> List[RegressionDetail]:
        """Get only critical severity regressions."""
        return [r for r in self.regressions if r.severity == RegressionSeverity.CRITICAL]
    
    @property
    def alert_regressions(self) -> List[RegressionDetail]:
        """Get alert-level regressions."""
        return [r for r in self.regressions if r.severity == RegressionSeverity.ALERT]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "baseline_name": self.baseline_name,
            "baseline_run_id": self.baseline_run_id,
            "baseline_timestamp": self.baseline_timestamp.isoformat(),
            "current_run_id": self.current_run_id,
            "current_timestamp": self.current_timestamp.isoformat(),
            "overall_accuracy_delta": round(self.overall_accuracy_delta, 2),
            "category_deltas": {
                k: round(v, 2) for k, v in self.category_deltas.items()
            },
            "regressions": [r.to_dict() for r in self.regressions],
            "improvements": [i.to_dict() for i in self.improvements],
            "verdict": self.verdict.value,
            "verdict_reason": self.verdict_reason,
            "has_regressions": self.has_regressions,
            "has_improvements": self.has_improvements,
        }


# =============================================================================
# Report Manager
# =============================================================================

class ReportManager:
    """
    Generates reports and manages baselines for test results.
    
    This manager handles all reporting responsibilities:
    - JSON report generation for machine processing
    - HTML report generation for human review
    - Baseline storage and comparison for regression detection
    - Discord webhook notifications for team alerts
    
    Attributes:
        config_manager: Configuration manager
        secrets_manager: Secrets manager for webhook URL
        report_dir: Directory for report output
        baseline_dir: Directory for baseline storage
        jinja_env: Jinja2 environment for HTML templates
    
    Example:
        >>> reporter = create_report_manager(config_manager=config)
        >>> json_path = reporter.generate_json_report(analysis)
        >>> print(f"Report saved to: {json_path}")
    """
    
    def __init__(
        self,
        config_manager: Optional[Any] = None,
        secrets_manager: Optional[Any] = None,
        logging_manager: Optional[Any] = None,
        report_dir: Optional[str] = None,
        baseline_dir: Optional[str] = None,
    ):
        """
        Initialize the ReportManager.
        
        Args:
            config_manager: Optional ConfigManager
            secrets_manager: Optional SecretsManager for Discord webhook
            logging_manager: Optional LoggingConfigManager
            report_dir: Override report output directory
            baseline_dir: Override baseline storage directory
        
        Note:
            Use create_report_manager() factory function instead.
        """
        self._config = config_manager
        self._secrets = secrets_manager
        
        # Set up logger
        if logging_manager:
            self._logger = logging_manager.get_logger("report_manager")
        else:
            self._logger = logger
        
        # Resolve directories
        self._report_dir = Path(self._resolve_report_dir(report_dir))
        self._baseline_dir = Path(self._resolve_baseline_dir(baseline_dir))
        
        # Load regression thresholds
        self._regression_thresholds = self._load_regression_thresholds()
        
        # Initialize Jinja2 environment
        self._jinja_env = self._setup_jinja_environment()
        
        # Ensure directories exist
        self._ensure_directories()
        
        self._logger.info(
            f"✅ ReportManager {__version__} initialized "
            f"(reports: {self._report_dir}, baselines: {self._baseline_dir})"
        )
    
    def _resolve_report_dir(self, override: Optional[str]) -> str:
        """Resolve report directory from config or default."""
        if override:
            return override
        if self._config:
            return self._config.get("reporting", "output_directory") or DEFAULT_REPORT_DIR
        return DEFAULT_REPORT_DIR
    
    def _resolve_baseline_dir(self, override: Optional[str]) -> str:
        """Resolve baseline directory from config or default."""
        if override:
            return override
        if self._config:
            return self._config.get("baseline", "storage_directory") or DEFAULT_BASELINE_DIR
        return DEFAULT_BASELINE_DIR
    
    def _load_regression_thresholds(self) -> Dict[str, float]:
        """Load regression detection thresholds from config."""
        defaults = {
            "overall": 2.0,
            "category": 5.0,
            "false_positive": 3.0,
            "false_negative": 2.0,
            "latency_pct": 50.0,
        }
        
        if not self._config:
            return defaults
        
        try:
            return {
                "overall": self._config.get(
                    "baseline", "regression_overall_threshold"
                ) or defaults["overall"],
                "category": self._config.get(
                    "baseline", "regression_category_threshold"
                ) or defaults["category"],
                "false_positive": self._config.get(
                    "baseline", "regression_false_positive_threshold"
                ) or defaults["false_positive"],
                "false_negative": self._config.get(
                    "baseline", "regression_false_negative_threshold"
                ) or defaults["false_negative"],
                "latency_pct": self._config.get(
                    "baseline", "regression_latency_threshold_pct"
                ) or defaults["latency_pct"],
            }
        except Exception as e:
            self._logger.warning(f"⚠️ Failed to load regression thresholds: {e}")
            return defaults
    
    def _setup_jinja_environment(self) -> Environment:
        """Set up Jinja2 environment for HTML templates."""
        # Try to load templates from file system first
        template_paths = [
            Path(__file__).parent.parent / "templates",
            Path("/app/src/templates"),
            Path("src/templates"),
        ]
        
        for path in template_paths:
            if path.exists():
                self._logger.debug(f"📄 Using templates from: {path}")
                return Environment(
                    loader=FileSystemLoader(str(path)),
                    autoescape=select_autoescape(['html', 'xml']),
                )
        
        # Fall back to embedded template
        self._logger.debug("📄 Using embedded HTML template")
        return Environment(autoescape=select_autoescape(['html', 'xml']))
    
    def _ensure_directories(self) -> None:
        """Ensure report and baseline directories exist."""
        try:
            self._report_dir.mkdir(parents=True, exist_ok=True)
            self._baseline_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self._logger.warning(f"⚠️ Failed to create directories: {e}")
    
    # =========================================================================
    # JSON Report Generation
    # =========================================================================
    
    def generate_json_report(
        self, 
        analysis: AnalysisResult,
        comparison: Optional[BaselineComparison] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate a JSON report from analysis results.
        
        Args:
            analysis: AnalysisResult from ResultAnalyzerManager
            comparison: Optional baseline comparison to include
            filename: Override filename (default: auto-generated)
        
        Returns:
            Path to generated report file
        
        Example:
            >>> path = reporter.generate_json_report(analysis)
            >>> print(f"Report: {path}")
        """
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        
        if filename is None:
            filename = JSON_REPORT_PATTERN.format(
                run_id=analysis.run_id,
                timestamp=timestamp,
            )
        
        # Build report structure
        report = {
            "_metadata": {
                "report_version": "v5.0",
                "generated_at": datetime.now().isoformat(),
                "ash_thrash_version": __version__,
                "run_id": analysis.run_id,
            },
            "analysis": analysis.to_dict(),
        }
        
        # Include comparison if provided
        if comparison:
            report["baseline_comparison"] = comparison.to_dict()
        
        # Write to file
        output_path = self._report_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self._logger.info(f"📄 JSON report saved: {output_path}")
            return output_path
            
        except Exception as e:
            self._logger.error(f"❌ Failed to save JSON report: {e}")
            raise
    
    # =========================================================================
    # HTML Report Generation
    # =========================================================================
    
    def generate_html_report(
        self,
        analysis: AnalysisResult,
        comparison: Optional[BaselineComparison] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate an HTML report from analysis results.
        
        Args:
            analysis: AnalysisResult from ResultAnalyzerManager
            comparison: Optional baseline comparison to include
            filename: Override filename (default: auto-generated)
        
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        
        if filename is None:
            filename = HTML_REPORT_PATTERN.format(
                run_id=analysis.run_id,
                timestamp=timestamp,
            )
        
        # Try to load template file
        try:
            template = self._jinja_env.get_template("report_html.jinja2")
        except Exception:
            # Use embedded template
            template = self._jinja_env.from_string(self._get_embedded_html_template())
        
        # Prepare template context
        context = {
            "analysis": analysis,
            "comparison": comparison,
            "generated_at": datetime.now().isoformat(),
            "version": __version__,
            # Helper values for template
            "threshold_status_classes": {
                ThresholdStatus.MET: "status-pass",
                ThresholdStatus.NOT_MET: "status-fail",
                ThresholdStatus.WARNING: "status-warning",
                ThresholdStatus.NO_THRESHOLD: "status-info",
            },
        }
        
        # Render template
        html_content = template.render(**context)
        
        # Write to file
        output_path = self._report_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self._logger.info(f"📄 HTML report saved: {output_path}")
            return output_path
            
        except Exception as e:
            self._logger.error(f"❌ Failed to save HTML report: {e}")
            raise
    
    def _get_embedded_html_template(self) -> str:
        """Return embedded HTML template as fallback."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ash-Thrash Test Report - {{ analysis.run_id }}</title>
    <style>
        :root {
            --color-pass: #2ecc71;
            --color-fail: #e74c3c;
            --color-warning: #f39c12;
            --color-info: #3498db;
            --color-bg: #1a1a2e;
            --color-surface: #16213e;
            --color-text: #eee;
            --color-text-muted: #aaa;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
            padding: 2rem;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header {
            text-align: center;
            padding: 2rem;
            background: var(--color-surface);
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        header h1 { color: var(--color-pass); margin-bottom: 0.5rem; }
        header .subtitle { color: var(--color-text-muted); }
        .card {
            background: var(--color-surface);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .card h2 {
            border-bottom: 2px solid var(--color-info);
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        .stat-box {
            background: rgba(255,255,255,0.05);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        .stat-box .value { font-size: 2rem; font-weight: bold; }
        .stat-box .label { color: var(--color-text-muted); font-size: 0.9rem; }
        .status-pass { color: var(--color-pass); }
        .status-fail { color: var(--color-fail); }
        .status-warning { color: var(--color-warning); }
        .status-info { color: var(--color-info); }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        th { background: rgba(255,255,255,0.05); }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .badge-pass { background: var(--color-pass); color: #000; }
        .badge-fail { background: var(--color-fail); color: #fff; }
        .badge-warning { background: var(--color-warning); color: #000; }
        footer {
            text-align: center;
            padding: 2rem;
            color: var(--color-text-muted);
            font-size: 0.9rem;
        }
        footer a { color: var(--color-info); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧪 Ash-Thrash Test Report</h1>
            <p class="subtitle">Run ID: {{ analysis.run_id }}</p>
            <p class="subtitle">Generated: {{ generated_at }}</p>
        </header>

        <!-- Summary -->
        <div class="card">
            <h2>📊 Summary</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="value {% if analysis.overall_accuracy >= 90 %}status-pass{% elif analysis.overall_accuracy >= 80 %}status-warning{% else %}status-fail{% endif %}">
                        {{ "%.1f"|format(analysis.overall_accuracy) }}%
                    </div>
                    <div class="label">Overall Accuracy</div>
                </div>
                <div class="stat-box">
                    <div class="value">{{ analysis.total_tests }}</div>
                    <div class="label">Total Tests</div>
                </div>
                <div class="stat-box">
                    <div class="value status-pass">{{ analysis.passed_tests }}</div>
                    <div class="label">Passed</div>
                </div>
                <div class="stat-box">
                    <div class="value status-fail">{{ analysis.failed_tests }}</div>
                    <div class="label">Failed</div>
                </div>
                <div class="stat-box">
                    <div class="value status-warning">{{ analysis.error_tests }}</div>
                    <div class="label">Errors</div>
                </div>
                <div class="stat-box">
                    <div class="value">{{ "%.1f"|format(analysis.test_run_duration_seconds) }}s</div>
                    <div class="label">Duration</div>
                </div>
            </div>
        </div>

        <!-- Thresholds -->
        <div class="card">
            <h2>🎯 Threshold Status</h2>
            <p>
                {% if analysis.all_thresholds_met %}
                    <span class="badge badge-pass">✅ All Thresholds Met</span>
                {% else %}
                    <span class="badge badge-fail">❌ {{ analysis.thresholds_total_count - analysis.thresholds_met_count }} Threshold(s) Not Met</span>
                {% endif %}
            </p>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Accuracy</th>
                        <th>Target</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for name, result in analysis.threshold_results.items() %}
                    <tr>
                        <td>{{ name }}</td>
                        <td>{{ "%.1f"|format(result.actual_value) }}%</td>
                        <td>{{ "%.1f"|format(result.target_value) }}%</td>
                        <td>
                            {% if result.status.value == 'met' %}
                                <span class="badge badge-pass">✅ MET</span>
                            {% elif result.status.value == 'warning' %}
                                <span class="badge badge-warning">⚠️ WARNING</span>
                            {% else %}
                                <span class="badge badge-fail">❌ NOT MET</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- False Positive/Negative -->
        <div class="card">
            <h2>⚠️ False Positive / Negative Rates</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="value {% if analysis.false_positive_rate <= 5 %}status-pass{% elif analysis.false_positive_rate <= 10 %}status-warning{% else %}status-fail{% endif %}">
                        {{ "%.1f"|format(analysis.false_positive_rate) }}%
                    </div>
                    <div class="label">False Positive Rate</div>
                </div>
                <div class="stat-box">
                    <div class="value {% if analysis.false_negative_rate <= 5 %}status-pass{% elif analysis.false_negative_rate <= 10 %}status-warning{% else %}status-fail{% endif %}">
                        {{ "%.1f"|format(analysis.false_negative_rate) }}%
                    </div>
                    <div class="label">False Negative Rate</div>
                </div>
            </div>
            <p style="margin-top: 1rem; color: var(--color-text-muted);">
                TP: {{ analysis.true_positive_count }} | TN: {{ analysis.true_negative_count }} |
                FP: {{ analysis.false_positive_count }} | FN: {{ analysis.false_negative_count }}
            </p>
        </div>

        <!-- Latency -->
        <div class="card">
            <h2>⏱️ Latency Metrics</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="value">{{ "%.0f"|format(analysis.latency_metrics.median_ms) }}ms</div>
                    <div class="label">Median (p50)</div>
                </div>
                <div class="stat-box">
                    <div class="value {% if analysis.latency_metrics.p95_ms <= 500 %}status-pass{% else %}status-warning{% endif %}">
                        {{ "%.0f"|format(analysis.latency_metrics.p95_ms) }}ms
                    </div>
                    <div class="label">p95</div>
                </div>
                <div class="stat-box">
                    <div class="value">{{ "%.0f"|format(analysis.latency_metrics.p99_ms) }}ms</div>
                    <div class="label">p99</div>
                </div>
                <div class="stat-box">
                    <div class="value">{{ "%.0f"|format(analysis.latency_metrics.mean_ms) }}ms</div>
                    <div class="label">Mean</div>
                </div>
            </div>
        </div>

        {% if analysis.failed_test_details %}
        <!-- Failed Tests -->
        <div class="card">
            <h2>❌ Failed Tests ({{ analysis.failed_test_details|length }})</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Category</th>
                        <th>Expected</th>
                        <th>Actual</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
                    {% for test in analysis.failed_test_details[:50] %}
                    <tr>
                        <td>{{ test.phrase_id }}</td>
                        <td>{{ test.category }}/{{ test.subcategory }}</td>
                        <td>{{ test.expected_priorities|join(', ') }}</td>
                        <td class="status-fail">{{ test.actual_severity }}</td>
                        <td>{{ "%.2f"|format(test.crisis_score) if test.crisis_score else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% if analysis.failed_test_details|length > 50 %}
            <p style="margin-top: 1rem; color: var(--color-text-muted);">
                Showing 50 of {{ analysis.failed_test_details|length }} failed tests.
            </p>
            {% endif %}
        </div>
        {% endif %}

        {% if comparison %}
        <!-- Baseline Comparison -->
        <div class="card">
            <h2>📈 Baseline Comparison</h2>
            <p>Compared to baseline: <strong>{{ comparison.baseline_name }}</strong> ({{ comparison.baseline_run_id }})</p>
            <div class="stats-grid" style="margin-top: 1rem;">
                <div class="stat-box">
                    <div class="value {% if comparison.overall_accuracy_delta >= 0 %}status-pass{% else %}status-fail{% endif %}">
                        {{ "%+.1f"|format(comparison.overall_accuracy_delta) }}%
                    </div>
                    <div class="label">Accuracy Change</div>
                </div>
                <div class="stat-box">
                    <div class="value">
                        {% if comparison.verdict.value == 'pass' %}
                            <span class="badge badge-pass">✅ PASS</span>
                        {% elif comparison.verdict.value == 'warning' %}
                            <span class="badge badge-warning">⚠️ WARNING</span>
                        {% else %}
                            <span class="badge badge-fail">❌ FAIL</span>
                        {% endif %}
                    </div>
                    <div class="label">Verdict</div>
                </div>
            </div>
            {% if comparison.regressions %}
            <h3 style="margin-top: 1.5rem; color: var(--color-fail);">🔻 Regressions Detected</h3>
            <ul style="margin-top: 0.5rem;">
                {% for reg in comparison.regressions %}
                <li>{{ reg.description }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endif %}

        <footer>
            <p>Generated by Ash-Thrash {{ version }}</p>
            <p>
                <a href="https://discord.gg/alphabetcartel">The Alphabet Cartel</a> |
                <a href="https://alphabetcartel.org">alphabetcartel.org</a>
            </p>
            <p>Built with care for chosen family 🏳️‍🌈</p>
        </footer>
    </div>
</body>
</html>"""
    
    # =========================================================================
    # Baseline Operations
    # =========================================================================
    
    def save_baseline(
        self, 
        analysis: AnalysisResult, 
        name: str = "main"
    ) -> Path:
        """
        Save analysis result as a named baseline.
        
        Args:
            analysis: AnalysisResult to save
            name: Baseline name (default: "main")
        
        Returns:
            Path to saved baseline file
        
        Example:
            >>> reporter.save_baseline(analysis, name="pre-release")
        """
        filename = BASELINE_PATTERN.format(name=name)
        output_path = self._baseline_dir / filename
        
        baseline_data = {
            "_metadata": {
                "baseline_version": "v5.0",
                "saved_at": datetime.now().isoformat(),
                "name": name,
            },
            "analysis": analysis.to_dict(),
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)
            
            self._logger.info(f"💾 Baseline '{name}' saved: {output_path}")
            return output_path
            
        except Exception as e:
            self._logger.error(f"❌ Failed to save baseline '{name}': {e}")
            raise
    
    def load_baseline(self, name: str = "main") -> Optional[AnalysisResult]:
        """
        Load a named baseline.
        
        Args:
            name: Baseline name to load
        
        Returns:
            AnalysisResult or None if not found
        
        Example:
            >>> baseline = reporter.load_baseline("main")
            >>> if baseline:
            ...     comparison = reporter.compare_to_baseline(analysis, baseline)
        """
        filename = BASELINE_PATTERN.format(name=name)
        filepath = self._baseline_dir / filename
        
        if not filepath.exists():
            self._logger.warning(f"⚠️ Baseline '{name}' not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            analysis = AnalysisResult.from_dict(data["analysis"])
            self._logger.info(f"📂 Baseline '{name}' loaded (run: {analysis.run_id})")
            return analysis
            
        except Exception as e:
            self._logger.error(f"❌ Failed to load baseline '{name}': {e}")
            return None
    
    def list_baselines(self) -> List[str]:
        """
        List all available baseline names.
        
        Returns:
            List of baseline names
        """
        baselines = []
        
        try:
            for filepath in self._baseline_dir.glob("baseline_*.json"):
                # Extract name from filename
                name = filepath.stem.replace("baseline_", "")
                baselines.append(name)
        except Exception as e:
            self._logger.warning(f"⚠️ Failed to list baselines: {e}")
        
        return sorted(baselines)
    
    def compare_to_baseline(
        self,
        current: AnalysisResult,
        baseline: AnalysisResult,
        baseline_name: str = "unknown",
    ) -> BaselineComparison:
        """
        Compare current analysis to a baseline for regression detection.
        
        Args:
            current: Current AnalysisResult
            baseline: Baseline AnalysisResult to compare against
            baseline_name: Name of the baseline for reporting
        
        Returns:
            BaselineComparison with detected regressions and improvements
        
        Example:
            >>> baseline = reporter.load_baseline("main")
            >>> comparison = reporter.compare_to_baseline(analysis, baseline, "main")
            >>> if comparison.has_regressions:
            ...     print("Regressions detected!")
        """
        comparison = BaselineComparison(
            baseline_name=baseline_name,
            baseline_run_id=baseline.run_id,
            baseline_timestamp=baseline.timestamp,
            current_run_id=current.run_id,
            current_timestamp=current.timestamp,
        )
        
        # Overall accuracy delta
        comparison.overall_accuracy_delta = (
            current.overall_accuracy - baseline.overall_accuracy
        )
        
        # Check for overall regression
        if comparison.overall_accuracy_delta < -self._regression_thresholds["overall"]:
            comparison.regressions.append(RegressionDetail(
                metric_name="overall_accuracy",
                baseline_value=baseline.overall_accuracy,
                current_value=current.overall_accuracy,
                delta=comparison.overall_accuracy_delta,
                threshold=self._regression_thresholds["overall"],
                severity=RegressionSeverity.ALERT,
                description=f"Overall accuracy dropped by {abs(comparison.overall_accuracy_delta):.1f}% "
                           f"(from {baseline.overall_accuracy:.1f}% to {current.overall_accuracy:.1f}%)",
            ))
        elif comparison.overall_accuracy_delta > 1.0:
            comparison.improvements.append(ImprovementDetail(
                metric_name="overall_accuracy",
                baseline_value=baseline.overall_accuracy,
                current_value=current.overall_accuracy,
                delta=comparison.overall_accuracy_delta,
                description=f"Overall accuracy improved by {comparison.overall_accuracy_delta:.1f}%",
            ))
        
        # Category-level comparison
        for cat_name, current_metrics in current.category_metrics.items():
            baseline_metrics = baseline.category_metrics.get(cat_name)
            
            if baseline_metrics:
                delta = current_metrics.accuracy - baseline_metrics.accuracy
                comparison.category_deltas[cat_name] = delta
                
                # Check for regression
                if delta < -self._regression_thresholds["category"]:
                    comparison.regressions.append(RegressionDetail(
                        metric_name=f"category_{cat_name}",
                        baseline_value=baseline_metrics.accuracy,
                        current_value=current_metrics.accuracy,
                        delta=delta,
                        threshold=self._regression_thresholds["category"],
                        severity=RegressionSeverity.WARNING,
                        description=f"Category '{cat_name}' accuracy dropped by {abs(delta):.1f}%",
                    ))
                elif delta > 2.0:
                    comparison.improvements.append(ImprovementDetail(
                        metric_name=f"category_{cat_name}",
                        baseline_value=baseline_metrics.accuracy,
                        current_value=current_metrics.accuracy,
                        delta=delta,
                        description=f"Category '{cat_name}' accuracy improved by {delta:.1f}%",
                    ))
        
        # False positive rate comparison
        fp_delta = current.false_positive_rate - baseline.false_positive_rate
        if fp_delta > self._regression_thresholds["false_positive"]:
            comparison.regressions.append(RegressionDetail(
                metric_name="false_positive_rate",
                baseline_value=baseline.false_positive_rate,
                current_value=current.false_positive_rate,
                delta=fp_delta,
                threshold=self._regression_thresholds["false_positive"],
                severity=RegressionSeverity.WARNING,
                description=f"False positive rate increased by {fp_delta:.1f}%",
            ))
        
        # False negative rate comparison (more critical)
        fn_delta = current.false_negative_rate - baseline.false_negative_rate
        if fn_delta > self._regression_thresholds["false_negative"]:
            comparison.regressions.append(RegressionDetail(
                metric_name="false_negative_rate",
                baseline_value=baseline.false_negative_rate,
                current_value=current.false_negative_rate,
                delta=fn_delta,
                threshold=self._regression_thresholds["false_negative"],
                severity=RegressionSeverity.CRITICAL,  # FN is critical for crisis detection
                description=f"⚠️ CRITICAL: False negative rate increased by {fn_delta:.1f}% "
                           f"(crisis messages may be missed!)",
            ))
        
        # Latency comparison
        if baseline.latency_metrics.p95_ms > 0:
            latency_pct_change = (
                (current.latency_metrics.p95_ms - baseline.latency_metrics.p95_ms) 
                / baseline.latency_metrics.p95_ms
            ) * 100
            
            if latency_pct_change > self._regression_thresholds["latency_pct"]:
                comparison.regressions.append(RegressionDetail(
                    metric_name="latency_p95",
                    baseline_value=baseline.latency_metrics.p95_ms,
                    current_value=current.latency_metrics.p95_ms,
                    delta=latency_pct_change,
                    threshold=self._regression_thresholds["latency_pct"],
                    severity=RegressionSeverity.WARNING,
                    description=f"p95 latency increased by {latency_pct_change:.0f}% "
                               f"(from {baseline.latency_metrics.p95_ms:.0f}ms to "
                               f"{current.latency_metrics.p95_ms:.0f}ms)",
                ))
        
        # Determine overall verdict
        if comparison.critical_regressions:
            comparison.verdict = ComparisonVerdict.FAIL
            comparison.verdict_reason = "Critical regressions detected (false negatives increased)"
        elif comparison.alert_regressions:
            comparison.verdict = ComparisonVerdict.FAIL
            comparison.verdict_reason = f"{len(comparison.alert_regressions)} alert-level regression(s) detected"
        elif comparison.regressions:
            comparison.verdict = ComparisonVerdict.WARNING
            comparison.verdict_reason = f"{len(comparison.regressions)} minor regression(s) detected"
        else:
            comparison.verdict = ComparisonVerdict.PASS
            comparison.verdict_reason = "No regressions detected"
        
        self._logger.info(
            f"📊 Baseline comparison: {comparison.verdict.value.upper()} - "
            f"{len(comparison.regressions)} regressions, {len(comparison.improvements)} improvements"
        )
        
        return comparison
    
    # =========================================================================
    # Discord Notifications
    # =========================================================================
    
    async def send_discord_notification(
        self,
        analysis: AnalysisResult,
        comparison: Optional[BaselineComparison] = None,
    ) -> bool:
        """
        Send test results to Discord webhook.
        
        Args:
            analysis: AnalysisResult to report
            comparison: Optional baseline comparison to include
        
        Returns:
            True if notification sent successfully
        
        Example:
            >>> success = await reporter.send_discord_notification(analysis)
        """
        # Get webhook URL
        webhook_url = None
        if self._secrets:
            webhook_url = self._secrets.get_discord_alert_token()
        
        if not webhook_url:
            self._logger.warning("⚠️ Discord webhook not configured, skipping notification")
            return False
        
        # Determine embed color
        if analysis.all_thresholds_met:
            color = DISCORD_COLOR_SUCCESS
            status_emoji = "✅"
            status_text = "PASSED"
        elif analysis.overall_accuracy >= 80:
            color = DISCORD_COLOR_WARNING
            status_emoji = "⚠️"
            status_text = "WARNING"
        else:
            color = DISCORD_COLOR_FAILURE
            status_emoji = "❌"
            status_text = "FAILED"
        
        # Override color if comparison has regressions
        if comparison and comparison.verdict == ComparisonVerdict.FAIL:
            color = DISCORD_COLOR_FAILURE
            status_emoji = "🔻"
            status_text = "REGRESSION DETECTED"
        
        # Build embed
        embed = {
            "title": f"{status_emoji} Ash-Thrash Test Run: {status_text}",
            "description": f"Run ID: `{analysis.run_id}`",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {
                    "name": "📊 Overall Accuracy",
                    "value": f"**{analysis.overall_accuracy:.1f}%**",
                    "inline": True,
                },
                {
                    "name": "📋 Tests",
                    "value": f"✅ {analysis.passed_tests} | ❌ {analysis.failed_tests} | ⚠️ {analysis.error_tests}",
                    "inline": True,
                },
                {
                    "name": "⏱️ Duration",
                    "value": f"{analysis.test_run_duration_seconds:.1f}s",
                    "inline": True,
                },
                {
                    "name": "🎯 Thresholds",
                    "value": f"{analysis.thresholds_met_count}/{analysis.thresholds_total_count} met",
                    "inline": True,
                },
                {
                    "name": "⏱️ Latency (p95)",
                    "value": f"{analysis.latency_metrics.p95_ms:.0f}ms",
                    "inline": True,
                },
                {
                    "name": "⚠️ FP/FN Rate",
                    "value": f"FP: {analysis.false_positive_rate:.1f}% | FN: {analysis.false_negative_rate:.1f}%",
                    "inline": True,
                },
            ],
            "footer": {
                "text": f"Ash-Thrash {__version__} | The Alphabet Cartel 🏳️‍🌈",
            },
        }
        
        # Add comparison info if present
        if comparison:
            delta_str = f"{comparison.overall_accuracy_delta:+.1f}%"
            verdict_emoji = "✅" if comparison.verdict == ComparisonVerdict.PASS else "🔻"
            
            embed["fields"].append({
                "name": "📈 vs Baseline",
                "value": f"{verdict_emoji} {delta_str} ({comparison.baseline_name})",
                "inline": True,
            })
            
            if comparison.regressions:
                regression_text = "\n".join([
                    f"• {r.description}" for r in comparison.regressions[:3]
                ])
                if len(comparison.regressions) > 3:
                    regression_text += f"\n... and {len(comparison.regressions) - 3} more"
                
                embed["fields"].append({
                    "name": "🔻 Regressions",
                    "value": regression_text,
                    "inline": False,
                })
        
        # Send webhook
        payload = {
            "username": "Ash-Thrash",
            "avatar_url": "https://raw.githubusercontent.com/the-alphabet-cartel/ash/main/assets/ash-icon.png",
            "embeds": [embed],
        }
        
        try:
            async with httpx.AsyncClient(timeout=DISCORD_TIMEOUT) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
            
            self._logger.info("📨 Discord notification sent successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"❌ Failed to send Discord notification: {e}")
            return False
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get reporter status information."""
        return {
            "version": __version__,
            "report_directory": str(self._report_dir),
            "baseline_directory": str(self._baseline_dir),
            "baselines_available": self.list_baselines(),
            "regression_thresholds": self._regression_thresholds,
            "discord_configured": (
                self._secrets.has_discord_webhook() 
                if self._secrets else False
            ),
        }


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================

def create_report_manager(
    config_manager: Optional[Any] = None,
    secrets_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
    report_dir: Optional[str] = None,
    baseline_dir: Optional[str] = None,
) -> ReportManager:
    """
    Factory function for ReportManager (Clean Architecture v5.2.1 Pattern).
    
    This is the ONLY way to create a ReportManager instance.
    Direct instantiation should be avoided in production code.
    
    Args:
        config_manager: Optional ConfigManager for settings
        secrets_manager: Optional SecretsManager for Discord webhook
        logging_manager: Optional LoggingConfigManager for custom logging
        report_dir: Override report output directory
        baseline_dir: Override baseline storage directory
    
    Returns:
        Configured ReportManager instance
    
    Example:
        >>> reporter = create_report_manager(
        ...     config_manager=config,
        ...     secrets_manager=secrets,
        ...     logging_manager=logging_mgr,
        ... )
        >>> json_path = reporter.generate_json_report(analysis)
    """
    logger.debug("🏭 Creating ReportManager")
    
    return ReportManager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
        logging_manager=logging_manager,
        report_dir=report_dir,
        baseline_dir=baseline_dir,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "ReportManager",
    "create_report_manager",
    "BaselineComparison",
    "RegressionDetail",
    "ImprovementDetail",
    "ComparisonVerdict",
]
