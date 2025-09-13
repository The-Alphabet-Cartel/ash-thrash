# ash-thrash/main.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Ash-Thrash Main Application Entry Point for Ash Thrash Service
---
FILE VERSION: v3.1-4a-4
LAST MODIFIED: 2025-09-12
PHASE: 4a Step 4 - Main Application Client Classification Integration Fixed
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import sys
import logging
import colorlog

# ============================================================================
# MANAGER IMPORTS - ALL USING FACTORY FUNCTIONS (Clean Architecture)
# ============================================================================
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.nlp_client import create_nlp_client_manager
from managers.test_engine import create_test_engine_manager
from managers.results_manager import create_results_manager
from managers.analyze_results import create_analyze_results_manager
from managers.tuning_suggestions import create_tuning_suggestions_manager

# NEW: Import client classification manager
from managers.crisis_classifier import create_crisis_classifier_manager
# ============================================================================

# ============================================================================
# UNIFIED LOGGING SETUP
# ============================================================================
def setup_unified_logging(unified_config_manager):
    """
    Setup colorlog logging with unified configuration management
    """
    try:
        # Get logging configuration through unified config
        log_level = unified_config_manager.get_config_section('logging_settings', 'global_settings.log_level', 'INFO')
        log_detailed = unified_config_manager.get_config_section('logging_settings', 'detailed_logging.enable_detailed', True)
        enable_file_logging = unified_config_manager.get_config_section('logging_settings', 'global_settings.enable_file_output', False)
        log_file = unified_config_manager.get_config_section('logging_settings', 'global_settings.log_file', 'ash-thrash.log')
        
        # Configure colorlog formatter
        if log_detailed == False:
            log_format_string = '%(log_color)s%(levelname)s%(reset)s: %(message)s'
        else:  # detailed
            log_format_string = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s: %(message)s'
        
        # Create colorlog formatter
        formatter = colorlog.ColoredFormatter(
            log_format_string,
            datefmt='%Y-%m-%d %H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Optional file handler
        if enable_file_logging:
            try:
                file_handler = logging.FileHandler(log_file)
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                root_logger.addHandler(file_handler)
                logging.info(f"File logging enabled: {log_file}")
            except Exception as e:
                logging.warning(f"Could not setup file logging: {e}")
        
        logging.info("Unified colorlog logging configured successfully")
        logging.info(f"Log level: {log_level}")
        
    except Exception as e:
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to setup unified logging: {e}")
        logging.info("Using fallback basic logging configuration")
# ============================================================================

# ============================================================================
# UNIFIED MANAGER INITIALIZATION (Updated for Client Classification)
# ============================================================================
def initialize_managers():
    """
    Initialize all managers using factory functions (Clean Architecture v3.1) - Phase 4a Enhanced
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Initializing Ash-Thrash managers...")
    logger.info("=" * 70)
    
    try:
        # Core configuration managers
        unified_config = create_unified_config_manager()
        logging_config = create_logging_config_manager(unified_config)
        
        # Client classification manager (NEW) - Using correct configuration method
        client_classifier = None
        try:
            client_classification_enabled = unified_config.get_config_section('client_classification', 'client_classification.enable_client_classification', True)
            if client_classification_enabled:
                client_classifier = create_crisis_classifier_manager(unified_config)
                logger.info("Client classification manager initialized - DUAL CLASSIFICATION MODE")
            else:
                logger.info("Client classification disabled - SERVER-ONLY MODE")
        except Exception as e:
            logger.warning(f"Client classification manager failed to initialize: {e}")
            logger.info("Continuing with server-only classification")
            client_classifier = None
        
        # Testing managers (UPDATED to include client classifier)
        nlp_client = create_nlp_client_manager(unified_config)
        test_engine = create_test_engine_manager(unified_config, nlp_client, client_classifier)  # UPDATED
        
        # Results and analysis managers
        results_manager = create_results_manager(unified_config)
        analyze_manager = create_analyze_results_manager(unified_config, results_manager, logging_config)
        
        # Advanced tuning intelligence manager
        tuning_manager = create_tuning_suggestions_manager(unified_config, results_manager, analyze_manager)

        managers = {
            'unified_config': unified_config,
            'logging_config': logging_config,
            'nlp_client': nlp_client,
            'client_classifier': client_classifier,  # NEW
            'test_engine': test_engine,
            'results_manager': results_manager,
            'analyze_manager': analyze_manager,
            'tuning_manager': tuning_manager,
        }
        
        manager_count = len([m for m in managers.values() if m is not None])
        logger.info(f"All managers initialized successfully: {manager_count} total")
        logger.info("Phase 3a: Advanced Tuning Intelligence enabled")
        
        if client_classifier:
            logger.info("Phase 4a: Client-Side Crisis Classification enabled")
            strategy = unified_config.get_config_section('client_classification', 'client_classification.strategy', 'conservative')
            threshold_config = unified_config.get_config_section('client_classification', 'client_classification.threshold_config', 'standard')
            logger.info(f"   Strategy: {strategy}, Threshold Config: {threshold_config}")
        
        return managers
        
    except Exception as e:
        logger.error(f"Manager initialization failed: {e}")
        raise
# ============================================================================

# ============================================================================
# ENHANCED TEST EXECUTION FUNCTIONS (Updated for Client Classification)
# ============================================================================
def run_comprehensive_test(managers):
    """Run comprehensive test suite across all categories with integrated reporting, Phase 3a tuning intelligence, and Phase 4a dual classification"""
    logger = logging.getLogger(__name__)
    test_engine = managers['test_engine']
    results_manager = managers['results_manager']
    analyze_manager = managers['analyze_manager']
    tuning_manager = managers['tuning_manager']  # Phase 3a addition
    client_classifier = managers.get('client_classifier')  # Phase 4a addition
    
    # Log classification mode
    if client_classifier:
        logger.info("Starting comprehensive test suite with DUAL CLASSIFICATION...")
        strategy = managers['unified_config'].get_config_section('client_classification', 'client_classification.strategy', 'conservative')
        logger.info(f"Using strategy: {strategy}")
    else:
        logger.info("Starting comprehensive test suite with SERVER-ONLY classification...")
    
    try:
        # Run all category tests
        suite_result = test_engine.run_test_suite()
        
        # Store test results to disk
        try:
            result_path = results_manager.store_test_results(suite_result)
            logger.info(f"Test results saved to: {result_path}")
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
        
        # Generate markdown reports automatically
        try:
            logger.info("Generating comprehensive markdown reports...")
            report_success = analyze_manager.generate_all_reports()
            if report_success:
                logger.info("All markdown reports generated successfully:")
                logger.info("   reports/latest_run_summary.md")
                logger.info("   reports/threshold_recommendations.md") 
                logger.info("   reports/historical_performance.md")
            else:
                logger.warning("Some markdown reports failed to generate")
        except Exception as e:
            logger.error(f"Failed to generate markdown reports: {e}")
        
        # Generate advanced tuning intelligence and recommendations
        try:
            logger.info("=" * 50)
            logger.info("PHASE 3A: GENERATING ADVANCED TUNING INTELLIGENCE")
            logger.info("=" * 50)
            
            # Convert suite result to format needed by tuning manager
            test_results_dict = _convert_suite_result_to_dict(suite_result)
            
            # Generate comprehensive tuning analysis
            logger.info("Analyzing failure patterns and generating threshold recommendations...")
            tuning_analysis = tuning_manager.generate_tuning_recommendations(test_results_dict)
            
            # Save tuning analysis to persistent files
            analysis_file = tuning_manager.save_tuning_analysis(tuning_analysis)
            env_file = tuning_manager.generate_env_file_recommendations(tuning_analysis)
            
            # Log tuning intelligence summary
            logger.info("=" * 50)
            logger.info("TUNING INTELLIGENCE SUMMARY")
            logger.info("=" * 50)
            logger.info(f"Current ensemble mode: {tuning_analysis.ensemble_mode.value}")
            logger.info(f"Critical issues identified: {len(tuning_analysis.critical_issues)}")
            logger.info(f"Threshold recommendations: {len(tuning_analysis.recommendations)}")
            logger.info(f"Risk level: {tuning_analysis.risk_assessment.get('overall_risk_level', 'unknown')}")
            
            # Display confidence summary
            confidence_summary = tuning_analysis.confidence_summary
            if confidence_summary.get('total_recommendations', 0) > 0:
                logger.info("Recommendation confidence breakdown:")
                logger.info(f"  High confidence: {confidence_summary.get('high', 0)} recommendations")
                logger.info(f"  Medium confidence: {confidence_summary.get('medium', 0)} recommendations")
                logger.info(f"  Low confidence: {confidence_summary.get('low', 0)} recommendations")
                logger.info(f"  Uncertain: {confidence_summary.get('uncertain', 0)} recommendations")
            
            # Display critical issues
            if tuning_analysis.critical_issues:
                logger.warning("Critical issues requiring immediate attention:")
                for issue in tuning_analysis.critical_issues[:3]:  # Show first 3
                    logger.warning(f"   {issue}")
                if len(tuning_analysis.critical_issues) > 3:
                    logger.warning(f"   ... and {len(tuning_analysis.critical_issues) - 3} more")
            
            # Display file locations
            logger.info("Analysis files generated:")
            if analysis_file:
                logger.info(f"   Detailed analysis: {analysis_file}")
            if env_file:
                logger.info(f"   Recommended settings: {env_file}")
            
            # Show implementation order preview
            if tuning_analysis.implementation_order:
                logger.info("Implementation priority order (top 3):")
                for i, order_item in enumerate(tuning_analysis.implementation_order[:3], 1):
                    logger.info(f"   {i}. {order_item}")
                if len(tuning_analysis.implementation_order) > 3:
                    logger.info(f"   ... and {len(tuning_analysis.implementation_order) - 3} more")
            
        except Exception as e:
            logger.error(f"Phase 3a tuning intelligence failed: {e}")
            logger.warning("Continuing with standard test reporting...")
        
        # Phase 4a: Client Classification Analysis (NEW)
        if client_classifier and suite_result.client_classification_summary:
            try:
                logger.info("=" * 50)
                logger.info("PHASE 4A: CLIENT CLASSIFICATION ANALYSIS")
                logger.info("=" * 50)
                
                summary = suite_result.client_classification_summary
                logger.info("Dual Classification Performance Summary:")
                logger.info(f"  Total categories tested: {summary['total_categories_tested']}")
                logger.info(f"  Total phrases analyzed: {summary['total_phrases_tested']}")
                logger.info(f"  Server accuracy: {summary['overall_server_accuracy']:.1f}%")
                logger.info(f"  Client accuracy: {summary['overall_client_accuracy']:.1f}%")
                logger.info(f"  Agreement rate: {summary['overall_agreement_rate']:.1f}%")
                
                # Performance comparison
                if summary['overall_client_accuracy'] > summary['overall_server_accuracy']:
                    improvement = summary['overall_client_accuracy'] - summary['overall_server_accuracy']
                    logger.info(f"  Client outperformed server by {improvement:.1f} percentage points")
                elif summary['overall_server_accuracy'] > summary['overall_client_accuracy']:
                    difference = summary['overall_server_accuracy'] - summary['overall_client_accuracy']
                    logger.info(f"  Server outperformed client by {difference:.1f} percentage points")
                else:
                    logger.info(f"  Server and client performed equally")
                
                # Category breakdown
                logger.info(f"  Client won categories: {summary['client_won_categories']}")
                logger.info(f"  Server won categories: {summary['server_won_categories']}")
                
                # Strategy effectiveness
                logger.info(f"  Strategy used: {summary['strategy_used']}")
                logger.info(f"  Threshold config: {summary['threshold_config_used']}")
                
                # Agreement analysis
                if summary['overall_agreement_rate'] >= 80:
                    logger.info("  High agreement rate - classifications are consistent")
                elif summary['overall_agreement_rate'] >= 70:
                    logger.info("  Moderate agreement rate - some classification differences")
                else:
                    logger.warning("  Low agreement rate - significant classification differences")
                
                # Category-specific insights
                if summary.get('category_breakdown'):
                    logger.info("Category-specific performance:")
                    for cat_info in summary['category_breakdown'][:5]:  # Show first 5
                        status = "Client" if cat_info['client_won'] else "Server"
                        logger.info(f"   {status} {cat_info['category']}: "
                                   f"Server {cat_info['server_accuracy']:.1f}%, "
                                   f"Client {cat_info['client_accuracy']:.1f}%, "
                                   f"Agreement {cat_info['agreement_rate']:.1f}%")
                    
                    if len(summary['category_breakdown']) > 5:
                        logger.info(f"   ... and {len(summary['category_breakdown']) - 5} more categories")
                
            except Exception as e:
                logger.error(f"Phase 4a client classification analysis failed: {e}")
                logger.warning("Continuing with standard test reporting...")
        
        # Log test execution summary
        logger.info("=" * 50)
        logger.info("COMPREHENSIVE TEST COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Overall pass rate: {suite_result.overall_pass_rate:.1f}%")
        logger.info(f"Total phrases tested: {suite_result.total_phrases}")
        logger.info(f"Passed: {suite_result.total_passed}")
        logger.info(f"Failed: {suite_result.total_failed}")
        logger.info(f"Errors: {suite_result.total_errors}")
        logger.info(f"Execution time: {suite_result.total_execution_time_ms/1000:.1f}s")
        
        if suite_result.early_termination:
            logger.warning(f"Early termination: {suite_result.termination_reason}")
        
        # Display quick analysis summary
        try:
            logger.info("=" * 50)
            logger.info("ANALYSIS SUMMARY")
            logger.info("=" * 50)
            analyze_manager.display_latest_results()
        except Exception as e:
            logger.error(f"Failed to display analysis summary: {e}")
        
        return suite_result
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return None

def run_category_test(managers, category_name: str):
    """Run test for specific category with integrated reporting, Phase 3a tuning intelligence, and Phase 4a dual classification"""
    logger = logging.getLogger(__name__)
    test_engine = managers['test_engine']
    results_manager = managers['results_manager']
    analyze_manager = managers['analyze_manager']
    tuning_manager = managers['tuning_manager']  # Phase 3a addition
    client_classifier = managers.get('client_classifier')  # Phase 4a addition
    
    # Log classification mode
    if client_classifier:
        logger.info(f"Starting test for category: {category_name} with DUAL CLASSIFICATION")
    else:
        logger.info(f"Starting test for category: {category_name} with SERVER-ONLY classification")
    
    try:
        suite_result = test_engine.run_test_suite([category_name])
        
        # Store test results to disk
        try:
            result_path = results_manager.store_test_results(suite_result)
            logger.info(f"Test results saved to: {result_path}")
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
        
        # Generate reports for single category tests too
        try:
            logger.info("Generating markdown reports for category test...")
            report_success = analyze_manager.generate_all_reports()
            if report_success:
                logger.info("All markdown reports updated with category test results")
            else:
                logger.warning("Some markdown reports failed to generate")
        except Exception as e:
            logger.error(f"Failed to generate markdown reports: {e}")
        
        # Generate targeted tuning intelligence for single category
        try:
            logger.info("=" * 50)
            logger.info("GENERATING CATEGORY-SPECIFIC TUNING ANALYSIS")
            logger.info("=" * 50)
            
            # Convert suite result to format needed by tuning manager
            test_results_dict = _convert_suite_result_to_dict(suite_result)
            
            # Generate tuning analysis focused on this category
            logger.info(f"Analyzing {category_name} for threshold optimization opportunities...")
            tuning_analysis = tuning_manager.generate_tuning_recommendations(test_results_dict)
            
            # Filter recommendations relevant to this category
            category_specific_recs = [
                rec for rec in tuning_analysis.recommendations
                if category_name in rec.reasoning or category_name in rec.expected_improvement
            ]
            
            # Log category-specific tuning insights
            logger.info(f"{category_name.upper()} TUNING ANALYSIS")
            logger.info(f"Category-specific recommendations: {len(category_specific_recs)}")
            
            if category_specific_recs:
                logger.info("Top recommendations for this category:")
                for i, rec in enumerate(category_specific_recs[:2], 1):  # Show top 2
                    logger.info(f"  {i}. {rec.variable_name}: {rec.current_value:.3f} -> {rec.recommended_value:.3f}")
                    logger.info(f"     Risk: {rec.risk_level.value}, Confidence: {rec.confidence_level.value}")
            else:
                # Show general recommendations that might help
                if tuning_analysis.recommendations:
                    logger.info("General recommendations that may impact this category:")
                    for i, rec in enumerate(tuning_analysis.recommendations[:2], 1):
                        logger.info(f"  {i}. {rec.variable_name}: {rec.current_value:.3f} -> {rec.recommended_value:.3f}")
                        logger.info(f"     Risk: {rec.risk_level.value}, Confidence: {rec.confidence_level.value}")
                else:
                    logger.info("No specific threshold recommendations generated for this category")
            
            # Save analysis files with category prefix
            if tuning_analysis.recommendations:
                analysis_file = tuning_manager.save_tuning_analysis(tuning_analysis)
                env_file = tuning_manager.generate_env_file_recommendations(tuning_analysis)
                
                logger.info("Category analysis files:")
                if analysis_file:
                    logger.info(f"   Analysis: {analysis_file}")
                if env_file:
                    logger.info(f"   Settings: {env_file}")
            
        except Exception as e:
            logger.error(f"Phase 3a category tuning analysis failed: {e}")
            logger.warning("Continuing with standard category reporting...")
        
        # Phase 4a: Category-specific Client Classification Analysis (NEW)
        if client_classifier and suite_result.client_classification_summary:
            try:
                logger.info("=" * 50)
                logger.info("CATEGORY CLIENT CLASSIFICATION ANALYSIS")
                logger.info("=" * 50)
                
                summary = suite_result.client_classification_summary
                if summary['category_breakdown']:
                    cat_info = summary['category_breakdown'][0]  # Single category
                    
                    logger.info(f"Category: {cat_info['category']}")
                    logger.info(f"  Server accuracy: {cat_info['server_accuracy']:.1f}%")
                    logger.info(f"  Client accuracy: {cat_info['client_accuracy']:.1f}%")
                    logger.info(f"  Agreement rate: {cat_info['agreement_rate']:.1f}%")
                    logger.info(f"  Strategy used: {cat_info['strategy']}")
                    
                    if cat_info['client_won']:
                        improvement = cat_info['client_accuracy'] - cat_info['server_accuracy']
                        logger.info(f"  Client outperformed server by {improvement:.1f} percentage points")
                    else:
                        difference = cat_info['server_accuracy'] - cat_info['client_accuracy']
                        if difference > 0:
                            logger.info(f"  Server outperformed client by {difference:.1f} percentage points")
                        else:
                            logger.info(f"  Server and client performed equally")
                    
                    # Agreement assessment
                    if cat_info['agreement_rate'] >= 80:
                        logger.info("  High classification agreement")
                    elif cat_info['agreement_rate'] >= 70:
                        logger.info("  Moderate classification agreement")
                    else:
                        logger.warning("  Low classification agreement - investigate discrepancies")
                
            except Exception as e:
                logger.error(f"Phase 4a category client classification analysis failed: {e}")
        
        # Log category results
        if suite_result.category_results:
            category_result = suite_result.category_results[0]
            logger.info("=" * 50)
            logger.info(f"CATEGORY TEST COMPLETE: {category_name}")
            logger.info("=" * 50)
            logger.info(f"Pass rate: {category_result.pass_rate:.1f}%")
            logger.info(f"Target: {category_result.target_pass_rate}%")
            logger.info(f"Phrases: {category_result.passed_tests}/{category_result.total_tests}")
            logger.info(f"False negatives: {category_result.false_negatives}")
            logger.info(f"False positives: {category_result.false_positives}")
            
            # Status assessment
            if category_result.pass_rate >= float(category_result.target_pass_rate):
                logger.info("Category meeting target performance")
            else:
                if category_result.is_critical:
                    logger.error(f"CRITICAL: Category {category_result.pass_rate:.1f}% below {category_result.target_pass_rate}% target")
                else:
                    logger.warning(f"Category {category_result.pass_rate:.1f}% below {category_result.target_pass_rate}% target")
        
        return suite_result
        
    except Exception as e:
        logger.error(f"Category test failed: {e}")
        return None

def _convert_suite_result_to_dict(suite_result) -> dict:
    """
    Convert TestSuiteResult to dictionary format expected by TuningSuggestionsManager
    
    Args:
        suite_result: TestSuiteResult object from test execution
        
    Returns:
        Dictionary format compatible with tuning analysis
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.debug("=" * 50)
        logger.debug("CONVERTING SUITE RESULT TO DICT")
        logger.debug("=" * 50)
        
        # Create the expected dictionary structure
        test_results = {
            'metadata': {
                'timestamp': getattr(suite_result, 'timestamp', ''),
                'early_termination': getattr(suite_result, 'early_termination', False),
                'termination_reason': getattr(suite_result, 'termination_reason', ''),
                'total_execution_time_ms': getattr(suite_result, 'total_execution_time_ms', 0)
            },
            'summary': {
                'overall_pass_rate': getattr(suite_result, 'overall_pass_rate', 0.0),
                'total_phrases': getattr(suite_result, 'total_phrases', 0),
                'total_passed': getattr(suite_result, 'total_passed', 0),
                'total_failed': getattr(suite_result, 'total_failed', 0),
                'total_errors': getattr(suite_result, 'total_errors', 0)
            },
            'category_results': {}
        }
        
        logger.debug(f"Basic metadata created:")
        logger.debug(f"  Overall pass rate: {test_results['summary']['overall_pass_rate']}")
        logger.debug(f"  Total failed: {test_results['summary']['total_failed']}")
        
        # Convert category results
        if hasattr(suite_result, 'category_results') and suite_result.category_results:
            logger.debug(f"Processing {len(suite_result.category_results)} category results...")
            
            for i, category_result in enumerate(suite_result.category_results):
                logger.debug(f"--- Processing category {i+1} ---")
                
                category_name = getattr(category_result, 'category_name', 'unknown')
                logger.debug(f"Category name: {category_name}")
                
                # Create category summary
                category_data = {
                    'summary': {
                        'category_name': category_name,
                        'pass_rate': getattr(category_result, 'pass_rate', 0.0),
                        'target_pass_rate': getattr(category_result, 'target_pass_rate', 85.0),
                        'total_tests': getattr(category_result, 'total_tests', 0),
                        'passed_tests': getattr(category_result, 'passed_tests', 0),
                        'failed_tests': getattr(category_result, 'failed_tests', 0),
                        'false_negatives': getattr(category_result, 'false_negatives', 0),
                        'false_positives': getattr(category_result, 'false_positives', 0),
                        'is_critical': getattr(category_result, 'is_critical', False)
                    }
                }
                
                logger.debug(f"Category summary created:")
                logger.debug(f"  Pass rate: {category_data['summary']['pass_rate']}%")
                logger.debug(f"  Failed tests: {category_data['summary']['failed_tests']}")
                logger.debug(f"  False positives: {category_data['summary']['false_positives']}")
                
                # Add failed test details if available
                test_details_attr = None
                for attr_name in ['phrase_results', 'test_details', 'test_results', 'details', 'results']:
                    if hasattr(category_result, attr_name):
                        test_details_attr = attr_name
                        break
                
                if test_details_attr:
                    test_details = getattr(category_result, test_details_attr)
                    logger.debug(f"Found test details in attribute: {test_details_attr}")
                    logger.debug(f"Test details count: {len(test_details) if test_details else 0}")
                    
                    if test_details:
                        failed_tests = []
                        passed_count = 0
                        failed_count = 0
                        
                        for j, test_detail in enumerate(test_details):
                            is_false_positive = getattr(test_detail, 'is_false_positive', False)
                            is_false_negative = getattr(test_detail, 'is_false_negative', False)
                            test_passed = not (is_false_positive or is_false_negative)
                            
                            if test_passed:
                                passed_count += 1
                            else:
                                failed_count += 1
                                
                                failed_test = {
                                    'phrase': getattr(test_detail, 'test_phrase', getattr(test_detail, 'phrase', '')),
                                    'expected_crisis_level': test_detail.expected_priorities[0] if test_detail.expected_priorities else 'low',
                                    'actual_crisis_level': getattr(test_detail, 'actual_priority', 'unknown'),
                                    'confidence_score': getattr(test_detail, 'confidence_score', 0.0),
                                    'processing_time_ms': getattr(test_detail, 'processing_time_ms', 0),
                                    'severity_score': getattr(test_detail, 'severity_score', 0),
                                    'error_message': getattr(test_detail, 'error_message', '')
                                }
                                failed_tests.append(failed_test)
                                
                                # Log first few failed tests for debugging
                                if len(failed_tests) <= 3:
                                    logger.debug(f"  Failed test {len(failed_tests)}: {failed_test['expected_crisis_level']} -> {failed_test['actual_crisis_level']}")
                        
                        logger.debug(f"Processed test details: {passed_count} passed, {failed_count} failed")
                        
                        if failed_tests:
                            category_data['failed_tests_details'] = failed_tests
                            logger.debug(f"Added {len(failed_tests)} failed test details to category data")
                        else:
                            logger.debug(f"No failed tests found - failed_tests count = {category_data['summary']['failed_tests']}")
                else:
                    logger.warning(f"No test details found for category {category_name}")
                
                test_results['category_results'][category_name] = category_data
        else:
            logger.warning("No category results found in suite result")
        
        logger.debug("=" * 50)
        logger.debug("FINAL CONVERTED DICTIONARY STRUCTURE")
        logger.debug("=" * 50)
        logger.debug(f"Categories in result: {list(test_results['category_results'].keys())}")
        
        for cat_name, cat_data in test_results['category_results'].items():
            logger.debug(f"Category {cat_name}:")
            logger.debug(f"  Failed tests: {cat_data['summary']['failed_tests']}")
            logger.debug(f"  Has failed_tests_details: {'failed_tests_details' in cat_data}")
            if 'failed_tests_details' in cat_data:
                logger.debug(f"  Failed test details count: {len(cat_data['failed_tests_details'])}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error converting suite result to dictionary: {e}")
        logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return minimal structure as fallback
        return {
            'metadata': {'error': str(e)},
            'summary': {'overall_pass_rate': 0.0},
            'category_results': {}
        }
# ============================================================================

# ============================================================================
# WEIGHT OPTIMIZER (Unchanged)
# ============================================================================
def weight_optimizer(sample_run=None):
    """
    Run model ensemble and weights optimization using evolutionary algorithm
    
    Args:
        sample_run: If True, use reduced parameters for quick testing
        
    Returns:
        Dictionary with optimal label set configuration
    """
    from managers.weight_optimizer import OptimizationConfiguration, create_weight_optimizer
    from managers.weight_data_loader import create_weight_data_loader

    generations = 50
    population_size = 20
    api_endpoint = 'http://172.20.0.11:8881/analyze'
    phrases_dir = './config/phrases'
    results_dir = './results/optimizer-weights'
    
    try:
        logger.info("Starting Ash-NLP Weight Optimization")
        logger.info(f"Configuration: {generations} generations, {population_size} population")
        logger.info("Loading test dataset...")

        weight_data_loader = create_weight_data_loader(unified_config, phrases_dir)

        if sample_run:
            logger.info("Running in sample mode with reduced dataset")
            generations = 25
            population_size = 10
            test_dataset = weight_data_loader.create_sample_dataset(sample_size=10)
        else:
            test_dataset = weight_data_loader.load_all_test_data()
        
        validation_report = weight_data_loader.validate_dataset(test_dataset)
        if not validation_report['valid']:
            logger.error(f"Dataset validation failed: {validation_report['issues']}")
            return 1
        
        logger.info(f"Dataset loaded: {validation_report['total_phrases']} total phrases")

        config = OptimizationConfiguration(
            population_size=population_size,
            generations=generations,
            api_endpoint=api_endpoint
        )
        
        # Create optimizer
        optimizer = create_weight_optimizer(unified_config, test_dataset, config)
        
        # Establish baseline
        logger.info("Establishing baseline performance...")
        baseline_performance = optimizer.establish_baseline_performance()
        
        # Run optimization
        logger.info("Starting optimization process...")
        best_individual, optimization_results = optimizer.optimize_weights()
        
        # Save results
        logger.info("Saving optimization results...")
        results_file = optimizer.save_results(optimization_results, results_dir)
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("OPTIMIZATION COMPLETE")
        logger.info("="*80)
        
        summary = optimization_results['optimization_summary']
        logger.info(f"Improvement: {summary['improvement_percentage']:.2f}%")
        logger.info(f"Target Met: {'YES' if summary['target_met'] else 'NO'}")
        logger.info(f"Total Time: {summary['total_time_minutes']:.1f} minutes")
        logger.info(f"API Calls: {summary['total_api_calls']:,}")
        
        best_config = optimization_results['best_configuration']
        logger.info(f"\nOPTIMAL CONFIGURATION:")
        logger.info(f"   Ensemble Mode: {best_config['ensemble_mode']}")
        logger.info(f"   Depression Weight: {best_config['weights']['depression']:.3f}")
        logger.info(f"   Sentiment Weight: {best_config['weights']['sentiment']:.3f}")
        logger.info(f"   Distress Weight: {best_config['weights']['emotional_distress']:.3f}")
        
        logger.info(f"\nRecommendation: {optimization_results['recommendation']}")
        logger.info(f"Results saved to: {results_file}")
        
        return {
            "best_label_set": best_config,
            "summary": summary,
            "results_file": results_file
        }

    except KeyboardInterrupt:
        logger.info("Optimization interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        logger.exception("Full error details:")
        return 1
# ============================================================================

# ============================================================================
# ZERO-SHOT LABEL OPTIMIZER (Unchanged)
# ============================================================================
def label_optimizer(sample_run=None):
    """
    Run label set optimization using evolutionary algorithm
    
    Args:
        sample_run: If True, use reduced parameters for quick testing
        
    Returns:
        Dictionary with optimal label set configuration
    """
    import sys
    from pathlib import Path
    
    # Import optimization components
    from managers.label_data_loader import create_label_data_loader
    from managers.label_optimizer import create_label_set_optimizer, LabelOptimizationConfiguration
    
    api_endpoint = "http://172.20.0.11:8881/analyze"
    admin_endpoint = "http://172.20.0.11:8881/admin"
    phrases_dir = './config/phrases'
    results_dir = './results/optimizer-labels'
    
    try:
        # Setup logging
        logger.info("STARTING LABEL SET OPTIMIZATION")
        logger.info("="*80)
        
        # Load test data
        logger.info("Loading test phrase data...")
        data_loader = create_label_data_loader(unified_config, phrases_dir)
        test_dataset = data_loader.load_all_test_data()
        
        # Validate test data
        validation_result = data_loader.validate_test_data(test_dataset)
        if not validation_result['valid']:
            logger.error("Test data validation failed:")
            for error in validation_result['errors']:
                logger.error(f"   {error}")
            return 1
        
        # Display test data statistics
        stats = data_loader.get_category_statistics(test_dataset)
        logger.info(f"Loaded {stats['total_phrases']} test phrases across {stats['total_categories']} categories")
        for category, info in stats['category_breakdown'].items():
            logger.info(f"   {category}: {info['count']} phrases, {info['subcategories']} subcategories")
        
        # Create balanced subset for optimization if requested
        if sample_run:
            logger.info("Creating balanced subset for sample run...")
            test_dataset = data_loader.create_balanced_subset(test_dataset, max_phrases_per_category=10)
        
        # Configure optimization
        config = LabelOptimizationConfiguration(
            api_endpoint=api_endpoint,
            admin_endpoint=admin_endpoint
        )
        
        if sample_run:
            # Reduce parameters for sample run
            config.generations = 10
            config.population_size = 5
            logger.info("Sample run configuration applied")
        
        # Create optimizer
        optimizer = create_label_set_optimizer(unified_config, test_dataset, config)
        
        # Establish baseline
        logger.info("Establishing baseline performance...")
        baseline_performance = optimizer.establish_baseline_performance()
        
        # Check if we have multiple label sets to optimize
        if len(optimizer.available_label_sets) < 2:
            logger.warning("Only one label set available - no optimization possible")
            logger.info(f"Current label set '{optimizer.original_label_set}' performance:")
            logger.info(f"   F1-Score: {baseline_performance['f1_score']:.4f}")
            logger.info(f"   Precision: {baseline_performance['precision']:.4f}")
            logger.info(f"   Recall: {baseline_performance['recall']:.4f}")
            return {"current_label_set": optimizer.original_label_set, "status": "no_optimization_needed"}
        
        # Run optimization
        logger.info("Starting label set optimization process...")
        best_individual, optimization_results = optimizer.optimize_label_sets()
        
        # Save results
        logger.info("Saving optimization results...")
        results_file = optimizer.save_results(optimization_results, results_dir)
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("LABEL SET OPTIMIZATION COMPLETE")
        logger.info("="*80)
        
        summary = optimization_results['optimization_summary']
        logger.info(f"Improvement: {summary['improvement_percentage']:.2f}%")
        logger.info(f"Target Met: {'YES' if summary['target_met'] else 'NO'}")
        logger.info(f"Total Time: {summary['total_time_minutes']:.1f} minutes")
        logger.info(f"API Calls: {summary['total_api_calls']:,}")
        
        best_config = optimization_results['best_label_set']
        logger.info(f"\nOPTIMAL LABEL SET:")
        logger.info(f"   Label Set: {best_config}")
        logger.info(f"   F1-Score: {optimization_results['best_performance']['f1_score']:.4f}")
        logger.info(f"   Precision: {optimization_results['best_performance']['precision']:.4f}")
        logger.info(f"   Recall: {optimization_results['best_performance']['recall']:.4f}")
        logger.info(f"   Avg Response Time: {optimization_results['best_performance']['avg_response_time_ms']:.1f}ms")
        
        # Show all label set results
        logger.info(f"\nALL LABEL SET RESULTS (ranked by F1-Score):")
        for i, result in enumerate(summary['all_results'][:5], 1):  # Top 5 results
            logger.info(f"   {i}. {result['label_set']}: F1={result['f1_score']:.4f}, "
                       f"P={result['precision']:.4f}, R={result['recall']:.4f}")
        
        logger.info(f"\nRecommendation: {optimization_results['recommendation']}")
        logger.info(f"Results saved to: {results_file}")
        
        return {
            "best_label_set": best_config,
            "improvement": summary['improvement_percentage'],
            "results_file": results_file,
            "all_results": summary['all_results']
        }

    except KeyboardInterrupt:
        logger.info("Label optimization interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Label optimization failed: {e}")
        logger.exception("Full error details:")
        return 1
# ============================================================================

# ============================================================================
# SHOW USAGE HELP (Updated for Phase 4a)
# ============================================================================
def show_usage():
    """Show usage information"""
    logger = logging.getLogger(__name__)
    
    logger.info("Ash-Thrash Crisis Detection Testing Suite v3.1")
    logger.info("Phase 3a: Advanced Tuning Intelligence Enabled")
    logger.info("Phase 4a: Client-Side Crisis Classification Enabled")
    logger.info("")
    logger.info("Usage:")
    logger.info("  docker compose exec ash-thrash python main.py                         # Run comprehensive test suite")
    logger.info("  docker compose exec ash-thrash python main.py [category]              # Run specific category test")
    logger.info("  docker compose exec ash-thrash python analyze.py                      # Analyze results")
    logger.info("  docker compose exec ash-thrash python main.py weight-optimize         # Run Model Weight Optimization (Full)")
    logger.info("  docker compose exec ash-thrash python main.py weight-optimize-sample  # Run Model Weight Optimization (Sample)")
    logger.info("  docker compose exec ash-thrash python main.py label-optimize          # Run Model Label Optimization (Full)")
    logger.info("  docker compose exec ash-thrash python main.py label-optimize-sample   # Run Model Label Optimization (Sample)")
    logger.info("")
    logger.info("Available categories:")
    logger.info("  definite_high       # High priority crisis phrases")
    logger.info("  definite_medium     # Medium priority crisis phrases") 
    logger.info("  definite_low        # Low priority crisis phrases")
    logger.info("  definite_none       # No priority crisis phrases")
    logger.info("  maybe_high_medium   # High/medium boundary tests")
    logger.info("  maybe_medium_low    # Medium/low boundary tests")
    logger.info("  maybe_low_none      # Low/none boundary tests")
    logger.info("")
    logger.info("Generated reports and analysis:")
    logger.info("  reports/latest_run_summary.md           # Latest test results")
    logger.info("  reports/threshold_recommendations.md    # NLP tuning suggestions")
    logger.info("  reports/historical_performance.md       # Performance trends")
    logger.info("  results/tuning_analysis/*.json          # Advanced tuning intelligence")
    logger.info("  reports/recommended_thresholds_*.env   # Recommended threshold settings")
    logger.info("")
    logger.info("Phase 3a Features:")
    logger.info("  Intelligent threshold mapping by ensemble mode")
    logger.info("  Confidence-based recommendations with risk assessment") 
    logger.info("  Boundary testing suggestions for optimal values")
    logger.info("  Safety-first analysis for LGBTQIA+ community protection")
    logger.info("  Automated .env file generation with recommended settings")
    logger.info("")
    logger.info("Phase 4a Features:")
    logger.info("  Dual classification: Server suggestions + Client determinations")
    logger.info("  Multiple classification strategies: conservative, aggressive, consensus, client-only")
    logger.info("  Configurable threshold sets: standard, conservative, aggressive")
    logger.info("  Category-specific strategy overrides for optimal performance")
    logger.info("  Real-time agreement tracking between server and client classifications")
    logger.info("  Performance comparison reports showing client vs server accuracy")
    logger.info("")
    logger.info("Client Classification Configuration:")
    logger.info("  Edit config/client_classification.json to adjust:")
    logger.info("    - enable_client_classification: true/false")
    logger.info("    - strategy: conservative/aggressive/consensus/client_only")
    logger.info("    - threshold_config: standard/conservative/aggressive")
    logger.info("")
# ============================================================================

# ============================================================================
# MAIN APPLICATION ENTRY POINT (Updated for Phase 4a)
# ============================================================================
if __name__ == "__main__":
    
    try:
        # Initialize unified configuration manager first
        unified_config = create_unified_config_manager()
        
        # Setup unified logging
        setup_unified_logging(unified_config)
        
        logger = logging.getLogger(__name__)
        logger.info("Starting Ash-Thrash Crisis Detection Testing Suite v3.1")
        logger.info("Phase 3a: Advanced Tuning Intelligence")
        logger.info("Phase 4a: Client-Side Crisis Classification")
        logger.info("Serving The Alphabet Cartel LGBTQIA+ Community")
        logger.info("Repository: https://github.com/the-alphabet-cartel/ash-thrash")
        logger.info("Discord: https://discord.gg/alphabetcartel")
        logger.info("Website: https://alphabetcartel.org")
        logger.info("")
        logger.info("=" * 70)
        logger.info("          ASH-THRASH STARTUP - PHASE 4A")
        logger.info("=" * 70)
        
        # Initialize all managers (including Phase 4a client classification)
        managers = initialize_managers()
        
        # Parse command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] in ['--help', '-h', 'help']:
                show_usage()
                sys.exit(0)
            elif sys.argv[1] in ['weight-optimize']:
                result = weight_optimizer()
            elif sys.argv[1] in ['weight-optimize-sample']:
                sample_run = True
                result = weight_optimizer(sample_run)
            elif sys.argv[1] in ['label-optimize']:
                result = label_optimizer()
            elif sys.argv[1] in ['label-optimize-sample']:
                sample_run = True
                result = label_optimizer(sample_run)
            else:
                # Run specific category test
                category_name = sys.argv[1]
                result = run_category_test(managers, category_name)
        else:
            # Run comprehensive test suite
            result = run_comprehensive_test(managers)
        
        # Exit with appropriate codes
        if result is None:
            logger.error("Test execution failed")
            sys.exit(1)
        elif result.early_termination:
            logger.warning("Tests terminated early due to poor performance")
            logger.info("Check generated tuning analysis files for intelligent threshold recommendations")
            sys.exit(2)
        else:
            logger.info("Test execution completed successfully")
            logger.info("Analysis files and recommendations available in ./reports/ and ./results/ directories")
            sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)
# ============================================================================