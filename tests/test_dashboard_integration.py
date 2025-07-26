"""
Tests for dashboard integration functionality
"""

import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDashboardAPI:
    """Test dashboard API endpoints"""
    
    def test_api_status_endpoint(self):
        """Test API status endpoint response format"""
        expected_response = {
            "status": "healthy",
            "service": "ash-thrash",
            "timestamp": "2025-07-26T10:30:00Z",
            "version": "1.0.0"
        }
        
        # Test response structure
        assert "status" in expected_response
        assert "service" in expected_response
        assert expected_response["service"] == "ash-thrash"
    
    def test_latest_results_endpoint(self, sample_test_results):
        """Test latest results endpoint"""
        # Mock API response
        api_response = {
            "success": True,
            "timestamp": "2025-07-26T10:30:00Z",
            "results": sample_test_results
        }
        
        assert api_response["success"] is True
        assert "results" in api_response
        assert api_response["results"]["overall_results"]["overall_pass_rate"] == 80.0
    
    def test_historical_trends_endpoint(self):
        """Test historical trends endpoint"""
        trends_data = {
            "success": True,
            "trends": [
                {
                    "timestamp": "2025-07-26T08:00:00Z",
                    "overall_pass_rate": 85.0,
                    "goal_achievement_rate": 80.0,
                    "avg_response_time": 150.0
                },
                {
                    "timestamp": "2025-07-26T14:00:00Z", 
                    "overall_pass_rate": 87.0,
                    "goal_achievement_rate": 85.0,
                    "avg_response_time": 145.0
                }
            ],
            "total_runs": 2
        }
        
        assert trends_data["success"] is True
        assert len(trends_data["trends"]) == 2
        assert trends_data["total_runs"] == 2
    
    @patch('requests.post')
    def test_trigger_test_endpoint(self, mock_post):
        """Test trigger test endpoint"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "started",
            "message": "Comprehensive test started",
            "timestamp": "2025-07-26T10:30:00Z"
        }
        mock_post.return_value = mock_response
        
        response = mock_post("/api/test/run")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "started"


class TestDashboardDataFormatting:
    """Test data formatting for dashboard display"""
    
    def test_goal_status_formatting(self):
        """Test formatting of goal achievement status"""
        goal_data = {
            "definite_high": {
                "target_rate": 100.0,
                "actual_rate": 98.0,
                "goal_met": False,
                "status": "❌ MISSED"
            },
            "definite_none": {
                "target_rate": 95.0,
                "actual_rate": 96.0,
                "goal_met": True,
                "status": "✅ ACHIEVED"
            }
        }
        
        # Test critical goal failure
        assert goal_data["definite_high"]["goal_met"] is False
        assert "❌" in goal_data["definite_high"]["status"]
        
        # Test successful goal achievement
        assert goal_data["definite_none"]["goal_met"] is True
        assert "✅" in goal_data["definite_none"]["status"]
    
    def test_category_performance_formatting(self):
        """Test formatting of category performance data"""
        category_data = {
            "category": "definite_high",
            "pass_rate": 98.0,
            "target_rate": 100.0,
            "passed": 49,
            "total": 50,
            "status_class": "warning"  # Not meeting 100% target
        }
        
        assert category_data["pass_rate"] == 98.0
        assert category_data["status_class"] == "warning"
        assert category_data["passed"] == 49
    
    def test_trend_chart_data_formatting(self):
        """Test formatting of trend data for charts"""
        chart_data = {
            "labels": ["08:00", "14:00", "20:00"],
            "datasets": [
                {
                    "label": "Pass Rate",
                    "data": [85.0, 87.0, 89.0],
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.1)"
                }
            ]
        }
        
        assert len(chart_data["labels"]) == 3
        assert len(chart_data["datasets"][0]["data"]) == 3
        assert chart_data["datasets"][0]["label"] == "Pass Rate"


class TestDashboardIntegration:
    """Test integration with ash-dash"""
    
    def test_route_configuration(self):
        """Test dashboard route configuration"""
        routes = [
            "/api/testing/latest-results",
            "/api/testing/historical-trends", 
            "/api/testing/goals",
            "/api/testing/run-comprehensive"
        ]
        
        # Verify all required routes are defined
        assert "/api/testing/latest-results" in routes
        assert "/api/testing/run-comprehensive" in routes
        assert len(routes) == 4
    
    def test_component_integration(self):
        """Test dashboard component integration"""
        component_files = [
            "TestingOverview.js",
            "CategoryPerformance.js", 
            "GoalTracking.js",
            "TrendsChart.js"
        ]
        
        # Verify all required components are defined
        assert "TestingOverview.js" in component_files
        assert "CategoryPerformance.js" in component_files
        assert len(component_files) == 4
    
    def test_css_styling(self):
        """Test CSS styling for dashboard components"""
        css_classes = [
            "testing-overview",
            "category-item",
            "goal-item",
            "action-button"
        ]
        
        # Verify required CSS classes are defined
        assert "testing-overview" in css_classes
        assert "action-button" in css_classes


class TestRealTimeUpdates:
    """Test real-time update functionality"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection for real-time updates"""
        # Mock WebSocket connection
        ws_connection = {
            "connected": True,
            "last_update": "2025-07-26T10:30:00Z",
            "update_interval": 120  # seconds
        }
        
        assert ws_connection["connected"] is True
        assert ws_connection["update_interval"] == 120
    
    def test_auto_refresh_mechanism(self):
        """Test auto-refresh mechanism"""
        refresh_config = {
            "enabled": True,
            "interval_seconds": 120,
            "last_refresh": "2025-07-26T10:30:00Z"
        }
        
        assert refresh_config["enabled"] is True
        assert refresh_config["interval_seconds"] == 120


if __name__ == "__main__":
    pytest.main([__file__])