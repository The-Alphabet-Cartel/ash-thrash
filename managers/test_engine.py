# ash-thrash/managers/test_engine.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Core Test Execution Engine for Ash-Thrash Service
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
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# ========================================================================
# CLASS SETUP
# ========================================================================
class TestResult(Enum):
    """Test result enumeration"""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIP = "skip"

@dataclass
class PhraseTestResult:
    """Individual phrase test result"""
    phrase_id: str
    message: str
    expected_priorities: List[str]
    actual_priority: str
    confidence_score: float
    processing_time_ms: float
    result: TestResult
    failure_severity: int = 0  # 0 = pass, 1-3 = severity levels
    is_false_negative: bool = False
    is_false_positive: bool = False
    error_message: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None

@dataclass 
class CategoryTestResult:
    """Test category result summary"""
    category_name: str
    category_file: str
    expected_priorities: List[str]
    target_pass_rate: int
    is_critical: bool
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    pass_rate: float = 0.0
    weighted_score: float = 0.0
    false_negatives: int = 0
    false_positives: int = 0
    phrase_results: List[PhraseTestResult] = field(default_factory=list)
    execution_time_ms: float = 0.0

@dataclass
class TestSuiteResult:
    """Complete test suite result"""
    start_time: float
    end_time: float
    total_execution_time_ms: float
    categories_tested: int
    total_phrases: int
    total_passed: int
    total_failed: int
    total_errors: int
    overall_pass_rate: float
    weighted_safety_score: float
    early_termination: bool
    termination_reason: Optional[str]
    category_results: List[CategoryTestResult] = field(default_factory=list)
    server_info: Optional[Dict[str, Any]] = None
# ========================================================================

# ========================================================================
# TestEngineMananger
# ========================================================================
class TestEngineManager:
    """
    Core test execution engine for Ash-Thrash testing suite
    
    Handles phrase loading, test execution, result calculation,
    and safety-first failure analysis with early termination.
    """
    
    # ========================================================================
    # INITIALIZE
    # ========================================================================
    def __init__(self, unified_config_manager, nlp_client_manager):
        """
        Initialize Test Engine Manager
        
        Args:
            unified_config_manager: UnifiedConfigManager instance
            nlp_client_manager: NLPClientManager instance
        """
        self.unified_config = unified_config_manager
        self.nlp_client = nlp_client_manager
        
        try:
            # Load test configuration
            self.test_config = self.unified_config.get_config_section('test_settings', 'test_execution', {})
            self.category_config = self.unified_config.get_config_section('test_settings', 'test_categories', {})
            self.failure_config = self.unified_config.get_config_section('test_settings', 'failure_weighting', {})
            self.storage_config = self.unified_config.get_config_section('test_settings', 'storage', {})
            
            # Extract configuration values
            self.max_concurrent = self.test_config.get('max_concurrent_tests', 3)
            self.test_delay_ms = self.test_config.get('test_delay_ms', 500)
            self.failure_halt_threshold = self.test_config.get('failure_halt_threshold', 60)
            self.progress_interval = self.test_config.get('progress_report_interval', 10)
            self.enable_early_termination = self.test_config.get('enable_early_termination', True)
            self.test_user_id = self.test_config.get('test_user_id', 'ash_thrash_test')
            self.test_channel_id = self.test_config.get('test_channel_id', 'testing_channel')
            
            # Failure weighting configuration
            self.false_negative_multiplier = self.failure_config.get('false_negative_multiplier', 3.0)
            self.severity_weights = self.failure_config.get('severity_weights', {
                '1_level_miss': 1.0,
                '2_level_miss': 2.0, 
                '3_level_miss': 3.0
            })
            self.critical_multiplier = self.failure_config.get('critical_category_multiplier', 1.5)
            
            # Storage configuration
            self.phrases_dir = Path(self.storage_config.get('phrase_files_directory', './config/phrases'))
            
            # Priority level mapping for severity calculation
            self.priority_levels = {
                'none': 0,
                'low': 1, 
                'medium': 2,
                'high': 3,
                'critical': 4
            }
            
            logger.info(f"TestEngineManager initialized: {len(self.category_config)} categories, "
                       f"halt threshold: {self.failure_halt_threshold}%, delay: {self.test_delay_ms}ms")
            
        except Exception as e:
            logger.error(f"Error initializing TestEngineManager: {e}")
            raise
    
    def load_phrase_category(self, category_name: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Load phrases from category file
        
        Args:
            category_name: Name of test category
            
        Returns:
            Tuple of (phrase_list, category_info)
        """
        try:
            if category_name not in self.category_config:
                raise ValueError(f"Unknown category: {category_name}")
            
            category_info = self.category_config[category_name]
            phrase_file = category_info.get('file')
            
            if not phrase_file:
                raise ValueError(f"No file specified for category: {category_name}")
            
            phrase_path = self.phrases_dir / phrase_file
            
            if not phrase_path.exists():
                raise FileNotFoundError(f"Phrase file not found: {phrase_path}")
            
            with open(phrase_path, 'r', encoding='utf-8') as f:
                phrase_data = json.load(f)
            
            # Extract phrases from subcategories
            phrases = []
            category_section = phrase_data.get('category', {})
            subcategories = category_section.get('subcategories', {})
            
            for subcategory_name, phrase_list in subcategories.items():
                for i, phrase_info in enumerate(phrase_list):
                    phrases.append({
                        'id': f"{category_name}_{subcategory_name}_{i}",
                        'message': phrase_info['message'],
                        'description': phrase_info['description'],
                        'subcategory': subcategory_name
                    })
            
            logger.debug(f"Loaded {len(phrases)} phrases from {category_name}")
            return phrases, category_info
            
        except Exception as e:
            logger.error(f"Error loading phrase category {category_name}: {e}")
            raise
    # ========================================================================
    
    # ========================================================================
    # CALCULATIONS
    # ========================================================================
    def calculate_failure_severity(self, expected_priorities: List[str], actual_priority: str) -> Tuple[int, bool, bool]:
        """
        Calculate failure severity and classify false negative/positive
        
        Args:
            expected_priorities: List of acceptable priority levels
            actual_priority: Actual classified priority level
            
        Returns:
            Tuple of (severity_level, is_false_negative, is_false_positive)
        """
        if actual_priority in expected_priorities:
            return 0, False, False  # Pass
        
        # Calculate minimum distance from any expected priority
        expected_levels = [self.priority_levels.get(p, 0) for p in expected_priorities]
        actual_level = self.priority_levels.get(actual_priority, 0)
        
        min_distance = min(abs(actual_level - exp_level) for exp_level in expected_levels)
        severity = min(min_distance, 3)  # Cap at 3 levels
        
        # Determine false negative/positive
        max_expected = max(expected_levels)
        min_expected = min(expected_levels)
        
        is_false_negative = actual_level < min_expected  # Classified lower than expected
        is_false_positive = actual_level > max_expected  # Classified higher than expected
        
        return severity, is_false_negative, is_false_positive
    
    def calculate_weighted_score(self, phrase_result: PhraseTestResult, is_critical_category: bool) -> float:
        """
        Calculate weighted failure score for safety-first analysis
        
        Args:
            phrase_result: Individual phrase test result
            is_critical_category: Whether this is a safety-critical category
            
        Returns:
            Weighted failure score (0.0 = pass, higher = worse failure)
        """
        if phrase_result.result == TestResult.PASS:
            return 0.0
        
        if phrase_result.result == TestResult.ERROR:
            return 5.0  # Errors are always serious
        
        # Base severity score
        severity_key = f"{phrase_result.failure_severity}_level_miss"
        base_score = self.severity_weights.get(severity_key, phrase_result.failure_severity)
        
        # Apply false negative multiplier (safety-first)
        if phrase_result.is_false_negative:
            base_score *= self.false_negative_multiplier
        
        # Apply critical category multiplier
        if is_critical_category:
            base_score *= self.critical_multiplier
        
        return base_score
    
    def should_halt_testing(self, category_result: CategoryTestResult) -> Tuple[bool, str]:
        """
        Determine if testing should halt due to poor performance
        
        Args:
            category_result: Current category test result
            
        Returns:
            Tuple of (should_halt, reason)
        """
        if not self.enable_early_termination:
            return False, ""
        
        # Check if critical category falls below threshold
        if category_result.is_critical and category_result.pass_rate < self.failure_halt_threshold:
            return True, f"Critical category '{category_result.category_name}' pass rate {category_result.pass_rate:.1f}% < {self.failure_halt_threshold}%"
        
        # Check for excessive false negatives in any category
        if category_result.false_negatives > (category_result.total_tests * 0.4):
            return True, f"Excessive false negatives in '{category_result.category_name}': {category_result.false_negatives}/{category_result.total_tests}"
        
        return False, ""
    # ========================================================================
    
    # ========================================================================
    # RUN TESTS
    # ========================================================================
    def run_category_test(self, category_name: str) -> CategoryTestResult:
        """
        Run tests for a specific category
        
        Args:
            category_name: Name of category to test
            
        Returns:
            CategoryTestResult with complete results
        """
        logger.info(f"Starting tests for category: {category_name}")
        start_time = time.time()
        
        try:
            # Load category phrases and configuration
            phrases, category_info = self.load_phrase_category(category_name)
            
            expected_priorities = self.unified_config.get_config_section('test_settings', f'test_categories.{category_name}.expected_priority', [])
            logger.info(f'Found expected priorities: {expected_priorities}')

            target_pass_rate = category_info.get('target_pass_rate', 85)
            is_critical = category_info.get('critical', False)
            
            # Initialize category result
            category_result = CategoryTestResult(
                category_name=category_name,
                category_file=category_info.get('file', ''),
                expected_priorities=expected_priorities,
                target_pass_rate=target_pass_rate,
                is_critical=is_critical,
                total_tests=len(phrases)
            )
            
            logger.info(f"Testing {len(phrases)} phrases, target: {target_pass_rate}%, critical: {is_critical}")
            
            # Test each phrase
            for i, phrase_info in enumerate(phrases):
                try:
                    # Progress reporting
                    if (i + 1) % self.progress_interval == 0 or i == 0:
                        logger.info(f"  Progress: {i + 1}/{len(phrases)} phrases tested")
                    
                    # Analyze phrase
                    analysis_result = self.nlp_client.analyze_message(
                        message=phrase_info['message'],
                        user_id=self.test_user_id,
                        channel_id=self.test_channel_id
                    )
                    
                    if analysis_result is None:
                        # Analysis error
                        phrase_result = PhraseTestResult(
                            phrase_id=phrase_info['id'],
                            message=phrase_info['message'],
                            expected_priorities=expected_priorities,
                            actual_priority='error',
                            confidence_score=0.0,
                            processing_time_ms=0.0,
                            result=TestResult.ERROR,
                            error_message="Analysis request failed"
                        )
                        category_result.error_tests += 1
                    else:
                        # Calculate test result
                        severity, is_false_neg, is_false_pos = self.calculate_failure_severity(
                            expected_priorities, analysis_result.crisis_level
                        )
                        
                        result_type = TestResult.PASS if severity == 0 else TestResult.FAIL
                        
                        phrase_result = PhraseTestResult(
                            phrase_id=phrase_info['id'],
                            message=phrase_info['message'],
                            expected_priorities=expected_priorities,
                            actual_priority=analysis_result.crisis_level,
                            confidence_score=analysis_result.confidence_score,
                            processing_time_ms=analysis_result.processing_time_ms,
                            result=result_type,
                            failure_severity=severity,
                            is_false_negative=is_false_neg,
                            is_false_positive=is_false_pos,
                            analysis_data=analysis_result.raw_response
                        )
                        
                        # Update counters
                        if result_type == TestResult.PASS:
                            category_result.passed_tests += 1
                        else:
                            category_result.failed_tests += 1
                            if is_false_neg:
                                category_result.false_negatives += 1
                            if is_false_pos:
                                category_result.false_positives += 1
                    
                    category_result.phrase_results.append(phrase_result)
                    
                    # Add delay between tests
                    if i < len(phrases) - 1:  # Don't delay after last test
                        time.sleep(self.test_delay_ms / 1000.0)
                    
                except Exception as e:
                    logger.error(f"Error testing phrase {phrase_info['id']}: {e}")
                    error_result = PhraseTestResult(
                        phrase_id=phrase_info['id'],
                        message=phrase_info['message'],
                        expected_priorities=expected_priorities,
                        actual_priority='error',
                        confidence_score=0.0,
                        processing_time_ms=0.0,
                        result=TestResult.ERROR,
                        error_message=str(e)
                    )
                    category_result.phrase_results.append(error_result)
                    category_result.error_tests += 1
            
            # Calculate final statistics
            category_result.execution_time_ms = (time.time() - start_time) * 1000
            
            if category_result.total_tests > 0:
                category_result.pass_rate = (category_result.passed_tests / category_result.total_tests) * 100
            
            # Calculate weighted safety score
            total_weighted_score = sum(
                self.calculate_weighted_score(phrase_result, is_critical)
                for phrase_result in category_result.phrase_results
            )
            category_result.weighted_score = total_weighted_score / max(1, len(category_result.phrase_results))
            
            logger.info(f"Category '{category_name}' complete: {category_result.pass_rate:.1f}% pass rate "
                       f"({category_result.passed_tests}/{category_result.total_tests}), "
                       f"{category_result.false_negatives} false negatives")
            
            return category_result
            
        except Exception as e:
            logger.error(f"Error running category test {category_name}: {e}")
            raise
    
    def run_test_suite(self, categories: Optional[List[str]] = None) -> TestSuiteResult:
        """
        Run complete test suite or specified categories
        
        Args:
            categories: Optional list of category names to test (None = all)
            
        Returns:
            TestSuiteResult with complete results
        """
        start_time = time.time()
        logger.info("=" * 70)
        logger.info("Starting Ash-Thrash Test Suite Execution")
        logger.info("=" * 70)
        
        # Verify NLP server is ready
        is_ready, status_msg = self.nlp_client.verify_server_ready()
        if not is_ready:
            raise RuntimeError(f"NLP server not ready: {status_msg}")
        
        logger.info(f"NLP server verified: {status_msg}")
        
        # Determine categories to test
        test_categories = categories if categories else list(self.category_config.keys())
        
        # Initialize test suite result
        suite_result = TestSuiteResult(
            start_time=start_time,
            end_time=0.0,
            total_execution_time_ms=0.0,
            categories_tested=len(test_categories),
            total_phrases=0,
            total_passed=0,
            total_failed=0,
            total_errors=0,
            overall_pass_rate=0.0,
            weighted_safety_score=0.0,
            early_termination=False,
            termination_reason=None,
            server_info=self.nlp_client.get_server_info()
        )
        
        # Run tests for each category
        for category_name in test_categories:
            try:
                logger.info("=" * 50)
                logger.info(f"Testing category: {category_name}")
                logger.info("=" * 50)
                
                category_result = self.run_category_test(category_name)
                suite_result.category_results.append(category_result)
                
                # Update totals
                suite_result.total_phrases += category_result.total_tests
                suite_result.total_passed += category_result.passed_tests
                suite_result.total_failed += category_result.failed_tests
                suite_result.total_errors += category_result.error_tests
                
                # Check for early termination
                should_halt, halt_reason = self.should_halt_testing(category_result)
                if should_halt:
                    logger.warning(f"Early termination triggered: {halt_reason}")
                    suite_result.early_termination = True
                    suite_result.termination_reason = halt_reason
                    break
                
                logger.info("=" * 50)
                logger.info("")

            except Exception as e:
                logger.error(f"Failed to test category {category_name}: {e}")
                # Continue with other categories rather than failing entire suite
                continue
        
        # Calculate final statistics
        end_time = time.time()
        suite_result.end_time = end_time
        suite_result.total_execution_time_ms = (end_time - start_time) * 1000
        
        if suite_result.total_phrases > 0:
            suite_result.overall_pass_rate = (suite_result.total_passed / suite_result.total_phrases) * 100
        
        # Calculate weighted safety score across all categories
        if suite_result.category_results:
            suite_result.weighted_safety_score = sum(
                cat.weighted_score for cat in suite_result.category_results
            ) / len(suite_result.category_results)
        
        logger.info("=" * 70)
        logger.info(f"Test Suite Complete: {suite_result.overall_pass_rate:.1f}% pass rate")
        logger.info(f"Total: {suite_result.total_passed}/{suite_result.total_phrases} passed, "
                   f"{suite_result.total_failed} failed, {suite_result.total_errors} errors")
        logger.info(f"Execution time: {suite_result.total_execution_time_ms/1000:.1f}s")
        if suite_result.early_termination:
            logger.warning(f"Early termination: {suite_result.termination_reason}")
        logger.info("=" * 70)
        
        return suite_result
    # ========================================================================

# ========================================================================
# FACTORY FUNCTION
# ========================================================================
def create_test_engine_manager(unified_config_manager, nlp_client_manager) -> TestEngineManager:
    """
    Factory function for TestEngineManager (Clean v3.1 Pattern)
    
    Args:
        unified_config_manager: UnifiedConfigManager instance
        nlp_client_manager: NLPClientManager instance
        
    Returns:
        Initialized TestEngineManager instance
        
    Raises:
        ValueError: If required managers are None or invalid
    """
    logger.debug("Creating TestEngineManager with Clean v3.1 architecture")
    
    if not unified_config_manager:
        raise ValueError("UnifiedConfigManager is required for TestEngineManager factory")
    
    if not nlp_client_manager:
        raise ValueError("NLPClientManager is required for TestEngineManager factory")
    
    return TestEngineManager(unified_config_manager, nlp_client_manager)
# ========================================================================

# ========================================================================
# Public interface
# ========================================================================
__all__ = [
    'TestEngineManager',
    'TestSuiteResult',
    'CategoryTestResult',
    'PhraseTestResult', 
    'TestResult',
    'create_test_engine_manager'
]

logger.info("TestEngineManager v3.1-1a-1 loaded")
# ========================================================================