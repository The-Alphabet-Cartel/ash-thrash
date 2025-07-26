"""
Results Processor for Ash-Thrash Testing

Processes test results, calculates metrics, analyzes performance,
and generates insights for crisis detection testing.
"""

import json
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import os


@dataclass
class CategoryAnalysis:
    """Analysis results for a specific test category"""
    category: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    target_rate: float
    goal_met: bool
    avg_confidence: float
    avg_response_time: float
    failures: List[Dict[str, Any]]


@dataclass
class OverallAnalysis:
    """Overall test analysis results"""
    total_tests: int
    total_passed: int
    total_failed: int
    total_errors: int
    overall_pass_rate: float
    avg_response_time: float
    avg_processing_time: float
    execution_time: float
    goals_achieved: int
    total_goals: int
    goal_achievement_rate: float


class ResultsProcessor:
    """Processes and analyzes test results"""
    
    def __init__(self, testing_goals: Optional[Dict[str, Any]] = None):
        """
        Initialize results processor
        
        Args:
            testing_goals: Dictionary of testing goals and targets
        """
        self.testing_goals = testing_goals or self._get_default_goals()
    
    def process_results(self, results: List[Dict[str, Any]], execution_time: float = 0.0) -> Dict[str, Any]:
        """
        Process a list of test results and generate comprehensive analysis
        
        Args:
            results: List of test results from comprehensive testing
            execution_time: Total test execution time in seconds
            
        Returns:
            dict: Comprehensive analysis results
        """
        if not results:
            return self._empty_analysis()
        
        # Overall analysis
        overall = self._analyze_overall_performance(results, execution_time)
        
        # Category-specific analysis
        categories = self._analyze_by_category(results)
        
        # Goal achievement analysis
        goal_analysis = self._analyze_goal_achievement(categories)
        
        # Performance metrics
        performance = self._calculate_performance_metrics(results)
        
        # Failure analysis
        failures = self._analyze_failures(results)
        
        # Confidence distribution
        confidence_dist = self._analyze_confidence_distribution(results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_results": overall.__dict__,
            "category_results": {cat.category: self._category_to_dict(cat) for cat in categories.values()},
            "goal_achievement": goal_analysis,
            "performance_metrics": performance,
            "failure_analysis": failures,
            "confidence_distribution": confidence_dist,
            "summary": self._generate_summary(overall, goal_analysis)
        }
    
    def _analyze_overall_performance(self, results: List[Dict[str, Any]], execution_time: float) -> OverallAnalysis:
        """Analyze overall test performance"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('passed', False))
        failed_tests = sum(1 for r in results if not r.get('passed', False) and not r.get('error_message'))
        error_tests = sum(1 for r in results if r.get('error_message'))
        
        # Response times (excluding errors)
        valid_results = [r for r in results if not r.get('error_message')]
        avg_response_time = statistics.mean([r.get('response_time_ms', 0) for r in valid_results]) if valid_results else 0
        avg_processing_time = statistics.mean([r.get('processing_time_ms', 0) for r in valid_results if r.get('processing_time_ms', 0) > 0]) if valid_results else 0
        
        # Goal achievement
        categories = self._analyze_by_category(results)
        goals_achieved = sum(1 for cat in categories.values() if cat.goal_met)
        total_goals = len(categories)
        
        return OverallAnalysis(
            total_tests=total_tests,
            total_passed=passed_tests,
            total_failed=failed_tests,
            total_errors=error_tests,
            overall_pass_rate=(passed_tests / total_tests * 100) if total_tests > 0 else 0,
            avg_response_time=avg_response_time,
            avg_processing_time=avg_processing_time,
            execution_time=execution_time,
            goals_achieved=goals_achieved,
            total_goals=total_goals,
            goal_achievement_rate=(goals_achieved / total_goals * 100) if total_goals > 0 else 0
        )
    
    def _analyze_by_category(self, results: List[Dict[str, Any]]) -> Dict[str, CategoryAnalysis]:
        """Analyze results by test category"""
        category_data = {}
        
        # Group results by category
        for result in results:
            phrase = result.get('phrase', {})
            category = phrase.get('category', 'unknown')
            
            if category not in category_data:
                category_data[category] = []
            category_data[category].append(result)
        
        # Analyze each category
        category_analyses = {}
        for category, cat_results in category_data.items():
            category_analyses[category] = self._analyze_single_category(category, cat_results)
        
        return category_analyses
    
    def _analyze_single_category(self, category: str, results: List[Dict[str, Any]]) -> CategoryAnalysis:
        """Analyze results for a single category"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('passed', False))
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Get target rate from goals
        target_rate = self.testing_goals.get(category, {}).get('target_pass_rate', 0)
        goal_met = pass_rate >= target_rate
        
        # Calculate averages (excluding errors)
        valid_results = [r for r in results if not r.get('error_message')]
        avg_confidence = statistics.mean([r.get('confidence_score', 0) for r in valid_results]) if valid_results else 0
        avg_response_time = statistics.mean([r.get('response_time_ms', 0) for r in valid_results]) if valid_results else 0
        
        # Collect failures
        failures = []
        for result in results:
            if not result.get('passed', False) and not result.get('error_message'):
                phrase = result.get('phrase', {})
                failures.append({
                    'message': phrase.get('message', ''),
                    'expected': phrase.get('expected_priority', ''),
                    'detected': result.get('detected_priority', ''),
                    'confidence': result.get('confidence_score', 0),
                    'description': phrase.get('description', '')
                })
        
        return CategoryAnalysis(
            category=category,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            pass_rate=pass_rate,
            target_rate=target_rate,
            goal_met=goal_met,
            avg_confidence=avg_confidence,
            avg_response_time=avg_response_time,
            failures=failures
        )
    
    def _analyze_goal_achievement(self, categories: Dict[str, CategoryAnalysis]) -> Dict[str, Any]:
        """Analyze goal achievement across all categories"""
        goal_analysis = {}
        goals_achieved = 0
        total_goals = len(categories)
        
        for category, analysis in categories.items():
            goal_info = self.testing_goals.get(category, {})
            
            goal_analysis[category] = {
                'description': goal_info.get('description', category),
                'target_rate': analysis.target_rate,
                'actual_rate': analysis.pass_rate,
                'goal_met': analysis.goal_met,
                'difference': analysis.pass_rate - analysis.target_rate,
                'critical': goal_info.get('critical', False),
                'status': '✅ ACHIEVED' if analysis.goal_met else '❌ MISSED'
            }
            
            if analysis.goal_met:
                goals_achieved += 1
        
        # Overall goal achievement
        achievement_rate = (goals_achieved / total_goals * 100) if total_goals > 0 else 0
        overall_status = "🎯 ALL GOALS MET" if goals_achieved == total_goals else f"⚠️ {goals_achieved}/{total_goals} GOALS MET"
        
        goal_analysis['summary'] = {
            'goals_achieved': goals_achieved,
            'total_goals': total_goals,
            'achievement_rate': achievement_rate,
            'overall_status': overall_status
        }
        
        return goal_analysis
    
    def _calculate_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed performance metrics"""
        valid_results = [r for r in results if not r.get('error_message')]
        
        if not valid_results:
            return {'error': 'No valid results for performance analysis'}
        
        response_times = [r.get('response_time_ms', 0) for r in valid_results]
        processing_times = [r.get('processing_time_ms', 0) for r in valid_results if r.get('processing_time_ms', 0) > 0]
        confidence_scores = [r.get('confidence_score', 0) for r in valid_results]
        
        return {
            'response_time': {
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0,
                'mean': statistics.mean(response_times) if response_times else 0,
                'median': statistics.median(response_times) if response_times else 0,
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            'processing_time': {
                'min': min(processing_times) if processing_times else 0,
                'max': max(processing_times) if processing_times else 0,
                'mean': statistics.mean(processing_times) if processing_times else 0,
                'median': statistics.median(processing_times) if processing_times else 0,
                'std_dev': statistics.stdev(processing_times) if len(processing_times) > 1 else 0
            },
            'confidence': {
                'min': min(confidence_scores) if confidence_scores else 0,
                'max': max(confidence_scores) if confidence_scores else 0,
                'mean': statistics.mean(confidence_scores) if confidence_scores else 0,
                'median': statistics.median(confidence_scores) if confidence_scores else 0,
                'std_dev': statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 0
            },
            'error_rate': (len(results) - len(valid_results)) / len(results) * 100 if results else 0
        }
    
    def _analyze_failures(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze failure patterns and critical issues"""
        failures = [r for r in results if not r.get('passed', False) and not r.get('error_message')]
        
        # Critical failures (high priority or false positives)
        critical_failures = []
        for result in failures:
            phrase = result.get('phrase', {})
            category = phrase.get('category', '')
            expected = phrase.get('expected_priority', '')
            detected = result.get('detected_priority', '')
            
            # High priority misses are critical
            if expected == 'high':
                critical_failures.append({
                    'type': 'high_priority_miss',
                    'message': phrase.get('message', ''),
                    'expected': expected,
                    'detected': detected,
                    'confidence': result.get('confidence_score', 0)
                })
            
            # False positives are critical
            elif expected == 'none' and detected != 'none':
                critical_failures.append({
                    'type': 'false_positive',
                    'message': phrase.get('message', ''),
                    'expected': expected,
                    'detected': detected,
                    'confidence': result.get('confidence_score', 0)
                })
        
        # Failure patterns by category
        failure_by_category = {}
        for result in failures:
            phrase = result.get('phrase', {})
            category = phrase.get('category', 'unknown')
            if category not in failure_by_category:
                failure_by_category[category] = 0
            failure_by_category[category] += 1
        
        return {
            'total_failures': len(failures),
            'critical_failures': len(critical_failures),
            'critical_failure_details': critical_failures,
            'failure_by_category': failure_by_category,
            'failure_rate_by_category': {
                cat: (count / len([r for r in results if r.get('phrase', {}).get('category') == cat]) * 100)
                for cat, count in failure_by_category.items()
            }
        }
    
    def _analyze_confidence_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze confidence score distribution"""
        valid_results = [r for r in results if not r.get('error_message') and r.get('confidence_score') is not None]
        
        if not valid_results:
            return {'error': 'No valid confidence scores'}
        
        confidences = [r.get('confidence_score', 0) for r in valid_results]
        
        # Distribution ranges
        ranges = {
            '0.0-0.2': sum(1 for c in confidences if 0.0 <= c < 0.2),
            '0.2-0.4': sum(1 for c in confidences if 0.2 <= c < 0.4),
            '0.4-0.6': sum(1 for c in confidences if 0.4 <= c < 0.6),
            '0.6-0.8': sum(1 for c in confidences if 0.6 <= c < 0.8),
            '0.8-1.0': sum(1 for c in confidences if 0.8 <= c <= 1.0)
        }
        
        return {
            'total_samples': len(confidences),
            'min': min(confidences),
            'max': max(confidences),
            'mean': statistics.mean(confidences),
            'median': statistics.median(confidences),
            'std_dev': statistics.stdev(confidences) if len(confidences) > 1 else 0,
            'distribution_ranges': ranges,
            'distribution_percentages': {
                range_name: (count / len(confidences) * 100) for range_name, count in ranges.items()
            }
        }
    
    def _generate_summary(self, overall: OverallAnalysis, goal_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate human-readable summary"""
        summary = {
            'overall_status': '',
            'key_findings': [],
            'recommendations': []
        }
        
        # Overall status
        if overall.goal_achievement_rate >= 85:
            summary['overall_status'] = '🎯 Excellent Performance - System Ready'
        elif overall.goal_achievement_rate >= 70:
            summary['overall_status'] = '⚠️ Good Performance - Minor Improvements Needed'
        else:
            summary['overall_status'] = '🚨 Performance Issues - System Needs Attention'
        
        # Key findings
        summary['key_findings'].append(f"Overall pass rate: {overall.overall_pass_rate:.1f}%")
        summary['key_findings'].append(f"Goals achieved: {overall.goals_achieved}/{overall.total_goals}")
        summary['key_findings'].append(f"Average response time: {overall.avg_response_time:.1f}ms")
        
        if overall.total_errors > 0:
            summary['key_findings'].append(f"⚠️ {overall.total_errors} test errors occurred")
        
        # Recommendations
        if overall.goal_achievement_rate < 85:
            summary['recommendations'].append("Review failed test categories for improvement opportunities")
        
        if overall.avg_response_time > 200:
            summary['recommendations'].append("Consider performance optimization - response time exceeds 200ms")
        
        if overall.total_errors > overall.total_tests * 0.05:  # More than 5% errors
            summary['recommendations'].append("Investigate server stability - high error rate detected")
        
        return summary
    
    def _category_to_dict(self, category: CategoryAnalysis) -> Dict[str, Any]:
        """Convert CategoryAnalysis to dictionary"""
        return {
            'total_tests': category.total_tests,
            'passed_tests': category.passed_tests,
            'failed_tests': category.failed_tests,
            'pass_rate': category.pass_rate,
            'target_rate': category.target_rate,
            'goal_met': category.goal_met,
            'avg_confidence': category.avg_confidence,
            'avg_response_time': category.avg_response_time,
            'failures': category.failures
        }
    
    def _get_default_goals(self) -> Dict[str, Any]:
        """Get default testing goals"""
        return {
            'definite_high': {'target_pass_rate': 100.0, 'critical': True, 'description': 'High Priority Crisis'},
            'definite_medium': {'target_pass_rate': 65.0, 'critical': False, 'description': 'Medium Priority Crisis'},
            'definite_low': {'target_pass_rate': 65.0, 'critical': False, 'description': 'Low Priority Crisis'},
            'definite_none': {'target_pass_rate': 95.0, 'critical': True, 'description': 'No Priority Crisis'},
            'maybe_high_medium': {'target_pass_rate': 90.0, 'critical': False, 'description': 'Maybe High/Medium'},
            'maybe_medium_low': {'target_pass_rate': 80.0, 'critical': False, 'description': 'Maybe Medium/Low'},
            'maybe_low_none': {'target_pass_rate': 90.0, 'critical': True, 'description': 'Maybe Low/None'}
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_results': {
                'total_tests': 0,
                'overall_pass_rate': 0,
                'error': 'No results to analyze'
            },
            'category_results': {},
            'goal_achievement': {'summary': {'goals_achieved': 0, 'total_goals': 0}},
            'performance_metrics': {},
            'failure_analysis': {},
            'confidence_distribution': {},
            'summary': {'overall_status': '❌ No Data Available'}
        }


def load_and_process_results(results_file: str, goals_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load results from file and process them
    
    Args:
        results_file: Path to results JSON file
        goals_file: Optional path to goals configuration file
        
    Returns:
        dict: Processed results analysis
    """
    # Load testing goals if provided
    goals = None
    if goals_file and os.path.exists(goals_file):
        with open(goals_file, 'r') as f:
            goals_data = json.load(f)
            goals = goals_data.get('goals', {})
    
    # Load results
    with open(results_file, 'r') as f:
        results_data = json.load(f)
    
    # Extract results list and execution time
    if 'detailed_results' in results_data:
        results = results_data['detailed_results']
        execution_time = results_data.get('test_metadata', {}).get('total_execution_time_seconds', 0)
    else:
        results = results_data
        execution_time = 0
    
    # Process results
    processor = ResultsProcessor(goals)
    return processor.process_results(results, execution_time)