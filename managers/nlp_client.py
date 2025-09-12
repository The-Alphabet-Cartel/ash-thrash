# ash-thrash/managers/nlp_client.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
NLP API Communication Manager for Ash-Thrash Service
---
FILE VERSION: v3.1-1a-2
LAST MODIFIED: 2025-09-12
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import time
import requests
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status enumeration for NLP server"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"

@dataclass
class AnalysisResult:
    """Analysis result from NLP server"""
    crisis_level: str
    confidence_score: float
    crisis_score: float  # NEW: Final calculated crisis score after all processing
    needs_response: bool
    processing_time_ms: float
    method: str
    reasoning: Optional[str] = None
    detected_categories: Optional[list] = None
    raw_response: Optional[Dict[str, Any]] = None

@dataclass
class HealthCheckResult:
    """Health check result from NLP server"""
    status: HealthStatus
    timestamp: float
    version: Optional[str] = None
    total_managers: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

class NLPClientManager:
    """
    NLP API Communication Manager for Ash-Thrash testing suite
    
    Handles communication with Ash-NLP server including health checks,
    analysis requests, retry logic, and error handling.
    
    Enhanced in v3.1-1a-2 to capture crisis_score for threshold optimization.
    """
    
    def __init__(self, unified_config_manager):
        """
        Initialize NLP Client Manager
        
        Args:
            unified_config_manager: UnifiedConfigManager instance for configuration
        """
        self.unified_config = unified_config_manager
        
        try:
            # Load NLP server configuration
            self.server_config = self.unified_config.get_config_section('test_settings', 'nlp_server', {})
            
            self.base_url = self.server_config.get('base_url', 'http://172.20.0.11:8881')
            self.health_endpoint = self.server_config.get('health_endpoint', '/health')
            self.analyze_endpoint = self.server_config.get('analyze_endpoint', '/analyze')
            self.timeout = self.server_config.get('timeout_seconds', 30)
            self.max_retries = self.server_config.get('max_retries', 3)
            self.retry_delay_ms = self.server_config.get('retry_delay_ms', 1000)
            
            # Construct full URLs
            self.health_url = f"{self.base_url}{self.health_endpoint}"
            self.analyze_url = f"{self.base_url}{self.analyze_endpoint}"
            
            logger.info(f"NLPClientManager v3.1-1a-2 initialized for server: {self.base_url}")
            logger.debug(f"Health URL: {self.health_url}")
            logger.debug(f"Analyze URL: {self.analyze_url}")
            
        except Exception as e:
            logger.error(f"Error initializing NLPClientManager: {e}")
            raise
    
    def check_health(self) -> HealthCheckResult:
        """
        Check NLP server health status
        
        Returns:
            HealthCheckResult with server status and metadata
        """
        start_time = time.time()
        
        try:
            logger.debug(f"Checking NLP server health at: {self.health_url}")
            
            response = requests.get(
                self.health_url,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Validate expected health response format
                if health_data.get('status') == 'healthy':
                    result = HealthCheckResult(
                        status=HealthStatus.HEALTHY,
                        timestamp=health_data.get('timestamp', time.time()),
                        version=health_data.get('version'),
                        total_managers=health_data.get('total_managers'),
                        response_time_ms=response_time_ms,
                        raw_response=health_data
                    )
                    
                    logger.info(f"NLP server health check successful: {health_data.get('version', 'unknown')} "
                               f"({health_data.get('total_managers', 0)} managers) - {response_time_ms:.1f}ms")
                    return result
                else:
                    logger.warning(f"NLP server reports unhealthy status: {health_data.get('status')}")
                    return HealthCheckResult(
                        status=HealthStatus.UNHEALTHY,
                        timestamp=time.time(),
                        response_time_ms=response_time_ms,
                        error_message=f"Server status: {health_data.get('status')}",
                        raw_response=health_data
                    )
            else:
                logger.error(f"Health check failed with status code: {response.status_code}")
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    timestamp=time.time(),
                    response_time_ms=response_time_ms,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during health check: {e}")
            return HealthCheckResult(
                status=HealthStatus.UNREACHABLE,
                timestamp=time.time(),
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error during health check: {e}")
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                timestamp=time.time(),
                error_message=str(e)
            )
    
    def analyze_message(self, message: str, user_id: str = "ash_thrash_test", 
                       channel_id: str = "testing_channel") -> Optional[AnalysisResult]:
        """
        Analyze message using NLP server with retry logic
        
        Enhanced in v3.1-1a-2 to capture crisis_score for threshold optimization.
        
        Args:
            message: Message text to analyze
            user_id: Discord user ID for the request
            channel_id: Discord channel ID for the request
            
        Returns:
            AnalysisResult or None if all retries failed
        """
        request_data = {
            "message": message,
            "user_id": user_id,
            "channel_id": channel_id
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Analyzing message (attempt {attempt + 1}/{self.max_retries + 1}): "
                           f"'{message[:50]}{'...' if len(message) > 50 else ''}'")
                
                start_time = time.time()
                
                response = requests.post(
                    self.analyze_url,
                    json=request_data,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                processing_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    analysis_data = response.json()
                    
                    # Extract crisis_score with fallback to confidence_score for backward compatibility
                    crisis_score = analysis_data.get('crisis_score')
                    confidence_score = analysis_data.get('confidence_score', 0.0)
                    
                    # If crisis_score is not available, use confidence_score as fallback
                    # This ensures backward compatibility while we transition
                    if crisis_score is None:
                        crisis_score = confidence_score
                        logger.debug(f"crisis_score not found, using confidence_score as fallback: {crisis_score:.3f}")
                    else:
                        logger.debug(f"Extracted crisis_score: {crisis_score:.3f}, confidence_score: {confidence_score:.3f}")
                    
                    result = AnalysisResult(
                        crisis_level=analysis_data.get('crisis_level', 'unknown'),
                        confidence_score=confidence_score,
                        crisis_score=crisis_score,  # NEW: Crisis score for threshold optimization
                        needs_response=analysis_data.get('needs_response', False),
                        processing_time_ms=analysis_data.get('processing_time_ms', processing_time),
                        method=analysis_data.get('method', 'unknown'),
                        reasoning=analysis_data.get('reasoning'),
                        detected_categories=analysis_data.get('detected_categories'),
                        raw_response=analysis_data
                    )
                    
                    logger.debug(f"Analysis successful: {result.crisis_level} "
                               f"(crisis_score: {result.crisis_score:.3f}, "
                               f"confidence: {result.confidence_score:.3f}, "
                               f"time: {result.processing_time_ms:.1f}ms)")
                    return result
                else:
                    logger.warning(f"Analysis failed with status code: {response.status_code} - {response.text}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay_ms / 1000.0)
                        continue
                    else:
                        logger.error(f"Analysis failed after {self.max_retries + 1} attempts")
                        return None
                        
            except requests.exceptions.RequestException as e:
                logger.warning(f"Network error during analysis (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay_ms / 1000.0)
                    continue
                else:
                    logger.error(f"Analysis failed after {self.max_retries + 1} attempts due to network errors")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error during analysis: {e}")
                return None
        
        return None
    
    def verify_server_ready(self) -> Tuple[bool, str]:
        """
        Verify NLP server is ready for testing
        
        Returns:
            Tuple of (is_ready, status_message)
        """
        health_result = self.check_health()
        
        if health_result.status == HealthStatus.HEALTHY:
            return True, f"NLP server ready: {health_result.version} ({health_result.total_managers} managers)"
        elif health_result.status == HealthStatus.UNHEALTHY:
            return False, f"NLP server unhealthy: {health_result.error_message}"
        else:  # UNREACHABLE
            return False, f"NLP server unreachable: {health_result.error_message}"
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get comprehensive server information for reporting
        
        Returns:
            Dictionary with server configuration and status
        """
        health_result = self.check_health()
        
        return {
            'configuration': {
                'base_url': self.base_url,
                'timeout_seconds': self.timeout,
                'max_retries': self.max_retries,
                'retry_delay_ms': self.retry_delay_ms
            },
            'health_status': {
                'status': health_result.status.value,
                'version': health_result.version,
                'total_managers': health_result.total_managers,
                'response_time_ms': health_result.response_time_ms,
                'timestamp': health_result.timestamp,
                'error_message': health_result.error_message
            },
            'endpoints': {
                'health_url': self.health_url,
                'analyze_url': self.analyze_url
            }
        }

def create_nlp_client_manager(unified_config_manager) -> NLPClientManager:
    """
    Factory function for NLPClientManager (Clean v3.1 Pattern)
    
    Args:
        unified_config_manager: UnifiedConfigManager instance
        
    Returns:
        Initialized NLPClientManager instance
        
    Raises:
        ValueError: If unified_config_manager is None or invalid
    """
    logger.debug("Creating NLPClientManager v3.1-1a-2 with Clean v3.1 architecture")
    
    if not unified_config_manager:
        raise ValueError("UnifiedConfigManager is required for NLPClientManager factory")
    
    return NLPClientManager(unified_config_manager)

# Export public interface
__all__ = ['NLPClientManager', 'AnalysisResult', 'HealthCheckResult', 'HealthStatus', 'create_nlp_client_manager']

logger.info("NLPClientManager v3.1-1a-2 loaded with crisis_score support")