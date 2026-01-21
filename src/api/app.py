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
FILE VERSION: v5.0-2-2.4-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 2 - Test Execution Engine
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
__version__ = "v5.0-2-2.4-1"

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
