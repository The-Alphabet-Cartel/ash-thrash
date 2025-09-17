# ash-nlp/optimization/weight_optimizer.py
"""
Ash-NLP: Crisis Detection Backend for The Alphabet Cartel Discord Community
CORE PRINCIPLE: Zero-Shot AI Models → Pattern Enhancement → Crisis Classification
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-NLP is a CRISIS DETECTION BACKEND that:
1. FIRST: Uses Zero-Shot AI models for primary semantic classification
2. SECOND: Enhances AI results with contextual pattern analysis  
3. FALLBACK: Uses pattern-only classification if AI models fail
4. PURPOSE: Detect crisis messages in Discord community communications
********************************************************************************
Ensemble Weight Optimization Framework for Ash-NLP Service
---
FILE VERSION: v3.1-wo-1-2
LAST MODIFIED: 2025-09-07
PHASE: Weight Optimization Implementation - Enhanced Response Processing
CLEAN ARCHITECTURE: v3.1 Compliant
Repository: https://github.com/the-alphabet-cartel/ash-nlp
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import os
import json
import time
import logging
import requests
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report
from sklearn.model_selection import StratifiedKFold
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class OptimizationConfiguration:
    """Configuration for ensemble weight optimization"""
    population_size: int = 20
    generations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    weight_precision: float = 0.05
    performance_target_ms: float = 300.0
    improvement_threshold: float = 0.02  # 2% improvement required
    k_fold_validation: int = 5
    holdout_percentage: float = 0.2
    api_endpoint: str = "http://localhost:8881/analyze"

@dataclass
class Individual:
    """Individual solution in evolutionary algorithm"""
    ensemble_mode: str
    depression_weight: float
    sentiment_weight: float
    distress_weight: float
    fitness: float = 0.0
    performance_ms: float = 0.0
    
    def to_weights_dict(self) -> Dict[str, float]:
        """Convert to weights dictionary"""
        return {
            'depression': self.depression_weight,
            'sentiment': self.sentiment_weight,
            'emotional_distress': self.distress_weight
        }
    
    def normalize_weights(self):
        """Ensure weights sum to 1.0"""
        total = self.depression_weight + self.sentiment_weight + self.distress_weight
        if total > 0:
            self.depression_weight /= total
            self.sentiment_weight /= total
            self.distress_weight /= total

class WeightOptimizer:
    """
    Evolutionary Algorithm for Optimizing Ensemble Model Weights and Modes
    
    This optimizer follows Clean Architecture v3.1 patterns:
    - Factory function pattern for initialization
    - Dependency injection for configuration
    - Comprehensive error handling with graceful fallbacks
    - Extensive logging for monitoring and debugging
    """
    
    def __init__(self, unified_config, test_dataset: Dict[str, List[Dict]], config: OptimizationConfiguration):
        """
        Initialize Weight Optimizer
        
        Args:
            config: Optimization configuration parameters
            test_dataset: Dictionary of test data by category
        """
        self.unified_config = unified_config
        self.config = config
        self.test_dataset = test_dataset
        self.all_test_data = self._flatten_test_dataset()
        
        # Optimization state
        self.current_generation = 0
        self.best_individual: Optional[Individual] = None
        self.baseline_performance: Optional[Dict[str, float]] = None
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.total_api_calls = 0
        self.total_optimization_time = 0.0
        
        logger.info(f"WeightOptimizer initialized with {len(self.all_test_data)} test phrases")
        logger.info(f"Target: >{self.config.improvement_threshold*100:.1f}% F1-score improvement")
        logger.info(f"Performance target: ≤{self.config.performance_target_ms:.0f}ms")
    
    def _flatten_test_dataset(self) -> List[Dict[str, Any]]:
        """Flatten test dataset into single list with ground truth labels"""
        flattened_data = []
        
        # Priority mappings for ground truth
        priority_mappings = {
            'high_priority': ['high', 'critical'],
            'medium_priority': ['medium'],
            'low_priority': ['low'],
            'none_priority': ['none'],
            'maybe_high_medium': ['medium', 'high', 'critical'],
            'maybe_medium_low': ['low', 'medium'],
            'maybe_low_none': ['none', 'low']
        }
        
        for category, phrases in self.test_dataset.items():
            expected_levels = priority_mappings.get(category, ['none'])
            
            for phrase_data in phrases:
                # Extract message from nested structure
                if isinstance(phrase_data, dict):
                    message = phrase_data.get('message', str(phrase_data))
                    description = phrase_data.get('description', '')
                else:
                    message = str(phrase_data)
                    description = ''
                
                # Use the highest acceptable level as ground truth for optimization
                ground_truth = expected_levels[0] if expected_levels else 'none'
                
                flattened_data.append({
                    'message': message,
                    'ground_truth': ground_truth,
                    'acceptable_levels': expected_levels,
                    'category': category,
                    'description': description
                })
        
        logger.info(f"Flattened {len(flattened_data)} test phrases across {len(self.test_dataset)} categories")
        return flattened_data
    
    def establish_baseline_performance(self) -> Dict[str, float]:
        """
        Establish baseline performance with current configuration
        
        Returns:
            Dictionary with baseline performance metrics
        """
        logger.info("🎯 Establishing baseline performance with default weights...")
        
        # Current configuration (40/30/30 with weighted mode)
        baseline_individual = Individual(
            ensemble_mode='weighted',
            depression_weight=0.400,
            sentiment_weight=0.300,
            distress_weight=0.300
        )
        
        # Evaluate baseline performance
        performance = self._evaluate_individual(baseline_individual, is_baseline=True)
        self.baseline_performance = performance
        
        logger.info("📊 Baseline Performance Established:")
        logger.info(f"   F1-Score: {performance['f1_score']:.4f}")
        logger.info(f"   Precision: {performance['precision']:.4f}")
        logger.info(f"   Recall: {performance['recall']:.4f}")
        logger.info(f"   Average Response Time: {performance['avg_response_time_ms']:.1f}ms")
        logger.info(f"   Accuracy by Category: {performance.get('category_accuracy', {})}")
        
        return performance
    
    def optimize_weights(self) -> Tuple[Individual, Dict[str, Any]]:
        """
        Execute evolutionary algorithm optimization
        
        Returns:
            Tuple of (best_individual, optimization_results)
        """
        optimization_start_time = time.time()
        logger.info("🚀 Starting evolutionary algorithm optimization...")
        
        try:
            # Initialize population
            population = self._initialize_population()
            logger.info(f"Initialized population of {len(population)} individuals")
            
            # Evolution loop
            for generation in range(self.config.generations):
                self.current_generation = generation
                generation_start_time = time.time()
                
                # Evaluate population
                self._evaluate_population(population)
                
                # Track best individual
                current_best = max(population, key=lambda ind: ind.fitness)
                if self.best_individual is None or current_best.fitness > self.best_individual.fitness:
                    self.best_individual = current_best
                
                # Log generation progress
                generation_time = time.time() - generation_start_time
                avg_fitness = statistics.mean(ind.fitness for ind in population)
                
                logger.info(f"Generation {generation + 1}/{self.config.generations}: "
                           f"Best F1={current_best.fitness:.4f}, "
                           f"Avg F1={avg_fitness:.4f}, "
                           f"Time={generation_time:.1f}s")
                
                # Store generation history
                self._record_generation_history(generation, population, current_best)
                
                # Early stopping if we find excellent solution
                if current_best.fitness > 0.95:
                    logger.info(f"🎉 Excellent solution found (F1={current_best.fitness:.4f}), stopping early")
                    break
                
                # Create next generation (except for last generation)
                if generation < self.config.generations - 1:
                    population = self._create_next_generation(population)
            
            # Calculate optimization results
            total_optimization_time = time.time() - optimization_start_time
            optimization_results = self._compile_optimization_results(total_optimization_time)
            
            logger.info("✅ Optimization completed successfully!")
            logger.info(f"Best configuration: {self.best_individual.ensemble_mode} mode, "
                       f"weights=({self.best_individual.depression_weight:.3f}, "
                       f"{self.best_individual.sentiment_weight:.3f}, "
                       f"{self.best_individual.distress_weight:.3f})")
            
            return self.best_individual, optimization_results
            
        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            raise
    
    def _initialize_population(self) -> List[Individual]:
        """Initialize population with depression model always having highest weight"""
        population = []
        ensemble_modes = ['weighted']
        
        for _ in range(self.config.population_size):
            mode = np.random.choice(ensemble_modes)
            
            # Generate weights with depression >= 0.4 and depression > others
            min_depression = 0.4  # Minimum depression weight
            depression_weight = np.random.uniform(min_depression, 0.8)
            
            # Remaining weight split between sentiment and distress
            remaining_weight = 1.0 - depression_weight
            sentiment_weight = np.random.uniform(0.1, remaining_weight - 0.1)
            distress_weight = remaining_weight - sentiment_weight
            
            # Ensure depression is highest
            max_other = max(sentiment_weight, distress_weight)
            if depression_weight <= max_other:
                # Redistribute to ensure depression dominance
                excess = max_other - depression_weight + 0.05
                if sentiment_weight > distress_weight:
                    sentiment_weight -= excess
                else:
                    distress_weight -= excess
                depression_weight += excess
            
            individual = Individual(
                ensemble_mode=mode,
                depression_weight=depression_weight,
                sentiment_weight=sentiment_weight,
                distress_weight=distress_weight
            )
            
            individual.normalize_weights()
            population.append(individual)
        
        return population
    
    def _evaluate_population(self, population: List[Individual]):
        """Evaluate fitness for all individuals in population"""
        logger.info(f"🧬 Evaluating population of {len(population)} individuals...")
        
        for i, individual in enumerate(population):
            if individual.fitness == 0.0:  # Not yet evaluated
                try:
                    eval_start_time = time.time()
                    logger.info(f"🧪 Evaluating individual {i+1}/{len(population)}: "
                               f"{individual.ensemble_mode} mode, "
                               f"weights=({individual.depression_weight:.3f}, "
                               f"{individual.sentiment_weight:.3f}, {individual.distress_weight:.3f})")
                    
                    performance = self._evaluate_individual(individual)
                    individual.fitness = performance['f1_score']
                    individual.performance_ms = performance['avg_response_time_ms']
                    
                    eval_time = time.time() - eval_start_time
                    logger.info(f"✅ Individual {i+1} complete: F1={individual.fitness:.4f}, "
                               f"Performance={individual.performance_ms:.1f}ms, Time={eval_time:.1f}s")
                    
                except Exception as e:
                    logger.warning(f"❌ Evaluation failed for individual {i+1}: {e}")
                    individual.fitness = 0.0
                    individual.performance_ms = 999.0
    
    def _evaluate_individual(self, individual: Individual, is_baseline: bool = False) -> Dict[str, float]:
        """
        Evaluate individual using the actual NLP API
        
        Args:
            individual: Individual to evaluate
            is_baseline: Whether this is baseline evaluation
            
        Returns:
            Performance metrics dictionary
        """
        logger.debug(f"Evaluating individual: {individual.ensemble_mode} mode, "
                    f"weights=({individual.depression_weight:.3f}, "
                    f"{individual.sentiment_weight:.3f}, {individual.distress_weight:.3f})")
        
        predictions = []
        ground_truths = []
        response_times = []
        category_results = {}
        api_errors = 0
        parsing_errors = 0
        correct_predictions = 0  # Track correct predictions using acceptable levels
        
        # Temporarily set weights for evaluation
        original_env = self._backup_environment_variables()
        self._set_temporary_weights(individual)
        
        try:
            # Wait for configuration to propagate
            time.sleep(2.0 if is_baseline else 1.0)
            
            # Evaluate on test data
            for i, test_item in enumerate(self.all_test_data):
                try:
                    # Make API call
                    start_time = time.time()
                    response = requests.post(
                        self.config.api_endpoint,
                        json={
                            "message": test_item['message'],
                            "user_id": "weight_optimizer",
                            "channel_id": "optimization_test"
                        },
                        timeout=30
                    )
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            
                            # ENHANCED: Better crisis level extraction with fallbacks
                            predicted_level = result.get('crisis_level', 'none')

                            # ENHANCED: Validate and normalize crisis level
                            if predicted_level not in ['none', 'low', 'medium', 'high', 'critical']:
                                logger.warning(f"Invalid crisis level '{predicted_level}' for phrase {i+1}, "
                                             f"defaulting to 'none'. Message: '{test_item['message'][:50]}...'")
                                predicted_level = 'none'
                                parsing_errors += 1
                            
                            predictions.append(predicted_level)
                            
                            # FIXED: Use the predicted level as ground truth for sklearn metrics
                            # but check correctness using acceptable_levels
                            is_correct = predicted_level in test_item['acceptable_levels']
                            if is_correct:
                                # Use the prediction as ground truth for sklearn (this ensures exact matches)
                                ground_truths.append(predicted_level)
                                correct_predictions += 1
                            else:
                                # Use the expected ground truth for sklearn to mark as wrong
                                ground_truths.append(test_item['ground_truth'])
                            
                            response_times.append(response_time)
                            
                            # Track category-specific results
                            category = test_item['category']
                            if category not in category_results:
                                category_results[category] = {'correct': 0, 'total': 0}
                            
                            category_results[category]['correct'] += int(is_correct)
                            category_results[category]['total'] += 1
                            
                            self.total_api_calls += 1
                            
                            # ENHANCED: More detailed progress logging
                            if (i + 1) % 50 == 0:
                                progress_pct = ((i + 1) / len(self.all_test_data)) * 100
                                recent_predictions = predictions[-10:] if len(predictions) >= 10 else predictions
                                recent_correct_count = sum(1 for j in range(max(0, i-9), i+1) 
                                                         if j < len(self.all_test_data) 
                                                         and predictions[j] in self.all_test_data[j]['acceptable_levels'])
                                recent_accuracy = recent_correct_count / min(10, len(recent_predictions)) * 100
                                
                                logger.info(f"Progress: {i+1}/{len(self.all_test_data)} phrases ({progress_pct:.1f}%) - "
                                          f"Avg Response: {statistics.mean(response_times[-25:]):.1f}ms, "
                                          f"Accuracy: {recent_correct_count}/10 "
                                          f"({recent_accuracy:.1f}%)")
                        
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error for phrase {i+1}: {e}")
                            logger.error(f"Response content: {response.text[:200]}...")
                            predictions.append('none')
                            ground_truths.append(test_item['ground_truth'])
                            response_times.append(999.0)
                            parsing_errors += 1
                    
                    else:
                        logger.warning(f"API call failed with status {response.status_code} for phrase {i+1}")
                        logger.warning(f"Response: {response.text[:200]}...")
                        predictions.append('none')  # Conservative fallback
                        ground_truths.append(test_item['ground_truth'])
                        response_times.append(999.0)  # Penalty for failure
                        api_errors += 1
                
                except Exception as e:
                    logger.warning(f"Error evaluating phrase {i+1}: {e}")
                    logger.warning(f"Message: '{test_item['message'][:50]}...'")
                    predictions.append('none')  # Conservative fallback
                    ground_truths.append(test_item['ground_truth'])
                    response_times.append(999.0)  # Penalty for failure
                    api_errors += 1
            
            # ENHANCED: Detailed evaluation summary
            logger.info(f"Evaluation complete: {len(predictions)} predictions, "
                       f"{api_errors} API errors, {parsing_errors} parsing errors")
            logger.info(f"Correct predictions using acceptable levels: {correct_predictions}/{len(predictions)} "
                       f"({correct_predictions/len(predictions)*100:.1f}%)")
            
            # Log prediction distribution for debugging
            prediction_counts = {}
            ground_truth_counts = {}
            for pred in predictions:
                prediction_counts[pred] = prediction_counts.get(pred, 0) + 1
            for gt in ground_truths:
                ground_truth_counts[gt] = ground_truth_counts.get(gt, 0) + 1
                
            logger.info(f"Prediction distribution: {prediction_counts}")
            logger.info(f"Ground truth distribution (for sklearn): {ground_truth_counts}")
            
            # Calculate metrics
            # Convert crisis levels to numerical for sklearn
            level_to_num = {'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            y_true = [level_to_num.get(gt, 0) for gt in ground_truths]
            y_pred = [level_to_num.get(pred, 0) for pred in predictions]
            
            # ENHANCED: Validate that we have predictions to work with
            if not predictions or not ground_truths:
                logger.error("No predictions or ground truths available for metric calculation!")
                return {
                    'f1_score': 0.0,
                    'raw_f1_score': 0.0,
                    'precision': 0.0,
                    'recall': 0.0,
                    'avg_response_time_ms': 999.0,
                    'performance_penalty': 999.0,
                    'category_accuracy': {},
                    'total_evaluations': 0,
                    'api_errors': api_errors,
                    'parsing_errors': parsing_errors
                }
            
            # Calculate primary metrics
            f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
            precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            
            # ALTERNATIVE: Calculate F1 based on correct/incorrect using acceptable levels
            overall_accuracy = correct_predictions / len(predictions) if predictions else 0.0
            # Use accuracy as a proxy for F1 when we're doing acceptable-level matching
            adjusted_f1_from_accuracy = overall_accuracy
            
            # ENHANCED: Log detailed metric calculation
            logger.info(f"Sklearn metrics: F1={f1:.4f}, Precision={precision:.4f}, Recall={recall:.4f}")
            logger.info(f"Acceptable-level accuracy: {overall_accuracy:.4f}")
            
            # Log some sample comparisons for debugging
            sample_size = min(5, len(predictions))
            for idx in range(sample_size):
                is_acceptable = predictions[idx] in self.all_test_data[idx]['acceptable_levels']
                logger.debug(f"Sample {idx+1}: predicted='{predictions[idx]}', "
                            f"ground_truth='{self.all_test_data[idx]['ground_truth']}', "
                            f"acceptable={self.all_test_data[idx]['acceptable_levels']}, "
                            f"correct={is_acceptable}")
            
            # Calculate category accuracy
            category_accuracy = {}
            for category, results in category_results.items():
                if results['total'] > 0:
                    accuracy = results['correct'] / results['total']
                    category_accuracy[category] = accuracy
                    logger.debug(f"Category {category}: {results['correct']}/{results['total']} "
                               f"({accuracy:.3f} accuracy)")
            
            # Calculate performance metrics
            avg_response_time = statistics.mean(response_times) if response_times else 999.0
            performance_penalty = max(0, avg_response_time - self.config.performance_target_ms) / 100.0
            
            # FIXED: Use acceptable-level accuracy as the primary F1 score
            primary_f1 = adjusted_f1_from_accuracy
            adjusted_f1 = primary_f1 - performance_penalty
            
            performance_metrics = {
                'f1_score': adjusted_f1,
                'raw_f1_score': primary_f1,
                'sklearn_f1_score': f1,  # Keep sklearn F1 for reference
                'precision': precision,
                'recall': recall,
                'overall_accuracy': overall_accuracy,
                'avg_response_time_ms': avg_response_time,
                'performance_penalty': performance_penalty,
                'category_accuracy': category_accuracy,
                'total_evaluations': len(predictions),
                'api_errors': api_errors,
                'parsing_errors': parsing_errors,
                'correct_predictions': correct_predictions
            }
            
            logger.info(f"Final metrics: Adjusted F1={adjusted_f1:.4f} "
                       f"(Accuracy-based F1={primary_f1:.4f} - Penalty={performance_penalty:.4f})")
            logger.info(f"Sklearn F1 for reference: {f1:.4f}")
            
            return performance_metrics
            
        finally:
            # Restore original environment
            self._restore_environment_variables(original_env)
    
    def _backup_environment_variables(self) -> Dict[str, str]:
        """Backup current environment variables"""
        return {
            'NLP_MODEL_DEPRESSION_WEIGHT': os.getenv('NLP_MODEL_DEPRESSION_WEIGHT', '0.4'),
            'NLP_MODEL_SENTIMENT_WEIGHT': os.getenv('NLP_MODEL_SENTIMENT_WEIGHT', '0.3'),
            'NLP_MODEL_DISTRESS_WEIGHT': os.getenv('NLP_MODEL_DISTRESS_WEIGHT', '0.3'),
            'NLP_ENSEMBLE_MODE': os.getenv('NLP_ENSEMBLE_MODE', 'weighted')
        }
    
    def _set_temporary_weights(self, individual: Individual):
        """Set weights via API call"""
        try:
            set_weights_endpoint = self.config.api_endpoint.replace('/analyze', '/ensemble/set-weights')
            
            response = requests.post(set_weights_endpoint, params={
                'depression_weight': individual.depression_weight,
                'sentiment_weight': individual.sentiment_weight,
                'distress_weight': individual.distress_weight,
                'ensemble_mode': individual.ensemble_mode
            }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Weights set successfully: {result['weights']}")
                return True
            else:
                logger.error(f"Failed to set weights: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set weights via API: {e}")
            return False
    
    def _restore_environment_variables(self, backup: Dict[str, str]):
        """Restore environment variables from backup and refresh cache"""
        for key, value in backup.items():
            os.environ[key] = value
        
        # CRITICAL: Refresh cache after restoring original weights
        try:
            refresh_endpoint = self.config.api_endpoint.replace('/analyze', '/ensemble/refresh-weights')
            response = requests.post(refresh_endpoint, timeout=10)
            if response.status_code == 200:
                logger.info("Cache refreshed after restoring original weights")
            else:
                logger.warning(f"Failed to refresh cache after restore: {response.status_code}")
        except Exception as e:
            logger.warning(f"Failed to refresh cache after restore: {e}")
    
    def _create_next_generation(self, population: List[Individual]) -> List[Individual]:
        """Create next generation using evolutionary operators"""
        # Sort by fitness (descending)
        population.sort(key=lambda ind: ind.fitness, reverse=True)
        
        next_generation = []
        elite_count = max(2, int(0.1 * len(population)))  # Keep top 10%
        
        # Elitism - keep best individuals
        next_generation.extend(population[:elite_count])
        
        # Generate rest through crossover and mutation
        ensemble_modes = ['consensus', 'majority', 'weighted']
        
        while len(next_generation) < self.config.population_size:
            if np.random.random() < self.config.crossover_rate:
                # Crossover
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                child = self._crossover(parent1, parent2, ensemble_modes)
            else:
                # Copy and mutate
                parent = self._tournament_selection(population)
                child = self._mutate(parent, ensemble_modes)
            
            # Ensure constraints
            child.normalize_weights()
            child.fitness = 0.0  # Reset fitness for re-evaluation
            child.performance_ms = 0.0
            
            next_generation.append(child)
        
        return next_generation[:self.config.population_size]
    
    def _tournament_selection(self, population: List[Individual], tournament_size: int = 3) -> Individual:
        """Tournament selection for parent selection"""
        tournament = np.random.choice(population, min(tournament_size, len(population)), replace=False)
        return max(tournament, key=lambda ind: ind.fitness)
    
    def _crossover(self, parent1: Individual, parent2: Individual, ensemble_modes: List[str]) -> Individual:
        """Crossover operation to create child"""
        # Ensemble mode crossover (choose randomly from parents)
        child_mode = np.random.choice([parent1.ensemble_mode, parent2.ensemble_mode])
        
        # Weight crossover (blend crossover)
        alpha = np.random.uniform(0, 1)
        child_depression = alpha * parent1.depression_weight + (1 - alpha) * parent2.depression_weight
        child_sentiment = alpha * parent1.sentiment_weight + (1 - alpha) * parent2.sentiment_weight
        child_distress = alpha * parent1.distress_weight + (1 - alpha) * parent2.distress_weight
        
        child = Individual(
            ensemble_mode=child_mode,
            depression_weight=child_depression,
            sentiment_weight=child_sentiment,
            distress_weight=child_distress
        )
        
        return child
    
    def _mutate(self, individual: Individual, ensemble_modes: List[str]) -> Individual:
        """Mutation operation with depression dominance constraint"""
        child = Individual(
            ensemble_mode=individual.ensemble_mode,
            depression_weight=individual.depression_weight,
            sentiment_weight=individual.sentiment_weight,
            distress_weight=individual.distress_weight
        )
        
        if np.random.random() < self.config.mutation_rate:
            child.ensemble_mode = np.random.choice(ensemble_modes)
        
        if np.random.random() < self.config.mutation_rate:
            # Constrained weight mutation
            noise = np.random.normal(0, 0.05, 3)  # Smaller mutations
            
            child.depression_weight += noise[0]
            child.sentiment_weight += noise[1]
            child.distress_weight += noise[2]
            
            # Enforce minimum bounds
            child.depression_weight = max(0.4, child.depression_weight)  # Min 40%
            child.sentiment_weight = max(0.1, child.sentiment_weight)
            child.distress_weight = max(0.1, child.distress_weight)
            
            # Normalize
            child.normalize_weights()
            
            # Ensure depression remains dominant after normalization
            max_other = max(child.sentiment_weight, child.distress_weight)
            if child.depression_weight <= max_other:
                # Force redistribution
                target_depression = max_other + 0.05
                reduction_needed = target_depression - child.depression_weight
                
                # Take from the larger of the other two
                if child.sentiment_weight > child.distress_weight:
                    child.sentiment_weight -= reduction_needed
                else:
                    child.distress_weight -= reduction_needed
                
                child.depression_weight = target_depression
                child.normalize_weights()
        
        return child
    
    def _record_generation_history(self, generation: int, population: List[Individual], best_individual: Individual):
        """Record generation history for analysis"""
        generation_data = {
            'generation': generation,
            'best_fitness': best_individual.fitness,
            'best_performance_ms': best_individual.performance_ms,
            'best_config': {
                'ensemble_mode': best_individual.ensemble_mode,
                'depression_weight': best_individual.depression_weight,
                'sentiment_weight': best_individual.sentiment_weight,
                'distress_weight': best_individual.distress_weight
            },
            'avg_fitness': statistics.mean(ind.fitness for ind in population),
            'fitness_std': statistics.stdev(ind.fitness for ind in population) if len(population) > 1 else 0.0,
            'population_diversity': self._calculate_population_diversity(population)
        }
        
        self.optimization_history.append(generation_data)
    
    def _calculate_population_diversity(self, population: List[Individual]) -> float:
        """Calculate population diversity metric"""
        try:
            # Calculate diversity based on weight differences
            weights_matrix = np.array([[ind.depression_weight, ind.sentiment_weight, ind.distress_weight] 
                                     for ind in population])
            
            # Calculate average pairwise distance
            distances = []
            for i in range(len(weights_matrix)):
                for j in range(i+1, len(weights_matrix)):
                    dist = np.linalg.norm(weights_matrix[i] - weights_matrix[j])
                    distances.append(dist)
            
            return statistics.mean(distances) if distances else 0.0
            
        except Exception as e:
            logger.warning(f"Diversity calculation failed: {e}")
            return 0.0
    
    def _compile_optimization_results(self, total_time: float) -> Dict[str, Any]:
        """Compile comprehensive optimization results"""
        improvement = 0.0
        improvement_percentage = 0.0
        
        if self.baseline_performance and self.best_individual:
            baseline_f1 = self.baseline_performance['f1_score']
            best_f1 = self.best_individual.fitness
            improvement = best_f1 - baseline_f1
            improvement_percentage = (improvement / baseline_f1) * 100 if baseline_f1 > 0 else 0
        
        results = {
            'optimization_summary': {
                'total_generations': self.current_generation + 1,
                'total_time_minutes': total_time / 60,
                'total_api_calls': self.total_api_calls,
                'improvement_achieved': improvement,
                'improvement_percentage': improvement_percentage,
                'target_met': improvement_percentage >= (self.config.improvement_threshold * 100)
            },
            'baseline_performance': self.baseline_performance,
            'best_configuration': {
                'ensemble_mode': self.best_individual.ensemble_mode,
                'weights': {
                    'depression': self.best_individual.depression_weight,
                    'sentiment': self.best_individual.sentiment_weight,
                    'emotional_distress': self.best_individual.distress_weight
                },
                'performance_metrics': {
                    'f1_score': self.best_individual.fitness,
                    'performance_ms': self.best_individual.performance_ms
                }
            },
            'optimization_history': self.optimization_history,
            'recommendation': self._generate_recommendation(improvement_percentage)
        }
        
        return results
    
    def _generate_recommendation(self, improvement_percentage: float) -> str:
        """Generate deployment recommendation"""
        if improvement_percentage >= (self.config.improvement_threshold * 100):
            return f"RECOMMENDED FOR DEPLOYMENT: {improvement_percentage:.2f}% improvement achieved (target: ≥{self.config.improvement_threshold*100:.1f}%)"
        elif improvement_percentage > 0:
            return f"MARGINAL IMPROVEMENT: {improvement_percentage:.2f}% improvement (below {self.config.improvement_threshold*100:.1f}% target). Consider additional optimization."
        else:
            return f"NO IMPROVEMENT: {improvement_percentage:.2f}% change. Recommend keeping current configuration."
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "./results/optimizer-weights"):
        """Save optimization results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = output_path / f"optimization_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save deployment configuration if recommended
        if results['optimization_summary']['target_met'] and self.best_individual:
            deploy_config = {
                'NLP_MODEL_DEPRESSION_WEIGHT': str(self.best_individual.depression_weight),
                'NLP_MODEL_SENTIMENT_WEIGHT': str(self.best_individual.sentiment_weight), 
                'NLP_MODEL_DISTRESS_WEIGHT': str(self.best_individual.distress_weight),
                'NLP_ENSEMBLE_MODE': self.best_individual.ensemble_mode
            }
            
            deploy_file = output_path / f"deploy_config_{timestamp}.env"
            with open(deploy_file, 'w') as f:
                for key, value in deploy_config.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"💾 Deployment configuration saved to: {deploy_file}")
        
        logger.info(f"💾 Optimization results saved to: {results_file}")
        return results_file

def create_weight_optimizer(unified_config, test_dataset: Dict[str, List[Dict]], config: Optional[OptimizationConfiguration] = None) -> WeightOptimizer:
    """
    Factory function to create WeightOptimizer instance
    
    Args:
        test_dataset: Dictionary of test data by category
        config: Optional optimization configuration
        
    Returns:
        WeightOptimizer instance
    """
    if config is None:
        config = OptimizationConfiguration()
    
    return WeightOptimizer(unified_config, test_dataset, config)

__all__ = [
    'WeightOptimizer',
    'OptimizationConfiguration', 
    'Individual',
    'create_weight_optimizer'
]

logger.info("✅ Weight Optimization Framework v3.1-wo-1-2 loaded")