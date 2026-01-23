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
Ash-Thrash API Package
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.4-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 2 - Test Execution Engine
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

This package contains the FastAPI application for Ash-Thrash:

- Health endpoint for Docker health checks
- Status endpoint for detailed service information
- Future: Test execution API endpoints

USAGE:
    from src.api import create_app
    
    app = create_app()
    
    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=30888)
"""

__version__ = "5.0.0"
__author__ = "The Alphabet Cartel"
__email__ = "dev@alphabetcartel.org"
__url__ = "https://github.com/the-alphabet-cartel/ash-thrash"

from src.api.app import create_app, get_app

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__url__",
    "create_app",
    "get_app",
]
