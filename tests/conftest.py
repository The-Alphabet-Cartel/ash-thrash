"""
Pytest configuration and shared fixtures for Ash-Thrash tests
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock, patch
import json


@pytest.fixture
def temp_results_dir():
    """Create a temporary directory for test results"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_nlp_server():
    """Mock NLP server responses"""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'crisis_level': 'medium',
            'confidence_score': 0.75,
            'processing_time_ms': 150.0,
            'detected_categories': ['depression', 'anxiety']
        }
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def sample_test_results():
    """Sample test results for testing"""
    return {
        "test_metadata": {
            "timestamp": "2025-07-26T10:30:00Z",
            "total_phrases_tested": 10,
            "test_type": "unit_test_sample"
        },
        "overall_results": {
            "total_passed": 8,
            "total_failed": 2,
            "overall_pass_rate": 80.0,
            "avg_response_time_ms": 150.0
        },
        "goal_achievement": {
            "summary": {
                "goals_achieved": 3,
                "total_goals": 4,
                "achievement_rate": 75.0
            }
        }
    }


@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        "GLOBAL_NLP_API_URL": "http://localhost:8881",
        "max_concurrent_tests": 2,
        "test_timeout": 5
    }