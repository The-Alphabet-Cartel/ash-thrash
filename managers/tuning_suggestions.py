"""
Ash-Thrash: Testing Suite for Ash-NLP Backend for The Alphabet Cartel Discord Community
********************************************************************************
Advanced Tuning Intelligence Manager for Ash-Thrash Service
---
FILE VERSION: v3.1-3a-4
LAST MODIFIED: 2025-09-12
PHASE: 3a Step 1 - Enhanced with Crisis Score Analysis
CLEAN ARCHITECTURE: v3.1 Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND DATA STRUCTURES - Clean Architecture v3.1
# ============================================================================

class EnsembleMode(Enum):
    """Supported NLP ensemble modes for threshold mapping"""
    CONSENSUS = "consensus"
    MAJORITY = "majority"
    WEIGHTED = "weighted"

class ConfidenceLevel(Enum):
    """Confidence levels for tuning recommendations"""
    HIGH = "high"        # >80% confidence in recommendation
    MEDIUM = "medium"    # 60-80% confidence in recommendation
    LOW = "low"          # 40-60% confidence in recommendation
    UNCERTAIN = "uncertain"  # <40% confidence in recommendation

class RiskLevel(Enum):
    """Risk assessment levels for threshold changes"""
    CRITICAL = "critical"    # High risk - could affect safety
    MODERATE = "moderate"    # Medium risk - needs careful testing
    LOW = "low"              # Low risk - relatively safe
    MINIMAL = "minimal"      # Very low risk - minor adjustments

@dataclass
class ThresholdRecommendation:
    """Data class for individual threshold adjustment recommendations"""
    variable_name: str
    current_value: float
    recommended_value: float
    confidence_level: ConfidenceLevel
    risk_level: RiskLevel
    reasoning: str
    expected_improvement: str
    rollback_plan: str
    test_priority: int  # 1=highest, 5=lowest priority for testing
    crisis_score_analysis: Optional[Dict[str, Any]] = None  # NEW: Crisis score insights

@dataclass
class TuningAnalysis:
    """Complete tuning analysis results"""
    ensemble_mode: EnsembleMode
    critical_issues: List[str]
    recommendations: List[ThresholdRecommendation]
    boundary_test_suggestions: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    confidence_summary: Dict[str, int]
    implementation_order: List[str]
    crisis_score_insights: Dict[str, Any] = None  # NEW: Overall crisis score analysis

# ============================================================================
# TUNING SUGGESTIONS MANAGER - Clean Architecture v3.1
# ============================================================================

class TuningSuggestionsManager:
    """
    Advanced tuning intelligence manager for threshold optimization
    
    Enhanced in v3.1-3a-4 to utilize both crisis_score and confidence_score 
    for more sophisticated threshold adjustment recommendations.
    
    Provides intelligent threshold adjustment recommendations with confidence levels,
    risk assessment, and boundary testing capabilities for The Alphabet Cartel
    LGBTQIA+ community crisis detection optimization.
    
    Clean Architecture v3.1 Compliant - Phase 3a
    """
    
    def __init__(self, unified_config_manager, results_manager, analyze_results_manager):
        """
        Initialize TuningSuggestionsManager with dependency injection
        
        Args:
            unified_config_manager: UnifiedConfigManager for configuration access
            results_manager: ResultsManager for test result access  
            analyze_results_manager: AnalyzeResultsManager for analysis data
        """
        logger.debug("Initializing TuningSuggestionsManager v3.1-3a-4 with crisis score analysis")
        
        if not unified_config_manager:
            raise ValueError("UnifiedConfigManager is required for TuningSuggestionsManager")
        if not results_manager:
            raise ValueError("ResultsManager is required for TuningSuggestionsManager")  
        if not analyze_results_manager:
            raise ValueError("AnalyzeResultsManager is required for TuningSuggestionsManager")
            
        self.config_manager = unified_config_manager
        self.results_manager = results_manager
        self.analyze_manager = analyze_results_manager
        
        # Get base configuration paths using correct UnifiedConfigManager method
        app_data_dir = os.environ.get('APP_DATA_DIR', '/app')
        self.config_dir = Path(app_data_dir) / 'config'
        self.results_dir = Path(app_data_dir) / 'results' 
        self.reports_dir = Path(app_data_dir) / 'reports'
        
        # Threshold mapping configuration
        self.threshold_mappings = self._initialize_threshold_mappings()
        
        # Confidence and risk assessment parameters - loaded from JSON config
        config_data = self._load_config_parameters()
        self.confidence_thresholds = config_data.get('confidence_parameters', {
            'high_confidence_min': 0.80,
            'medium_confidence_min': 0.60, 
            'low_confidence_min': 0.40
        })
        
        # Safety-first parameters for LGBTQIA+ community - loaded from JSON config
        self.safety_parameters = config_data.get('safety_parameters', {
            'false_negative_weight': 3.0,
            'critical_category_weight': 2.0,
            'minimum_improvement_threshold': 0.05,
            'maximum_risk_tolerance': 'moderate'
        })
        
        # NEW: Crisis score analysis parameters
        self.crisis_score_parameters = config_data.get('crisis_score_parameters', {
            'score_variance_threshold': 0.15,  # Flag high variance between crisis/confidence scores
            'boundary_sensitivity': 0.05,     # Sensitivity for boundary detection
            'correlation_significance': 0.70   # Minimum correlation for pattern significance
        })
        
        logger.info("TuningSuggestionsManager v3.1-3a-4 initialized successfully with crisis score analysis")
    
    def _load_config_parameters(self) -> Dict[str, Any]:
        """Load configuration parameters using UnifiedConfigManager with placeholder resolution"""
        try:
            # Use UnifiedConfigManager to load configuration sections with automatic placeholder replacement
            resolved_config = {}
            
            # Process confidence parameters - UnifiedConfigManager handles ${ENV_VAR} replacement automatically
            try:
                resolved_config['confidence_parameters'] = {
                    'high_confidence_min': self.config_manager.get_config_section('threshold_mappings', 'confidence_parameters.high_confidence_min', 0.80),
                    'medium_confidence_min': self.config_manager.get_config_section('threshold_mappings', 'confidence_parameters.medium_confidence_min', 0.60),
                    'low_confidence_min': self.config_manager.get_config_section('threshold_mappings', 'confidence_parameters.low_confidence_min', 0.40)
                }
            except Exception as e:
                logger.warning(f"Could not load confidence parameters: {e}, using defaults")
                resolved_config['confidence_parameters'] = {
                    'high_confidence_min': 0.80,
                    'medium_confidence_min': 0.60,
                    'low_confidence_min': 0.40
                }
            
            # Process safety parameters - UnifiedConfigManager handles ${ENV_VAR} replacement automatically  
            try:
                resolved_config['safety_parameters'] = {
                    'false_negative_weight': self.config_manager.get_config_section('threshold_mappings', 'safety_parameters.false_negative_weight', 3.0),
                    'critical_category_weight': self.config_manager.get_config_section('threshold_mappings', 'safety_parameters.critical_category_weight', 2.0),
                    'minimum_improvement_threshold': self.config_manager.get_config_section('threshold_mappings', 'safety_parameters.minimum_improvement_threshold', 0.05),
                    'maximum_risk_tolerance': self.config_manager.get_config_section('threshold_mappings', 'safety_parameters.maximum_risk_tolerance', 'moderate')
                }
            except Exception as e:
                logger.warning(f"Could not load safety parameters: {e}, using defaults")
                resolved_config['safety_parameters'] = {
                    'false_negative_weight': 3.0,
                    'critical_category_weight': 2.0,
                    'minimum_improvement_threshold': 0.05,
                    'maximum_risk_tolerance': 'moderate'
                }
            
            # NEW: Process crisis score parameters
            try:
                resolved_config['crisis_score_parameters'] = {
                    'score_variance_threshold': self.config_manager.get_config_section('threshold_mappings', 'crisis_score_parameters.score_variance_threshold', 0.15),
                    'boundary_sensitivity': self.config_manager.get_config_section('threshold_mappings', 'crisis_score_parameters.boundary_sensitivity', 0.05),
                    'correlation_significance': self.config_manager.get_config_section('threshold_mappings', 'crisis_score_parameters.correlation_significance', 0.70)
                }
            except Exception as e:
                logger.warning(f"Could not load crisis score parameters: {e}, using defaults")
                resolved_config['crisis_score_parameters'] = {
                    'score_variance_threshold': 0.15,
                    'boundary_sensitivity': 0.05,
                    'correlation_significance': 0.70
                }
            
            logger.debug("Configuration parameters loaded successfully with environment variable resolution")
            return resolved_config
            
        except Exception as e:
            logger.error(f"Error loading configuration parameters: {e}")
            # Return safe defaults
            return {
                'confidence_parameters': {
                    'high_confidence_min': 0.80,
                    'medium_confidence_min': 0.60,
                    'low_confidence_min': 0.40
                },
                'safety_parameters': {
                    'false_negative_weight': 3.0,
                    'critical_category_weight': 2.0,
                    'minimum_improvement_threshold': 0.05,
                    'maximum_risk_tolerance': 'moderate'
                },
                'crisis_score_parameters': {
                    'score_variance_threshold': 0.15,
                    'boundary_sensitivity': 0.05,
                    'correlation_significance': 0.70
                }
            }
    
    def _initialize_threshold_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize threshold variable mappings from JSON configuration"""
        try:
            # Load threshold mappings from JSON configuration
            mappings_file = self.config_dir / 'threshold_mappings.json'
            
            if not mappings_file.exists():
                logger.warning(f"Threshold mappings file not found: {mappings_file}")
                return self._create_fallback_mappings()
            
            # Load and parse JSON with environment variable substitution
            with open(mappings_file, 'r') as f:
                config_data = json.load(f)
            
            # Extract threshold mappings and convert risk levels to enums
            raw_mappings = config_data.get('threshold_mappings', {})
            processed_mappings = {}
            
            # Map risk level strings to enums
            risk_mapping = {
                'critical': RiskLevel.CRITICAL,
                'moderate': RiskLevel.MODERATE,
                'low': RiskLevel.LOW,
                'minimal': RiskLevel.MINIMAL
            }
            
            for mode, mode_data in raw_mappings.items():
                processed_mappings[mode] = {}
                
                for threshold_type in ['individual_thresholds', 'ensemble_thresholds']:
                    if threshold_type in mode_data:
                        processed_mappings[mode][threshold_type] = {}
                        
                        for var_name, var_data in mode_data[threshold_type].items():
                            # Convert range format and risk level enum
                            processed_var = dict(var_data)
                            processed_var['range'] = (var_data['range_min'], var_data['range_max'])
                            processed_var['risk_level'] = risk_mapping.get(
                                var_data['risk_level'].lower(), 
                                RiskLevel.LOW
                            )
                            
                            # Remove the separate min/max fields
                            processed_var.pop('range_min', None)
                            processed_var.pop('range_max', None)
                            
                            processed_mappings[mode][threshold_type][var_name] = processed_var
            
            logger.debug(f"Loaded threshold mappings for {len(processed_mappings)} ensemble modes")
            return processed_mappings
            
        except Exception as e:
            logger.error(f"Error loading threshold mappings from JSON: {e}")
            return self._create_fallback_mappings()
    
    def _create_fallback_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Create minimal fallback mappings if JSON loading fails"""
        logger.warning("Using fallback threshold mappings")
        return {mode.value: {'individual_thresholds': {}, 'ensemble_thresholds': {}} 
               for mode in EnsembleMode}
    
    def get_current_ensemble_mode(self) -> EnsembleMode:
        """
        Determine current NLP ensemble mode using UnifiedConfigManager
        
        Returns:
            Current ensemble mode with graceful fallback
        """
        try:
            # Use UnifiedConfigManager to get ensemble mode (no specific JSON file needed for this env var)
            mode_str = os.environ.get('NLP_ENSEMBLE_MODE', 'consensus').lower()
            
            # Map string to enum with validation
            mode_mapping = {
                'consensus': EnsembleMode.CONSENSUS,
                'majority': EnsembleMode.MAJORITY, 
                'weighted': EnsembleMode.WEIGHTED
            }
            
            if mode_str in mode_mapping:
                logger.debug(f"Current ensemble mode: {mode_str}")
                return mode_mapping[mode_str]
            else:
                logger.warning(f"Unknown ensemble mode '{mode_str}', defaulting to consensus")
                return EnsembleMode.CONSENSUS
                
        except Exception as e:
            logger.error(f"Error determining ensemble mode: {e}, defaulting to consensus")
            return EnsembleMode.CONSENSUS
    
    def _analyze_crisis_score_patterns(self, failed_tests: List[Dict]) -> Dict[str, Any]:
        """
        NEW: Analyze crisis score patterns to identify threshold adjustment opportunities
        
        Args:
            failed_tests: List of failed test details with crisis_score and confidence_score
            
        Returns:
            Analysis of crisis score patterns for threshold optimization
        """
        try:
            logger.debug(f"Analyzing crisis score patterns for {len(failed_tests)} failed tests")
            
            # Extract scores for analysis
            crisis_scores = []
            confidence_scores = []
            score_variances = []
            
            for test in failed_tests:
                crisis_score = test.get('crisis_score', test.get('confidence_score', 0.0))
                confidence_score = test.get('confidence_score', 0.0)
                
                crisis_scores.append(crisis_score)
                confidence_scores.append(confidence_score)
                
                # Calculate variance between crisis and confidence scores
                variance = abs(crisis_score - confidence_score)
                score_variances.append(variance)
            
            if not crisis_scores:
                return {'error': 'No crisis scores available for analysis'}
            
            # Calculate statistical measures
            avg_crisis_score = sum(crisis_scores) / len(crisis_scores)
            avg_confidence_score = sum(confidence_scores) / len(confidence_scores)
            avg_variance = sum(score_variances) / len(score_variances)
            
            # Identify boundary cases (scores near threshold boundaries)
            boundary_cases = self._identify_boundary_cases(crisis_scores, confidence_scores)
            
            # Analyze score correlation
            correlation = self._calculate_score_correlation(crisis_scores, confidence_scores)
            
            # Identify threshold adjustment opportunities
            threshold_opportunities = self._identify_threshold_opportunities(
                crisis_scores, confidence_scores, failed_tests
            )
            
            analysis = {
                'statistics': {
                    'avg_crisis_score': avg_crisis_score,
                    'avg_confidence_score': avg_confidence_score,
                    'avg_score_variance': avg_variance,
                    'score_correlation': correlation,
                    'high_variance_count': len([v for v in score_variances 
                                              if v > self.crisis_score_parameters['score_variance_threshold']])
                },
                'boundary_analysis': boundary_cases,
                'threshold_opportunities': threshold_opportunities,
                'insights': self._generate_crisis_score_insights(
                    avg_crisis_score, avg_confidence_score, avg_variance, correlation
                )
            }
            
            logger.debug(f"Crisis score analysis complete: correlation={correlation:.3f}, "
                        f"avg_variance={avg_variance:.3f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing crisis score patterns: {e}")
            return {'error': str(e)}
    
    def _identify_boundary_cases(self, crisis_scores: List[float], 
                                confidence_scores: List[float]) -> Dict[str, Any]:
        """Identify scores near threshold boundaries for focused analysis"""
        try:
            # Common threshold boundaries (these could be loaded from config)
            threshold_boundaries = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            boundary_sensitivity = self.crisis_score_parameters['boundary_sensitivity']
            
            boundary_cases = {
                'crisis_score_boundaries': {},
                'confidence_score_boundaries': {},
                'dual_boundary_cases': []
            }
            
            # Analyze crisis score boundaries
            for boundary in threshold_boundaries:
                near_boundary = [score for score in crisis_scores 
                               if abs(score - boundary) <= boundary_sensitivity]
                if near_boundary:
                    boundary_cases['crisis_score_boundaries'][boundary] = {
                        'count': len(near_boundary),
                        'scores': near_boundary,
                        'avg_score': sum(near_boundary) / len(near_boundary)
                    }
            
            # Analyze confidence score boundaries
            for boundary in threshold_boundaries:
                near_boundary = [score for score in confidence_scores 
                               if abs(score - boundary) <= boundary_sensitivity]
                if near_boundary:
                    boundary_cases['confidence_score_boundaries'][boundary] = {
                        'count': len(near_boundary),
                        'scores': near_boundary,
                        'avg_score': sum(near_boundary) / len(near_boundary)
                    }
            
            # Identify cases where both scores are near boundaries
            for i, (crisis, confidence) in enumerate(zip(crisis_scores, confidence_scores)):
                crisis_near_boundary = any(abs(crisis - b) <= boundary_sensitivity 
                                         for b in threshold_boundaries)
                confidence_near_boundary = any(abs(confidence - b) <= boundary_sensitivity 
                                             for b in threshold_boundaries)
                
                if crisis_near_boundary and confidence_near_boundary:
                    boundary_cases['dual_boundary_cases'].append({
                        'index': i,
                        'crisis_score': crisis,
                        'confidence_score': confidence,
                        'variance': abs(crisis - confidence)
                    })
            
            return boundary_cases
            
        except Exception as e:
            logger.error(f"Error identifying boundary cases: {e}")
            return {}
    
    def _calculate_score_correlation(self, crisis_scores: List[float], 
                                   confidence_scores: List[float]) -> float:
        """Calculate correlation between crisis and confidence scores"""
        try:
            if len(crisis_scores) != len(confidence_scores) or len(crisis_scores) < 2:
                return 0.0
            
            # Calculate Pearson correlation coefficient
            n = len(crisis_scores)
            sum_crisis = sum(crisis_scores)
            sum_confidence = sum(confidence_scores)
            sum_crisis_sq = sum(x * x for x in crisis_scores)
            sum_confidence_sq = sum(x * x for x in confidence_scores)
            sum_products = sum(x * y for x, y in zip(crisis_scores, confidence_scores))
            
            numerator = n * sum_products - sum_crisis * sum_confidence
            denominator = ((n * sum_crisis_sq - sum_crisis * sum_crisis) * 
                          (n * sum_confidence_sq - sum_confidence * sum_confidence)) ** 0.5
            
            if denominator == 0:
                return 0.0
                
            correlation = numerator / denominator
            return max(-1.0, min(1.0, correlation))  # Clamp to [-1, 1]
            
        except Exception as e:
            logger.error(f"Error calculating score correlation: {e}")
            return 0.0
    
    def _identify_threshold_opportunities(self, crisis_scores: List[float], 
                                        confidence_scores: List[float],
                                        failed_tests: List[Dict]) -> List[Dict[str, Any]]:
        """Identify specific threshold adjustment opportunities based on crisis scores"""
        try:
            opportunities = []
            
            # Group by expected vs actual crisis levels
            level_groups = {}
            for i, test in enumerate(failed_tests):
                expected = test.get('expected_crisis_level', 'unknown')
                actual = test.get('actual_crisis_level', 'unknown')
                pattern = f"{expected}_to_{actual}"
                
                if pattern not in level_groups:
                    level_groups[pattern] = []
                
                level_groups[pattern].append({
                    'crisis_score': crisis_scores[i] if i < len(crisis_scores) else 0.0,
                    'confidence_score': confidence_scores[i] if i < len(confidence_scores) else 0.0,
                    'test_data': test
                })
            
            # Analyze each pattern for threshold opportunities
            for pattern, tests in level_groups.items():
                if len(tests) < 2:  # Need multiple examples for meaningful analysis
                    continue
                
                pattern_crisis_scores = [t['crisis_score'] for t in tests]
                pattern_confidence_scores = [t['confidence_score'] for t in tests]
                
                avg_crisis = sum(pattern_crisis_scores) / len(pattern_crisis_scores)
                avg_confidence = sum(pattern_confidence_scores) / len(pattern_confidence_scores)
                
                # Identify potential threshold adjustments
                if avg_crisis < avg_confidence:
                    # Crisis scores lower than confidence - might need to lower thresholds
                    opportunity = {
                        'pattern': pattern,
                        'type': 'lower_threshold',
                        'avg_crisis_score': avg_crisis,
                        'avg_confidence_score': avg_confidence,
                        'score_difference': avg_confidence - avg_crisis,
                        'test_count': len(tests),
                        'suggested_adjustment': -(avg_confidence - avg_crisis) * 0.5,
                        'reasoning': f"Crisis scores ({avg_crisis:.3f}) lower than confidence ({avg_confidence:.3f}) for {pattern}"
                    }
                    opportunities.append(opportunity)
                    
                elif avg_crisis > avg_confidence + 0.1:  # Significant difference
                    # Crisis scores higher than confidence - might need to raise thresholds  
                    opportunity = {
                        'pattern': pattern,
                        'type': 'raise_threshold',
                        'avg_crisis_score': avg_crisis,
                        'avg_confidence_score': avg_confidence,
                        'score_difference': avg_crisis - avg_confidence,
                        'test_count': len(tests),
                        'suggested_adjustment': (avg_crisis - avg_confidence) * 0.3,
                        'reasoning': f"Crisis scores ({avg_crisis:.3f}) higher than confidence ({avg_confidence:.3f}) for {pattern}"
                    }
                    opportunities.append(opportunity)
            
            logger.debug(f"Identified {len(opportunities)} threshold opportunities from crisis score analysis")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying threshold opportunities: {e}")
            return []
    
    def _generate_crisis_score_insights(self, avg_crisis: float, avg_confidence: float,
                                      avg_variance: float, correlation: float) -> List[str]:
        """Generate human-readable insights from crisis score analysis"""
        insights = []
        
        try:
            # Correlation insights
            if correlation > self.crisis_score_parameters['correlation_significance']:
                insights.append(f"Strong correlation ({correlation:.2f}) between crisis and confidence scores indicates consistent scoring")
            elif correlation < 0.3:
                insights.append(f"Low correlation ({correlation:.2f}) suggests crisis and confidence scores measure different aspects")
            
            # Variance insights
            if avg_variance > self.crisis_score_parameters['score_variance_threshold']:
                insights.append(f"High average variance ({avg_variance:.3f}) between scores indicates potential calibration issues")
            else:
                insights.append(f"Low variance ({avg_variance:.3f}) between scores indicates good calibration")
            
            # Score comparison insights
            if avg_crisis < avg_confidence - 0.1:
                insights.append("Crisis scores consistently lower than confidence - consider lowering thresholds")
            elif avg_crisis > avg_confidence + 0.1:
                insights.append("Crisis scores consistently higher than confidence - consider raising thresholds")
            else:
                insights.append("Crisis and confidence scores are well-aligned")
            
            # Threshold adjustment suggestions
            if avg_variance > 0.2:
                insights.append("High score variance suggests reviewing threshold boundaries for better consistency")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating crisis score insights: {e}")
            return ["Error generating insights from crisis score analysis"]
    
    def analyze_failure_patterns(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test failure patterns to identify threshold adjustment opportunities
        Enhanced in v3.1-3a-4 to include crisis score analysis.
        
        Args:
            test_results: Complete test results from latest run
            
        Returns:
            Analysis of failure patterns with specific threshold mapping and crisis score insights
        """
        try:
            logger.info("Analyzing failure patterns for threshold recommendations with crisis score analysis")
            logger.debug("=" * 50)
            logger.debug("🔍 ENHANCED FAILURE PATTERN ANALYSIS DEBUG")
            logger.debug("=" * 50)
            
            current_mode = self.get_current_ensemble_mode()
            category_results = test_results.get('category_results', {})
            
            logger.debug(f"Current ensemble mode: {current_mode.value}")
            logger.debug(f"Number of categories to analyze: {len(category_results)}")
            logger.debug(f"Category names: {list(category_results.keys())}")
            
            failure_analysis = {
                'ensemble_mode': current_mode.value,
                'critical_failures': [],
                'threshold_candidates': [],
                'pattern_insights': {},
                'safety_concerns': [],
                'crisis_score_analysis': {}  # NEW: Crisis score analysis results
            }
            
            # Collect all failed tests for overall crisis score analysis
            all_failed_tests = []
            
            # Analyze each category for failure patterns
            for category, results in category_results.items():
                logger.debug(f"--- Analyzing category: {category} ---")
                logger.debug(f"Results type: {type(results)}")
                logger.debug(f"Results keys: {list(results.keys()) if results else 'None'}")
                
                if not results or 'summary' not in results:
                    logger.warning(f"No summary found for category {category}")
                    continue
                    
                summary = results['summary']
                pass_rate = summary.get('pass_rate', 0.0)
                total_tests = summary.get('total_tests', 0)
                failed_tests = summary.get('failed_tests', 0)
                
                logger.debug(f"Category {category} stats:")
                logger.debug(f"  Pass rate: {pass_rate}%")
                logger.debug(f"  Total tests: {total_tests}")
                logger.debug(f"  Failed tests: {failed_tests}")
                logger.debug(f"  Has failed_tests_details: {'failed_tests_details' in results}")
                
                # Identify critical failure patterns
                if category.startswith('definite_high') and pass_rate < 95:
                    logger.warning(f"🚨 CRITICAL FAILURE: {category} pass rate {pass_rate}% < 95%")
                    failure_analysis['critical_failures'].append({
                        'category': category,
                        'issue': 'Critical safety category under-performing',
                        'pass_rate': pass_rate,
                        'risk': 'HIGH - False negatives in crisis detection',
                        'priority': 1
                    })
                elif category.startswith('definite_') and pass_rate < 80:
                    logger.warning(f"⚠️ SIGNIFICANT FAILURE: {category} pass rate {pass_rate}% < 80%")
                    failure_analysis['critical_failures'].append({
                        'category': category,
                        'issue': 'Definite category significantly under-performing', 
                        'pass_rate': pass_rate,
                        'risk': 'MODERATE - Classification accuracy compromised',
                        'priority': 2
                    })
                else:
                    logger.debug(f"Category {category} does not meet critical failure criteria")
                
                # Identify threshold adjustment candidates
                if failed_tests > 0:
                    logger.debug(f"Processing {failed_tests} failed tests for threshold candidates...")
                    
                    if 'failed_tests_details' in results:
                        failed_test_details = results['failed_tests_details']
                        logger.debug(f"Found {len(failed_test_details)} failed test details")
                        
                        # Add to overall collection for crisis score analysis
                        all_failed_tests.extend(failed_test_details)
                        
                        # Log first few failed tests for inspection
                        for i, failed_test in enumerate(failed_test_details[:3], 1):
                            crisis_score = failed_test.get('crisis_score', 'N/A')
                            confidence_score = failed_test.get('confidence_score', 'N/A')
                            logger.debug(f"  Failed test {i}: {failed_test.get('expected_crisis_level', 'unknown')} → {failed_test.get('actual_crisis_level', 'unknown')} "
                                       f"(crisis: {crisis_score}, confidence: {confidence_score})")
                        
                        self._analyze_threshold_candidates(
                            category, 
                            failed_test_details,
                            current_mode,
                            failure_analysis['threshold_candidates']
                        )
                    else:
                        logger.warning(f"Category {category} has {failed_tests} failed tests but no failed_tests_details")
                else:
                    logger.debug(f"Category {category} has no failed tests to analyze")
            
            # NEW: Perform overall crisis score analysis
            if all_failed_tests:
                logger.debug(f"Performing crisis score analysis on {len(all_failed_tests)} total failed tests")
                failure_analysis['crisis_score_analysis'] = self._analyze_crisis_score_patterns(all_failed_tests)
            else:
                logger.debug("No failed tests available for crisis score analysis")
                failure_analysis['crisis_score_analysis'] = {'message': 'No failed tests available for analysis'}
            
            logger.debug(f"Critical failures found: {len(failure_analysis['critical_failures'])}")
            logger.debug(f"Threshold candidates found: {len(failure_analysis['threshold_candidates'])}")
            
            # Generate pattern insights
            failure_analysis['pattern_insights'] = self._generate_pattern_insights(
                category_results, current_mode
            )
            
            # Assess safety concerns
            failure_analysis['safety_concerns'] = self._assess_safety_concerns(
                failure_analysis['critical_failures']
            )
            
            logger.debug("=" * 50)
            logger.debug("🔍 ENHANCED FAILURE ANALYSIS SUMMARY")
            logger.debug("=" * 50)
            logger.debug(f"Critical failures: {len(failure_analysis['critical_failures'])}")
            logger.debug(f"Threshold candidates: {len(failure_analysis['threshold_candidates'])}")
            logger.debug(f"Safety concerns: {len(failure_analysis['safety_concerns'])}")
            logger.debug(f"Crisis score analysis available: {'error' not in failure_analysis['crisis_score_analysis']}")
            
            logger.info(f"Enhanced failure pattern analysis complete: {len(failure_analysis['critical_failures'])} critical issues found")
            return failure_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing failure patterns: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'ensemble_mode': self.get_current_ensemble_mode().value,
                'critical_failures': [],
                'threshold_candidates': [],
                'pattern_insights': {},
                'safety_concerns': [],
                'crisis_score_analysis': {'error': str(e)},
                'error': str(e)
            }
    
    def _analyze_threshold_candidates(self, category: str, failed_tests: List[Dict], 
                                    mode: EnsembleMode, candidates: List[Dict]):
        """
        Analyze failed tests to identify specific threshold adjustment candidates
        Enhanced to include crisis score analysis in candidate evaluation.
        """
        try:
            logger.debug(f"🔍 Analyzing threshold candidates for category: {category}")
            logger.debug(f"Failed tests count: {len(failed_tests)}")
            logger.debug(f"Ensemble mode: {mode.value}")
            
            mode_mappings = self.threshold_mappings.get(mode.value, {})
            logger.debug(f"Available threshold mappings: {list(mode_mappings.keys())}")
            
            definite_high = self.config_manager.get_config_section('test_settings', 'test_categories.definite_high.expected_priority', ['high'])
            definite_medium = self.config_manager.get_config_section('test_settings', 'test_categories.definite_medium.expected_priority', ['medium'])
            definite_low = self.config_manager.get_config_section('test_settings', 'test_categories.definite_low.expected_priority', ['low'])
            definite_none = self.config_manager.get_config_section('test_settings', 'test_categories.definite_none.expected_priority', ['none'])
            maybe_high_medium = self.config_manager.get_config_section('test_settings', 'test_categories.maybe_high_medium.expected_priority', ['medium', 'high'])
            maybe_medium_low = self.config_manager.get_config_section('test_settings', 'test_categories.maybe_medium_low.expected_priority', ['low', 'medium'])
            maybe_low_none = self.config_manager.get_config_section('test_settings', 'test_categories.maybe_low_none.expected_priority', ['none', 'low'])

            # Map category to expected crisis levels
            category_mapping = {
                'definite_high': definite_high,
                'definite_medium': definite_medium, 
                'definite_low': definite_low,
                'definite_none': definite_none,
                'maybe_high_medium': maybe_high_medium,
                'maybe_medium_low': maybe_medium_low,
                'maybe_low_none': maybe_low_none
            }
            
            expected_levels = category_mapping.get(category, [])
            logger.debug(f"Expected crisis levels for {category}: {expected_levels}")
            
            if not expected_levels:
                logger.warning(f"No expected levels found for category: {category}")
                return
                
            # Analyze failure patterns with crisis score analysis
            misclassification_patterns = {}
            
            logger.debug("Processing individual failed tests with crisis score analysis...")
            for i, failed_test in enumerate(failed_tests):
                actual_level = failed_test.get('actual_crisis_level', 'unknown')
                expected_level = failed_test.get('expected_crisis_level', expected_levels[0])
                confidence = failed_test.get('confidence_score', 0.0)
                crisis_score = failed_test.get('crisis_score', confidence)  # Fallback to confidence if crisis_score not available
                
                logger.debug(f"  Test {i+1}: Expected={expected_level}, Actual={actual_level}, "
                           f"Confidence={confidence:.3f}, Crisis={crisis_score:.3f}")
                
                pattern_key = f"{expected_level}_to_{actual_level}"
                if pattern_key not in misclassification_patterns:
                    misclassification_patterns[pattern_key] = {
                        'count': 0,
                        'avg_confidence': 0.0,
                        'avg_crisis_score': 0.0,  # NEW: Track crisis scores
                        'confidences': [],
                        'crisis_scores': []       # NEW: Track crisis scores
                    }
                
                misclassification_patterns[pattern_key]['count'] += 1
                misclassification_patterns[pattern_key]['confidences'].append(confidence)
                misclassification_patterns[pattern_key]['crisis_scores'].append(crisis_score)
            
            logger.debug(f"Misclassification patterns found: {list(misclassification_patterns.keys())}")
            
            # Calculate average scores and identify threshold candidates
            for pattern, data in misclassification_patterns.items():
                data['avg_confidence'] = sum(data['confidences']) / len(data['confidences'])
                data['avg_crisis_score'] = sum(data['crisis_scores']) / len(data['crisis_scores'])
                
                logger.debug(f"Pattern {pattern}: {data['count']} occurrences, "
                           f"avg confidence: {data['avg_confidence']:.3f}, "
                           f"avg crisis score: {data['avg_crisis_score']:.3f}")
                
                # Find relevant thresholds for this misclassification pattern
                relevant_thresholds = self._find_relevant_thresholds(pattern, mode_mappings)
                logger.debug(f"  Relevant thresholds: {list(relevant_thresholds.keys())}")
                
                for threshold_var, threshold_info in relevant_thresholds.items():
                    # Enhanced suggestion calculation using both scores
                    suggested_adjustment = self._calculate_enhanced_suggested_adjustment(
                        pattern, data['avg_confidence'], data['avg_crisis_score'], threshold_info
                    )
                    
                    candidate = {
                        'category': category,
                        'misclassification_pattern': pattern,
                        'threshold_variable': threshold_var,
                        'threshold_info': threshold_info,
                        'failure_count': data['count'],
                        'avg_confidence': data['avg_confidence'],
                        'avg_crisis_score': data['avg_crisis_score'],  # NEW: Include crisis score
                        'score_variance': abs(data['avg_crisis_score'] - data['avg_confidence']),  # NEW: Score variance
                        'suggested_adjustment': suggested_adjustment
                    }
                    
                    candidates.append(candidate)
                    
                    logger.debug(f"  Added enhanced threshold candidate:")
                    logger.debug(f"    Variable: {threshold_var}")
                    logger.debug(f"    Adjustment: {suggested_adjustment.get('adjustment', 0):.3f}")
                    logger.debug(f"    Direction: {suggested_adjustment.get('direction', 'none')}")
                    logger.debug(f"    Confidence: {suggested_adjustment.get('confidence', 0):.3f}")
                    logger.debug(f"    Crisis Score Factor: {suggested_adjustment.get('crisis_score_factor', 1.0):.3f}")
            
            logger.debug(f"Total enhanced threshold candidates added: {len([c for c in candidates if c['category'] == category])}")
                    
        except Exception as e:
            logger.error(f"Error analyzing threshold candidates for {category}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _calculate_enhanced_suggested_adjustment(self, pattern: str, avg_confidence: float, 
                                               avg_crisis_score: float, threshold_info: Dict) -> Dict[str, Any]:
        """
        NEW: Calculate enhanced threshold adjustment using both crisis_score and confidence_score
        
        Args:
            pattern: Misclassification pattern (e.g., "high_to_medium")
            avg_confidence: Average confidence score for this pattern
            avg_crisis_score: Average crisis score for this pattern  
            threshold_info: Threshold configuration information
            
        Returns:
            Enhanced adjustment recommendation with crisis score factor
        """
        try:
            current_default = threshold_info.get('default', 0.5)
            range_min, range_max = threshold_info.get('range', (0.0, 1.0))
            
            # Base adjustment on crisis score patterns
            parts = pattern.split('_to_')
            if len(parts) != 2:
                return {'adjustment': 0.0, 'direction': 'none', 'confidence': 0.0}
                
            expected, actual = parts[0], parts[1]
            
            # Determine adjustment direction and magnitude using crisis score
            level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
            expected_rank = level_hierarchy.get(expected, 1)
            actual_rank = level_hierarchy.get(actual, 1)
            
            # Base adjustment calculation
            if expected_rank > actual_rank:
                # Under-classifying (e.g., high classified as medium) - lower threshold
                direction = 'decrease'
                base_adjustment = -0.05
            elif expected_rank < actual_rank:
                # Over-classifying (e.g., low classified as medium) - raise threshold  
                direction = 'increase'
                base_adjustment = 0.05
            else:
                return {'adjustment': 0.0, 'direction': 'none', 'confidence': 0.0}
            
            # NEW: Crisis score factor - how much to weight the crisis score vs confidence score
            score_variance = abs(avg_crisis_score - avg_confidence)
            
            if score_variance > self.crisis_score_parameters['score_variance_threshold']:
                # High variance - use crisis score more heavily
                crisis_score_weight = 0.75
                confidence_weight = 0.25
                logger.debug(f"High score variance ({score_variance:.3f}) - weighting crisis score heavily")
            else:
                # Low variance - balanced weighting
                crisis_score_weight = 0.6
                confidence_weight = 0.4
                logger.debug(f"Low score variance ({score_variance:.3f}) - balanced score weighting")
            
            # Calculate weighted score for adjustment magnitude
            weighted_score = (avg_crisis_score * crisis_score_weight + 
                            avg_confidence * confidence_weight)
            
            # Scale adjustment based on weighted score - lower scores suggest bigger adjustment needed
            score_multiplier = max(0.5, 1.0 - weighted_score)
            suggested_adjustment = base_adjustment * score_multiplier
            
            # NEW: Crisis score factor for fine-tuning
            if avg_crisis_score < avg_confidence:
                # Crisis score lower than confidence - might need more aggressive threshold lowering
                crisis_score_factor = 1.2
            elif avg_crisis_score > avg_confidence + 0.1:
                # Crisis score significantly higher - might need less aggressive adjustment
                crisis_score_factor = 0.8
            else:
                crisis_score_factor = 1.0
            
            suggested_adjustment *= crisis_score_factor
            
            # Ensure adjustment stays within valid range
            new_value = current_default + suggested_adjustment
            new_value = max(range_min, min(range_max, new_value))
            final_adjustment = new_value - current_default
            
            # Calculate confidence in this suggestion using both scores
            suggestion_confidence = min(0.9, weighted_score + 0.2)
            if abs(final_adjustment) > 0.02:
                suggestion_confidence += 0.1  # More confidence in larger adjustments
            
            # Penalty for high variance (less confident when scores disagree)
            if score_variance > 0.2:
                suggestion_confidence *= 0.8
            
            return {
                'adjustment': final_adjustment,
                'direction': direction,
                'new_value': new_value,
                'confidence': suggestion_confidence,
                'crisis_score_factor': crisis_score_factor,
                'weighted_score': weighted_score,
                'score_variance': score_variance,
                'reasoning': (f"Pattern {pattern} with crisis score {avg_crisis_score:.2f} "
                            f"and confidence {avg_confidence:.2f} suggests {direction} threshold "
                            f"(variance: {score_variance:.3f}, factor: {crisis_score_factor:.2f})")
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced suggested adjustment: {e}")
            return {'adjustment': 0.0, 'direction': 'none', 'confidence': 0.0, 'error': str(e)}
    
    def _find_relevant_thresholds(self, pattern: str, mode_mappings: Dict) -> Dict[str, Any]:
        """Find threshold variables relevant to a misclassification pattern"""
        relevant_thresholds = {}
        
        try:
            # Extract expected and actual levels from pattern
            parts = pattern.split('_to_')
            if len(parts) != 2:
                return relevant_thresholds
                
            expected, actual = parts[0], parts[1]
            
            # Search both individual and ensemble thresholds
            for threshold_type in ['individual_thresholds', 'ensemble_thresholds']:
                thresholds = mode_mappings.get(threshold_type, {})
                
                for var_name, var_info in thresholds.items():
                    affects = var_info.get('affects', [])
                    
                    # Check if this threshold affects the levels in the pattern
                    if expected in affects or actual in affects:
                        relevant_thresholds[var_name] = var_info
                        
        except Exception as e:
            logger.error(f"Error finding relevant thresholds for pattern {pattern}: {e}")
        
        return relevant_thresholds
    
    def _generate_pattern_insights(self, category_results: Dict, mode: EnsembleMode) -> Dict[str, Any]:
        """Generate insights about overall failure patterns"""
        try:
            insights = {
                'ensemble_mode': mode.value,
                'overall_trends': [],
                'category_specific': {},
                'recommended_focus_areas': []
            }
            
            total_categories = len(category_results)
            failing_categories = 0
            total_pass_rate = 0.0
            
            # Analyze category-specific patterns
            for category, results in category_results.items():
                if not results or 'summary' not in results:
                    continue
                    
                summary = results['summary']
                pass_rate = summary.get('pass_rate', 0.0)
                total_pass_rate += pass_rate
                
                target_rate = self._get_target_rate_for_category(category)
                
                if pass_rate < target_rate:
                    failing_categories += 1
                    
                insights['category_specific'][category] = {
                    'pass_rate': pass_rate,
                    'target_rate': target_rate,
                    'performance_gap': target_rate - pass_rate,
                    'status': 'failing' if pass_rate < target_rate else 'passing'
                }
            
            # Generate overall trends
            avg_pass_rate = total_pass_rate / total_categories if total_categories > 0 else 0.0
            failure_percentage = (failing_categories / total_categories * 100) if total_categories > 0 else 0.0
            
            insights['overall_trends'].append({
                'metric': 'average_pass_rate',
                'value': avg_pass_rate,
                'assessment': 'good' if avg_pass_rate > 0.85 else 'needs_improvement'
            })
            
            insights['overall_trends'].append({
                'metric': 'failing_categories_percentage',
                'value': failure_percentage,
                'assessment': 'concerning' if failure_percentage > 30 else 'acceptable'
            })
            
            # Identify focus areas
            if failure_percentage > 50:
                insights['recommended_focus_areas'].append('Comprehensive threshold review needed')
            if any(cat.startswith('definite_high') and data.get('status') == 'failing' 
                  for cat, data in insights['category_specific'].items()):
                insights['recommended_focus_areas'].append('CRITICAL: High-priority crisis detection failing')
            if failure_percentage > 30:
                insights['recommended_focus_areas'].append('Mode-specific threshold calibration required')
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating pattern insights: {e}")
            return {'ensemble_mode': mode.value, 'error': str(e)}
    
    def _get_target_rate_for_category(self, category: str) -> float:
        """Get target pass rate for category based on implementation plan"""
        target_mapping = {
            'definite_high': 0.98,
            'definite_medium': 0.85,
            'definite_low': 0.85,
            'definite_none': 0.95,
            'maybe_high_medium': 0.90,
            'maybe_medium_low': 0.85,
            'maybe_low_none': 0.90
        }
        
        return target_mapping.get(category, 0.85)
    
    def _assess_safety_concerns(self, critical_failures: List[Dict]) -> List[Dict[str, Any]]:
        """Assess safety concerns based on critical failures"""
        try:
            safety_concerns = []
            
            # Check for high-priority crisis detection failures
            high_priority_failures = [f for f in critical_failures 
                                    if f.get('category', '').startswith('definite_high')]
            
            if high_priority_failures:
                safety_concerns.append({
                    'level': 'CRITICAL',
                    'concern': 'High-priority crisis detection compromised',
                    'description': f"{len(high_priority_failures)} high-priority categories failing",
                    'impact': 'False negatives in life-threatening situations',
                    'immediate_action': 'Review high-priority thresholds immediately',
                    'affected_categories': [f['category'] for f in high_priority_failures]
                })
            
            # Check for widespread failure patterns
            if len(critical_failures) > 3:
                safety_concerns.append({
                    'level': 'MODERATE',
                    'concern': 'Widespread classification accuracy issues',
                    'description': f"{len(critical_failures)} categories showing significant failures",
                    'impact': 'Overall crisis detection reliability compromised',
                    'immediate_action': 'Comprehensive threshold review and testing',
                    'affected_categories': [f['category'] for f in critical_failures]
                })
            
            # Check for specific pattern concerns
            definite_failures = [f for f in critical_failures 
                               if f.get('category', '').startswith('definite_')]
            
            if len(definite_failures) > 2:
                safety_concerns.append({
                    'level': 'MODERATE', 
                    'concern': 'Multiple definite categories failing accuracy targets',
                    'description': 'Core classification reliability affected',
                    'impact': 'Reduced confidence in crisis level assignments',
                    'immediate_action': 'Focus on definite category threshold tuning',
                    'affected_categories': [f['category'] for f in definite_failures]
                })
            
            return safety_concerns
            
        except Exception as e:
            logger.error(f"Error assessing safety concerns: {e}")
            return [{'level': 'ERROR', 'concern': 'Safety assessment failed', 'error': str(e)}]
    
    def generate_tuning_recommendations(self, test_results: Dict[str, Any]) -> TuningAnalysis:
        """
        Generate comprehensive tuning recommendations with confidence levels
        Enhanced in v3.1-3a-4 to include crisis score analysis in recommendations.
        """
        try:
            logger.info("Generating comprehensive tuning recommendations with crisis score analysis")
            
            # Analyze failure patterns first (now includes crisis score analysis)
            failure_analysis = self.analyze_failure_patterns(test_results)
            current_mode = EnsembleMode(failure_analysis['ensemble_mode'])
            
            # Generate specific threshold recommendations (enhanced with crisis score data)
            recommendations = self._generate_threshold_recommendations(failure_analysis, current_mode)
            
            # Create boundary test suggestions
            boundary_tests = self._generate_boundary_test_suggestions(recommendations, current_mode)
            
            # Assess overall risk
            risk_assessment = self._assess_tuning_risks(recommendations, failure_analysis)
            
            # Generate confidence summary
            confidence_summary = self._generate_confidence_summary(recommendations)
            
            # Determine implementation order
            implementation_order = self._determine_implementation_order(recommendations)
            
            # Create comprehensive analysis with crisis score insights
            analysis = TuningAnalysis(
                ensemble_mode=current_mode,
                critical_issues=[f['issue'] for f in failure_analysis['critical_failures']],
                recommendations=recommendations,
                boundary_test_suggestions=boundary_tests,
                risk_assessment=risk_assessment,
                confidence_summary=confidence_summary,
                implementation_order=implementation_order,
                crisis_score_insights=failure_analysis.get('crisis_score_analysis', {})
            )
            
            logger.info(f"Generated {len(recommendations)} enhanced threshold recommendations with crisis score analysis")
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating tuning recommendations: {e}")
            return TuningAnalysis(
                ensemble_mode=self.get_current_ensemble_mode(),
                critical_issues=[f"Error generating recommendations: {str(e)}"],
                recommendations=[],
                boundary_test_suggestions=[],
                risk_assessment={'error': str(e)},
                confidence_summary={},
                implementation_order=[],
                crisis_score_insights={'error': str(e)}
            )
    
    def _generate_threshold_recommendations(self, failure_analysis: Dict, 
                                          mode: EnsembleMode) -> List[ThresholdRecommendation]:
        """
        Generate specific threshold adjustment recommendations
        Enhanced to include crisis score analysis in recommendation creation.
        """
        try:
            recommendations = []
            candidates = failure_analysis.get('threshold_candidates', [])
            
            # Group candidates by threshold variable
            variable_candidates = {}
            for candidate in candidates:
                var_name = candidate['threshold_variable']
                if var_name not in variable_candidates:
                    variable_candidates[var_name] = []
                variable_candidates[var_name].append(candidate)
            
            # Generate enhanced recommendations for each variable
            for var_name, var_candidates in variable_candidates.items():
                recommendation = self._create_enhanced_threshold_recommendation(
                    var_name, var_candidates, mode, failure_analysis.get('crisis_score_analysis', {})
                )
                if recommendation:
                    recommendations.append(recommendation)
            
            # Sort by priority (test_priority field)
            recommendations.sort(key=lambda r: r.test_priority)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating threshold recommendations: {e}")
            return []
    
    def _create_enhanced_threshold_recommendation(self, var_name: str, candidates: List[Dict], 
                                                mode: EnsembleMode, crisis_score_analysis: Dict) -> Optional[ThresholdRecommendation]:
        """
        Create an enhanced threshold recommendation incorporating crisis score analysis
        
        Args:
            var_name: Threshold variable name
            candidates: List of candidate adjustments for this variable
            mode: Current ensemble mode
            crisis_score_analysis: Overall crisis score analysis results
            
        Returns:
            Enhanced ThresholdRecommendation with crisis score insights
        """
        try:
            if not candidates:
                return None
                
            # Get current value using environment variable
            threshold_info = candidates[0]['threshold_info']
            current_value = float(os.environ.get(var_name, threshold_info['default']))
            
            # Calculate weighted average of suggested adjustments with crisis score weighting
            total_weight = 0
            weighted_adjustment = 0.0
            crisis_score_factors = []
            
            for candidate in candidates:
                # Weight by number of failures and crisis score confidence
                base_weight = candidate['failure_count']
                crisis_score_factor = candidate['suggested_adjustment'].get('crisis_score_factor', 1.0)
                weight = base_weight * crisis_score_factor
                
                adjustment = candidate['suggested_adjustment']['adjustment']
                weighted_adjustment += adjustment * weight
                total_weight += weight
                crisis_score_factors.append(crisis_score_factor)
            
            if total_weight == 0:
                return None
                
            avg_adjustment = weighted_adjustment / total_weight
            recommended_value = current_value + avg_adjustment
            
            # Ensure within valid range
            range_min, range_max = threshold_info['range']
            recommended_value = max(range_min, min(range_max, recommended_value))
            
            # Calculate enhanced confidence level incorporating crisis score analysis
            confidence = self._calculate_enhanced_recommendation_confidence(
                candidates, avg_adjustment, crisis_score_analysis
            )
            
            # Determine risk level
            risk = threshold_info['risk_level']
            
            # Generate enhanced reasoning with crisis score insights
            reasoning = self._generate_enhanced_recommendation_reasoning(
                var_name, candidates, avg_adjustment, crisis_score_analysis
            )
            
            # Generate expected improvement description
            expected_improvement = self._generate_enhanced_expected_improvement(
                candidates, avg_adjustment, crisis_score_analysis
            )
            
            # Generate rollback plan
            rollback_plan = f"Revert {var_name} from {recommended_value:.3f} back to {current_value:.3f}"
            
            # Determine test priority with crisis score considerations
            test_priority = self._calculate_enhanced_test_priority(
                candidates, risk, confidence, crisis_score_analysis
            )
            
            # Create crisis score analysis summary for this recommendation
            crisis_score_summary = {
                'avg_crisis_score_factor': sum(crisis_score_factors) / len(crisis_score_factors),
                'score_variance_considered': any(c.get('score_variance', 0) > 0.1 for c in candidates),
                'crisis_confidence_correlation': crisis_score_analysis.get('statistics', {}).get('score_correlation', 0.0),
                'boundary_cases_involved': len(crisis_score_analysis.get('boundary_analysis', {}).get('dual_boundary_cases', [])) > 0
            }
            
            return ThresholdRecommendation(
                variable_name=var_name,
                current_value=current_value,
                recommended_value=recommended_value,
                confidence_level=confidence,
                risk_level=risk,
                reasoning=reasoning,
                expected_improvement=expected_improvement,
                rollback_plan=rollback_plan,
                test_priority=test_priority,
                crisis_score_analysis=crisis_score_summary
            )
            
        except Exception as e:
            logger.error(f"Error creating enhanced recommendation for {var_name}: {e}")
            return None
    
    def _calculate_enhanced_recommendation_confidence(self, candidates: List[Dict], 
                                                    avg_adjustment: float, 
                                                    crisis_score_analysis: Dict) -> ConfidenceLevel:
        """
        Calculate enhanced confidence level incorporating crisis score analysis
        """
        try:
            # Base confidence on consistency across candidates and adjustment magnitude
            candidate_confidences = [c['suggested_adjustment']['confidence'] for c in candidates]
            avg_candidate_confidence = sum(candidate_confidences) / len(candidate_confidences)
            
            # Factor in crisis score correlation
            correlation = crisis_score_analysis.get('statistics', {}).get('score_correlation', 0.5)
            correlation_bonus = 0.0
            if correlation > self.crisis_score_parameters['correlation_significance']:
                correlation_bonus = 0.1  # Boost confidence for high correlation
            elif correlation < 0.3:
                correlation_bonus = -0.1  # Reduce confidence for low correlation
            
            # Factor in score variance - high variance reduces confidence
            avg_variance = crisis_score_analysis.get('statistics', {}).get('avg_score_variance', 0.1)
            variance_penalty = 0.0
            if avg_variance > self.crisis_score_parameters['score_variance_threshold']:
                variance_penalty = -0.15
            
            # Factor in adjustment magnitude (larger adjustments are less certain)
            magnitude_factor = max(0.5, 1.0 - abs(avg_adjustment) * 10)
            
            # Factor in number of supporting candidates
            candidate_factor = min(1.0, len(candidates) / 5.0)
            
            overall_confidence = (avg_candidate_confidence * magnitude_factor * candidate_factor + 
                                correlation_bonus + variance_penalty)
            
            # Clamp to valid range
            overall_confidence = max(0.0, min(1.0, overall_confidence))
            
            # Map to confidence levels
            if overall_confidence >= self.confidence_thresholds['high_confidence_min']:
                return ConfidenceLevel.HIGH
            elif overall_confidence >= self.confidence_thresholds['medium_confidence_min']:
                return ConfidenceLevel.MEDIUM  
            elif overall_confidence >= self.confidence_thresholds['low_confidence_min']:
                return ConfidenceLevel.LOW
            else:
                return ConfidenceLevel.UNCERTAIN
                
        except Exception as e:
            logger.error(f"Error calculating enhanced recommendation confidence: {e}")
            return ConfidenceLevel.UNCERTAIN
    
    def _generate_enhanced_recommendation_reasoning(self, var_name: str, candidates: List[Dict], 
                                                  adjustment: float, crisis_score_analysis: Dict) -> str:
        """Generate enhanced reasoning incorporating crisis score insights"""
        try:
            direction = "increase" if adjustment > 0 else "decrease"
            magnitude = abs(adjustment)
            
            # Identify primary failure categories
            categories = list(set(c['category'] for c in candidates))
            category_str = ", ".join(categories)
            
            # Count total failures
            total_failures = sum(c['failure_count'] for c in candidates)
            
            # Crisis score insights
            correlation = crisis_score_analysis.get('statistics', {}).get('score_correlation', 0.0)
            avg_variance = crisis_score_analysis.get('statistics', {}).get('avg_score_variance', 0.0)
            
            # Base reasoning
            reasoning = (
                f"Recommended to {direction} {var_name} by {magnitude:.3f} based on "
                f"{total_failures} failures across categories: {category_str}. "
            )
            
            # Add crisis score insights
            if correlation > 0.7:
                reasoning += f"High crisis/confidence correlation ({correlation:.2f}) supports reliable adjustment. "
            elif correlation < 0.3:
                reasoning += f"Low crisis/confidence correlation ({correlation:.2f}) suggests cautious implementation. "
            
            if avg_variance > 0.15:
                reasoning += f"High score variance ({avg_variance:.3f}) indicates potential calibration issues addressed by this change. "
            
            reasoning += "This adjustment should improve classification accuracy while maintaining safety margins."
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Error generating enhanced reasoning for {var_name}: {e}")
            return f"Enhanced adjustment recommended for {var_name} based on test failures and crisis score analysis"
    
    def _generate_enhanced_expected_improvement(self, candidates: List[Dict], adjustment: float,
                                              crisis_score_analysis: Dict) -> str:
        """Generate enhanced description of expected improvement"""
        try:
            total_failures = sum(c['failure_count'] for c in candidates)
            categories = len(set(c['category'] for c in candidates))
            
            direction = "Reducing false negatives" if adjustment < 0 else "Reducing false positives"
            
            # Base improvement description
            improvement = (
                f"{direction} by improving threshold sensitivity. "
                f"Expected to address {total_failures} classification failures "
                f"across {categories} categories. "
            )
            
            # Add crisis score specific improvements
            opportunities = crisis_score_analysis.get('threshold_opportunities', [])
            if opportunities:
                opportunity_count = len(opportunities)
                improvement += f"Crisis score analysis identified {opportunity_count} specific threshold optimization opportunities. "
            
            improvement += "Should improve overall system accuracy while maintaining safety standards."
            
            return improvement
            
        except Exception as e:
            logger.error(f"Error generating enhanced expected improvement: {e}")
            return "Expected to improve classification accuracy based on crisis score analysis"
    
    def _calculate_enhanced_test_priority(self, candidates: List[Dict], risk: RiskLevel, 
                                        confidence: ConfidenceLevel, crisis_score_analysis: Dict) -> int:
        """Calculate enhanced testing priority incorporating crisis score insights"""
        try:
            # Start with base priority
            priority = 3
            
            # Adjust for risk level
            risk_adjustments = {
                RiskLevel.CRITICAL: -2,
                RiskLevel.MODERATE: -1,
                RiskLevel.LOW: 0,
                RiskLevel.MINIMAL: 1
            }
            priority += risk_adjustments.get(risk, 0)
            
            # Adjust for confidence  
            confidence_adjustments = {
                ConfidenceLevel.HIGH: -1,
                ConfidenceLevel.MEDIUM: 0,
                ConfidenceLevel.LOW: 1,
                ConfidenceLevel.UNCERTAIN: 2
            }
            priority += confidence_adjustments.get(confidence, 1)
            
            # Crisis score specific adjustments
            correlation = crisis_score_analysis.get('statistics', {}).get('score_correlation', 0.5)
            if correlation > 0.8:
                priority -= 1  # High correlation = higher priority
            elif correlation < 0.3:
                priority += 1  # Low correlation = lower priority
                
            # High variance cases get higher priority for testing
            avg_variance = crisis_score_analysis.get('statistics', {}).get('avg_score_variance', 0.1)
            if avg_variance > 0.2:
                priority -= 1
            
            # Adjust for high-priority category involvement
            high_priority_involved = any(c['category'].startswith('definite_high') for c in candidates)
            if high_priority_involved:
                priority -= 1
            
            # Ensure priority is within valid range
            return max(1, min(5, priority))
            
        except Exception as e:
            logger.error(f"Error calculating enhanced test priority: {e}")
            return 3
    
    def _generate_boundary_test_suggestions(self, recommendations: List[ThresholdRecommendation], 
                                          mode: EnsembleMode) -> List[Dict[str, Any]]:
        """Generate boundary testing suggestions for recommended thresholds"""
        try:
            suggestions = []
            
            for rec in recommendations:
                # Create test points around recommended value
                test_points = []
                
                # Get threshold range
                threshold_info = self.threshold_mappings.get(mode.value, {})
                for threshold_type in ['individual_thresholds', 'ensemble_thresholds']:
                    thresholds = threshold_info.get(threshold_type, {})
                    if rec.variable_name in thresholds:
                        range_min, range_max = thresholds[rec.variable_name]['range']
                        
                        # Create test points: current, recommended, and boundary points
                        step_size = (range_max - range_min) / 20  # 5% steps
                        
                        test_points = [
                            rec.current_value,
                            rec.recommended_value,
                            max(range_min, rec.recommended_value - step_size),
                            min(range_max, rec.recommended_value + step_size),
                            max(range_min, rec.recommended_value - 2 * step_size),
                            min(range_max, rec.recommended_value + 2 * step_size)
                        ]
                        
                        # Remove duplicates and sort
                        test_points = sorted(list(set(test_points)))
                        break
                
                if test_points:
                    suggestions.append({
                        'variable_name': rec.variable_name,
                        'current_value': rec.current_value,
                        'recommended_value': rec.recommended_value,
                        'test_points': test_points,
                        'test_strategy': 'boundary_sweep',
                        'expected_optimal_range': (
                            min(test_points[len(test_points)//2:]),  # Middle range
                            max(test_points[:len(test_points)//2 + 1])
                        ),
                        'priority': rec.test_priority,
                        'risk_level': rec.risk_level.value,
                        'crisis_score_informed': True  # NEW: Flag that this uses crisis score analysis
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating boundary test suggestions: {e}")
            return []
    
    def _assess_tuning_risks(self, recommendations: List[ThresholdRecommendation], 
                           failure_analysis: Dict) -> Dict[str, Any]:
        """Assess overall risks of implementing tuning recommendations"""
        try:
            risk_assessment = {
                'overall_risk_level': RiskLevel.LOW.value,
                'risk_factors': [],
                'mitigation_strategies': [],
                'safety_considerations': [],
                'rollback_readiness': 'high',
                'crisis_score_considerations': []  # NEW: Crisis score specific risks
            }
            
            # Assess individual recommendation risks
            critical_risks = [r for r in recommendations if r.risk_level == RiskLevel.CRITICAL]
            moderate_risks = [r for r in recommendations if r.risk_level == RiskLevel.MODERATE]
            
            if critical_risks:
                risk_assessment['overall_risk_level'] = RiskLevel.CRITICAL.value
                risk_assessment['risk_factors'].append(
                    f"{len(critical_risks)} critical-risk threshold changes proposed"
                )
                risk_assessment['mitigation_strategies'].append(
                    "Implement critical changes one at a time with immediate validation"
                )
            elif moderate_risks:
                risk_assessment['overall_risk_level'] = RiskLevel.MODERATE.value
                risk_assessment['risk_factors'].append(
                    f"{len(moderate_risks)} moderate-risk threshold changes proposed"
                )
            
            # Check for high-priority category involvement
            high_priority_changes = [r for r in recommendations 
                                   if 'high' in str(r.reasoning).lower()]
            if high_priority_changes:
                risk_assessment['risk_factors'].append(
                    "Changes affect high-priority crisis detection thresholds"
                )
                risk_assessment['safety_considerations'].append(
                    "Monitor false negative rates carefully during implementation"
                )
            
            # NEW: Crisis score specific risk assessment
            crisis_score_analysis = failure_analysis.get('crisis_score_analysis', {})
            correlation = crisis_score_analysis.get('statistics', {}).get('score_correlation', 0.5)
            avg_variance = crisis_score_analysis.get('statistics', {}).get('avg_score_variance', 0.1)
            
            if correlation < 0.3:
                risk_assessment['crisis_score_considerations'].append(
                    f"Low crisis/confidence correlation ({correlation:.2f}) increases adjustment uncertainty"
                )
                risk_assessment['mitigation_strategies'].append(
                    "Extra validation needed due to low score correlation"
                )
            
            if avg_variance > 0.2:
                risk_assessment['crisis_score_considerations'].append(
                    f"High score variance ({avg_variance:.3f}) suggests calibration issues"
                )
                risk_assessment['mitigation_strategies'].append(
                    "Gradual implementation recommended due to score variance"
                )
            
            # Assess safety concerns from failure analysis
            safety_concerns = failure_analysis.get('safety_concerns', [])
            if safety_concerns:
                risk_assessment['safety_considerations'].extend([
                    concern.get('concern', 'Unknown safety concern') for concern in safety_concerns
                ])
            
            # Add general mitigation strategies
            risk_assessment['mitigation_strategies'].extend([
                "Test all changes in controlled environment before production",
                "Implement gradual rollout with performance monitoring", 
                "Maintain rollback capability at all times",
                "Monitor false negative/positive rates closely",
                "Validate crisis score consistency after threshold changes"  # NEW
            ])
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error assessing tuning risks: {e}")
            return {'error': str(e), 'overall_risk_level': 'unknown'}
    
    def _generate_confidence_summary(self, recommendations: List[ThresholdRecommendation]) -> Dict[str, int]:
        """Generate summary of confidence levels across recommendations"""
        try:
            summary = {
                ConfidenceLevel.HIGH.value: 0,
                ConfidenceLevel.MEDIUM.value: 0, 
                ConfidenceLevel.LOW.value: 0,
                ConfidenceLevel.UNCERTAIN.value: 0
            }
            
            for rec in recommendations:
                summary[rec.confidence_level.value] += 1
            
            # Add total and crisis score enhanced count
            summary['total_recommendations'] = len(recommendations)
            summary['crisis_score_enhanced'] = len([r for r in recommendations 
                                                  if r.crisis_score_analysis is not None])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating confidence summary: {e}")
            return {'error': str(e)}
    
    def _determine_implementation_order(self, recommendations: List[ThresholdRecommendation]) -> List[str]:
        """Determine recommended order for implementing threshold changes"""
        try:
            # Sort recommendations by priority and risk
            sorted_recs = sorted(recommendations, 
                               key=lambda r: (r.test_priority, r.risk_level.value))
            
            implementation_order = []
            
            for rec in sorted_recs:
                # Enhanced order entry with crisis score info
                crisis_enhanced = "✓" if rec.crisis_score_analysis else "○"
                order_entry = (
                    f"{rec.variable_name}: "
                    f"{rec.current_value:.3f} → {rec.recommended_value:.3f} "
                    f"(Priority: {rec.test_priority}, Risk: {rec.risk_level.value}, "
                    f"Confidence: {rec.confidence_level.value}, Crisis Score: {crisis_enhanced})"
                )
                implementation_order.append(order_entry)
            
            return implementation_order
            
        except Exception as e:
            logger.error(f"Error determining implementation order: {e}")
            return []
    
    def save_tuning_analysis(self, analysis: TuningAnalysis, run_timestamp: str = None) -> str:
        """
        Save tuning analysis to persistent file
        Enhanced to include crisis score analysis data.
        
        Args:
            analysis: TuningAnalysis to save
            run_timestamp: Optional timestamp for the run
            
        Returns:
            Path to saved analysis file
        """
        try:
            if not run_timestamp:
                run_timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            
            # Create analysis directory if it doesn't exist
            analysis_dir = self.results_dir / 'tuning_analysis'
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Save detailed analysis as JSON
            analysis_file = analysis_dir / f'tuning_analysis_{run_timestamp}.json'
            
            analysis_data = {
                'metadata': {
                    'timestamp': run_timestamp,
                    'analysis_version': 'v3.1-3a-4',
                    'ensemble_mode': analysis.ensemble_mode.value,
                    'crisis_score_enhanced': True
                },
                'critical_issues': analysis.critical_issues,
                'recommendations': [
                    {
                        'variable_name': rec.variable_name,
                        'current_value': rec.current_value,
                        'recommended_value': rec.recommended_value,
                        'confidence_level': rec.confidence_level.value,
                        'risk_level': rec.risk_level.value,
                        'reasoning': rec.reasoning,
                        'expected_improvement': rec.expected_improvement,
                        'rollback_plan': rec.rollback_plan,
                        'test_priority': rec.test_priority,
                        'crisis_score_analysis': rec.crisis_score_analysis
                    }
                    for rec in analysis.recommendations
                ],
                'boundary_test_suggestions': analysis.boundary_test_suggestions,
                'risk_assessment': analysis.risk_assessment,
                'confidence_summary': analysis.confidence_summary,
                'implementation_order': analysis.implementation_order,
                'crisis_score_insights': analysis.crisis_score_insights
            }
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            logger.info(f"Enhanced tuning analysis with crisis score data saved to: {analysis_file}")
            return str(analysis_file)
            
        except Exception as e:
            logger.error(f"Error saving tuning analysis: {e}")
            return ""
    
    def generate_env_file_recommendations(self, analysis: TuningAnalysis) -> str:
        """
        Generate .env file with recommended threshold values
        Enhanced with crisis score analysis context.
        
        Args:
            analysis: TuningAnalysis with recommendations
            
        Returns:
            Path to generated .env file with recommendations
        """
        try:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            env_file = self.reports_dir / f'recommended_thresholds_{timestamp}.env'
            
            # Ensure reports directory exists
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            
            with open(env_file, 'w') as f:
                f.write("# Enhanced Threshold Adjustments with Crisis Score Analysis\n")
                f.write(f"# Generated: {timestamp}\n")
                f.write(f"# Ensemble Mode: {analysis.ensemble_mode.value}\n")
                f.write(f"# Total Recommendations: {len(analysis.recommendations)}\n")
                f.write(f"# Crisis Score Enhanced: {len([r for r in analysis.recommendations if r.crisis_score_analysis])} recommendations\n")
                f.write("#\n")
                f.write("# IMPORTANT: Test these values thoroughly before production use!\n")
                f.write("# The Alphabet Cartel community safety depends on accurate crisis detection.\n")
                f.write("#\n")
                
                # Add crisis score analysis summary
                if analysis.crisis_score_insights:
                    stats = analysis.crisis_score_insights.get('statistics', {})
                    if stats:
                        f.write("# Crisis Score Analysis Summary:\n")
                        f.write(f"# - Score Correlation: {stats.get('score_correlation', 0.0):.3f}\n")
                        f.write(f"# - Average Variance: {stats.get('avg_score_variance', 0.0):.3f}\n")
                        f.write(f"# - High Variance Cases: {stats.get('high_variance_count', 0)}\n")
                        f.write("#\n")
                
                f.write("\n")
                
                # Group recommendations by confidence level
                for confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, 
                                 ConfidenceLevel.LOW, ConfidenceLevel.UNCERTAIN]:
                    
                    confidence_recs = [r for r in analysis.recommendations 
                                     if r.confidence_level == confidence]
                    
                    if confidence_recs:
                        f.write(f"# {confidence.value.upper()} CONFIDENCE RECOMMENDATIONS\n")
                        f.write(f"# ({len(confidence_recs)} recommendations)\n")
                        
                        for rec in confidence_recs:
                            f.write(f"#\n")
                            f.write(f"# {rec.variable_name}\n") 
                            f.write(f"# Current: {rec.current_value:.3f} → Recommended: {rec.recommended_value:.3f}\n")
                            f.write(f"# Risk Level: {rec.risk_level.value.upper()}\n")
                            f.write(f"# Priority: {rec.test_priority}\n")
                            
                            # Add crisis score analysis info if available
                            if rec.crisis_score_analysis:
                                crisis_factor = rec.crisis_score_analysis.get('avg_crisis_score_factor', 1.0)
                                f.write(f"# Crisis Score Factor: {crisis_factor:.3f}\n")
                            
                            f.write(f"# Reasoning: {rec.reasoning[:100]}...\n")
                            f.write(f"{rec.variable_name}={rec.recommended_value:.3f}\n")
                            f.write(f"\n")
                        
                        f.write("\n")
                
                f.write("# End of enhanced recommendations\n")
                f.write("# Remember to backup current configuration before applying changes\n")
                f.write("# Monitor both crisis_score and confidence_score after implementation\n")
            
            logger.info(f"Enhanced environment file recommendations saved to: {env_file}")
            return str(env_file)
            
        except Exception as e:
            logger.error(f"Error generating enhanced .env file recommendations: {e}")
            return ""

# ============================================================================
# FACTORY FUNCTION - Clean Architecture v3.1 Compliance
# ============================================================================

def create_tuning_suggestions_manager(unified_config_manager, results_manager, analyze_results_manager) -> TuningSuggestionsManager:
    """
    Factory function for TuningSuggestionsManager (Clean v3.1 Pattern)
    Enhanced for crisis score analysis capabilities.
    
    Args:
        unified_config_manager: UnifiedConfigManager instance for dependency injection
        results_manager: ResultsManager instance for test result access
        analyze_results_manager: AnalyzeResultsManager instance for analysis data
        
    Returns:
        Initialized TuningSuggestionsManager instance with crisis score analysis
        
    Raises:
        ValueError: If any required manager is None or invalid
    """
    logger.debug("Creating TuningSuggestionsManager v3.1-3a-4 with Clean v3.1 architecture and crisis score analysis")
    
    if not unified_config_manager:
        raise ValueError("UnifiedConfigManager is required for TuningSuggestionsManager factory")
    if not results_manager:
        raise ValueError("ResultsManager is required for TuningSuggestionsManager factory")
    if not analyze_results_manager:
        raise ValueError("AnalyzeResultsManager is required for TuningSuggestionsManager factory")
    
    return TuningSuggestionsManager(unified_config_manager, results_manager, analyze_results_manager)

# Export public interface
__all__ = [
    'TuningSuggestionsManager', 
    'EnsembleMode', 
    'ConfidenceLevel', 
    'RiskLevel',
    'ThresholdRecommendation',
    'TuningAnalysis',
    'create_tuning_suggestions_manager'
]

logger.info("TuningSuggestionsManager v3.1-3a-4 loaded with enhanced crisis score analysis capabilities")