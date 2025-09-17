# ash-thrash/managers/results_manager.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Results Storage and Analysis Manager for Ash-Thrash Service
---
FILE VERSION: v3.1-1a-1
LAST MODIFIED: 2025-08-30
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class TestRunSummary:
    """Summary data for a test run"""
    run_id: str
    timestamp: float
    total_phrases: int
    total_passed: int
    total_failed: int
    total_errors: int
    overall_pass_rate: float
    weighted_safety_score: float
    execution_time_ms: float
    categories_tested: List[str]
    early_termination: bool
    termination_reason: Optional[str]
    server_version: Optional[str]

@dataclass
class CategorySummary:
    """Summary data for a category within a test run"""
    category_name: str
    pass_rate: float
    target_pass_rate: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    false_negatives: int
    false_positives: int
    weighted_score: float
    is_critical: bool
    met_target: bool

class ResultsManager:
    """
    Results Storage and Analysis Manager for Ash-Thrash testing suite
    
    Handles test result storage, historical tracking, summary generation,
    and basic performance analysis with Clean Architecture patterns.
    """
    
    def __init__(self, unified_config_manager):
        """
        Initialize Results Manager
        
        Args:
            unified_config_manager: UnifiedConfigManager instance for configuration
        """
        self.unified_config = unified_config_manager
        
        try:
            # Load storage configuration
            self.storage_config = self.unified_config.get_config_section('test_settings', 'storage', {})
            
            self.results_dir = Path(self.storage_config.get('results_directory', './results'))
            self.reports_dir = Path(self.storage_config.get('reports_directory', './reports'))
            self.timestamp_format = self.storage_config.get('timestamp_format', '%Y-%m-%d_%H-%M-%S')
            
            # Create directories if they don't exist
            self._ensure_directories_exist()
            
            logger.info(f"ResultsManager initialized: results_dir={self.results_dir}, reports_dir={self.reports_dir}")
            
        except Exception as e:
            logger.error(f"Error initializing ResultsManager: {e}")
            raise
    
    def _ensure_directories_exist(self):
        """Create necessary directories if they don't exist"""
        try:
            # Create main directories
            self.results_dir.mkdir(parents=True, exist_ok=True)
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self.results_dir / 'test_runs').mkdir(exist_ok=True)
            (self.results_dir / 'historical').mkdir(exist_ok=True)
            (self.results_dir / 'backups').mkdir(exist_ok=True)
            
            logger.debug("All necessary directories created or verified")
            
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise
    
    def store_test_results(self, suite_result) -> str:
        """
        Store test suite results to JSON files with comprehensive metadata
        
        Args:
            suite_result: TestSuiteResult from test execution
            
        Returns:
            String path to the stored results directory
        """
        try:
            # Create timestamped directory for this test run
            timestamp = datetime.fromtimestamp(suite_result.start_time)
            run_dir_name = timestamp.strftime(self.timestamp_format)
            run_dir = self.results_dir / 'test_runs' / run_dir_name
            run_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique run ID
            run_id = f"thrash_{run_dir_name}_{int(suite_result.start_time * 1000) % 100000}"
            
            # Store raw results (complete data)
            raw_results_path = run_dir / 'raw_results.json'
            raw_results = {
                'run_metadata': {
                    'run_id': run_id,
                    'timestamp': suite_result.start_time,
                    'execution_time_ms': suite_result.total_execution_time_ms,
                    'thrash_version': 'v3.1-1a-1'
                },
                'suite_summary': {
                    'categories_tested': suite_result.categories_tested,
                    'total_phrases': suite_result.total_phrases,
                    'total_passed': suite_result.total_passed,
                    'total_failed': suite_result.total_failed,
                    'total_errors': suite_result.total_errors,
                    'overall_pass_rate': suite_result.overall_pass_rate,
                    'weighted_safety_score': suite_result.weighted_safety_score,
                    'early_termination': suite_result.early_termination,
                    'termination_reason': suite_result.termination_reason
                },
                'server_info': suite_result.server_info,
                'category_results': []
            }
            
            # Store category results with phrase details
            for category_result in suite_result.category_results:
                category_data = {
                    'category_name': category_result.category_name,
                    'category_file': category_result.category_file,
                    'expected_priorities': category_result.expected_priorities,
                    'target_pass_rate': category_result.target_pass_rate,
                    'is_critical': category_result.is_critical,
                    'statistics': {
                        'total_tests': category_result.total_tests,
                        'passed_tests': category_result.passed_tests,
                        'failed_tests': category_result.failed_tests,
                        'error_tests': category_result.error_tests,
                        'pass_rate': category_result.pass_rate,
                        'weighted_score': category_result.weighted_score,
                        'false_negatives': category_result.false_negatives,
                        'false_positives': category_result.false_positives,
                        'execution_time_ms': category_result.execution_time_ms
                    },
                    'phrase_results': []
                }
                
                # Store individual phrase results
                for phrase_result in category_result.phrase_results:
                    phrase_data = {
                        'phrase_id': phrase_result.phrase_id,
                        'message': phrase_result.message,
                        'expected_priorities': phrase_result.expected_priorities,
                        'actual_priority': phrase_result.actual_priority,
                        'confidence_score': phrase_result.confidence_score,
                        'crisis_score': phrase_result.crisis_score,
                        'processing_time_ms': phrase_result.processing_time_ms,
                        'result': phrase_result.result.value,
                        'failure_severity': phrase_result.failure_severity,
                        'is_false_negative': phrase_result.is_false_negative,
                        'is_false_positive': phrase_result.is_false_positive,
                        'error_message': phrase_result.error_message
                        # Note: analysis_data excluded to keep file size manageable
                    }
                    category_data['phrase_results'].append(phrase_data)
                
                raw_results['category_results'].append(category_data)
            
            # Write raw results
            with open(raw_results_path, 'w', encoding='utf-8') as f:
                json.dump(raw_results, f, indent=2)
            
            logger.info(f"Raw results stored: {raw_results_path}")
            
            # Generate and store summary report
            self._generate_summary_report(suite_result, run_dir, run_id)
            
            # Update historical tracking
            self._update_historical_data(suite_result, run_id)
            
            logger.info(f"Test results stored successfully: {run_dir}")
            return str(run_dir)
            
        except Exception as e:
            logger.error(f"Error storing test results: {e}")
            raise
    
    def _generate_summary_report(self, suite_result, run_dir: Path, run_id: str):
        """Generate human-readable summary report"""
        try:
            summary_path = run_dir / 'summary_report.json'
            
            # Create test run summary
            run_summary = TestRunSummary(
                run_id=run_id,
                timestamp=suite_result.start_time,
                total_phrases=suite_result.total_phrases,
                total_passed=suite_result.total_passed,
                total_failed=suite_result.total_failed,
                total_errors=suite_result.total_errors,
                overall_pass_rate=suite_result.overall_pass_rate,
                weighted_safety_score=suite_result.weighted_safety_score,
                execution_time_ms=suite_result.total_execution_time_ms,
                categories_tested=[cat.category_name for cat in suite_result.category_results] if suite_result.category_results else [],
                early_termination=suite_result.early_termination,
                termination_reason=suite_result.termination_reason,
                server_version=suite_result.server_info.get('health_status', {}).get('version') if suite_result.server_info else None
            )
            
            # Create category summaries
            category_summaries = []
            for category_result in suite_result.category_results:
                category_summary = CategorySummary(
                    category_name=category_result.category_name,
                    pass_rate=category_result.pass_rate,
                    target_pass_rate=int(category_result.target_pass_rate),
                    total_tests=category_result.total_tests,
                    passed_tests=category_result.passed_tests,
                    failed_tests=category_result.failed_tests,
                    error_tests=category_result.error_tests,
                    false_negatives=category_result.false_negatives,
                    false_positives=category_result.false_positives,
                    weighted_score=category_result.weighted_score,
                    is_critical=category_result.is_critical,
                    met_target=category_result.pass_rate >= float(category_result.target_pass_rate)
                )
                category_summaries.append(category_summary)
            
            # Build summary data structure
            summary_data = {
                'run_summary': asdict(run_summary),
                'category_summaries': [asdict(cs) for cs in category_summaries],
                'performance_analysis': self._analyze_performance(suite_result),
                'recommendations': self._generate_basic_recommendations(suite_result)
            }
            
            # Write summary report
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2)
            
            logger.info(f"Summary report generated: {summary_path}")
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
    
    def _analyze_performance(self, suite_result) -> Dict[str, Any]:
        """Analyze test performance and identify issues"""
        try:
            logger.debug("Starting performance analysis...")

            analysis = {
                'overall_status': 'pass' if suite_result.overall_pass_rate >= 85.0 else 'fail',
                'safety_assessment': 'acceptable' if suite_result.weighted_safety_score <= 1.0 else 'needs_attention',
                'critical_failures': [],
                'performance_issues': [],
                'strengths': []
            }
            
            # Analyze each category
            for category_result in suite_result.category_results:
                category_name = category_result.category_name
                pass_rate = float(category_result.pass_rate)
                target = float(category_result.target_pass_rate)
                    
                logger.debug(f"Category: {category_name}, pass_rate type: {type(pass_rate)}, target type: {type(target)}")
                logger.debug(f"Values: pass_rate={pass_rate}, target={target}")

                # Critical failures
                if category_result.is_critical and pass_rate < target:
                    analysis['critical_failures'].append({
                        'category': category_name,
                        'pass_rate': pass_rate,
                        'target': target,
                        'gap': float(target) - pass_rate,
                        'false_negatives': category_result.false_negatives
                    })
                
                # Performance issues
                if pass_rate < float(target) - 10:  # More than 10% below target
                    analysis['performance_issues'].append({
                        'category': category_name,
                        'pass_rate': pass_rate,
                        'target': target,
                        'issue_type': 'significantly_below_target'
                    })
                elif category_result.false_negatives > 0:
                    analysis['performance_issues'].append({
                        'category': category_name,
                        'false_negatives': category_result.false_negatives,
                        'issue_type': 'false_negatives_detected'
                    })
                
                # Strengths
                if pass_rate >= float(target) + 5:  # 5% above target
                    analysis['strengths'].append({
                        'category': category_name,
                        'pass_rate': pass_rate,
                        'target': target,
                        'strength_type': 'exceeds_target'
                    })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {}
    
    def _generate_basic_recommendations(self, suite_result) -> List[Dict[str, Any]]:
        """Generate basic tuning recommendations based on test results"""
        try:
            recommendations = []
            
            for category_result in suite_result.category_results:
                category_name = category_result.category_name
                pass_rate = float(category_result.pass_rate)
                target = float(category_result.target_pass_rate)
                
                # High priority recommendations for critical categories
                if category_result.is_critical and pass_rate < float(target):
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': category_name,
                        'issue': f"Critical category below target: {pass_rate:.1f}% (need {target}%)",
                        'recommendation': f"Consider lowering thresholds for {category_name} detection",
                        'confidence': 'medium'
                    })
                
                # False negative recommendations
                if category_result.false_negatives > 0:
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'category': category_name,
                        'issue': f"{category_result.false_negatives} false negatives detected",
                        'recommendation': "Review threshold settings to reduce false negatives",
                        'confidence': 'high'
                    })
                
                # False positive recommendations
                if category_result.false_positives > (category_result.total_tests * 0.1):  # >10% false positives
                    recommendations.append({
                        'priority': 'LOW',
                        'category': category_name,
                        'issue': f"{category_result.false_positives} false positives detected",
                        'recommendation': "Consider raising thresholds to reduce false positives",
                        'confidence': 'medium'
                    })
            
            # Overall system recommendations
            if suite_result.overall_pass_rate < 80.0:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'SYSTEM',
                    'issue': f"Overall pass rate critically low: {suite_result.overall_pass_rate:.1f}%",
                    'recommendation': "Comprehensive threshold review required",
                    'confidence': 'high'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _update_historical_data(self, suite_result, run_id: str):
        """Update historical performance tracking"""
        try:
            historical_file = self.results_dir / 'historical' / 'performance_trends.json'
            
            # Load existing historical data
            historical_data = {'test_runs': []}
            if historical_file.exists():
                try:
                    with open(historical_file, 'r', encoding='utf-8') as f:
                        historical_data = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Historical data file corrupted, starting fresh")
            
            # Add this test run to history
            run_entry = {
                'run_id': run_id,
                'timestamp': suite_result.start_time,
                'overall_pass_rate': suite_result.overall_pass_rate,
                'weighted_safety_score': suite_result.weighted_safety_score,
                'total_phrases': suite_result.total_phrases,
                'execution_time_ms': suite_result.total_execution_time_ms,
                'early_termination': suite_result.early_termination,
                'server_version': suite_result.server_info.get('health_status', {}).get('version') if suite_result.server_info else None,
                'category_performance': {}
            }
            
            # Add category performance data
            for category_result in suite_result.category_results:
                run_entry['category_performance'][category_result.category_name] = {
                    'pass_rate': category_result.pass_rate,
                    'target_pass_rate': category_result.target_pass_rate,
                    'false_negatives': category_result.false_negatives,
                    'false_positives': category_result.false_positives,
                    'met_target': category_result.pass_rate >= float(category_result.target_pass_rate)
                }
            
            # Add to historical data (keep last 100 runs)
            historical_data['test_runs'].append(run_entry)
            historical_data['test_runs'] = historical_data['test_runs'][-100:]  # Keep last 100 runs
            
            # Update metadata
            historical_data['last_updated'] = time.time()
            historical_data['total_runs'] = len(historical_data['test_runs'])
            
            # Write updated historical data
            with open(historical_file, 'w', encoding='utf-8') as f:
                json.dump(historical_data, f, indent=2)
            
            logger.debug(f"Historical data updated: {len(historical_data['test_runs'])} total runs")
            
        except Exception as e:
            logger.error(f"Error updating historical data: {e}")
    
    def get_latest_results(self) -> Optional[Dict[str, Any]]:
        """Get the most recent test results"""
        try:
            test_runs_dir = self.results_dir / 'test_runs'
            
            if not test_runs_dir.exists():
                return None
            
            # Find most recent test run directory
            run_dirs = [d for d in test_runs_dir.iterdir() if d.is_dir()]
            if not run_dirs:
                return None
            
            latest_dir = max(run_dirs, key=os.path.getctime)
            summary_file = latest_dir / 'summary_report.json'
            
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest results: {e}")
            return None
    
    def get_historical_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get historical performance trends"""
        try:
            historical_file = self.results_dir / 'historical' / 'performance_trends.json'
            
            if not historical_file.exists():
                return {'test_runs': [], 'trends': {}}
            
            with open(historical_file, 'r', encoding='utf-8') as f:
                historical_data = json.load(f)
            
            # Filter by date if requested
            if days > 0:
                cutoff_time = time.time() - (days * 24 * 60 * 60)
                filtered_runs = [
                    run for run in historical_data.get('test_runs', [])
                    if run['timestamp'] >= cutoff_time
                ]
                historical_data['test_runs'] = filtered_runs
            
            # Calculate trends
            runs = historical_data.get('test_runs', [])
            if len(runs) >= 2:
                latest = runs[-1]
                previous = runs[-2]
                
                trends = {
                    'overall_pass_rate_trend': latest['overall_pass_rate'] - previous['overall_pass_rate'],
                    'safety_score_trend': latest['weighted_safety_score'] - previous['weighted_safety_score'],
                    'execution_time_trend': latest['execution_time_ms'] - previous['execution_time_ms'],
                    'total_runs_analyzed': len(runs)
                }
                historical_data['trends'] = trends
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical trends: {e}")
            return {'test_runs': [], 'trends': {}}
    
    def cleanup_old_results(self, keep_days: int = 30) -> int:
        """Clean up old test results to save disk space"""
        try:
            cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
            test_runs_dir = self.results_dir / 'test_runs'
            
            if not test_runs_dir.exists():
                return 0
            
            removed_count = 0
            
            for run_dir in test_runs_dir.iterdir():
                if run_dir.is_dir():
                    dir_mtime = os.path.getmtime(run_dir)
                    if dir_mtime < cutoff_time:
                        # Move to backup before deletion
                        backup_dir = self.results_dir / 'backups' / run_dir.name
                        backup_dir.parent.mkdir(exist_ok=True)
                        run_dir.rename(backup_dir)
                        removed_count += 1
                        logger.debug(f"Moved old results to backup: {run_dir.name}")
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old test result directories")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old results: {e}")
            return 0

def create_results_manager(unified_config_manager) -> ResultsManager:
    """
    Factory function for ResultsManager (Clean v3.1 Pattern)
    
    Args:
        unified_config_manager: UnifiedConfigManager instance
        
    Returns:
        Initialized ResultsManager instance
        
    Raises:
        ValueError: If unified_config_manager is None or invalid
    """
    logger.debug("Creating ResultsManager with Clean v3.1 architecture")
    
    if not unified_config_manager:
        raise ValueError("UnifiedConfigManager is required for ResultsManager factory")
    
    return ResultsManager(unified_config_manager)

# Export public interface
__all__ = ['ResultsManager', 'TestRunSummary', 'CategorySummary', 'create_results_manager']

logger.info("ResultsManager v3.1-1a-1 loaded")