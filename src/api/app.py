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
FastAPI Application for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-6-6.3-4
LAST MODIFIED: 2026-02-07
PHASE: Phase 6 - A/B Testing Infrastructure (v5.1 Migration Phase 1)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Provide HTTP API for Ash-Thrash service
- Health check endpoint for Docker/Kubernetes
- Status endpoint for detailed service information
- Future: Test execution endpoints

ENDPOINTS:
    GET  /health  - Simple health check (for Docker HEALTHCHECK)
    GET  /status  - Detailed service status
    GET  /        - Service information
    GET  /snapshots           - List available test run snapshots
    POST /snapshots/capture   - Capture snapshot from last test run
    POST /comparisons/compare - Compare two snapshots (A/B analysis)
    GET  /comparisons/thresholds - Get current comparison thresholds

PORT: 30888 (configured via THRASH_API_PORT)

USAGE:
    from src.api.app import create_app
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=30888)
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Module version
__version__ = "v5.0-6-6.3-4"

# Initialize logger
logger = logging.getLogger(__name__)

# Global app instance (for module-level access)
_app: Optional[FastAPI] = None

# Service metadata
SERVICE_NAME = "ash-thrash"
SERVICE_DESCRIPTION = "Discord Crisis Detection Testing Suite"
SERVICE_VERSION = "5.0.0"

# Start time (for uptime calculation)
_start_time: Optional[datetime] = None


# =============================================================================
# Application State
# =============================================================================

class AppState:
    """
    Application state container.
    
    Holds references to managers and configuration for use in endpoints.
    """
    
    def __init__(self):
        self.config_manager = None
        self.logging_manager = None
        self.nlp_client = None
        self.phrase_loader = None
        self.test_runner = None
        self.snapshot_manager = None
        self.comparison_analyzer = None
        self.is_ready = False
        self.initialization_error: Optional[str] = None


# Global state
app_state = AppState()


# =============================================================================
# Lifespan Management
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    global _start_time
    
    # Startup
    _start_time = datetime.now()
    logger.info(f"🚀 {SERVICE_NAME} v{SERVICE_VERSION} starting up...")
    
    # Initialize managers if not already done
    if not app_state.is_ready and not app_state.initialization_error:
        try:
            await _initialize_managers()
            app_state.is_ready = True
            logger.info(f"✅ {SERVICE_NAME} is ready")
        except Exception as e:
            app_state.initialization_error = str(e)
            logger.error(f"❌ Initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"🛑 {SERVICE_NAME} shutting down...")
    
    # Cleanup
    if app_state.nlp_client:
        try:
            await app_state.nlp_client.close()
        except Exception as e:
            logger.warning(f"Error closing NLP client: {e}")


async def _initialize_managers():
    """
    Initialize all managers for the application.
    
    This is called during startup if managers haven't been injected.
    """
    # Lazy imports to avoid circular dependencies
    from src.managers import (
        create_config_manager,
        create_logging_config_manager,
        create_nlp_client_manager,
        create_phrase_loader_manager,
        create_test_runner_manager,
        create_snapshot_manager,
        create_comparison_analyzer_manager,
    )
    from src.validators import (
        create_classification_validator,
        create_response_validator,
    )
    
    logger.info("📦 Initializing managers...")
    
    # Config
    if not app_state.config_manager:
        app_state.config_manager = create_config_manager()
    
    # Logging
    if not app_state.logging_manager:
        app_state.logging_manager = create_logging_config_manager(
            config_manager=app_state.config_manager
        )
    
    # NLP Client
    if not app_state.nlp_client:
        app_state.nlp_client = create_nlp_client_manager(
            config_manager=app_state.config_manager,
            logging_manager=app_state.logging_manager,
        )
    
    # Phrase Loader
    if not app_state.phrase_loader:
        app_state.phrase_loader = create_phrase_loader_manager(
            config_manager=app_state.config_manager,
            logging_manager=app_state.logging_manager,
        )
    
    # Validators
    class_validator = create_classification_validator(
        logging_manager=app_state.logging_manager
    )
    resp_validator = create_response_validator(
        logging_manager=app_state.logging_manager
    )
    
    # Test Runner
    if not app_state.test_runner:
        app_state.test_runner = create_test_runner_manager(
            nlp_client=app_state.nlp_client,
            phrase_loader=app_state.phrase_loader,
            classification_validator=class_validator,
            response_validator=resp_validator,
            config_manager=app_state.config_manager,
            logging_manager=app_state.logging_manager,
        )

    # Snapshot Manager (Phase 6)
    if not app_state.snapshot_manager:
        app_state.snapshot_manager = create_snapshot_manager(
            config_manager=app_state.config_manager,
            logging_manager=app_state.logging_manager,
        )

    # Comparison Analyzer (Phase 6)
    if not app_state.comparison_analyzer:
        app_state.comparison_analyzer = create_comparison_analyzer_manager(
            config_manager=app_state.config_manager,
            logging_manager=app_state.logging_manager,
        )
    
    logger.info("✅ All managers initialized")


# =============================================================================
# Application Factory
# =============================================================================

def create_app(
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
    nlp_client: Optional[Any] = None,
    phrase_loader: Optional[Any] = None,
    test_runner: Optional[Any] = None,
    snapshot_manager: Optional[Any] = None,
    comparison_analyzer: Optional[Any] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    This is the factory function for the Ash-Thrash API.
    Optionally accepts pre-configured managers for dependency injection.
    
    Args:
        config_manager: Optional ConfigManager instance
        logging_manager: Optional LoggingConfigManager instance
        nlp_client: Optional NLPClientManager instance
        phrase_loader: Optional PhraseLoaderManager instance
        test_runner: Optional TestRunnerManager instance
    
    Returns:
        Configured FastAPI application
    
    Example:
        >>> app = create_app()
        >>> uvicorn.run(app, host="0.0.0.0", port=30888)
        
        >>> # With dependency injection
        >>> config = create_config_manager()
        >>> app = create_app(config_manager=config)
    """
    global _app
    
    # Store injected managers
    if config_manager:
        app_state.config_manager = config_manager
    if logging_manager:
        app_state.logging_manager = logging_manager
    if nlp_client:
        app_state.nlp_client = nlp_client
    if phrase_loader:
        app_state.phrase_loader = phrase_loader
    if test_runner:
        app_state.test_runner = test_runner
    if snapshot_manager:
        app_state.snapshot_manager = snapshot_manager
    if comparison_analyzer:
        app_state.comparison_analyzer = comparison_analyzer
    
    # Mark as ready if all critical managers are provided
    if all([config_manager, nlp_client, phrase_loader, test_runner]):
        app_state.is_ready = True
    
    # Create FastAPI app
    app = FastAPI(
        title="Ash-Thrash",
        description="Discord Crisis Detection Testing Suite - The Alphabet Cartel",
        version=SERVICE_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Register routes
    _register_routes(app)
    
    # Store global reference
    _app = app
    
    logger.debug(f"🏭 Created FastAPI application")
    
    return app


def get_app() -> Optional[FastAPI]:
    """
    Get the current FastAPI application instance.
    
    Returns:
        FastAPI app if created, None otherwise
    """
    return _app


def _register_routes(app: FastAPI) -> None:
    """Register all API routes."""
    
    @app.get("/", tags=["Info"])
    async def root() -> Dict[str, Any]:
        """
        Service information endpoint.
        
        Returns basic information about the Ash-Thrash service.
        """
        return {
            "service": SERVICE_NAME,
            "description": SERVICE_DESCRIPTION,
            "version": SERVICE_VERSION,
            "community": "The Alphabet Cartel",
            "links": {
                "discord": "https://discord.gg/alphabetcartel",
                "website": "https://alphabetcartel.org",
                "repository": "https://github.com/the-alphabet-cartel/ash-thrash",
            },
            "endpoints": {
                "health": "/health",
                "status": "/status",
                "snapshots": "/snapshots",
                "capture_snapshot": "/snapshots/capture",
                "compare": "/comparisons/compare",
                "thresholds": "/comparisons/thresholds",
                "docs": "/docs",
            },
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check() -> JSONResponse:
        """
        Health check endpoint for Docker/Kubernetes.
        
        Returns:
            - 200 OK if service is healthy
            - 503 Service Unavailable if service is unhealthy
        
        Response format:
            {"status": "ok|unhealthy", "timestamp": "ISO8601"}
        """
        timestamp = datetime.now().isoformat()
        
        if app_state.is_ready:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "ok",
                    "timestamp": timestamp,
                }
            )
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": timestamp,
                    "error": app_state.initialization_error or "Service not ready",
                }
            )
    
    @app.get("/status", tags=["Health"])
    async def detailed_status() -> Dict[str, Any]:
        """
        Detailed service status endpoint.
        
        Returns comprehensive information about service state.
        """
        timestamp = datetime.now()
        
        # Calculate uptime
        uptime_seconds = 0.0
        if _start_time:
            uptime_seconds = (timestamp - _start_time).total_seconds()
        
        # Base response
        response: Dict[str, Any] = {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "status": "ready" if app_state.is_ready else "initializing",
            "timestamp": timestamp.isoformat(),
            "uptime_seconds": uptime_seconds,
        }
        
        # Add component status
        components: Dict[str, Any] = {
            "config_manager": app_state.config_manager is not None,
            "logging_manager": app_state.logging_manager is not None,
            "nlp_client": app_state.nlp_client is not None,
            "phrase_loader": app_state.phrase_loader is not None,
            "test_runner": app_state.test_runner is not None,
            "snapshot_manager": app_state.snapshot_manager is not None,
            "comparison_analyzer": app_state.comparison_analyzer is not None,
        }
        response["components"] = components
        
        # Add phrase statistics if available
        if app_state.phrase_loader:
            try:
                stats = app_state.phrase_loader.get_statistics()
                response["phrases"] = {
                    "total": stats.total_phrases,
                    "files_loaded": stats.files_loaded,
                    "categories": list(stats.by_category.keys()),
                }
            except Exception as e:
                response["phrases"] = {"error": str(e)}
        
        # Add NLP client status if available
        if app_state.nlp_client:
            try:
                response["nlp_client"] = app_state.nlp_client.get_status_info()
            except Exception as e:
                response["nlp_client"] = {"error": str(e)}
        
        # Add current test run if any
        if app_state.test_runner:
            try:
                current_run = app_state.test_runner.get_current_run()
                if current_run:
                    response["current_run"] = {
                        "run_id": current_run.run_id,
                        "total_tests": current_run.total_tests,
                        "passed": current_run.passed_tests,
                        "failed": current_run.failed_tests,
                        "errors": current_run.error_tests,
                    }
            except Exception:
                pass
        
        # Add error if not ready
        if app_state.initialization_error:
            response["error"] = app_state.initialization_error
        
        return response

    # =================================================================
    # Snapshot Endpoints (Phase 6 - A/B Testing)
    # =================================================================

    @app.get("/snapshots", tags=["A/B Testing"])
    async def list_snapshots(
        sort_by: str = "captured_at",
        reverse: bool = True,
    ) -> Dict[str, Any]:
        """
        List available test run snapshots.

        Returns metadata for all captured snapshots, sorted by the
        specified field. Used to identify baselines and candidates
        for A/B comparison.
        """
        if not app_state.snapshot_manager:
            return JSONResponse(
                status_code=503,
                content={"error": "Snapshot manager not initialized"},
            )

        snapshots = app_state.snapshot_manager.list_snapshots(
            sort_by=sort_by, reverse=reverse,
        )

        return {
            "total": len(snapshots),
            "snapshots": [s.to_dict() for s in snapshots],
            "snapshot_dir": app_state.snapshot_manager.get_snapshot_dir(),
        }

    @app.post("/snapshots/capture", tags=["A/B Testing"])
    async def capture_snapshot(
        label: str,
        description: str = "",
        nlp_version: str = "",
        nlp_git_commit: str = "",
    ) -> Dict[str, Any]:
        """
        Capture a snapshot from the most recent test run.

        Requires that a test run has been completed. Saves the
        complete results as a versioned JSON snapshot for future
        A/B comparison.
        """
        if not app_state.snapshot_manager:
            return JSONResponse(
                status_code=503,
                content={"error": "Snapshot manager not initialized"},
            )

        if not app_state.test_runner:
            return JSONResponse(
                status_code=503,
                content={"error": "Test runner not initialized"},
            )

        # Get most recent test run
        current_run = app_state.test_runner.get_current_run()
        if not current_run:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No completed test run available to capture",
                },
            )

        # We need an analysis result too - lazy import to avoid circular
        from src.managers import create_result_analyzer_manager

        analyzer = create_result_analyzer_manager(
            config_manager=app_state.config_manager,
            logging_manager=app_state.logging_manager,
        )
        analysis = analyzer.analyze(current_run)

        # Capture the snapshot
        filepath = app_state.snapshot_manager.capture_snapshot(
            test_run_summary=current_run,
            analysis_result=analysis,
            label=label,
            description=description,
            nlp_version=nlp_version,
            nlp_git_commit=nlp_git_commit,
        )

        return {
            "status": "captured",
            "filepath": filepath,
            "label": label,
            "overall_accuracy": current_run.overall_accuracy,
            "total_phrases": current_run.total_tests,
        }

    # =================================================================
    # Comparison Endpoints (Phase 6 - A/B Testing)
    # =================================================================

    @app.post("/comparisons/compare", tags=["A/B Testing"])
    async def compare_snapshots(
        baseline_path: str,
        candidate_path: str,
    ) -> Dict[str, Any]:
        """
        Compare two snapshots side-by-side (A/B analysis).

        Loads the specified baseline and candidate snapshots, then
        runs the comparison analyzer to produce per-category deltas,
        per-phrase changes, latency comparison, and an overall verdict.
        """
        if not app_state.snapshot_manager:
            return JSONResponse(
                status_code=503,
                content={"error": "Snapshot manager not initialized"},
            )

        if not app_state.comparison_analyzer:
            return JSONResponse(
                status_code=503,
                content={"error": "Comparison analyzer not initialized"},
            )

        try:
            baseline = app_state.snapshot_manager.load_snapshot(
                baseline_path
            )
            candidate = app_state.snapshot_manager.load_snapshot(
                candidate_path
            )
        except FileNotFoundError as e:
            return JSONResponse(
                status_code=404,
                content={"error": str(e)},
            )
        except (ValueError, Exception) as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid snapshot: {e}"},
            )

        result = app_state.comparison_analyzer.compare(
            baseline_snapshot=baseline,
            candidate_snapshot=candidate,
        )

        return result.to_dict()

    @app.get("/comparisons/thresholds", tags=["A/B Testing"])
    async def get_comparison_thresholds() -> Dict[str, Any]:
        """
        Get current comparison verdict thresholds.

        Returns the configured regression thresholds and critical
        categories that determine PASS/WARN/FAIL verdicts.
        """
        if not app_state.comparison_analyzer:
            return JSONResponse(
                status_code=503,
                content={"error": "Comparison analyzer not initialized"},
            )

        return app_state.comparison_analyzer.get_thresholds()


# =============================================================================
# Export
# =============================================================================

__all__ = [
    "create_app",
    "get_app",
    "app_state",
    "AppState",
    "SERVICE_NAME",
    "SERVICE_VERSION",
]
