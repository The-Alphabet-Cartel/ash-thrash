"""
API package for Ash-Thrash testing system

Provides REST API endpoints for testing operations, results retrieval,
and dashboard integration.
"""

from .server import create_app

__all__ = ['create_app']