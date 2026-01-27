#!/usr/bin/env python3
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
Main Entry Point for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-3-3.2-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 3 - Analysis & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

USAGE:
    # Run with default settings (starts API server)
    python main.py

    # Run tests immediately and exit
    python main.py --run-tests

    # Run tests for specific category
    python main.py --run-tests --category critical_high_priority

    # Run tests and save baseline
    python main.py --run-tests --save-baseline main

    # Run tests and compare to baseline
    python main.py --run-tests --compare-baseline main

    # Generate HTML reports
    python main.py --run-tests --report-format html

    # Run Ash-Vigil model evaluation
    python main.py --run-vigil-eval

    # Run Ash-Vigil evaluation and save baseline
    python main.py --run-vigil-eval --save-baseline primary-model-v1

    # Run with testing environment
    THRASH_ENVIRONMENT=testing python main.py

ENVIRONMENT VARIABLES:
    THRASH_ENVIRONMENT     - Environment (production, testing, development)
    THRASH_LOG_LEVEL       - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    THRASH_LOG_FORMAT      - Log format (human, json)
    THRASH_API_HOST        - API server host (default: 0.0.0.0)
    THRASH_API_PORT        - API server port (default: 30888)
    See .env.template for complete list
"""

import argparse
import asyncio
import os
import signal
import sys
from typing import List, Optional

import uvicorn

# Module version
__version__ = "v5.0-3-3.2-1"

# =============================================================================
# Manager Imports
# =============================================================================

from src.managers import (
    create_config_manager,
    create_secrets_manager,
    create_logging_config_manager,
    create_nlp_client_manager,
    create_phrase_loader_manager,
    create_test_runner_manager,
    create_result_analyzer_manager,
    create_report_manager,
    ConfigManager,
    SecretsManager,
    LoggingConfigManager,
    NLPClientManager,
    PhraseLoaderManager,
    TestRunnerManager,
    TestResult,
    ResultAnalyzerManager,
    ReportManager,
    AnalysisResult,
)

from src.validators import (
    create_classification_validator,
    create_response_validator,
    ClassificationValidator,
    ResponseValidator,
)

from src.evaluators import (
    create_vigil_evaluator,
    create_evaluation_report_generator,
    VigilEvaluator,
    EvaluationReportGenerator,
)

from src.api.app import create_app, app_state


# =============================================================================
# Constants
# =============================================================================

DEFAULT_API_HOST = "0.0.0.0"
DEFAULT_API_PORT = 30888


# =============================================================================
# Application Class
# =============================================================================


class AshThrash:
    """
    Main application class for Ash-Thrash testing suite.

    Manages lifecycle of all managers and coordinates test execution.

    Attributes:
        config: ConfigManager instance
        secrets: SecretsManager instance
        logging_mgr: LoggingConfigManager instance
        nlp_client: NLPClientManager instance
        phrase_loader: PhraseLoaderManager instance
        test_runner: TestRunnerManager instance
    """

    def __init__(self):
        """Initialize the application (managers created in startup)."""
        self.config: Optional[ConfigManager] = None
        self.secrets: Optional[SecretsManager] = None
        self.logging_mgr: Optional[LoggingConfigManager] = None
        self.nlp_client: Optional[NLPClientManager] = None
        self.phrase_loader: Optional[PhraseLoaderManager] = None
        self.classification_validator: Optional[ClassificationValidator] = None
        self.response_validator: Optional[ResponseValidator] = None
        self.test_runner: Optional[TestRunnerManager] = None
        self.result_analyzer: Optional[ResultAnalyzerManager] = None
        self.report_manager: Optional[ReportManager] = None
        self._logger = None
        self._shutdown_event = asyncio.Event()

    async def startup(self) -> bool:
        """
        Initialize all managers and verify system readiness.

        Returns:
            True if startup successful, False otherwise
        """
        try:
            # Step 1: Configuration Manager
            self.config = create_config_manager()

            # Step 2: Secrets Manager
            self.secrets = create_secrets_manager()

            # Step 3: Logging Manager (depends on config)
            self.logging_mgr = create_logging_config_manager(config_manager=self.config)
            self._logger = self.logging_mgr.get_logger("main")

            # Print startup banner
            # self._print_banner()

            # Step 4: NLP Client Manager (depends on config, logging)
            self._logger.info("Initializing NLP Client...")
            self.nlp_client = create_nlp_client_manager(
                config_manager=self.config,
                logging_manager=self.logging_mgr,
            )

            # Step 5: Phrase Loader Manager (depends on config, logging)
            self._logger.info("Loading test phrases...")
            self.phrase_loader = create_phrase_loader_manager(
                config_manager=self.config,
                logging_manager=self.logging_mgr,
            )

            # Step 6: Validators (Phase 2)
            self._logger.info("Initializing validators...")
            self.classification_validator = create_classification_validator(
                logging_manager=self.logging_mgr
            )
            self.response_validator = create_response_validator(
                logging_manager=self.logging_mgr
            )

            # Step 7: Test Runner (Phase 2)
            self._logger.info("Initializing test runner...")
            self.test_runner = create_test_runner_manager(
                nlp_client=self.nlp_client,
                phrase_loader=self.phrase_loader,
                classification_validator=self.classification_validator,
                response_validator=self.response_validator,
                config_manager=self.config,
                logging_manager=self.logging_mgr,
            )

            # Step 8: Result Analyzer (Phase 3)
            self._logger.info("Initializing result analyzer...")
            self.result_analyzer = create_result_analyzer_manager(
                config_manager=self.config,
                logging_manager=self.logging_mgr,
            )

            # Step 9: Report Manager (Phase 3)
            self._logger.info("Initializing report manager...")
            self.report_manager = create_report_manager(
                config_manager=self.config,
                secrets_manager=self.secrets,
                logging_manager=self.logging_mgr,
            )

            # Verify Ash-NLP connectivity
            self._logger.info("Checking Ash-NLP connectivity...")
            if await self.nlp_client.is_available():
                self._logger.success("Ash-NLP server is available")
            else:
                self._logger.warning(
                    "⚠️ Ash-NLP server is not available - tests will fail"
                )

            # Update API app state
            app_state.config_manager = self.config
            app_state.logging_manager = self.logging_mgr
            app_state.nlp_client = self.nlp_client
            app_state.phrase_loader = self.phrase_loader
            app_state.test_runner = self.test_runner
            app_state.is_ready = True

            # Print summary
            self._print_startup_summary()

            return True

        except Exception as e:
            if self._logger:
                self._logger.critical(f"Startup failed: {e}")
            else:
                print(f"🚨 CRITICAL: Startup failed: {e}", file=sys.stderr)
            return False

    async def shutdown(self) -> None:
        """Clean shutdown of all managers."""
        if self._logger:
            self._logger.info("Shutting down Ash-Thrash...")

        # Close NLP client connection
        if self.nlp_client:
            await self.nlp_client.close()

        if self._logger:
            self._logger.success("Shutdown complete")

    async def run_server(
        self, host: str = DEFAULT_API_HOST, port: int = DEFAULT_API_PORT
    ) -> int:
        """
        Run the API server.

        Args:
            host: Server host (default: 0.0.0.0)
            port: Server port (default: 30888)

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        # Startup
        if not await self.startup():
            return 1

        try:
            # Create FastAPI app with injected managers
            app = create_app(
                config_manager=self.config,
                logging_manager=self.logging_mgr,
                nlp_client=self.nlp_client,
                phrase_loader=self.phrase_loader,
                test_runner=self.test_runner,
            )

            self._logger.info(f"Starting API server on {host}:{port}")
            self._logger.info(f"Health endpoint: http://{host}:{port}/health")
            self._logger.info(f"API docs: http://{host}:{port}/docs")

            # Configure uvicorn
            config = uvicorn.Config(
                app,
                host=host,
                port=port,
                log_level="info",
                access_log=False,  # We handle logging ourselves
            )
            server = uvicorn.Server(config)

            # Run server
            await server.serve()

            return 0

        except Exception as e:
            self._logger.error(f"Server error: {e}")
            return 1

        finally:
            await self.shutdown()

    async def run_tests(
        self,
        categories: Optional[List[str]] = None,
        verbose: bool = False,
        save_baseline: Optional[str] = None,
        compare_baseline: Optional[str] = None,
        report_formats: Optional[List[str]] = None,
        send_discord: bool = False,
    ) -> int:
        """
        Run tests, analyze results, and generate reports.

        Args:
            categories: Optional list of categories to test
            verbose: Whether to show verbose output
            save_baseline: Name to save results as baseline (e.g., "main")
            compare_baseline: Name of baseline to compare against
            report_formats: List of report formats to generate (json, html)
            send_discord: Whether to send Discord notification

        Returns:
            Exit code (0 if all pass, 1 if any fail)
        """
        # Startup
        if not await self.startup():
            return 1

        try:
            self._logger.info("Starting test run...")

            # Progress callback for verbose output
            def progress_callback(current: int, total: int, result: TestResult):
                if verbose:
                    status_icon = (
                        "✅" if result.passed else "❌" if result.failed else "⚠️"
                    )
                    self._logger.info(
                        f"[{current}/{total}] {status_icon} {result.category}/{result.subcategory}"
                    )

            # Default report formats
            if report_formats is None:
                report_formats = ["json"]

            # Run tests
            summary = await self.test_runner.run_all_tests(
                categories=categories,
                progress_callback=progress_callback if verbose else None,
            )

            # Analyze results (Phase 3)
            self._logger.info("Analyzing results...")
            analysis = self.result_analyzer.analyze(summary)

            # Print results
            self._logger.info("=" * 60)
            self._logger.info("Test Run Results")
            self._logger.info("=" * 60)
            self._logger.info(f"  Run ID:        {summary.run_id}")
            self._logger.info(f"  Duration:      {summary.duration_seconds:.1f}s")
            self._logger.info(f"  Total Tests:   {summary.total_tests}")
            self._logger.info(f"  Passed:        {summary.passed_tests}")
            self._logger.info(f"  Failed:        {summary.failed_tests}")
            self._logger.info(f"  Errors:        {summary.error_tests}")
            self._logger.info(f"  Accuracy:      {analysis.overall_accuracy:.1f}%")
            self._logger.info(
                f"  Avg Response:  {summary.average_response_time_ms:.1f}ms"
            )
            self._logger.info(
                f"  P95 Response:  {analysis.latency_metrics.p95_ms:.1f}ms"
            )

            # Threshold status
            self._logger.info("-" * 60)
            self._logger.info("Threshold Status:")
            threshold_icon = "✅" if analysis.all_thresholds_met else "❌"
            self._logger.info(
                f"  {threshold_icon} {analysis.thresholds_met_count}/{analysis.thresholds_total_count} thresholds met"
            )

            for cat, result in analysis.threshold_results.items():
                status_icon = (
                    "✅"
                    if result.status.value == "met"
                    else "⚠️"
                    if result.status.value == "warning"
                    else "❌"
                )
                self._logger.info(
                    f"  {status_icon} {cat}: {result.actual_value:.1f}% (target: {result.target_value:.1f}%)"
                )

            # False positive/negative rates
            self._logger.info("-" * 60)
            self._logger.info("Detection Quality:")
            self._logger.info(
                f"  False Positive Rate: {analysis.false_positive_rate:.1f}%"
            )
            self._logger.info(
                f"  False Negative Rate: {analysis.false_negative_rate:.1f}%"
            )

            # Baseline comparison (Phase 3)
            comparison = None
            if compare_baseline:
                self._logger.info("-" * 60)
                self._logger.info(f"Comparing to baseline: {compare_baseline}")
                baseline = self.report_manager.load_baseline(compare_baseline)
                if baseline:
                    comparison = self.report_manager.compare_to_baseline(
                        analysis, baseline, compare_baseline
                    )

                    delta_icon = (
                        "📈" if comparison.overall_accuracy_delta >= 0 else "📉"
                    )
                    self._logger.info(
                        f"  {delta_icon} Accuracy change: {comparison.overall_accuracy_delta:+.1f}%"
                    )

                    if comparison.regressions:
                        self._logger.warning(
                            f"  🔻 {len(comparison.regressions)} regression(s) detected!"
                        )
                        for reg in comparison.regressions[:5]:
                            self._logger.warning(f"    - {reg.description}")

                    if comparison.improvements:
                        self._logger.info(
                            f"  🔺 {len(comparison.improvements)} improvement(s)"
                        )
                else:
                    self._logger.warning(f"  Baseline '{compare_baseline}' not found")

            # Generate reports (Phase 3)
            self._logger.info("=" * 60)
            self._logger.info("Generating reports...")

            if "json" in report_formats:
                json_path = self.report_manager.generate_json_report(
                    analysis, comparison
                )
                self._logger.info(f"  📄 JSON: {json_path}")

            if "html" in report_formats:
                html_path = self.report_manager.generate_html_report(
                    analysis, comparison
                )
                self._logger.info(f"  📄 HTML: {html_path}")

            # Save baseline (Phase 3)
            if save_baseline:
                baseline_path = self.report_manager.save_baseline(
                    analysis, save_baseline
                )
                self._logger.info(
                    f"  💾 Baseline '{save_baseline}' saved: {baseline_path}"
                )

            # Discord notification (Phase 3)
            if send_discord:
                self._logger.info("Sending Discord notification...")
                if await self.report_manager.send_discord_notification(
                    analysis, comparison
                ):
                    self._logger.success("  📨 Discord notification sent")

            self._logger.info("=" * 60)

            # Return exit code based on results
            exit_code = 0

            if summary.failed_tests > 0 or summary.error_tests > 0:
                self._logger.warning(
                    f"⚠️ {summary.failed_tests} failures, {summary.error_tests} errors"
                )
                exit_code = 1

            if comparison and comparison.verdict.value == "fail":
                self._logger.error(
                    f"🔻 Regression check failed: {comparison.verdict_reason}"
                )
                exit_code = 1

            if exit_code == 0:
                self._logger.success(f"✅ All {summary.passed_tests} tests passed!")

            return exit_code

        except Exception as e:
            self._logger.error(f"Test execution error: {e}")
            return 1

        finally:
            await self.shutdown()

    async def run_vigil_eval(
        self,
        categories: Optional[List[str]] = None,
        verbose: bool = False,
        save_baseline: Optional[str] = None,
        report_formats: Optional[List[str]] = None,
    ) -> int:
        """
        Run Ash-Vigil model evaluation against specialty phrases.

        Args:
            categories: Optional list of specialty categories to test
            verbose: Whether to show verbose output
            save_baseline: Name to save results as baseline
            report_formats: List of report formats to generate (json, html)

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        # Minimal startup - just config and logging
        try:
            self.config = create_config_manager()
            self.secrets = create_secrets_manager()
            self.logging_mgr = create_logging_config_manager(config_manager=self.config)
            self._logger = self.logging_mgr.get_logger("vigil_eval")
        except Exception as e:
            print(f"🚨 CRITICAL: Startup failed: {e}", file=sys.stderr)
            return 1

        # Default report formats
        if report_formats is None:
            report_formats = ["json", "html"]

        # Get Vigil configuration
        vigil_host = os.environ.get("THRASH_VIGIL_HOST", "10.20.30.14")
        vigil_port = int(os.environ.get("THRASH_VIGIL_PORT", "30882"))

        self._logger.info("=" * 60)
        self._logger.info("🔍 ASH-VIGIL MODEL EVALUATION")
        self._logger.info("=" * 60)
        self._logger.info(f"Target: Ash-Vigil at {vigil_host}:{vigil_port}")

        try:
            # Create evaluator
            evaluator = create_vigil_evaluator(
                vigil_host=vigil_host,
                vigil_port=vigil_port,
                timeout=120,
                batch_size=50,
                logging_manager=self.logging_mgr,
            )

            async with evaluator:
                # Check availability
                self._logger.info("Checking Ash-Vigil availability...")
                if not await evaluator.is_available():
                    self._logger.error(
                        f"❌ Ash-Vigil is not available at {vigil_host}:{vigil_port}"
                    )
                    return 1

                # Get model info
                version, model = await evaluator.get_vigil_info()
                self._logger.success(f"Connected to Ash-Vigil {version}")
                self._logger.info(f"Model: {model}")

                # Run evaluation
                self._logger.info("-" * 60)
                self._logger.info("Running evaluation (this may take 1-2 minutes)...")

                result = await evaluator.evaluate_model(categories=categories)

                # Print results
                self._logger.info("=" * 60)
                self._logger.info("📊 EVALUATION RESULTS")
                self._logger.info("=" * 60)
                self._logger.info(f"Status: {result.status.value}")
                self._logger.info(f"Model: {result.model_name}")
                self._logger.info(f"Total Phrases: {result.total_phrases}")
                self._logger.info(f"Overall Accuracy: {result.overall_accuracy:.1f}%")
                self._logger.info(f"  ✅ Passed: {result.total_passed}")
                self._logger.info(f"  ⬆️  Escalated: {result.total_escalated}")
                self._logger.info(f"  ❌ Failed: {result.total_failed}")
                self._logger.info(f"  ⚠️  Errors: {result.total_errors}")
                self._logger.info(f"Avg Inference: {result.average_inference_time_ms:.1f}ms")

                self._logger.info("-" * 60)
                self._logger.info("Per-Category Results:")
                for cat_name, cat_acc in result.category_accuracies.items():
                    status_icon = (
                        "✅" if cat_acc.accuracy >= 70
                        else "⚠️" if cat_acc.accuracy >= 50
                        else "❌"
                    )
                    self._logger.info(
                        f"  {status_icon} {cat_name}: {cat_acc.accuracy:.1f}% "
                        f"({cat_acc.passed + cat_acc.escalated}/{cat_acc.total_phrases})"
                    )

            # Generate reports
            self._logger.info("=" * 60)
            self._logger.info("Generating reports...")

            reporter = create_evaluation_report_generator(
                config_manager=self.config,
                logging_manager=self.logging_mgr,
            )

            if "json" in report_formats:
                json_path = reporter.generate_json_report(result, include_phrase_details=True)
                self._logger.info(f"  📄 JSON: {json_path}")

            if "html" in report_formats:
                html_path = reporter.generate_html_report(result)
                self._logger.info(f"  📄 HTML: {html_path}")

            if save_baseline:
                baseline_path = reporter.save_baseline(result, name=save_baseline)
                self._logger.info(f"  💾 Baseline '{save_baseline}' saved: {baseline_path}")

            # Decision gate summary
            self._logger.info("=" * 60)
            self._logger.info("📋 DECISION GATE SUMMARY")
            self._logger.info("-" * 60)

            targets = {
                "specialty_lgbtqia": {"min": 50, "target": 70},
                "specialty_gaming": {"min": 70, "target": 90},
                "specialty_slang": {"min": 40, "target": 60},
                "specialty_irony": {"min": 30, "target": 50},
                "specialty_multilang": {"min": 30, "target": 50},
                "specialty_quotes": {"min": 40, "target": 60},
            }

            all_minimum_met = True
            for cat_name, thresholds in targets.items():
                if cat_name in result.category_accuracies:
                    acc = result.category_accuracies[cat_name].accuracy
                    meets_min = acc >= thresholds["min"]
                    meets_target = acc >= thresholds["target"]

                    if meets_target:
                        status = "✅ TARGET MET"
                    elif meets_min:
                        status = "⚠️ MINIMUM MET"
                    else:
                        status = "❌ BELOW MINIMUM"
                        all_minimum_met = False

                    self._logger.info(
                        f"  {cat_name}: {acc:.1f}% "
                        f"(min: {thresholds['min']}%, target: {thresholds['target']}%) "
                        f"→ {status}"
                    )

            self._logger.info("=" * 60)
            if all_minimum_met:
                self._logger.success("✅ RECOMMENDATION: Proceed to Phase 3")
                self._logger.info("   All categories meet minimum thresholds.")
            else:
                self._logger.warning("⚠️ RECOMMENDATION: Review results before proceeding")
                self._logger.info("   Some categories are below minimum thresholds.")

            return 0 if all_minimum_met else 1

        except Exception as e:
            self._logger.error(f"Evaluation error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def _print_banner(self) -> None:
        """Print the startup banner."""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                       ║
║     █████╗ ███████╗██╗  ██╗      ████████╗██╗  ██╗██████╗  █████╗ ███████╗██╗  ██╗    ║
║    ██╔══██╗██╔════╝██║  ██║      ╚══██╔══╝██║  ██║██╔══██╗██╔══██╗██╔════╝██║  ██║    ║
║    ███████║███████╗███████║█████╗   ██║   ███████║██████╔╝███████║███████╗███████║    ║
║    ██╔══██║╚════██║██╔══██║╚════╝   ██║   ██╔══██║██╔══██╗██╔══██║╚════██║██╔══██║    ║
║    ██║  ██║███████║██║  ██║         ██║   ██║  ██║██║  ██║██║  ██║███████║██║  ██║    ║
║    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝         ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ║
║                                                                                       ║
║                         Crisis Detection Testing Suite v5.0                           ║
║                                                                                       ║
║                   The Alphabet Cartel - https://discord.gg/alphabetcartel             ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝
"""
        # Print banner without logging (direct to console)
        print(banner)

        self._logger.info(f"Ash-Thrash {__version__} starting...")
        self._logger.info(f"Environment: {self.config.get_environment()}")

    def _print_startup_summary(self) -> None:
        """Print startup summary."""
        stats = self.phrase_loader.get_statistics()

        self._logger.info("=" * 60)
        self._logger.info("Startup Summary")
        self._logger.info("=" * 60)
        self._logger.info(f"  Environment:    {self.config.get_environment()}")
        self._logger.info(f"  Log Level:      {self.logging_mgr.log_level}")
        self._logger.info(f"  NLP Server:     {self.nlp_client.base_url}")
        self._logger.info(f"  Total Phrases:  {stats.total_phrases}")
        self._logger.info(f"  Files Loaded:   {stats.files_loaded}")

        if stats.by_category_type:
            self._logger.info("  By Type:")
            for cat_type, count in stats.by_category_type.items():
                self._logger.info(f"    - {cat_type}: {count}")

        webhook_status = (
            "Configured" if self.secrets.has_discord_webhook() else "Not configured"
        )
        self._logger.info(f"  Discord Webhook: {webhook_status}")
        self._logger.info("=" * 60)
        self._logger.success("Ash-Thrash initialized successfully")


# =============================================================================
# CLI Argument Parser
# =============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Ash-Thrash: Discord Crisis Detection Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          Start API server
  python main.py --run-tests              Run all tests and exit
  python main.py --run-tests --verbose    Run tests with verbose output
  python main.py --run-tests --category critical_high_priority
  python main.py --run-tests --save-baseline main
  python main.py --run-tests --compare-baseline main
  python main.py --run-tests --report-format html --report-format json
  python main.py --run-tests --send-discord
  python main.py --run-vigil-eval         Run Ash-Vigil model evaluation
  python main.py --run-vigil-eval --save-baseline primary-model-v1
        """,
    )

    # Server options
    parser.add_argument(
        "--host",
        default=os.environ.get("THRASH_API_HOST", DEFAULT_API_HOST),
        help=f"API server host (default: {DEFAULT_API_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("THRASH_API_PORT", DEFAULT_API_PORT)),
        help=f"API server port (default: {DEFAULT_API_PORT})",
    )

    # Test execution options
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run tests immediately and exit (don't start server)",
    )
    parser.add_argument(
        "--run-vigil-eval",
        action="store_true",
        help="Run Ash-Vigil model evaluation against specialty phrases",
    )
    parser.add_argument(
        "--category",
        action="append",
        dest="categories",
        help="Category to test (can be specified multiple times)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output during test execution",
    )

    # Phase 3: Reporting options
    parser.add_argument(
        "--save-baseline",
        metavar="NAME",
        help="Save results as named baseline (e.g., 'main', 'pre-release')",
    )
    parser.add_argument(
        "--compare-baseline",
        metavar="NAME",
        help="Compare results against named baseline for regression detection",
    )
    parser.add_argument(
        "--report-format",
        action="append",
        dest="report_formats",
        choices=["json", "html"],
        help="Report format to generate (can be specified multiple times, default: json)",
    )
    parser.add_argument(
        "--send-discord",
        action="store_true",
        help="Send results to Discord webhook (requires configured webhook)",
    )

    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"Ash-Thrash {__version__}",
    )

    return parser.parse_args()


# =============================================================================
# Entry Point
# =============================================================================


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code
    """
    args = parse_args()
    app = AshThrash()

    try:
        if args.run_vigil_eval:
            # Run Ash-Vigil model evaluation
            return asyncio.run(
                app.run_vigil_eval(
                    categories=args.categories,
                    verbose=args.verbose,
                    save_baseline=args.save_baseline,
                    report_formats=args.report_formats,
                )
            )
        elif args.run_tests:
            # Run tests and exit
            return asyncio.run(
                app.run_tests(
                    categories=args.categories,
                    verbose=args.verbose,
                    save_baseline=args.save_baseline,
                    compare_baseline=args.compare_baseline,
                    report_formats=args.report_formats,
                    send_discord=args.send_discord,
                )
            )
        else:
            # Run API server
            return asyncio.run(
                app.run_server(
                    host=args.host,
                    port=args.port,
                )
            )
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        return 0


if __name__ == "__main__":
    sys.exit(main())
