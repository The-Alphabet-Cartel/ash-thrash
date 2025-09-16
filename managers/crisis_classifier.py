# ash-thrash/managers/client_crisis_classifier.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Client-Side Crisis Classification Manager for Ash-Thrash Service
---
FILE VERSION: v3.1-4a-1
LAST MODIFIED: 2025-09-12
PHASE: 4a Step 1 - Client-Side Crisis Classification Implementation
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import json
import os
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND DATA STRUCTURES - Clean Architecture v3.1
# ============================================================================
class ClassificationStrategy(Enum):
    """Client-side classification strategies"""
    CONSERVATIVE = "conservative"  # Use higher of server vs client
    AGGRESSIVE = "aggressive"      # Use client with server fallback
    CONSENSUS = "consensus"        # Require agreement, escalate disagreements
    CLIENT_ONLY = "client_only"    # Client decision only

class ClassificationAgreement(Enum):
    """Agreement status between server and client classifications"""
    FULL_AGREEMENT = "full_agreement"
    PARTIAL_AGREEMENT = "partial_agreement"  # Adjacent levels
    DISAGREEMENT = "disagreement"
    SERVER_HIGHER = "server_higher"
    CLIENT_HIGHER = "client_higher"

@dataclass
class ClassificationResult:
    """Result of client-side crisis classification"""
    crisis_score: float
    confidence_score: float
    server_suggested_level: str
    client_determined_level: str
    final_classification: str
    classification_agreement: ClassificationAgreement
    strategy_used: ClassificationStrategy
    threshold_details: Dict[str, Any]
    reasoning: str

@dataclass
class ThresholdConfig:
    """Configuration for crisis level thresholds"""
    critical_min: float
    high_min: float
    medium_min: float
    low_min: float
    confidence_weight: float = 0.0  # 0.0 = ignore confidence, 1.0 = full weight
    variance_penalty: float = 0.1   # Penalty for high score variance

# ============================================================================
# CLIENT CRISIS CLASSIFIER MANAGER - Clean Architecture v3.1
# ============================================================================
class CrisisClassifierManager:
    """
    Client-Side Crisis Classification Manager for Ash-Thrash testing suite
    
    Implements client-side crisis level determination using crisis_score and 
    confidence_score, allowing for community-specific threshold tuning and
    comparison with server-suggested classifications.
    
    Clean Architecture v3.1 Compliant - Phase 4a
    """
    
    # ============================================================================
    # INITIALIZE
    # ============================================================================
    def __init__(self, unified_config_manager):
        """
        Initialize CrisisClassifierManager with dependency injection
        
        Args:
            unified_config_manager: UnifiedConfigManager for configuration access
        """
        logger.debug("Initializing CrisisClassifierManager v3.1-4a-1")
        
        if not unified_config_manager:
            raise ValueError("UnifiedConfigManager is required for CrisisClassifierManager")
            
        self.config_manager = unified_config_manager
        
        # Load client classification configuration
        self.threshold_configs = self._load_threshold_configurations()
        self.classification_strategy = self._load_classification_strategy()
        
        # Statistical tracking for analysis
        self.classification_stats = {
            'total_classifications': 0,
            'agreements': 0,
            'disagreements': 0,
            'server_higher_count': 0,
            'client_higher_count': 0,
            'strategy_usage': {strategy.value: 0 for strategy in ClassificationStrategy}
        }
        
        logger.info("CrisisClassifierManager v3.1-4a-1 initialized successfully")
    
    def _load_threshold_configurations(self) -> Dict[str, ThresholdConfig]:
        """Load client-side threshold configurations from JSON config"""
        try:
            # Load from configuration with fallback defaults
            config_data = {}
            
            # Try to load from JSON configuration
            try:
                config_data = self.config_manager.get_config_section(
                    'client_classification',
                    'threshold_configurations',
                    {}
                )
            except Exception as e:
                logger.warning(f"Could not load client threshold configs: {e}, using defaults")
            
            # Define default threshold configurations for different scenarios
            default_configs = {
                'standard': ThresholdConfig(
                    critical_min=0.80,
                    high_min=0.60,
                    medium_min=0.40,
                    low_min=0.20,
                    confidence_weight=0.1,
                    variance_penalty=0.1
                ),
                'conservative': ThresholdConfig(
                    critical_min=0.70,  # Lower thresholds = more sensitive
                    high_min=0.50,
                    medium_min=0.30,
                    low_min=0.15,
                    confidence_weight=0.15,
                    variance_penalty=0.05
                ),
                'aggressive': ThresholdConfig(
                    critical_min=0.90,  # Higher thresholds = less sensitive
                    high_min=0.70,
                    medium_min=0.50,
                    low_min=0.25,
                    confidence_weight=0.05,
                    variance_penalty=0.15
                )
            }
            
            # Override defaults with loaded configuration
            threshold_configs = {}
            for config_name, default_config in default_configs.items():
                config_section = config_data.get(config_name, {})
                
                threshold_configs[config_name] = ThresholdConfig(
                    critical_min=config_section.get('crisis_thresholds.critical_min', default_config.critical_min),
                    high_min=config_section.get('crisis_thresholds.high_min', default_config.high_min),
                    medium_min=config_section.get('crisis_thresholds.medium_min', default_config.medium_min),
                    low_min=config_section.get('crisis_thresholds.low_min', default_config.low_min),
                    confidence_weight=config_section.get('confidence.confidence_weight', default_config.confidence_weight),
                    variance_penalty=config_section.get('confidence.variance_penalty', default_config.variance_penalty)
                )
            
            logger.debug(f"Loaded {len(threshold_configs)} threshold configurations")
            return threshold_configs
            
        except Exception as e:
            logger.error(f"Error loading threshold configurations: {e}")
            # Return minimal fallback configuration
            return {
                'standard': ThresholdConfig(
                    critical_min=0.80, high_min=0.60, medium_min=0.40, low_min=0.20
                )
            }
    
    def _load_classification_strategy(self) -> ClassificationStrategy:
        """Load default classification strategy from configuration"""
        try:
            strategy_str = self.config_manager.get_config_section(
                'client_classification',
                'client_classification.strategy',
                'conservative'
            )
            
            strategy_mapping = {
                'conservative': ClassificationStrategy.CONSERVATIVE,
                'aggressive': ClassificationStrategy.AGGRESSIVE,
                'consensus': ClassificationStrategy.CONSENSUS,
                'client_only': ClassificationStrategy.CLIENT_ONLY
            }
            
            strategy = strategy_mapping.get(strategy_str, ClassificationStrategy.CONSERVATIVE)
            logger.debug(f"Default classification strategy: {strategy.value}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error loading classification strategy: {e}")
            return ClassificationStrategy.CONSERVATIVE
    # ============================================================================

    # ============================================================================
    # CLASSIFY CRISIS
    # ============================================================================
    def classify_crisis_level(self, crisis_score: float, confidence_score: float, server_suggested_level: str, threshold_config: str = 'standard', strategy: Optional[ClassificationStrategy] = None) -> ClassificationResult:
        """
        Perform client-side crisis classification
        
        Args:
            crisis_score: Crisis score from NLP server (0.0-1.0)
            confidence_score: Confidence score from NLP server (0.0-1.0)
            server_suggested_level: Server's suggested crisis level
            threshold_config: Which threshold configuration to use
            strategy: Classification strategy override
            
        Returns:
            ClassificationResult with client determination and comparison
        """
        try:
            # Use provided strategy or default
            if strategy is None:
                strategy = self.classification_strategy
            
            # Get threshold configuration
            if threshold_config not in self.threshold_configs:
                logger.warning(f"Unknown threshold config '{threshold_config}', using 'standard'")
                threshold_config = 'standard'
            
            config = self.threshold_configs[threshold_config]
            
            # Calculate client-determined crisis level
            client_level = self._calculate_client_crisis_level(
                crisis_score, confidence_score, config
            )
            
            # Compare with server suggestion
            agreement = self._assess_classification_agreement(server_suggested_level, client_level)
            
            # Apply classification strategy to determine final result
            final_level = self._apply_classification_strategy(
                server_suggested_level, client_level, strategy, agreement
            )
            
            # Generate reasoning
            reasoning = self._generate_classification_reasoning(
                crisis_score, confidence_score, server_suggested_level, 
                client_level, final_level, config, strategy, agreement
            )
            
            # Create result
            result = ClassificationResult(
                crisis_score=crisis_score,
                confidence_score=confidence_score,
                server_suggested_level=server_suggested_level,
                client_determined_level=client_level,
                final_classification=final_level,
                classification_agreement=agreement,
                strategy_used=strategy,
                threshold_details={
                    'config_used': threshold_config,
                    'thresholds': {
                        'critical_min': config.critical_min,
                        'high_min': config.high_min,
                        'medium_min': config.medium_min,
                        'low_min': config.low_min
                    },
                    'confidence_weight': config.confidence_weight,
                    'score_variance': abs(crisis_score - confidence_score)
                },
                reasoning=reasoning
            )
            
            # Update statistics
            self._update_classification_stats(result)
            
            logger.debug(f"Client classification:")
            logger.debug(f"→ Suggested Level: {server_suggested_level}")
            logger.debug(f"→ Client Level: {client_level}")
            logger.debug(f"→ Final Level: {final_level}")
            logger.debug(f"(strategy: {strategy.value}, agreement: {agreement.value})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in client crisis classification: {e}")
            # Fallback to server suggestion
            return ClassificationResult(
                crisis_score=crisis_score,
                confidence_score=confidence_score,
                server_suggested_level=server_suggested_level,
                client_determined_level=server_suggested_level,
                final_classification=server_suggested_level,
                classification_agreement=ClassificationAgreement.FULL_AGREEMENT,
                strategy_used=strategy or self.classification_strategy,
                threshold_details={'error': str(e)},
                reasoning=f"Error in classification, using server fallback: {str(e)}"
            )
    
    def _calculate_client_crisis_level(self, crisis_score: float, confidence_score: float, config: ThresholdConfig) -> str:
        """Calculate client-determined crisis level using configured thresholds"""
        try:
            # Calculate effective score incorporating confidence if weighted
            if config.confidence_weight > 0:
                # Weight crisis score by confidence
                effective_score = (
                    crisis_score * (1.0 - config.confidence_weight) +
                    (crisis_score * confidence_score) * config.confidence_weight
                )
            else:
                effective_score = crisis_score
            
            # Apply variance penalty if scores disagree significantly
            score_variance = abs(crisis_score - confidence_score)
            if score_variance > 0.2:  # Significant disagreement
                effective_score *= (1.0 - config.variance_penalty)
            
            # Determine crisis level based on thresholds
            if effective_score >= config.critical_min:
                return "critical"
            elif effective_score >= config.high_min:
                return "high"
            elif effective_score >= config.medium_min:
                return "medium"
            elif effective_score >= config.low_min:
                return "low"
            else:
                return "none"
                
        except Exception as e:
            logger.error(f"Error calculating client crisis level: {e}")
            return "none"
    
    def _assess_classification_agreement(self, server_level: str, client_level: str) -> ClassificationAgreement:
        """Assess agreement between server and client classifications"""
        if server_level == client_level:
            return ClassificationAgreement.FULL_AGREEMENT
        
        # Define level hierarchy for comparison
        level_hierarchy = {
            'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4
        }
        
        server_rank = level_hierarchy.get(server_level, 0)
        client_rank = level_hierarchy.get(client_level, 0)
        
        # Check for adjacent levels (partial agreement)
        if abs(server_rank - client_rank) == 1:
            if server_rank > client_rank:
                return ClassificationAgreement.SERVER_HIGHER
            else:
                return ClassificationAgreement.CLIENT_HIGHER
        
        # Significant disagreement
        if server_rank > client_rank:
            return ClassificationAgreement.SERVER_HIGHER
        elif client_rank > server_rank:
            return ClassificationAgreement.CLIENT_HIGHER
        else:
            return ClassificationAgreement.DISAGREEMENT
    
    def _apply_classification_strategy(self, server_level: str, client_level: str, strategy: ClassificationStrategy, agreement: ClassificationAgreement) -> str:
        """Apply classification strategy to determine final crisis level"""
        try:
            if agreement == ClassificationAgreement.FULL_AGREEMENT:
                return client_level  # Both agree, use either
            
            level_hierarchy = {
                'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4
            }
            
            server_rank = level_hierarchy.get(server_level, 0)
            client_rank = level_hierarchy.get(client_level, 0)
            
            if strategy == ClassificationStrategy.CONSERVATIVE:
                # Use higher of the two (more sensitive)
                return server_level if server_rank > client_rank else client_level
                
            elif strategy == ClassificationStrategy.AGGRESSIVE:
                # Prefer client decision with server as fallback
                return client_level
                
            elif strategy == ClassificationStrategy.CONSENSUS:
                # Require agreement, escalate disagreements to higher level
                max_rank = max(server_rank, client_rank)
                return [k for k, v in level_hierarchy.items() if v == max_rank][0]
                
            elif strategy == ClassificationStrategy.CLIENT_ONLY:
                # Client decision only
                return client_level
                
            else:
                # Default to conservative
                return server_level if server_rank > client_rank else client_level
                
        except Exception as e:
            logger.error(f"Error applying classification strategy: {e}")
            return server_level  # Fallback to server
    
    def _generate_classification_reasoning(self, crisis_score: float, confidence_score: float, server_level: str, client_level: str, final_level: str, config: ThresholdConfig, strategy: ClassificationStrategy, agreement: ClassificationAgreement) -> str:
        """Generate human-readable reasoning for the classification decision"""
        try:
            reasoning_parts = []
            
            # Score analysis
            reasoning_parts.append(f"Crisis score: {crisis_score:.3f}, Confidence: {confidence_score:.3f}")
            
            # Threshold analysis
            score_variance = abs(crisis_score - confidence_score)
            if score_variance > 0.15:
                reasoning_parts.append(f"High score variance ({score_variance:.3f}) suggests uncertainty")
            
            # Classification comparison
            if agreement == ClassificationAgreement.FULL_AGREEMENT:
                reasoning_parts.append(f"Server and client agree on '{final_level}' classification")
            else:
                reasoning_parts.append(f"Server suggested '{server_level}', client determined '{client_level}'")
            
            # Strategy application
            if final_level != client_level:
                reasoning_parts.append(f"Strategy '{strategy.value}' selected server classification")
            elif final_level != server_level:
                reasoning_parts.append(f"Strategy '{strategy.value}' selected client classification")
            
            # Final decision
            reasoning_parts.append(f"Final classification: '{final_level}'")
            
            return ". ".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"Error generating classification reasoning: {e}")
            return f"Classification completed with final level: {final_level}"
    
    def _update_classification_stats(self, result: ClassificationResult):
        """Update classification statistics for analysis"""
        try:
            self.classification_stats['total_classifications'] += 1
            self.classification_stats['strategy_usage'][result.strategy_used.value] += 1
            
            if result.classification_agreement == ClassificationAgreement.FULL_AGREEMENT:
                self.classification_stats['agreements'] += 1
            else:
                self.classification_stats['disagreements'] += 1
                
                if result.classification_agreement == ClassificationAgreement.SERVER_HIGHER:
                    self.classification_stats['server_higher_count'] += 1
                elif result.classification_agreement == ClassificationAgreement.CLIENT_HIGHER:
                    self.classification_stats['client_higher_count'] += 1
                    
        except Exception as e:
            logger.error(f"Error updating classification stats: {e}")
    # ============================================================================

    # ============================================================================
    # STATS
    # ============================================================================
    def get_classification_statistics(self) -> Dict[str, Any]:
        """Get current classification statistics for analysis"""
        try:
            total = self.classification_stats['total_classifications']
            if total == 0:
                return {'message': 'No classifications performed yet'}
            
            agreement_rate = (self.classification_stats['agreements'] / total) * 100
            disagreement_rate = (self.classification_stats['disagreements'] / total) * 100
            
            return {
                'total_classifications': total,
                'agreement_rate_percent': agreement_rate,
                'disagreement_rate_percent': disagreement_rate,
                'server_higher_percent': (self.classification_stats['server_higher_count'] / total) * 100,
                'client_higher_percent': (self.classification_stats['client_higher_count'] / total) * 100,
                'strategy_usage': self.classification_stats['strategy_usage'],
                'raw_stats': self.classification_stats
            }
            
        except Exception as e:
            logger.error(f"Error generating classification statistics: {e}")
            return {'error': str(e)}
    
    def evaluate_threshold_performance(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate performance of different threshold configurations
        
        Args:
            test_results: List of test results with expected vs actual classifications
            
        Returns:
            Performance analysis for different threshold configurations
        """
        try:
            performance_data = {}
            
            for config_name in self.threshold_configs.keys():
                correct_classifications = 0
                total_tests = len(test_results)
                
                for test in test_results:
                    expected_level = test.get('expected_crisis_level', 'none')
                    crisis_score = test.get('crisis_score', 0.0)
                    confidence_score = test.get('confidence_score', 0.0)
                    
                    # Classify using this threshold configuration
                    client_level = self._calculate_client_crisis_level(
                        crisis_score, confidence_score, 
                        self.threshold_configs[config_name]
                    )
                    
                    if client_level == expected_level:
                        correct_classifications += 1
                
                accuracy = (correct_classifications / total_tests) * 100 if total_tests > 0 else 0
                performance_data[config_name] = {
                    'accuracy_percent': accuracy,
                    'correct_classifications': correct_classifications,
                    'total_tests': total_tests
                }
            
            # Find best performing configuration
            best_config = max(performance_data.keys(), 
                            key=lambda k: performance_data[k]['accuracy_percent'])
            
            return {
                'performance_by_config': performance_data,
                'best_performing_config': best_config,
                'best_accuracy': performance_data[best_config]['accuracy_percent']
            }
            
        except Exception as e:
            logger.error(f"Error evaluating threshold performance: {e}")
            return {'error': str(e)}
    # ============================================================================

# ============================================================================
# FACTORY FUNCTION - Clean Architecture v3.1 Compliance
# ============================================================================
def create_crisis_classifier_manager(unified_config_manager) -> CrisisClassifierManager:
    """
    Factory function for CrisisClassifierManager (Clean v3.1 Pattern)
    
    Args:
        unified_config_manager: UnifiedConfigManager instance for dependency injection
        
    Returns:
        Initialized CrisisClassifierManager instance
        
    Raises:
        ValueError: If unified_config_manager is None or invalid
    """
    logger.debug("Creating CrisisClassifierManager v3.1-4a-1 with Clean v3.1 architecture")
    
    if not unified_config_manager:
        raise ValueError("UnifiedConfigManager is required for CrisisClassifierManager factory")
    
    return CrisisClassifierManager(unified_config_manager)

# Export public interface
__all__ = [
    'CrisisClassifierManager',
    'ClassificationStrategy', 
    'ClassificationAgreement',
    'ClassificationResult',
    'ThresholdConfig',
    'create_crisis_classifier_manager'
]

logger.info("CrisisClassifierManager v3.1-4a-1 loaded with client-side crisis classification capabilities")