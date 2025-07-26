"""
API routes package for Ash-Thrash testing system

Contains organized route modules for different API functionality:
- health: Health check endpoints
- testing: Testing operation endpoints  
- results: Results retrieval endpoints
"""

from .health import health_bp
from .testing import testing_bp
from .results import results_bp

__all__ = ['health_bp', 'testing_bp', 'results_bp']