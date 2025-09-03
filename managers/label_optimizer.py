# managers/label_optimizer.py
"""
Ash-Thrash: Crisis Detection Testing Suite for The Alphabet Cartel Discord Community
CORE PRINCIPLE: Zero-Shot AI Models → Pattern Enhancement → Crisis Classification
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Thrash is a TESTING SUITE that validates crisis detection accuracy of Ash-NLP:
1. FIRST: Uses test phrases with known expected outcomes
2. SECOND: Evaluates detection accuracy across label sets  
3. THIRD: Optimizes label set selection via evolutionary algorithm
4. PURPOSE: Ensure optimal crisis detection for Discord community communications
********************************************************************************
Zero-Shot Label Set Optimization Framework for Ash-Thrash Testing Suite
---
FILE VERSION: v3.1-lo-1-1
LAST MODIFIED: 2025-09-03
PHASE: Label Set Optimization Implementation
CLEAN ARCHITECTURE: v3.1 Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
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
class LabelOptimizationConfiguration:
    """Configuration for zero-shot label set optimization"""
    population_size: int = 15  # Smaller than weight optimizer since we have fewer variables
    generations: int = 30     # Fewer generations needed for discrete optimization
    mutation_rate: float = 0.2  # Higher mutation rate for discrete values
    crossover_rate: float = 0.7
    performance_target_ms: float = 300.0  # Allow more time for label switching
    improvement_threshold: float = 0.03  # 3% improvement required
    k_fold_validation: int = 3  # Reduced for faster evaluation
    holdout_percentage: float = 0.2
    api_endpoint: str = "http://172.20.0.11:8881/analyze"
    admin_endpoint: str = "http://172.20.0.11:8881/admin"

@dataclass
class LabelSetIndividual:
    """Individual solution representing a label set configuration"""
    label_set_name: str
    fitness: float = 0.0
    performance_ms: float = 0.0
    f1_score: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    category_performance: Dict[str, float] = None
    
    def __post_init__(self):
        if self.category_performance is None:
            self.category_performance = {}

class LabelSetOptimizer:
    """
    Evolutionary Algorithm for Optimizing Zero-Shot Label Sets
    
    This optimizer follows Clean Architecture v3.1 patterns and integrates with
    the existing Ash-Thrash testing framework to find optimal label configurations.
    """
    
    def __init__(self, unified_config, test_dataset: Dict[str, List[Dict]], config: LabelOptimizationConfiguration):
        """
        Initialize Label Set Optimizer
        
        Args:
            unified_config: Unified configuration manager
            test_dataset: Dictionary of test data by category
            config: Optimization configuration parameters
        """
        self.unified_config = unified_config
        self.config = config
        self.test_dataset = test_dataset
        self.all_test_data = self._flatten_test_dataset()
        
        # Available label sets (discovered at runtime)
        self.available_label_sets: List[str] = []
        self.original_label_set: str = ""
        
        # Optimization state
        self.current_generation = 0
        self.best_individual: Optional[LabelSetIndividual] = None
        self.baseline_performance: Optional[Dict[str, float]] = None
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.total_api_calls = 0
        self.total_optimization_time = 0.0
        
        logger.info(f"LabelSetOptimizer initialized with {len(self.all_test_data)} test phrases")
        logger.info(f"Target: >{self.config.improvement_threshold*100:.1f}% F1-score improvement")
    
    def _flatten_test_dataset(self) -> List[Dict[str, Any]]:
        """Flatten test dataset into single list with category labels"""
        flattened = []
        for category, test_items in self.test_dataset.items():
            for item in test_items:
                flattened.append({
                    'message': item.get('message', ''),
                    'expected_priority': item.get('expected_priority', ['none']),
                    'category': category,
                    'user_id': f"test_user_{hash(item.get('message', '')) % 1000}",
                    'channel_id': f"test_channel_{category}"
                })
        return flattened
    
    def discover_available_label_sets(self) -> List[str]:
        """Discover available label sets from NLP server"""
        try:
            current_url = f"{self.config.admin_endpoint}/labels/current"
            current_response = requests.get(current_url, timeout=10)

            if current_response.status_code == 200:
                current_data = current_response.json()
                self.original_label_set = current_data.get('current_set', 'enhanced_crisis')
                logger.info(f"Current label set: {self.original_label_set}")
            
            list_url = f"{self.config.admin_endpoint}/labels/list"
            response = requests.get(list_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                label_sets = []
                
                # Extract label set names from response
                if 'sets' in data:
                    label_sets = [s['name'] for s in data['sets']]
                elif 'available_sets' in data:
                    label_sets = data['available_sets']
                else:
                    logger.warning(f"Unexpected response format: {data}")
                    return []
                
                self.available_label_sets = label_sets
                
                logger.info(f"Discovered {len(label_sets)} available label sets: {label_sets}")
                
                return label_sets
            
            else:
                logger.error(f"Failed to get label sets: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error discovering label sets: {e}")
            return []
    
    def switch_label_set(self, label_set_name: str) -> bool:
        """Switch to specific label set"""
        try:
            switch_url = f"{self.config.admin_endpoint}/labels/switch"
            response = requests.post(
                switch_url, 
                json={"label_set": label_set_name},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                if success:
                    logger.debug(f"Switched to label set: {label_set_name}")
                else:
                    logger.warning(f"Switch reported failure: {result.get('error', 'Unknown error')}")
                return success
            else:
                logger.error(f"Label set switch failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching label set: {e}")
            return False
    
    def test_message(self, message: str, user_id: str, channel_id: str) -> Optional[Dict[str, Any]]:
        """Test a single message against current label set"""
        try:
            response = requests.post(
                self.config.api_endpoint,
                json={
                    "message": message,
                    "user_id": user_id,
                    "channel_id": channel_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.total_api_calls += 1
                return response.json()
            else:
                logger.warning(f"Analysis request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"Error testing message: {e}")
            return None
    
    def evaluate_label_set(self, label_set_name: str) -> Dict[str, float]:
        """Evaluate performance of a specific label set"""
        logger.debug(f"Evaluating label set: {label_set_name}")
        
        # Switch to target label set
        if not self.switch_label_set(label_set_name):
            logger.error(f"Failed to switch to label set: {label_set_name}")
            return {"f1_score": 0.0, "precision": 0.0, "recall": 0.0, "avg_response_time_ms": 999.0}
        
        # Wait for switch to take effect
        time.sleep(1.0)
        
        # Test all messages
        predictions = []
        actuals = []
        response_times = []
        category_correct = {}
        category_total = {}
        
        for test_item in self.all_test_data:
            start_time = time.time()
            result = self.test_message(
                test_item['message'],
                test_item['user_id'],
                test_item['channel_id']
            )
            
            response_time = (time.time() - start_time) * 1000
            response_times.append(response_time)
            
            if result:
                predicted_priority = result.get('crisis_level', 'none').lower()
                expected_priorities = [p.lower() for p in test_item['expected_priority']]
                
                # Binary classification: correct vs incorrect
                is_correct = predicted_priority in expected_priorities
                predictions.append(1 if is_correct else 0)
                actuals.append(1)  # All test cases expect correct classification
                
                # Track category performance
                category = test_item['category']
                if category not in category_correct:
                    category_correct[category] = 0
                    category_total[category] = 0
                
                if is_correct:
                    category_correct[category] += 1
                category_total[category] += 1
            else:
                # API failure counts as incorrect
                predictions.append(0)
                actuals.append(1)
        
        # Calculate metrics
        if len(predictions) > 0 and len(actuals) > 0:
            f1 = f1_score(actuals, predictions, average='binary', zero_division=0)
            precision = precision_score(actuals, predictions, average='binary', zero_division=0)
            recall = recall_score(actuals, predictions, average='binary', zero_division=0)
        else:
            f1 = precision = recall = 0.0
        
        # Calculate category accuracies
        category_performance = {}
        for category in category_total:
            if category_total[category] > 0:
                category_performance[category] = category_correct[category] / category_total[category]
            else:
                category_performance[category] = 0.0
        
        avg_response_time = statistics.mean(response_times) if response_times else 999.0
        
        performance = {
            "f1_score": f1,
            "precision": precision,
            "recall": recall,
            "avg_response_time_ms": avg_response_time,
            "category_performance": category_performance,
            "total_tests": len(self.all_test_data),
            "successful_tests": len([p for p in predictions if p == 1])
        }
        
        logger.debug(f"Label set {label_set_name} performance: F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")
        
        return performance
    
    def establish_baseline_performance(self) -> Dict[str, Any]:
        """Establish baseline performance with current label set"""
        logger.info("🎯 Establishing baseline performance with current label set...")
        
        # Discover available label sets and current one
        self.available_label_sets = self.discover_available_label_sets()
        
        if not self.available_label_sets:
            raise RuntimeError("No label sets available for optimization")
        
        # Evaluate current/original label set
        baseline_performance = self.evaluate_label_set(self.original_label_set)
        self.baseline_performance = baseline_performance
        
        logger.info("📊 Baseline Performance Established:")
        logger.info(f"   Label Set: {self.original_label_set}")
        logger.info(f"   F1-Score: {baseline_performance['f1_score']:.4f}")
        logger.info(f"   Precision: {baseline_performance['precision']:.4f}")
        logger.info(f"   Recall: {baseline_performance['recall']:.4f}")
        logger.info(f"   Average Response Time: {baseline_performance['avg_response_time_ms']:.1f}ms")
        logger.info(f"   Category Performance: {baseline_performance.get('category_performance', {})}")
        
        return baseline_performance
    
    def optimize_label_sets(self) -> Tuple[LabelSetIndividual, Dict[str, Any]]:
        """Execute evolutionary algorithm optimization for label sets"""
        optimization_start_time = time.time()
        logger.info("🚀 Starting evolutionary algorithm for label set optimization...")
        
        try:
            # Initialize population with all available label sets
            population = self._initialize_population()
            logger.info(f"Initialized population of {len(population)} label sets")
            
            # Track best performance
            generation_best_scores = []
            
            # Evolution loop
            for generation in range(self.config.generations):
                self.current_generation = generation
                logger.info(f"🧬 Generation {generation + 1}/{self.config.generations}")
                
                # Evaluate population
                self._evaluate_population(population)
                
                # Find best individual
                generation_best = max(population, key=lambda ind: ind.fitness)
                generation_best_scores.append(generation_best.fitness)
                
                # Update global best
                if self.best_individual is None or generation_best.fitness > self.best_individual.fitness:
                    self.best_individual = generation_best
                    logger.info(f"🏆 New best label set: {generation_best.label_set_name} "
                              f"(F1: {generation_best.f1_score:.4f})")
                
                # Log generation summary
                avg_fitness = statistics.mean([ind.fitness for ind in population])
                logger.info(f"   Best: {generation_best.fitness:.4f}, Average: {avg_fitness:.4f}")
                
                # Early stopping if no improvement
                if generation > 5:
                    recent_improvement = max(generation_best_scores[-5:]) - min(generation_best_scores[-5:])
                    if recent_improvement < 0.01:  # Less than 1% improvement in 5 generations
                        logger.info(f"⏹️ Early stopping - minimal improvement detected")
                        break
                
                # Create next generation (for discrete optimization, this is mostly re-evaluation)
                if generation < self.config.generations - 1:
                    population = self._create_next_generation(population)
            
            # Calculate optimization results
            optimization_time = time.time() - optimization_start_time
            self.total_optimization_time = optimization_time
            
            # Restore original label set
            logger.info(f"🔄 Restoring original label set: {self.original_label_set}")
            self.switch_label_set(self.original_label_set)
            
            # Prepare results
            optimization_results = {
                "best_label_set": self.best_individual.label_set_name,
                "best_performance": {
                    "f1_score": self.best_individual.f1_score,
                    "precision": self.best_individual.precision,
                    "recall": self.best_individual.recall,
                    "avg_response_time_ms": self.best_individual.performance_ms,
                    "category_performance": self.best_individual.category_performance
                },
                "baseline_performance": self.baseline_performance,
                "improvement": {
                    "f1_score": self.best_individual.f1_score - self.baseline_performance['f1_score'],
                    "precision": self.best_individual.precision - self.baseline_performance['precision'],
                    "recall": self.best_individual.recall - self.baseline_performance['recall']
                },
                "optimization_summary": {
                    "generations_completed": generation + 1,
                    "total_time_minutes": optimization_time / 60,
                    "total_api_calls": self.total_api_calls,
                    "improvement_percentage": ((self.best_individual.f1_score - self.baseline_performance['f1_score']) / self.baseline_performance['f1_score'] * 100) if self.baseline_performance['f1_score'] > 0 else 0,
                    "target_met": (self.best_individual.f1_score - self.baseline_performance['f1_score']) >= self.config.improvement_threshold,
                    "available_label_sets": self.available_label_sets,
                    "all_results": [
                        {
                            "label_set": ind.label_set_name,
                            "f1_score": ind.f1_score,
                            "precision": ind.precision,
                            "recall": ind.recall
                        }
                        for ind in sorted(population, key=lambda x: x.fitness, reverse=True)
                    ]
                }
            }
            
            # Generate recommendation
            if optimization_results["optimization_summary"]["target_met"]:
                optimization_results["recommendation"] = f"RECOMMENDED: Switch to label set '{self.best_individual.label_set_name}' for {optimization_results['optimization_summary']['improvement_percentage']:.1f}% improvement"
            else:
                optimization_results["recommendation"] = f"CURRENT OPTIMAL: Label set '{self.original_label_set}' remains best choice (no significant improvement found)"
            
            logger.info(f"🎉 Label set optimization complete!")
            logger.info(f"Best label set: {self.best_individual.label_set_name}")
            logger.info(f"F1-Score improvement: {optimization_results['improvement']['f1_score']:.4f}")
            
            return self.best_individual, optimization_results
            
        except Exception as e:
            logger.error(f"❌ Label set optimization failed: {e}")
            # Always try to restore original label set
            try:
                self.switch_label_set(self.original_label_set)
            except:
                pass
            raise
    
    def _initialize_population(self) -> List[LabelSetIndividual]:
        """Initialize population with all available label sets"""
        population = []
        
        for label_set in self.available_label_sets:
            individual = LabelSetIndividual(label_set_name=label_set)
            population.append(individual)
        
        # If we have fewer label sets than desired population size, 
        # duplicate some (they'll be re-evaluated each time anyway)
        while len(population) < self.config.population_size and self.available_label_sets:
            for label_set in self.available_label_sets:
                if len(population) >= self.config.population_size:
                    break
                individual = LabelSetIndividual(label_set_name=label_set)
                population.append(individual)
        
        return population
    
    def _evaluate_population(self, population: List[LabelSetIndividual]):
        """Evaluate fitness for all individuals in population"""
        for i, individual in enumerate(population):
            logger.debug(f"Evaluating individual {i+1}/{len(population)}: {individual.label_set_name}")
            
            performance = self.evaluate_label_set(individual.label_set_name)
            
            # Update individual with performance metrics
            individual.f1_score = performance['f1_score']
            individual.precision = performance['precision']
            individual.recall = performance['recall']
            individual.performance_ms = performance['avg_response_time_ms']
            individual.category_performance = performance.get('category_performance', {})
            
            # Calculate composite fitness (weighted F1 score with response time penalty)
            time_penalty = max(0, (performance['avg_response_time_ms'] - self.config.performance_target_ms) / 1000)
            individual.fitness = performance['f1_score'] - (time_penalty * 0.1)  # 10% penalty per second over target
            
            logger.debug(f"   F1: {individual.f1_score:.3f}, Fitness: {individual.fitness:.3f}")
    
    def _create_next_generation(self, population: List[LabelSetIndividual]) -> List[LabelSetIndividual]:
        """Create next generation for discrete label set optimization"""
        # For discrete optimization, we mostly re-evaluate the same label sets
        # but we can introduce some variation by changing the evaluation order
        # and potentially re-running some evaluations
        
        # Sort by fitness
        population.sort(key=lambda ind: ind.fitness, reverse=True)
        
        # Keep the best performers and add some random re-evaluations
        next_generation = []
        
        # Keep top 50% 
        top_half = population[:len(population)//2]
        next_generation.extend(top_half)
        
        # Add random selections from available label sets for re-evaluation
        remaining_slots = self.config.population_size - len(next_generation)
        for _ in range(remaining_slots):
            label_set = np.random.choice(self.available_label_sets)
            individual = LabelSetIndividual(label_set_name=label_set)
            next_generation.append(individual)
        
        return next_generation
    
    def save_results(self, optimization_results: Dict[str, Any], results_dir: str = "./results") -> str:
        """Save optimization results to file"""
        results_path = Path(results_dir)
        results_path.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"label_optimization_results_{timestamp}.json"
        filepath = results_path / filename
        
        # Add metadata
        results_with_metadata = {
            "metadata": {
                "optimization_type": "zero_shot_label_sets",
                "timestamp": timestamp,
                "total_label_sets_evaluated": len(self.available_label_sets),
                "test_phrases": len(self.all_test_data),
                "categories": list(self.test_dataset.keys())
            },
            "configuration": {
                "population_size": self.config.population_size,
                "generations": self.config.generations,
                "mutation_rate": self.config.mutation_rate,
                "crossover_rate": self.config.crossover_rate,
                "improvement_threshold": self.config.improvement_threshold
            },
            "results": optimization_results
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_with_metadata, f, indent=2)
        
        logger.info(f"💾 Optimization results saved to: {filepath}")
        return str(filepath)


def create_label_set_optimizer(unified_config, test_dataset: Dict[str, List[Dict]], 
                              config: LabelOptimizationConfiguration) -> LabelSetOptimizer:
    """Factory function to create LabelSetOptimizer following Clean Architecture patterns"""
    logger.info("🏗️ Creating LabelSetOptimizer with clean architecture patterns...")
    
    try:
        optimizer = LabelSetOptimizer(unified_config, test_dataset, config)
        logger.info("✅ LabelSetOptimizer created successfully")
        return optimizer
        
    except Exception as e:
        logger.error(f"❌ Failed to create LabelSetOptimizer: {e}")
        raise


# Export key classes and functions
__all__ = [
    'LabelSetOptimizer',
    'LabelSetIndividual', 
    'LabelOptimizationConfiguration',
    'create_label_set_optimizer'
]