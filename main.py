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
FILE VERSION: v5.0-2-2.4-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 2 - Test Execution Engine
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
__version__ = "v5.0-2-2.4-1"

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
    ConfigManager,
    SecretsManager,
    LoggingConfigManager,
    NLPClientManager,
    PhraseLoaderManager,
    TestRunnerManager,
    TestResult,
)

from src.validators import (
    create_classification_validator,
    create_response_validator,
    ClassificationValidator,
    ResponseValidator,
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
            self.logging_mgr = create_logging_config_manager(
                config_manager=self.config
            )
            self._logger = self.logging_mgr.get_logger("main")
            
            # Print startup banner
            self._print_banner()
            
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
            
            # Verify Ash-NLP connectivity
            self._logger.info("Checking Ash-NLP connectivity...")
            if await self.nlp_client.is_available():
                self._logger.success("Ash-NLP server is available")
            else:
                self._logger.warning("⚠️ Ash-NLP server is not available - tests will fail")
            
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
    
    async def run_server(self, host: str = DEFAULT_API_HOST, port: int = DEFAULT_API_PORT) -> int:
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
    ) -> int:
        """
        Run tests and exit.
        
        Args:
            categories: Optional list of categories to test
            verbose: Whether to show verbose output
        
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
                    status_icon = "✅" if result.passed else "❌" if result.failed else "⚠️"
                    self._logger.info(
                        f"[{current}/{total}] {status_icon} {result.category}/{result.subcategory}"
                    )
            
            # Run tests
            summary = await self.test_runner.run_all_tests(
                categories=categories,
                progress_callback=progress_callback if verbose else None,
            )
            
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
            self._logger.info(f"  Accuracy:      {summary.overall_accuracy:.1f}%")
            self._logger.info(f"  Avg Response:  {summary.average_response_time_ms:.1f}ms")
            self._logger.info(f"  P95 Response:  {summary.p95_response_time_ms:.1f}ms")
            
            if summary.accuracy_by_category:
                self._logger.info("-" * 60)
                self._logger.info("Accuracy by Category:")
                for cat, acc in summary.accuracy_by_category.items():
                    self._logger.info(f"  {cat}: {acc:.1f}%")
            
            self._logger.info("=" * 60)
            
            # Return exit code based on results
            if summary.failed_tests > 0 or summary.error_tests > 0:
                self._logger.warning(
                    f"⚠️ {summary.failed_tests} failures, {summary.error_tests} errors"
                )
                return 1
            else:
                self._logger.success(f"✅ All {summary.passed_tests} tests passed!")
                return 0
            
        except Exception as e:
            self._logger.error(f"Test execution error: {e}")
            return 1
            
        finally:
            await self.shutdown()
    
    def _print_banner(self) -> None:
        """Print the startup banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     █████╗ ███████╗██╗  ██╗      ████████╗██╗  ██╗██████╗  █████╗ ███████╗   ║
║    ██╔══██╗██╔════╝██║  ██║      ╚══██╔══╝██║  ██║██╔══██╗██╔══██╗██╔════╝   ║
║    ███████║███████╗███████║█████╗   ██║   ███████║██████╔╝███████║███████╗   ║
║    ██╔══██║╚════██║██╔══██║╚════╝   ██║   ██╔══██║██╔══██╗██╔══██║╚════██║   ║
║    ██║  ██║███████║██║  ██║         ██║   ██║  ██║██║  ██║██║  ██║███████║   ║
║    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝         ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ║
║                                                                              ║
║                    Crisis Detection Testing Suite v5.0                       ║
║                                                                              ║
║              The Alphabet Cartel - https://discord.gg/alphabetcartel         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
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
        
        webhook_status = "Configured" if self.secrets.has_discord_webhook() else "Not configured"
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
        "--category",
        action="append",
        dest="categories",
        help="Category to test (can be specified multiple times)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output during test execution",
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
        if args.run_tests:
            # Run tests and exit
            return asyncio.run(
                app.run_tests(
                    categories=args.categories,
                    verbose=args.verbose,
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
