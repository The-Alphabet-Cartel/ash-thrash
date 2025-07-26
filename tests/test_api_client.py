"""
Tests for the NLP API client communication
"""

import pytest
import requests
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestNLPAPIClient:
    """Test NLP server API communication"""
    
    @patch('requests.post')
    def test_successful_analysis_request(self, mock_post):
        """Test successful analysis request to NLP server"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'crisis_level': 'high',
            'confidence_score': 0.85,
            'processing_time_ms': 125.0,
            'detected_categories': ['suicidal_ideation', 'depression']
        }
        mock_post.return_value = mock_response
        
        # Test the request
        url = "http://localhost:8881/analyze"
        payload = {
            "message": "I want to end my life",
            "user_id": "test_user",
            "channel_id": "test_channel"
        }
        
        response = mock_post(url, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data['crisis_level'] == 'high'
        assert data['confidence_score'] == 0.85
        assert 'suicidal_ideation' in data['detected_categories']
    
    @patch('requests.post')
    def test_timeout_handling(self, mock_post):
        """Test timeout handling for slow responses"""
        # Mock timeout
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(requests.exceptions.Timeout):
            mock_post("http://localhost:8881/analyze", timeout=5)
    
    @patch('requests.post')
    def test_connection_error_handling(self, mock_post):
        """Test connection error handling"""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            mock_post("http://localhost:8881/analyze")
    
    @patch('requests.post')
    def test_server_error_handling(self, mock_post):
        """Test server error (500) handling"""
        # Mock server error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        response = mock_post("http://localhost:8881/analyze")
        assert response.status_code == 500
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "service": "ash-nlp",
            "timestamp": "2025-07-26T10:30:00Z"
        }
        mock_get.return_value = mock_response
        
        response = mock_get("http://localhost:8881/health")
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    
    @patch('requests.get')
    def test_health_check_failure(self, mock_get):
        """Test failed health check"""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.json.return_value = {
            "status": "unhealthy",
            "error": "Service unavailable"
        }
        mock_get.return_value = mock_response
        
        response = mock_get("http://localhost:8881/health")
        assert response.status_code == 503
        assert response.json()['status'] == 'unhealthy'


class TestAPIErrorHandling:
    """Test various API error scenarios"""
    
    def test_malformed_response_handling(self):
        """Test handling of malformed JSON responses"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_post.return_value = mock_response
            
            response = mock_post("http://localhost:8881/analyze")
            assert response.status_code == 200
            
            with pytest.raises(ValueError):
                response.json()
    
    def test_missing_fields_handling(self):
        """Test handling of responses with missing required fields"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                # Missing crisis_level field
                'confidence_score': 0.5
            }
            mock_post.return_value = mock_response
            
            response = mock_post("http://localhost:8881/analyze")
            data = response.json()
            
            # Should handle missing crisis_level gracefully
            assert 'crisis_level' not in data
            assert data.get('crisis_level', 'none') == 'none'


if __name__ == "__main__":
    pytest.main([__file__])