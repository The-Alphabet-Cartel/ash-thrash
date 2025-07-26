"""
Dashboard Integration Utilities for Ash-Thrash

Provides utilities for integrating test results with ash-dash
and other dashboard systems.
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging


class DashboardIntegrator:
    """Integrates test results with dashboard systems"""
    
    def __init__(self, dashboard_url: str = "http://localhost:8883", api_key: Optional[str] = None):
        """
        Initialize dashboard integrator
        
        Args:
            dashboard_url: URL of the dashboard API
            api_key: Optional API key for authentication
        """
        self.dashboard_url = dashboard_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        self.logger = logging.getLogger(__name__)
    
    def format_for_dashboard(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format test results for dashboard consumption
        
        Args:
            results: Raw test results
            
        Returns:
            dict: Dashboard-formatted data
        """
        overall = results.get('overall_results', {})
        goals = results.get('goal_achievement', {})
        categories = results.get('category_results', {})
        
        # Dashboard metrics format
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_tests': overall.get('total_tests', 0),
                'pass_rate': overall.get('overall_pass_rate', 0),
                'avg_response_time': overall.get('avg_response_time', 0),
                'goals_achieved': goals.get('summary', {}).get('goals_achieved', 0),
                'total_goals': goals.get('summary', {}).get('total_goals', 0),
                'goal_achievement_rate': goals.get('summary', {}).get('achievement_rate', 0)
            },
            'status': self._determine_overall_status(overall, goals),
            'categories': [],
            'alerts': self._generate_alerts(results)
        }
        
        # Category data for dashboard
        for category, data in categories.items():
            dashboard_data['categories'].append({
                'name': category,
                'display_name': category.replace('_', ' ').title(),
                'pass_rate': data.get('pass_rate', 0),
                'target_rate': data.get('target_rate', 0),
                'goal_met': data.get('goal_met', False),
                'total_tests': data.get('total_tests', 0),
                'passed_tests': data.get('passed_tests', 0),
                'avg_confidence': data.get('avg_confidence', 0),
                'avg_response_time': data.get('avg_response_time', 0),
                'critical': self._is_critical_category(category),
                'status_class': 'success' if data.get('goal_met', False) else 'warning'
            })
        
        return dashboard_data
    
    def send_to_dashboard(self, results: Dict[str, Any], endpoint: str = "/api/testing/update") -> Dict[str, Any]:
        """
        Send test results to dashboard
        
        Args:
            results: Test results to send
            endpoint: Dashboard API endpoint
            
        Returns:
            dict: Response from dashboard
        """
        formatted_data = self.format_for_dashboard(results)
        url = f"{self.dashboard_url}{endpoint}"
        
        try:
            response = self.session.post(
                url,
                json=formatted_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Data sent to dashboard successfully',
                    'response': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"Dashboard returned {response.status_code}: {response.text}",
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Failed to connect to dashboard: {e}"
            }
    
    def create_dashboard_widget_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create data optimized for dashboard widgets
        
        Args:
            results: Test results
            
        Returns:
            dict: Widget-optimized data
        """
        overall = results.get('overall_results', {})
        goals = results.get('goal_achievement', {})
        categories = results.get('category_results', {})
        
        # Summary widget data
        summary_widget = {
            'type': 'summary',
            'title': 'Testing Overview',
            'metrics': [
                {
                    'label': 'Pass Rate',
                    'value': f"{overall.get('overall_pass_rate', 0):.1f}%",
                    'color': self._get_pass_rate_color(overall.get('overall_pass_rate', 0))
                },
                {
                    'label': 'Goals Met',
                    'value': f"{goals.get('summary', {}).get('goals_achieved', 0)}/{goals.get('summary', {}).get('total_goals', 0)}",
                    'color': self._get_goal_color(goals.get('summary', {}).get('achievement_rate', 0))
                },
                {
                    'label': 'Response Time',
                    'value': f"{overall.get('avg_response_time', 0):.0f}ms",
                    'color': self._get_response_time_color(overall.get('avg_response_time', 0))
                },
                {
                    'label': 'Total Tests',
                    'value': str(overall.get('total_tests', 0)),
                    'color': '#007bff'
                }
            ]
        }
        
        # Chart widget data
        chart_widget = {
            'type': 'chart',
            'title': 'Category Performance',
            'chart_type': 'bar',
            'data': {
                'labels': [],
                'datasets': [{
                    'label': 'Pass Rate (%)',
                    'data': [],
                    'backgroundColor': []
                }]
            }
        }
        
        for category, data in categories.items():
            chart_widget['data']['labels'].append(category.replace('_', ' ').title())
            chart_widget['data']['datasets'][0]['data'].append(data.get('pass_rate', 0))
            color = '#28a745' if data.get('goal_met', False) else '#dc3545'
            chart_widget['data']['datasets'][0]['backgroundColor'].append(color)
        
        # Status widget data
        status_widget = {
            'type': 'status',
            'title': 'System Status',
            'status': self._determine_overall_status(overall, goals),
            'last_updated': datetime.now().isoformat(),
            'details': [
                f"Last test: {overall.get('total_tests', 0)} phrases",
                f"Execution time: {overall.get('execution_time', 0):.1f}s",
                f"Error rate: {((overall.get('total_errors', 0) / overall.get('total_tests', 1)) * 100):.1f}%"
            ]
        }
        
        # Alerts widget data
        alerts_widget = {
            'type': 'alerts',
            'title': 'Active Alerts',
            'alerts': self._generate_alerts(results)
        }
        
        return {
            'widgets': [summary_widget, chart_widget, status_widget, alerts_widget],
            'last_updated': datetime.now().isoformat()
        }
    
    def generate_real_time_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate real-time metrics for live dashboard updates
        
        Args:
            results: Test results
            
        Returns:
            dict: Real-time metrics data
        """
        overall = results.get('overall_results', {})
        categories = results.get('category_results', {})
        
        # Critical metrics for real-time monitoring
        critical_metrics = {
            'timestamp': datetime.now().isoformat(),
            'pass_rate': overall.get('overall_pass_rate', 0),
            'response_time': overall.get('avg_response_time', 0),
            'error_count': overall.get('total_errors', 0),
            'high_priority_pass_rate': categories.get('definite_high', {}).get('pass_rate', 0),
            'false_positive_rate': 100 - categories.get('definite_none', {}).get('pass_rate', 100),
            'system_health': self._calculate_system_health(results)
        }
        
        # Add trend indicators
        critical_metrics['trends'] = {
            'pass_rate_trend': 'stable',  # Would be calculated from historical data
            'response_time_trend': 'stable',
            'error_rate_trend': 'stable'
        }
        
        return critical_metrics
    
    def _determine_overall_status(self, overall: Dict[str, Any], goals: Dict[str, Any]) -> str:
        """Determine overall system status"""
        goal_rate = goals.get('summary', {}).get('achievement_rate', 0)
        pass_rate = overall.get('overall_pass_rate', 0)
        error_rate = (overall.get('total_errors', 0) / overall.get('total_tests', 1)) * 100
        
        if goal_rate >= 85 and pass_rate >= 80 and error_rate < 5:
            return 'healthy'
        elif goal_rate >= 70 and pass_rate >= 70 and error_rate < 10:
            return 'warning'
        else:
            return 'critical'
    
    def _generate_alerts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on test results"""
        alerts = []
        overall = results.get('overall_results', {})
        categories = results.get('category_results', {})
        failure_analysis = results.get('failure_analysis', {})
        
        # High priority detection failures
        high_priority = categories.get('definite_high', {})
        if high_priority.get('pass_rate', 100) < 100:
            alerts.append({
                'type': 'critical',
                'title': 'High Priority Detection Failure',
                'message': f"High priority crisis detection at {high_priority.get('pass_rate', 0):.1f}% (Target: 100%)",
                'action': 'immediate_review_required'
            })
        
        # False positive rate too high
        none_priority = categories.get('definite_none', {})
        false_positive_rate = 100 - none_priority.get('pass_rate', 100)
        if false_positive_rate > 10:
            alerts.append({
                'type': 'warning',
                'title': 'High False Positive Rate',
                'message': f"False positive rate at {false_positive_rate:.1f}% (Target: <5%)",
                'action': 'tune_sensitivity'
            })
        
        # High error rate
        error_rate = (overall.get('total_errors', 0) / overall.get('total_tests', 1)) * 100
        if error_rate > 5:
            alerts.append({
                'type': 'warning',
                'title': 'High Error Rate',
                'message': f"Error rate at {error_rate:.1f}% ({overall.get('total_errors', 0)} errors)",
                'action': 'check_server_stability'
            })
        
        # Slow response times
        if overall.get('avg_response_time', 0) > 300:
            alerts.append({
                'type': 'info',
                'title': 'Slow Response Times',
                'message': f"Average response time: {overall.get('avg_response_time', 0):.0f}ms",
                'action': 'performance_optimization_needed'
            })
        
        # Critical failures
        critical_failures = failure_analysis.get('critical_failures', 0)
        if critical_failures > 0:
            alerts.append({
                'type': 'critical',
                'title': 'Critical Test Failures',
                'message': f"{critical_failures} critical failures detected",
                'action': 'review_failure_details'
            })
        
        return alerts
    
    def _is_critical_category(self, category: str) -> bool:
        """Check if category is critical"""
        critical_categories = ['definite_high', 'definite_none', 'maybe_low_none']
        return category in critical_categories
    
    def _get_pass_rate_color(self, pass_rate: float) -> str:
        """Get color for pass rate"""
        if pass_rate >= 90:
            return '#28a745'  # Green
        elif pass_rate >= 70:
            return '#ffc107'  # Yellow
        else:
            return '#dc3545'  # Red
    
    def _get_goal_color(self, achievement_rate: float) -> str:
        """Get color for goal achievement"""
        if achievement_rate >= 85:
            return '#28a745'  # Green
        elif achievement_rate >= 70:
            return '#ffc107'  # Yellow
        else:
            return '#dc3545'  # Red
    
    def _get_response_time_color(self, response_time: float) -> str:
        """Get color for response time"""
        if response_time <= 150:
            return '#28a745'  # Green
        elif response_time <= 300:
            return '#ffc107'  # Yellow
        else:
            return '#dc3545'  # Red
    
    def _calculate_system_health(self, results: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)"""
        overall = results.get('overall_results', {})
        goals = results.get('goal_achievement', {})
        categories = results.get('category_results', {})
        
        # Weighted health calculation
        pass_rate_weight = 0.4
        goal_achievement_weight = 0.3
        response_time_weight = 0.2
        error_rate_weight = 0.1
        
        # Pass rate score (0-100)
        pass_rate_score = min(overall.get('overall_pass_rate', 0), 100)
        
        # Goal achievement score (0-100)
        goal_score = goals.get('summary', {}).get('achievement_rate', 0)
        
        # Response time score (inverse relationship, 150ms = 100, 500ms = 0)
        response_time = overall.get('avg_response_time', 150)
        response_time_score = max(0, 100 - ((response_time - 150) / 350) * 100)
        
        # Error rate score (inverse relationship)
        error_rate = (overall.get('total_errors', 0) / overall.get('total_tests', 1)) * 100
        error_rate_score = max(0, 100 - error_rate * 10)
        
        # Calculate weighted health score
        health_score = (
            pass_rate_score * pass_rate_weight +
            goal_score * goal_achievement_weight +
            response_time_score * response_time_weight +
            error_rate_score * error_rate_weight
        )
        
        return round(health_score, 1)
    
    def create_webhook_payload(self, results: Dict[str, Any], webhook_type: str = "slack") -> Dict[str, Any]:
        """
        Create webhook payload for external notifications
        
        Args:
            results: Test results
            webhook_type: Type of webhook (slack, discord, teams)
            
        Returns:
            dict: Webhook payload
        """
        overall = results.get('overall_results', {})
        goals = results.get('goal_achievement', {})
        
        status = self._determine_overall_status(overall, goals)
        status_emoji = {'healthy': '✅', 'warning': '⚠️', 'critical': '🚨'}.get(status, '❓')
        
        if webhook_type.lower() == "slack":
            return {
                "text": f"{status_emoji} Ash-Thrash Testing Report",
                "attachments": [
                    {
                        "color": "good" if status == "healthy" else "warning" if status == "warning" else "danger",
                        "fields": [
                            {
                                "title": "Pass Rate",
                                "value": f"{overall.get('overall_pass_rate', 0):.1f}%",
                                "short": True
                            },
                            {
                                "title": "Goals Achieved",
                                "value": f"{goals.get('summary', {}).get('goals_achieved', 0)}/{goals.get('summary', {}).get('total_goals', 0)}",
                                "short": True
                            },
                            {
                                "title": "Response Time",
                                "value": f"{overall.get('avg_response_time', 0):.0f}ms",
                                "short": True
                            },
                            {
                                "title": "Total Tests",
                                "value": str(overall.get('total_tests', 0)),
                                "short": True
                            }
                        ],
                        "footer": "Ash-Thrash Testing Suite",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
        
        elif webhook_type.lower() == "discord":
            return {
                "embeds": [
                    {
                        "title": f"{status_emoji} Ash-Thrash Testing Report",
                        "color": 0x28a745 if status == "healthy" else 0xffc107 if status == "warning" else 0xdc3545,
                        "fields": [
                            {
                                "name": "Pass Rate",
                                "value": f"{overall.get('overall_pass_rate', 0):.1f}%",
                                "inline": True
                            },
                            {
                                "name": "Goals Achieved", 
                                "value": f"{goals.get('summary', {}).get('goals_achieved', 0)}/{goals.get('summary', {}).get('total_goals', 0)}",
                                "inline": True
                            },
                            {
                                "name": "Response Time",
                                "value": f"{overall.get('avg_response_time', 0):.0f}ms",
                                "inline": True
                            }
                        ],
                        "footer": {
                            "text": "Ash-Thrash Testing Suite"
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
        
        else:  # Generic/Teams format
            return {
                "summary": f"Ash-Thrash Testing Report - {status.title()}",
                "sections": [
                    {
                        "activityTitle": f"{status_emoji} Testing Results",
                        "facts": [
                            {
                                "name": "Pass Rate",
                                "value": f"{overall.get('overall_pass_rate', 0):.1f}%"
                            },
                            {
                                "name": "Goals Achieved",
                                "value": f"{goals.get('summary', {}).get('goals_achieved', 0)}/{goals.get('summary', {}).get('total_goals', 0)}"
                            },
                            {
                                "name": "Response Time", 
                                "value": f"{overall.get('avg_response_time', 0):.0f}ms"
                            },
                            {
                                "name": "Total Tests",
                                "value": str(overall.get('total_tests', 0))
                            }
                        ]
                    }
                ]
            }


# Convenience functions
def quick_dashboard_update(results: Dict[str, Any], dashboard_url: str = "http://localhost:8883") -> bool:
    """
    Quick dashboard update function
    
    Args:
        results: Test results
        dashboard_url: Dashboard URL
        
    Returns:
        bool: True if successful
    """
    try:
        integrator = DashboardIntegrator(dashboard_url)
        response = integrator.send_to_dashboard(results)
        return response.get('success', False)
    except Exception:
        return False


def generate_webhook_notification(results: Dict[str, Any], webhook_url: str, webhook_type: str = "slack") -> bool:
    """
    Send webhook notification
    
    Args:
        results: Test results
        webhook_url: Webhook URL
        webhook_type: Type of webhook
        
    Returns:
        bool: True if successful
    """
    try:
        integrator = DashboardIntegrator()
        payload = integrator.create_webhook_payload(results, webhook_type)
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False