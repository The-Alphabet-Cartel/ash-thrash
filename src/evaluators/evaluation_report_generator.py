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
Evaluation Report Generator - Model Comparison Reports for Ash-Vigil
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.4-1
LAST MODIFIED: 2026-01-26
PHASE: Phase 2 - Ash-Thrash Evaluation Infrastructure
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Generate JSON reports from EvaluationResult
- Generate HTML reports with visual comparison charts
- Support side-by-side model comparison
- Save baseline evaluations for future reference
- Load and compare against stored baselines

DESIGN NOTE:
This generator focuses on Ash-Vigil model evaluation reports, distinct from
the general Ash-Thrash test reports. It provides specialized visualizations
for model comparison and specialty category performance.

REPORT TYPES:
- Single Model Report: Detailed metrics for one model evaluation
- Comparison Report: Side-by-side comparison of multiple models
- Baseline Report: Comparison against a stored baseline evaluation

USAGE:
    from src.evaluators import create_evaluation_report_generator
    
    reporter = create_evaluation_report_generator(config_manager=config)
    
    # Generate single model report
    json_path = reporter.generate_json_report(evaluation_result)
    html_path = reporter.generate_html_report(evaluation_result)
    
    # Save as baseline
    reporter.save_baseline(evaluation_result, name="primary-model-v1")
    
    # Compare multiple models
    comparison = reporter.compare_models([result1, result2])
    reporter.generate_comparison_report(comparison)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .vigil_evaluator import (
    EvaluationResult,
    EvaluationStatus,
    CategoryAccuracy,
    PhraseResult,
    PassStatus,
)

# Module version
__version__ = "v5.0-2-2.4-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default directories
DEFAULT_EVALUATION_REPORT_DIR = "/app/reports/evaluations"
DEFAULT_EVALUATION_BASELINE_DIR = "/app/reports/evaluations/baselines"

# Report filename patterns
EVALUATION_JSON_PATTERN = "vigil_eval_{model}_{timestamp}.json"
EVALUATION_HTML_PATTERN = "vigil_eval_{model}_{timestamp}.html"
COMPARISON_JSON_PATTERN = "vigil_comparison_{timestamp}.json"
COMPARISON_HTML_PATTERN = "vigil_comparison_{timestamp}.html"
BASELINE_PATTERN = "baseline_{name}.json"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ModelPerformance:
    """Performance summary for a single model."""
    model_name: str
    overall_accuracy: float
    overall_pass_rate: float
    total_phrases: int
    total_passed: int
    total_failed: int
    total_escalated: int
    average_inference_ms: float
    categories: Dict[str, float] = field(default_factory=dict)  # category -> accuracy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "model_name": self.model_name,
            "overall_accuracy": round(self.overall_accuracy, 2),
            "overall_pass_rate": round(self.overall_pass_rate, 2),
            "total_phrases": self.total_phrases,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "total_escalated": self.total_escalated,
            "average_inference_ms": round(self.average_inference_ms, 2),
            "categories": {k: round(v, 2) for k, v in self.categories.items()},
        }


@dataclass
class ModelComparison:
    """Comparison of multiple model evaluations."""
    comparison_id: str
    timestamp: datetime
    models_compared: List[str]
    
    # Performance data for each model
    model_performances: Dict[str, ModelPerformance] = field(default_factory=dict)
    
    # Best performers by category
    best_overall: str = ""
    best_by_category: Dict[str, str] = field(default_factory=dict)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "comparison_id": self.comparison_id,
            "timestamp": self.timestamp.isoformat(),
            "models_compared": self.models_compared,
            "model_performances": {
                k: v.to_dict() for k, v in self.model_performances.items()
            },
            "best_overall": self.best_overall,
            "best_by_category": self.best_by_category,
            "recommendations": self.recommendations,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelComparison":
        """Create ModelComparison from dictionary."""
        comparison = cls(
            comparison_id=data.get("comparison_id", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            models_compared=data.get("models_compared", []),
        )
        comparison.best_overall = data.get("best_overall", "")
        comparison.best_by_category = data.get("best_by_category", {})
        comparison.recommendations = data.get("recommendations", [])
        return comparison


# =============================================================================
# Evaluation Report Generator
# =============================================================================

class EvaluationReportGenerator:
    """
    Generates evaluation reports and comparison charts for Ash-Vigil model testing.
    
    This generator creates detailed reports focused on model evaluation:
    - Per-category accuracy breakdowns
    - Side-by-side model comparisons
    - Visual charts for performance analysis
    - Baseline storage and comparison
    
    Attributes:
        report_dir: Directory for report output
        baseline_dir: Directory for baseline storage
        jinja_env: Jinja2 environment for HTML templates
    
    Example:
        >>> reporter = create_evaluation_report_generator(config_manager=config)
        >>> 
        >>> # Generate reports for a single evaluation
        >>> json_path = reporter.generate_json_report(result)
        >>> html_path = reporter.generate_html_report(result)
        >>> 
        >>> # Compare multiple models
        >>> comparison = reporter.compare_models([result1, result2])
        >>> reporter.generate_comparison_report(comparison)
    """
    
    def __init__(
        self,
        config_manager: Optional[Any] = None,
        logging_manager: Optional[Any] = None,
        report_dir: Optional[str] = None,
        baseline_dir: Optional[str] = None,
    ):
        """
        Initialize the EvaluationReportGenerator.
        
        Args:
            config_manager: Optional ConfigManager
            logging_manager: Optional LoggingConfigManager
            report_dir: Override report output directory
            baseline_dir: Override baseline storage directory
        
        Note:
            Use create_evaluation_report_generator() factory function instead.
        """
        self._config = config_manager
        
        # Set up logger
        if logging_manager:
            self._logger = logging_manager.get_logger("evaluation_report_generator")
        else:
            self._logger = logger
        
        # Resolve directories
        self._report_dir = Path(self._resolve_report_dir(report_dir))
        self._baseline_dir = Path(self._resolve_baseline_dir(baseline_dir))
        
        # Initialize Jinja2 environment
        self._jinja_env = self._setup_jinja_environment()
        
        # Ensure directories exist
        self._ensure_directories()
        
        self._logger.info(
            f"✅ EvaluationReportGenerator {__version__} initialized "
            f"(reports: {self._report_dir}, baselines: {self._baseline_dir})"
        )
    
    def _resolve_report_dir(self, override: Optional[str]) -> str:
        """Resolve report directory from config or default."""
        if override:
            return override
        if self._config:
            path = self._config.get("vigil_evaluation", "report_directory")
            if path:
                return path
        return DEFAULT_EVALUATION_REPORT_DIR
    
    def _resolve_baseline_dir(self, override: Optional[str]) -> str:
        """Resolve baseline directory from config or default."""
        if override:
            return override
        if self._config:
            path = self._config.get("vigil_evaluation", "baseline_directory")
            if path:
                return path
        return DEFAULT_EVALUATION_BASELINE_DIR
    
    def _setup_jinja_environment(self) -> Environment:
        """Set up Jinja2 environment for HTML templates."""
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
        
        self._logger.debug("📄 Using embedded HTML template")
        return Environment(autoescape=select_autoescape(['html', 'xml']))
    
    def _ensure_directories(self) -> None:
        """Ensure report and baseline directories exist."""
        try:
            self._report_dir.mkdir(parents=True, exist_ok=True)
            self._baseline_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self._logger.warning(f"⚠️ Failed to create directories: {e}")
    
    def _sanitize_model_name(self, model_name: str) -> str:
        """Sanitize model name for use in filenames."""
        return model_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
    
    # =========================================================================
    # Single Model Reports
    # =========================================================================
    
    def generate_json_report(
        self,
        evaluation: EvaluationResult,
        filename: Optional[str] = None,
        include_phrase_details: bool = False,
    ) -> Path:
        """
        Generate a JSON report for a single model evaluation.
        
        Args:
            evaluation: EvaluationResult to report
            filename: Override filename
            include_phrase_details: Include individual phrase results
        
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        
        if filename is None:
            model_safe = self._sanitize_model_name(evaluation.model_name)
            filename = EVALUATION_JSON_PATTERN.format(
                model=model_safe,
                timestamp=timestamp,
            )
        
        # Build report structure
        report = {
            "_metadata": {
                "report_type": "vigil_model_evaluation",
                "report_version": "v5.0",
                "generated_at": datetime.now().isoformat(),
                "ash_thrash_version": __version__,
            },
            "evaluation": evaluation.to_dict(),
        }
        
        # Optionally include all phrase results
        if include_phrase_details:
            report["phrase_details"] = [
                pr.to_dict() for pr in evaluation.phrase_results
            ]
        else:
            # Include only failed phrases
            report["failed_phrases"] = [
                pr.to_dict() for pr in evaluation.failed_phrase_results[:100]
            ]
            if len(evaluation.failed_phrase_results) > 100:
                report["failed_phrases_truncated"] = True
                report["total_failed"] = len(evaluation.failed_phrase_results)
        
        # Write to file
        output_path = self._report_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self._logger.info(f"📄 JSON evaluation report saved: {output_path}")
            return output_path
            
        except Exception as e:
            self._logger.error(f"❌ Failed to save JSON report: {e}")
            raise
    
    def generate_html_report(
        self,
        evaluation: EvaluationResult,
        comparison: Optional[ModelComparison] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Generate an HTML report for a single model evaluation.
        
        Args:
            evaluation: EvaluationResult to report
            comparison: Optional comparison data to include
            filename: Override filename
        
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        
        if filename is None:
            model_safe = self._sanitize_model_name(evaluation.model_name)
            filename = EVALUATION_HTML_PATTERN.format(
                model=model_safe,
                timestamp=timestamp,
            )
        
        # Try to load template file
        try:
            template = self._jinja_env.get_template("vigil_evaluation_report.jinja2")
        except Exception:
            template = self._jinja_env.from_string(self._get_embedded_evaluation_template())
        
        # Prepare template context
        context = {
            "evaluation": evaluation,
            "comparison": comparison,
            "generated_at": datetime.now().isoformat(),
            "version": __version__,
            "failed_phrases": evaluation.failed_phrase_results[:50],
            "show_more_failures": len(evaluation.failed_phrase_results) > 50,
            "total_failures": len(evaluation.failed_phrase_results),
        }
        
        # Render template
        html_content = template.render(**context)
        
        # Write to file
        output_path = self._report_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self._logger.info(f"📄 HTML evaluation report saved: {output_path}")
            return output_path
            
        except Exception as e:
            self._logger.error(f"❌ Failed to save HTML report: {e}")
            raise
    
    # =========================================================================
    # Model Comparison
    # =========================================================================
    
    def compare_models(
        self,
        evaluations: List[EvaluationResult],
    ) -> ModelComparison:
        """
        Compare multiple model evaluations.
        
        Args:
            evaluations: List of EvaluationResult objects to compare
        
        Returns:
            ModelComparison with analysis results
        """
        import uuid
        
        comparison_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        comparison = ModelComparison(
            comparison_id=comparison_id,
            timestamp=datetime.now(),
            models_compared=[e.model_name for e in evaluations],
        )
        
        # Build performance data for each model
        best_accuracy = -1.0
        best_model = ""
        category_best: Dict[str, tuple] = {}  # category -> (accuracy, model)
        
        for eval_result in evaluations:
            model_name = eval_result.model_name
            
            # Category accuracies
            categories = {}
            for cat_name, cat_acc in eval_result.category_accuracies.items():
                categories[cat_name] = cat_acc.accuracy
                
                # Track best per category
                if cat_name not in category_best or cat_acc.accuracy > category_best[cat_name][0]:
                    category_best[cat_name] = (cat_acc.accuracy, model_name)
            
            performance = ModelPerformance(
                model_name=model_name,
                overall_accuracy=eval_result.overall_accuracy,
                overall_pass_rate=eval_result.overall_pass_rate,
                total_phrases=eval_result.total_phrases,
                total_passed=eval_result.total_passed,
                total_failed=eval_result.total_failed,
                total_escalated=eval_result.total_escalated,
                average_inference_ms=eval_result.average_inference_time_ms,
                categories=categories,
            )
            
            comparison.model_performances[model_name] = performance
            
            # Track overall best
            if eval_result.overall_accuracy > best_accuracy:
                best_accuracy = eval_result.overall_accuracy
                best_model = model_name
        
        comparison.best_overall = best_model
        comparison.best_by_category = {
            cat: model for cat, (acc, model) in category_best.items()
        }
        
        # Generate recommendations
        comparison.recommendations = self._generate_recommendations(comparison)
        
        self._logger.info(
            f"📊 Model comparison complete: {len(evaluations)} models, "
            f"best overall: {best_model} ({best_accuracy:.1f}%)"
        )
        
        return comparison
    
    def _generate_recommendations(self, comparison: ModelComparison) -> List[str]:
        """Generate recommendations based on comparison results."""
        recommendations = []
        
        if not comparison.model_performances:
            return ["No models evaluated yet"]
        
        # Find the best overall model
        best = comparison.model_performances.get(comparison.best_overall)
        if best:
            if best.overall_accuracy >= 80:
                recommendations.append(
                    f"✅ {comparison.best_overall} achieves {best.overall_accuracy:.1f}% overall accuracy - "
                    "suitable for production use"
                )
            elif best.overall_accuracy >= 60:
                recommendations.append(
                    f"⚠️ {comparison.best_overall} achieves {best.overall_accuracy:.1f}% overall accuracy - "
                    "consider tuning thresholds or evaluating alternative models"
                )
            else:
                recommendations.append(
                    f"❌ {comparison.best_overall} achieves only {best.overall_accuracy:.1f}% overall accuracy - "
                    "evaluation of alternative models recommended"
                )
        
        # Check for category-specific insights
        for cat, model in comparison.best_by_category.items():
            perf = comparison.model_performances.get(model)
            if perf and cat in perf.categories:
                cat_acc = perf.categories[cat]
                
                if "lgbtqia" in cat.lower() and cat_acc < 70:
                    recommendations.append(
                        f"⚠️ LGBTQIA+ category at {cat_acc:.1f}% - critical for community safety, "
                        "consider fine-tuning or additional training data"
                    )
                elif "gaming" in cat.lower() and cat_acc < 80:
                    recommendations.append(
                        f"ℹ️ Gaming context at {cat_acc:.1f}% - may have elevated false positive rates"
                    )
        
        # Inference time recommendations
        for model_name, perf in comparison.model_performances.items():
            if perf.average_inference_ms > 100:
                recommendations.append(
                    f"⏱️ {model_name} averages {perf.average_inference_ms:.0f}ms per phrase - "
                    "may impact real-time performance"
                )
        
        return recommendations if recommendations else ["No specific recommendations"]
    
    def generate_comparison_report(
        self,
        comparison: ModelComparison,
        json_filename: Optional[str] = None,
        html_filename: Optional[str] = None,
    ) -> tuple:
        """
        Generate both JSON and HTML comparison reports.
        
        Args:
            comparison: ModelComparison to report
            json_filename: Override JSON filename
            html_filename: Override HTML filename
        
        Returns:
            Tuple of (json_path, html_path)
        """
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        
        # Generate JSON
        if json_filename is None:
            json_filename = COMPARISON_JSON_PATTERN.format(timestamp=timestamp)
        
        json_report = {
            "_metadata": {
                "report_type": "vigil_model_comparison",
                "report_version": "v5.0",
                "generated_at": datetime.now().isoformat(),
                "ash_thrash_version": __version__,
            },
            "comparison": comparison.to_dict(),
        }
        
        json_path = self._report_dir / json_filename
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        
        # Generate HTML
        if html_filename is None:
            html_filename = COMPARISON_HTML_PATTERN.format(timestamp=timestamp)
        
        try:
            template = self._jinja_env.get_template("vigil_comparison_report.jinja2")
        except Exception:
            template = self._jinja_env.from_string(self._get_embedded_comparison_template())
        
        context = {
            "comparison": comparison,
            "generated_at": datetime.now().isoformat(),
            "version": __version__,
        }
        
        html_content = template.render(**context)
        html_path = self._report_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self._logger.info(f"📄 Comparison reports saved: {json_path}, {html_path}")
        
        return (json_path, html_path)
    
    # =========================================================================
    # Baseline Operations
    # =========================================================================
    
    def save_baseline(
        self,
        evaluation: EvaluationResult,
        name: str = "primary",
    ) -> Path:
        """
        Save an evaluation result as a named baseline.
        
        Args:
            evaluation: EvaluationResult to save
            name: Baseline name
        
        Returns:
            Path to saved baseline file
        """
        filename = BASELINE_PATTERN.format(name=name)
        output_path = self._baseline_dir / filename
        
        baseline_data = {
            "_metadata": {
                "baseline_type": "vigil_evaluation",
                "baseline_version": "v5.0",
                "saved_at": datetime.now().isoformat(),
                "name": name,
            },
            "evaluation": evaluation.to_dict(),
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)
            
            self._logger.info(f"💾 Baseline '{name}' saved: {output_path}")
            return output_path
            
        except Exception as e:
            self._logger.error(f"❌ Failed to save baseline '{name}': {e}")
            raise
    
    def load_baseline(self, name: str = "primary") -> Optional[EvaluationResult]:
        """
        Load a named baseline.
        
        Args:
            name: Baseline name to load
        
        Returns:
            EvaluationResult or None if not found
        """
        filename = BASELINE_PATTERN.format(name=name)
        filepath = self._baseline_dir / filename
        
        if not filepath.exists():
            self._logger.warning(f"⚠️ Baseline '{name}' not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            evaluation = EvaluationResult.from_dict(data["evaluation"])
            self._logger.info(
                f"📂 Baseline '{name}' loaded (model: {evaluation.model_name})"
            )
            return evaluation
            
        except Exception as e:
            self._logger.error(f"❌ Failed to load baseline '{name}': {e}")
            return None
    
    def list_baselines(self) -> List[str]:
        """List all available baseline names."""
        baselines = []
        
        try:
            for filepath in self._baseline_dir.glob("baseline_*.json"):
                name = filepath.stem.replace("baseline_", "")
                baselines.append(name)
        except Exception as e:
            self._logger.warning(f"⚠️ Failed to list baselines: {e}")
        
        return sorted(baselines)
    
    # =========================================================================
    # Embedded Templates
    # =========================================================================
    
    def _get_embedded_evaluation_template(self) -> str:
        """Return embedded HTML template for single evaluation report."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ash-Vigil Evaluation: {{ evaluation.model_name }}</title>
    <style>
        :root {
            --color-pass: #2ecc71;
            --color-fail: #e74c3c;
            --color-warning: #f39c12;
            --color-info: #3498db;
            --color-escalated: #9b59b6;
            --color-bg: #1a1a2e;
            --color-surface: #16213e;
            --color-text: #eee;
            --color-text-muted: #aaa;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
        header h1 { color: var(--color-info); margin-bottom: 0.5rem; }
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
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }
        .stat-box {
            background: rgba(255,255,255,0.05);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        .stat-box .value { font-size: 2rem; font-weight: bold; }
        .stat-box .label { color: var(--color-text-muted); font-size: 0.85rem; }
        .status-pass { color: var(--color-pass); }
        .status-fail { color: var(--color-fail); }
        .status-warning { color: var(--color-warning); }
        .status-escalated { color: var(--color-escalated); }
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
        .badge-escalated { background: var(--color-escalated); color: #fff; }
        .progress-bar {
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            height: 24px;
            overflow: hidden;
            position: relative;
        }
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            color: #000;
            font-weight: bold;
            font-size: 0.85rem;
        }
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
            <h1>🔍 Ash-Vigil Model Evaluation</h1>
            <p class="subtitle">Model: <strong>{{ evaluation.model_name }}</strong></p>
            <p class="subtitle">Evaluation ID: {{ evaluation.evaluation_id }}</p>
            <p class="subtitle">Generated: {{ generated_at }}</p>
        </header>

        <!-- Summary -->
        <div class="card">
            <h2>📊 Overall Performance</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="value {% if evaluation.overall_accuracy >= 80 %}status-pass{% elif evaluation.overall_accuracy >= 60 %}status-warning{% else %}status-fail{% endif %}">
                        {{ "%.1f"|format(evaluation.overall_accuracy) }}%
                    </div>
                    <div class="label">Overall Accuracy</div>
                </div>
                <div class="stat-box">
                    <div class="value">{{ evaluation.total_phrases }}</div>
                    <div class="label">Total Phrases</div>
                </div>
                <div class="stat-box">
                    <div class="value status-pass">{{ evaluation.total_passed }}</div>
                    <div class="label">Passed</div>
                </div>
                <div class="stat-box">
                    <div class="value status-escalated">{{ evaluation.total_escalated }}</div>
                    <div class="label">Escalated</div>
                </div>
                <div class="stat-box">
                    <div class="value status-fail">{{ evaluation.total_failed }}</div>
                    <div class="label">Failed</div>
                </div>
                <div class="stat-box">
                    <div class="value">{{ "%.1f"|format(evaluation.average_inference_time_ms) }}ms</div>
                    <div class="label">Avg Inference</div>
                </div>
            </div>
        </div>

        <!-- Category Breakdown -->
        <div class="card">
            <h2>📂 Category Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Accuracy</th>
                        <th>Passed</th>
                        <th>Escalated</th>
                        <th>Failed</th>
                        <th>Performance</th>
                    </tr>
                </thead>
                <tbody>
                    {% for name, cat in evaluation.category_accuracies.items() %}
                    <tr>
                        <td><strong>{{ name }}</strong></td>
                        <td class="{% if cat.accuracy >= 80 %}status-pass{% elif cat.accuracy >= 60 %}status-warning{% else %}status-fail{% endif %}">
                            {{ "%.1f"|format(cat.accuracy) }}%
                        </td>
                        <td class="status-pass">{{ cat.passed }}</td>
                        <td class="status-escalated">{{ cat.escalated }}</td>
                        <td class="status-fail">{{ cat.failed }}</td>
                        <td style="width: 200px;">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {{ cat.accuracy }}%; background: {% if cat.accuracy >= 80 %}var(--color-pass){% elif cat.accuracy >= 60 %}var(--color-warning){% else %}var(--color-fail){% endif %};">
                                    {{ "%.0f"|format(cat.accuracy) }}%
                                </div>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {% if failed_phrases %}
        <!-- Failed Phrases -->
        <div class="card">
            <h2>❌ Failed Phrases ({{ total_failures }})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Subcategory</th>
                        <th>Expected</th>
                        <th>Actual</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    {% for phrase in failed_phrases %}
                    <tr>
                        <td>{{ phrase.category }}</td>
                        <td>{{ phrase.subcategory }}</td>
                        <td>{{ phrase.expected_risk_levels|join(', ') }}</td>
                        <td class="status-fail">{{ phrase.vigil_risk_level }}</td>
                        <td>{{ "%.2f"|format(phrase.vigil_confidence) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% if show_more_failures %}
            <p style="margin-top: 1rem; color: var(--color-text-muted);">
                Showing 50 of {{ total_failures }} failed phrases. See JSON report for full details.
            </p>
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
    
    def _get_embedded_comparison_template(self) -> str:
        """Return embedded HTML template for model comparison report."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ash-Vigil Model Comparison</title>
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
            --color-best: #f1c40f;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
            padding: 2rem;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            text-align: center;
            padding: 2rem;
            background: var(--color-surface);
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        header h1 { color: var(--color-info); margin-bottom: 0.5rem; }
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
        .best { background: rgba(241, 196, 15, 0.2); }
        .best::after { content: " 🏆"; }
        .recommendation {
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
        }
        footer {
            text-align: center;
            padding: 2rem;
            color: var(--color-text-muted);
        }
        footer a { color: var(--color-info); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Ash-Vigil Model Comparison</h1>
            <p>Comparison ID: {{ comparison.comparison_id }}</p>
            <p>Models: {{ comparison.models_compared|join(', ') }}</p>
            <p>Generated: {{ generated_at }}</p>
        </header>

        <!-- Overall Comparison -->
        <div class="card">
            <h2>🏆 Overall Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Accuracy</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Escalated</th>
                        <th>Avg Inference</th>
                    </tr>
                </thead>
                <tbody>
                    {% for model_name, perf in comparison.model_performances.items() %}
                    <tr class="{% if model_name == comparison.best_overall %}best{% endif %}">
                        <td><strong>{{ model_name }}</strong></td>
                        <td>{{ "%.1f"|format(perf.overall_accuracy) }}%</td>
                        <td>{{ perf.total_passed }}</td>
                        <td>{{ perf.total_failed }}</td>
                        <td>{{ perf.total_escalated }}</td>
                        <td>{{ "%.1f"|format(perf.average_inference_ms) }}ms</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Category Comparison -->
        <div class="card">
            <h2>📂 Per-Category Comparison</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        {% for model_name in comparison.models_compared %}
                        <th>{{ model_name.split('/')[-1] }}</th>
                        {% endfor %}
                        <th>Best</th>
                    </tr>
                </thead>
                <tbody>
                    {% for category in comparison.best_by_category.keys() %}
                    <tr>
                        <td><strong>{{ category }}</strong></td>
                        {% for model_name in comparison.models_compared %}
                        {% set perf = comparison.model_performances[model_name] %}
                        <td class="{% if model_name == comparison.best_by_category[category] %}best{% endif %}">
                            {{ "%.1f"|format(perf.categories.get(category, 0)) }}%
                        </td>
                        {% endfor %}
                        <td>{{ comparison.best_by_category[category].split('/')[-1] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Recommendations -->
        <div class="card">
            <h2>💡 Recommendations</h2>
            {% for rec in comparison.recommendations %}
            <div class="recommendation">{{ rec }}</div>
            {% endfor %}
        </div>

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
    # Status
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get reporter status information."""
        return {
            "version": __version__,
            "report_directory": str(self._report_dir),
            "baseline_directory": str(self._baseline_dir),
            "baselines_available": self.list_baselines(),
        }


# =============================================================================
# Factory Function - Clean Architecture v5.2.3 Compliance (Rule #1)
# =============================================================================

def create_evaluation_report_generator(
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
    report_dir: Optional[str] = None,
    baseline_dir: Optional[str] = None,
) -> EvaluationReportGenerator:
    """
    Factory function for EvaluationReportGenerator (Clean Architecture v5.2.3 Pattern).
    
    This is the ONLY way to create an EvaluationReportGenerator instance.
    Direct instantiation should be avoided in production code.
    
    Args:
        config_manager: Optional ConfigManager for settings
        logging_manager: Optional LoggingConfigManager for custom logging
        report_dir: Override report output directory
        baseline_dir: Override baseline storage directory
    
    Returns:
        Configured EvaluationReportGenerator instance
    
    Example:
        >>> reporter = create_evaluation_report_generator(
        ...     config_manager=config,
        ...     logging_manager=logging_mgr,
        ... )
        >>> json_path = reporter.generate_json_report(evaluation)
    """
    logger.debug("🏭 Creating EvaluationReportGenerator")
    
    return EvaluationReportGenerator(
        config_manager=config_manager,
        logging_manager=logging_manager,
        report_dir=report_dir,
        baseline_dir=baseline_dir,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "EvaluationReportGenerator",
    "create_evaluation_report_generator",
    "ModelComparison",
    "ModelPerformance",
]
