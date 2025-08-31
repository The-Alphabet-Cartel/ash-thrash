"""
Ash-Thrash: Testing Suite for Ash-NLP Backend for The Alphabet Cartel Discord Community
********************************************************************************
Advanced Tuning Intelligence Manager for Ash-Thrash Service
---
FILE VERSION: v3.1-3a-1
LAST MODIFIED: 2025-08-31
PHASE: 3a Step 1
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

# ============================================================================
# TUNING SUGGESTIONS MANAGER - Clean Architecture v3.1
# ============================================================================

class TuningSuggestionsManager:
    """
    Advanced tuning intelligence manager for threshold optimization
    
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
        logger.debug("Initializing TuningSuggestionsManager v3.1-3a-1")
        
        if not unified_config_manager:
            raise ValueError("UnifiedConfigManager is required for TuningSuggestionsManager")
        if not results_manager:
            raise ValueError("ResultsManager is required for TuningSuggestionsManager")  
        if not analyze_results_manager:
            raise ValueError("AnalyzeResultsManager is required for TuningSuggestionsManager")
            
        self.config_manager = unified_config_manager
        self.results_manager = results_manager
        self.analyze_manager = analyze_results_manager
        
        # Get base configuration paths
        self.config_dir = Path(self.config_manager.get_string('APP_DATA_DIR', '/app/ash-thrash')) / 'config'
        self.results_dir = Path(self.config_manager.get_string('APP_DATA_DIR', '/app/ash-thrash')) / 'results' 
        self.reports_dir = Path(self.config_manager.get_string('APP_DATA_DIR', '/app/ash-thrash')) / 'reports'
        
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
        
        logger.info("TuningSuggestionsManager v3.1-3a-1 initialized successfully")
    
    def _load_config_parameters(self) -> Dict[str, Any]:
        """Load configuration parameters from JSON with environment variable resolution"""
        try:
            mappings_file = self.config_dir / 'threshold_mappings.json'
            
            if not mappings_file.exists():
                logger.warning(f"Configuration file not found: {mappings_file}")
                return {}
            
            with open(mappings_file, 'r') as f:
                config_data = json.load(f)
            
            # Use UnifiedConfigManager to resolve environment variables in the config
            resolved_config = {}
            
            # Process confidence parameters
            if 'confidence_parameters' in config_data:
                confidence_config = config_data['confidence_parameters']
                resolved_config['confidence_parameters'] = {
                    'high_confidence_min': self.config_manager.get_float('THRASH_CONFIDENCE_HIGH_MIN', 
                                                                        confidence_config['defaults']['high_confidence_min']),
                    'medium_confidence_min': self.config_manager.get_float('THRASH_CONFIDENCE_MEDIUM_MIN', 
                                                                          confidence_config['defaults']['medium_confidence_min']),
                    'low_confidence_min': self.config_manager.get_float('THRASH_CONFIDENCE_LOW_MIN', 
                                                                       confidence_config['defaults']['low_confidence_min'])
                }
            
            # Process safety parameters  
            if 'safety_parameters' in config_data:
                safety_config = config_data['safety_parameters']
                resolved_config['safety_parameters'] = {
                    'false_negative_weight': self.config_manager.get_float('THRASH_FALSE_NEGATIVE_WEIGHT', 
                                                                          safety_config['defaults']['false_negative_weight']),
                    'critical_category_weight': self.config_manager.get_float('THRASH_CRITICAL_CATEGORY_WEIGHT', 
                                                                             safety_config['defaults']['critical_category_weight']),
                    'minimum_improvement_threshold': self.config_manager.get_float('THRASH_MIN_IMPROVEMENT_THRESHOLD', 
                                                                                  safety_config['defaults']['minimum_improvement_threshold']),
                    'maximum_risk_tolerance': self.config_manager.get_string('THRASH_MAX_RISK_TOLERANCE', 
                                                                            safety_config['defaults']['maximum_risk_tolerance'])
                }
            
            return resolved_config
            
        except Exception as e:
            logger.error(f"Error loading configuration parameters: {e}")
            return {}
    
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
        Determine current NLP ensemble mode from environment variables
        
        Returns:
            Current ensemble mode with graceful fallback
        """
        try:
            mode_str = self.config_manager.get_string('NLP_ENSEMBLE_MODE', 'consensus').lower()
            
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
    
    def analyze_failure_patterns(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test failure patterns to identify threshold adjustment opportunities
        
        Args:
            test_results: Complete test results from latest run
            
        Returns:
            Analysis of failure patterns with specific threshold mapping
        """
        try:
            logger.info("Analyzing failure patterns for threshold recommendations")
            
            current_mode = self.get_current_ensemble_mode()
            category_results = test_results.get('category_results', {})
            
            failure_analysis = {
                'ensemble_mode': current_mode.value,
                'critical_failures': [],
                'threshold_candidates': [],
                'pattern_insights': {},
                'safety_concerns': []
            }
            
            # Analyze each category for failure patterns
            for category, results in category_results.items():
                if not results or 'summary' not in results:
                    continue
                    
                summary = results['summary']
                pass_rate = summary.get('pass_rate', 0.0)
                total_tests = summary.get('total_tests', 0)
                failed_tests = summary.get('failed_tests', 0)
                
                # Identify critical failure patterns
                if category.startswith('definite_high') and pass_rate < 0.95:
                    failure_analysis['critical_failures'].append({
                        'category': category,
                        'issue': 'Critical safety category under-performing',
                        'pass_rate': pass_rate,
                        'risk': 'HIGH - False negatives in crisis detection',
                        'priority': 1
                    })
                elif category.startswith('definite_') and pass_rate < 0.80:
                    failure_analysis['critical_failures'].append({
                        'category': category,
                        'issue': 'Definite category significantly under-performing', 
                        'pass_rate': pass_rate,
                        'risk': 'MODERATE - Classification accuracy compromised',
                        'priority': 2
                    })
                
                # Identify threshold adjustment candidates
                if failed_tests > 0 and 'failed_tests_details' in results:
                    self._analyze_threshold_candidates(
                        category, 
                        results['failed_tests_details'],
                        current_mode,
                        failure_analysis['threshold_candidates']
                    )
            
            # Generate pattern insights
            failure_analysis['pattern_insights'] = self._generate_pattern_insights(
                category_results, current_mode
            )
            
            # Assess safety concerns
            failure_analysis['safety_concerns'] = self._assess_safety_concerns(
                failure_analysis['critical_failures']
            )
            
            logger.info(f"Failure pattern analysis complete: {len(failure_analysis['critical_failures'])} critical issues found")
            return failure_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing failure patterns: {e}")
            return {
                'ensemble_mode': self.get_current_ensemble_mode().value,
                'critical_failures': [],
                'threshold_candidates': [],
                'pattern_insights': {},
                'safety_concerns': [],
                'error': str(e)
            }
    
    def _analyze_threshold_candidates(self, category: str, failed_tests: List[Dict], 
                                    mode: EnsembleMode, candidates: List[Dict]):
        """Analyze failed tests to identify specific threshold adjustment candidates"""
        try:
            mode_mappings = self.threshold_mappings.get(mode.value, {})
            
            # Map category to expected crisis levels
            category_mapping = {
                'definite_high': ['high'],
                'definite_medium': ['medium'], 
                'definite_low': ['low'],
                'definite_none': ['none'],
                'maybe_high_medium': ['high', 'medium'],
                'maybe_medium_low': ['medium', 'low'],
                'maybe_low_none': ['low', 'none']
            }
            
            expected_levels = category_mapping.get(category, [])
            if not expected_levels:
                return
                
            # Analyze failure patterns
            misclassification_patterns = {}
            
            for failed_test in failed_tests:
                actual_level = failed_test.get('actual_crisis_level', 'unknown')
                expected_level = failed_test.get('expected_crisis_level', expected_levels[0])
                confidence = failed_test.get('confidence_score', 0.0)
                
                pattern_key = f"{expected_level}_to_{actual_level}"
                if pattern_key not in misclassification_patterns:
                    misclassification_patterns[pattern_key] = {
                        'count': 0,
                        'avg_confidence': 0.0,
                        'confidences': []
                    }
                
                misclassification_patterns[pattern_key]['count'] += 1
                misclassification_patterns[pattern_key]['confidences'].append(confidence)
            
            # Calculate average confidences and identify threshold candidates
            for pattern, data in misclassification_patterns.items():
                data['avg_confidence'] = sum(data['confidences']) / len(data['confidences'])
                
                # Find relevant thresholds for this misclassification pattern
                relevant_thresholds = self._find_relevant_thresholds(pattern, mode_mappings)
                
                for threshold_var, threshold_info in relevant_thresholds.items():
                    candidates.append({
                        'category': category,
                        'misclassification_pattern': pattern,
                        'threshold_variable': threshold_var,
                        'threshold_info': threshold_info,
                        'failure_count': data['count'],
                        'avg_confidence': data['avg_confidence'],
                        'suggested_adjustment': self._calculate_suggested_adjustment(
                            pattern, data['avg_confidence'], threshold_info
                        )
                    })
                    
        except Exception as e:
            logger.error(f"Error analyzing threshold candidates for {category}: {e}")
    
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
    
    def _calculate_suggested_adjustment(self, pattern: str, avg_confidence: float, 
                                      threshold_info: Dict) -> Dict[str, Any]:
        """Calculate suggested threshold adjustment based on failure pattern"""
        try:
            current_default = threshold_info.get('default', 0.5)
            range_min, range_max = threshold_info.get('range', (0.0, 1.0))
            
            # Base adjustment on confidence and pattern type
            parts = pattern.split('_to_')
            if len(parts) != 2:
                return {'adjustment': 0.0, 'direction': 'none', 'confidence': 0.0}
                
            expected, actual = parts[0], parts[1]
            
            # Determine adjustment direction and magnitude
            level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
            expected_rank = level_hierarchy.get(expected, 1)
            actual_rank = level_hierarchy.get(actual, 1)
            
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
            
            # Scale adjustment based on confidence - low confidence suggests bigger adjustment needed
            confidence_multiplier = max(0.5, 1.0 - avg_confidence)
            suggested_adjustment = base_adjustment * confidence_multiplier
            
            # Ensure adjustment stays within valid range
            new_value = current_default + suggested_adjustment
            new_value = max(range_min, min(range_max, new_value))
            final_adjustment = new_value - current_default
            
            # Calculate confidence in this suggestion
            suggestion_confidence = min(0.9, avg_confidence + 0.3) if abs(final_adjustment) > 0.02 else 0.4
            
            return {
                'adjustment': final_adjustment,
                'direction': direction,
                'new_value': new_value,
                'confidence': suggestion_confidence,
                'reasoning': f"Pattern {pattern} with {avg_confidence:.2f} confidence suggests {direction} threshold"
            }
            
        except Exception as e:
            logger.error(f"Error calculating suggested adjustment: {e}")
            return {'adjustment': 0.0, 'direction': 'none', 'confidence': 0.0}
    
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
        
        Args:
            test_results: Complete test results from latest run
            
        Returns:
            TuningAnalysis with recommendations, confidence levels, and risk assessment
        """
        try:
            logger.info("Generating comprehensive tuning recommendations")
            
            # Analyze failure patterns first
            failure_analysis = self.analyze_failure_patterns(test_results)
            current_mode = EnsembleMode(failure_analysis['ensemble_mode'])
            
            # Generate specific threshold recommendations
            recommendations = self._generate_threshold_recommendations(failure_analysis, current_mode)
            
            # Create boundary test suggestions
            boundary_tests = self._generate_boundary_test_suggestions(recommendations, current_mode)
            
            # Assess overall risk
            risk_assessment = self._assess_tuning_risks(recommendations, failure_analysis)
            
            # Generate confidence summary
            confidence_summary = self._generate_confidence_summary(recommendations)
            
            # Determine implementation order
            implementation_order = self._determine_implementation_order(recommendations)
            
            # Create comprehensive analysis
            analysis = TuningAnalysis(
                ensemble_mode=current_mode,
                critical_issues=[f['issue'] for f in failure_analysis['critical_failures']],
                recommendations=recommendations,
                boundary_test_suggestions=boundary_tests,
                risk_assessment=risk_assessment,
                confidence_summary=confidence_summary,
                implementation_order=implementation_order
            )
            
            logger.info(f"Generated {len(recommendations)} threshold recommendations with risk assessment")
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
                implementation_order=[]
            )
    
    def _generate_threshold_recommendations(self, failure_analysis: Dict, 
                                          mode: EnsembleMode) -> List[ThresholdRecommendation]:
        """Generate specific threshold adjustment recommendations"""
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
            
            # Generate recommendations for each variable
            for var_name, var_candidates in variable_candidates.items():
                recommendation = self._create_threshold_recommendation(var_name, var_candidates, mode)
                if recommendation:
                    recommendations.append(recommendation)
            
            # Sort by priority (test_priority field)
            recommendations.sort(key=lambda r: r.test_priority)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating threshold recommendations: {e}")
            return []
    
    def _create_threshold_recommendation(self, var_name: str, candidates: List[Dict], 
                                       mode: EnsembleMode) -> Optional[ThresholdRecommendation]:
        """Create a specific threshold recommendation from candidates"""
        try:
            if not candidates:
                return None
                
            # Get current value from environment or use default
            threshold_info = candidates[0]['threshold_info']
            current_value = self.config_manager.get_float(var_name, threshold_info['default'])
            
            # Calculate weighted average of suggested adjustments
            total_weight = 0
            weighted_adjustment = 0.0
            
            for candidate in candidates:
                weight = candidate['failure_count']  # Weight by number of failures
                adjustment = candidate['suggested_adjustment']['adjustment']
                weighted_adjustment += adjustment * weight
                total_weight += weight
            
            if total_weight == 0:
                return None
                
            avg_adjustment = weighted_adjustment / total_weight
            recommended_value = current_value + avg_adjustment
            
            # Ensure within valid range
            range_min, range_max = threshold_info['range']
            recommended_value = max(range_min, min(range_max, recommended_value))
            
            # Calculate confidence level
            confidence = self._calculate_recommendation_confidence(candidates, avg_adjustment)
            
            # Determine risk level
            risk = threshold_info['risk_level']
            
            # Generate reasoning
            reasoning = self._generate_recommendation_reasoning(var_name, candidates, avg_adjustment)
            
            # Generate expected improvement description
            expected_improvement = self._generate_expected_improvement(candidates, avg_adjustment)
            
            # Generate rollback plan
            rollback_plan = f"Revert {var_name} from {recommended_value:.3f} back to {current_value:.3f}"
            
            # Determine test priority
            test_priority = self._calculate_test_priority(candidates, risk, confidence)
            
            return ThresholdRecommendation(
                variable_name=var_name,
                current_value=current_value,
                recommended_value=recommended_value,
                confidence_level=confidence,
                risk_level=risk,
                reasoning=reasoning,
                expected_improvement=expected_improvement,
                rollback_plan=rollback_plan,
                test_priority=test_priority
            )
            
        except Exception as e:
            logger.error(f"Error creating recommendation for {var_name}: {e}")
            return None
    
    def _calculate_recommendation_confidence(self, candidates: List[Dict], 
                                           avg_adjustment: float) -> ConfidenceLevel:
        """Calculate confidence level for a recommendation"""
        try:
            # Base confidence on consistency across candidates and adjustment magnitude
            candidate_confidences = [c['suggested_adjustment']['confidence'] for c in candidates]
            avg_candidate_confidence = sum(candidate_confidences) / len(candidate_confidences)
            
            # Factor in adjustment magnitude (larger adjustments are less certain)
            magnitude_factor = max(0.5, 1.0 - abs(avg_adjustment) * 10)  # Scale by 10x adjustment
            
            # Factor in number of supporting candidates
            candidate_factor = min(1.0, len(candidates) / 5.0)  # More candidates = more confidence
            
            overall_confidence = avg_candidate_confidence * magnitude_factor * candidate_factor
            
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
            logger.error(f"Error calculating recommendation confidence: {e}")
            return ConfidenceLevel.UNCERTAIN
    
    def _generate_recommendation_reasoning(self, var_name: str, candidates: List[Dict], 
                                         adjustment: float) -> str:
        """Generate human-readable reasoning for recommendation"""
        try:
            direction = "increase" if adjustment > 0 else "decrease"
            magnitude = abs(adjustment)
            
            # Identify primary failure categories
            categories = list(set(c['category'] for c in candidates))
            category_str = ", ".join(categories)
            
            # Count total failures
            total_failures = sum(c['failure_count'] for c in candidates)
            
            # Identify most common misclassification pattern
            patterns = [c['misclassification_pattern'] for c in candidates]
            most_common_pattern = max(set(patterns), key=patterns.count) if patterns else "unknown"
            
            reasoning = (
                f"Recommended to {direction} {var_name} by {magnitude:.3f} based on "
                f"{total_failures} failures across categories: {category_str}. "
                f"Primary issue: {most_common_pattern} misclassification pattern. "
                f"This adjustment should improve classification accuracy while maintaining safety margins."
            )
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Error generating reasoning for {var_name}: {e}")
            return f"Adjustment recommended for {var_name} based on test failures"
    
    def _generate_expected_improvement(self, candidates: List[Dict], adjustment: float) -> str:
        """Generate description of expected improvement"""
        try:
            total_failures = sum(c['failure_count'] for c in candidates)
            categories = len(set(c['category'] for c in candidates))
            
            direction = "Reducing false negatives" if adjustment < 0 else "Reducing false positives"
            
            improvement = (
                f"{direction} by improving threshold sensitivity. "
                f"Expected to address {total_failures} classification failures "
                f"across {categories} categories. "
                f"Should improve overall system accuracy while maintaining safety standards."
            )
            
            return improvement
            
        except Exception as e:
            logger.error(f"Error generating expected improvement: {e}")
            return "Expected to improve classification accuracy"
    
    def _calculate_test_priority(self, candidates: List[Dict], risk: RiskLevel, 
                               confidence: ConfidenceLevel) -> int:
        """Calculate testing priority (1=highest, 5=lowest)"""
        try:
            # Start with base priority
            priority = 3
            
            # Adjust for risk level
            risk_adjustments = {
                RiskLevel.CRITICAL: -2,    # Higher priority
                RiskLevel.MODERATE: -1,
                RiskLevel.LOW: 0,
                RiskLevel.MINIMAL: 1       # Lower priority
            }
            priority += risk_adjustments.get(risk, 0)
            
            # Adjust for confidence  
            confidence_adjustments = {
                ConfidenceLevel.HIGH: -1,      # Higher priority
                ConfidenceLevel.MEDIUM: 0,
                ConfidenceLevel.LOW: 1,
                ConfidenceLevel.UNCERTAIN: 2   # Lower priority
            }
            priority += confidence_adjustments.get(confidence, 1)
            
            # Adjust for high-priority category involvement
            high_priority_involved = any(c['category'].startswith('definite_high') for c in candidates)
            if high_priority_involved:
                priority -= 1
            
            # Ensure priority is within valid range
            return max(1, min(5, priority))
            
        except Exception as e:
            logger.error(f"Error calculating test priority: {e}")
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
                        'risk_level': rec.risk_level.value
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
                'rollback_readiness': 'high'
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
                                   if any('high' in str(r.reasoning).lower())]
            if high_priority_changes:
                risk_assessment['risk_factors'].append(
                    "Changes affect high-priority crisis detection thresholds"
                )
                risk_assessment['safety_considerations'].append(
                    "Monitor false negative rates carefully during implementation"
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
                "Monitor false negative/positive rates closely"
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
            
            # Add total
            summary['total_recommendations'] = len(recommendations)
            
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
                order_entry = (
                    f"{rec.variable_name}: "
                    f"{rec.current_value:.3f} → {rec.recommended_value:.3f} "
                    f"(Priority: {rec.test_priority}, Risk: {rec.risk_level.value}, "
                    f"Confidence: {rec.confidence_level.value})"
                )
                implementation_order.append(order_entry)
            
            return implementation_order
            
        except Exception as e:
            logger.error(f"Error determining implementation order: {e}")
            return []
    
    def save_tuning_analysis(self, analysis: TuningAnalysis, run_timestamp: str = None) -> str:
        """
        Save tuning analysis to persistent file
        
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
                    'analysis_version': 'v3.1-3a-1',
                    'ensemble_mode': analysis.ensemble_mode.value
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
                        'test_priority': rec.test_priority
                    }
                    for rec in analysis.recommendations
                ],
                'boundary_test_suggestions': analysis.boundary_test_suggestions,
                'risk_assessment': analysis.risk_assessment,
                'confidence_summary': analysis.confidence_summary,
                'implementation_order': analysis.implementation_order
            }
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            logger.info(f"Tuning analysis saved to: {analysis_file}")
            return str(analysis_file)
            
        except Exception as e:
            logger.error(f"Error saving tuning analysis: {e}")
            return ""
    
    def generate_env_file_recommendations(self, analysis: TuningAnalysis) -> str:
        """
        Generate .env file with recommended threshold values
        
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
                f.write("# Recommended Threshold Adjustments\n")
                f.write(f"# Generated: {timestamp}\n")
                f.write(f"# Ensemble Mode: {analysis.ensemble_mode.value}\n")
                f.write(f"# Total Recommendations: {len(analysis.recommendations)}\n")
                f.write("#\n")
                f.write("# IMPORTANT: Test these values thoroughly before production use!\n")
                f.write("# The Alphabet Cartel community safety depends on accurate crisis detection.\n")
                f.write("#\n\n")
                
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
                            f.write(f"# Reasoning: {rec.reasoning[:100]}...\n")
                            f.write(f"{rec.variable_name}={rec.recommended_value:.3f}\n")
                            f.write(f"\n")
                        
                        f.write("\n")
                
                f.write("# End of recommendations\n")
                f.write("# Remember to backup current configuration before applying changes\n")
            
            logger.info(f"Environment file recommendations saved to: {env_file}")
            return str(env_file)
            
        except Exception as e:
            logger.error(f"Error generating .env file recommendations: {e}")
            return ""

# ============================================================================
# FACTORY FUNCTION - Clean Architecture v3.1 Compliance
# ============================================================================

def create_tuning_suggestions_manager(unified_config_manager, results_manager, analyze_results_manager) -> TuningSuggestionsManager:
    """
    Factory function for TuningSuggestionsManager (Clean v3.1 Pattern)
    
    Args:
        unified_config_manager: UnifiedConfigManager instance for dependency injection
        results_manager: ResultsManager instance for test result access
        analyze_results_manager: AnalyzeResultsManager instance for analysis data
        
    Returns:
        Initialized TuningSuggestionsManager instance
        
    Raises:
        ValueError: If any required manager is None or invalid
    """
    logger.debug("Creating TuningSuggestionsManager with Clean v3.1 architecture")
    
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

logger.info("TuningSuggestionsManager v3.1-3a-1 loaded")