"""
NLP Server API Client for Ash-Thrash Testing

Handles communication with the Ash NLP server for crisis detection testing.
Provides retry logic, error handling, and performance monitoring.
"""

import requests
import time
import logging
from typing import Dict, Optional, Any
from urllib.parse import urljoin


class NLPClient:
    """Client for communicating with Ash NLP server"""
    
    def __init__(self, base_url: str = "http://10.20.30.253:8881", timeout: int = 10, max_retries: int = 3):
        """
        Initialize NLP client
        
        Args:
            base_url: Base URL of NLP server
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Request statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'error_counts': {}
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if NLP server is healthy
        
        Returns:
            dict: Health status response
        """
        try:
            url = urljoin(self.base_url, '/health')
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'server_response': response.json()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'error': str(e),
                'response_time_ms': None
            }
    
    def analyze_message(self, message: str, user_id: str = "test_user", channel_id: str = "test_channel") -> Dict[str, Any]:
        """
        Analyze a message for crisis detection
        
        Args:
            message: Message to analyze
            user_id: User ID for request
            channel_id: Channel ID for request
            
        Returns:
            dict: Analysis results with crisis level, confidence, etc.
        """
        url = urljoin(self.base_url, '/analyze')
        payload = {
            "message": message,
            "user_id": user_id,
            "channel_id": channel_id
        }
        
        return self._make_request_with_retry('POST', url, json=payload)
    
    def get_server_stats(self) -> Dict[str, Any]:
        """
        Get server statistics
        
        Returns:
            dict: Server statistics
        """
        try:
            url = urljoin(self.base_url, '/stats')
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'stats': response.json(),
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters
            
        Returns:
            dict: Response data or error information
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                self.stats['total_requests'] += 1
                
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                response_time_ms = (time.time() - start_time) * 1000
                self.stats['total_response_time'] += response_time_ms
                
                if response.status_code == 200:
                    self.stats['successful_requests'] += 1
                    
                    try:
                        data = response.json()
                        return {
                            'success': True,
                            'data': data,
                            'response_time_ms': response_time_ms,
                            'attempt': attempt + 1,
                            **data  # Include all response fields at top level
                        }
                    except ValueError as e:
                        self.stats['failed_requests'] += 1
                        return {
                            'success': False,
                            'error': f"Invalid JSON response: {e}",
                            'response_time_ms': response_time_ms,
                            'attempt': attempt + 1,
                            'raw_response': response.text[:500]
                        }
                else:
                    self.stats['failed_requests'] += 1
                    error_key = f"http_{response.status_code}"
                    self.stats['error_counts'][error_key] = self.stats['error_counts'].get(error_key, 0) + 1
                    
                    if attempt == self.max_retries:
                        return {
                            'success': False,
                            'error': f"HTTP {response.status_code}: {response.text}",
                            'response_time_ms': response_time_ms,
                            'attempt': attempt + 1
                        }
                    
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    
            except requests.exceptions.Timeout as e:
                error_key = "timeout"
                self.stats['error_counts'][error_key] = self.stats['error_counts'].get(error_key, 0) + 1
                last_error = f"Request timeout: {e}"
                
            except requests.exceptions.ConnectionError as e:
                error_key = "connection_error"
                self.stats['error_counts'][error_key] = self.stats['error_counts'].get(error_key, 0) + 1
                last_error = f"Connection error: {e}"
                
            except requests.exceptions.RequestException as e:
                error_key = "request_error"
                self.stats['error_counts'][error_key] = self.stats['error_counts'].get(error_key, 0) + 1
                last_error = f"Request error: {e}"
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries:
                wait_time = (2 ** attempt) * 0.5  # 0.5, 1, 2 seconds
                time.sleep(wait_time)
        
        self.stats['failed_requests'] += 1
        response_time_ms = (time.time() - start_time) * 1000
        
        return {
            'success': False,
            'error': last_error or "Unknown error",
            'response_time_ms': response_time_ms,
            'attempt': self.max_retries + 1
        }
    
    def get_client_stats(self) -> Dict[str, Any]:
        """
        Get client-side request statistics
        
        Returns:
            dict: Client statistics
        """
        total_requests = self.stats['total_requests']
        
        if total_requests == 0:
            return {
                'total_requests': 0,
                'success_rate': 0.0,
                'average_response_time_ms': 0.0,
                'error_counts': {}
            }
        
        return {
            'total_requests': total_requests,
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': (self.stats['successful_requests'] / total_requests) * 100,
            'average_response_time_ms': self.stats['total_response_time'] / total_requests,
            'error_counts': self.stats['error_counts'].copy()
        }
    
    def reset_stats(self):
        """Reset client statistics"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'error_counts': {}
        }
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience function for quick testing
def quick_health_check(base_url: str = "http://10.20.30.253:8881") -> bool:
    """
    Quick health check function
    
    Args:
        base_url: NLP server base URL
        
    Returns:
        bool: True if server is healthy
    """
    try:
        with NLPClient(base_url) as client:
            result = client.health_check()
            return result.get('status') == 'healthy'
    except Exception:
        return False


def quick_analyze(message: str, base_url: str = "http://10.20.30.253:8881") -> Optional[Dict[str, Any]]:
    """
    Quick message analysis function
    
    Args:
        message: Message to analyze
        base_url: NLP server base URL
        
    Returns:
        dict or None: Analysis result or None if failed
    """
    try:
        with NLPClient(base_url) as client:
            result = client.analyze_message(message)
            return result if result.get('success') else None
    except Exception:
        return None