# ash-thrash/main.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Ash-Thrash Main Application Entry Point for Ash Thrash Service
---
FILE VERSION: v3.1-3a-3
LAST MODIFIED: 2025-08-31
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

# ============================================================================
# UNIFIED CONFIGURATION LOGGING SETUP
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
# UNIFIED MANAGER INITIALIZATION - PHASE 3A ENHANCED
# ============================================================================

def initialize_managers():
    """
    Initialize all managers using factory functions (Clean Architecture v3.1) - Phase 3a Enhanced
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Initializing Ash-Thrash managers...")
    logger.info("=" * 70)
    
    try:
        # Core configuration managers
        unified_config = create_unified_config_manager()
        logging_config = create_logging_config_manager(unified_config)
        
        # Testing managers
        nlp_client = create_nlp_client_manager(unified_config)
        test_engine = create_test_engine_manager(unified_config, nlp_client)
        
        # Results and analysis managers
        results_manager = create_results_manager(unified_config)
        analyze_manager = create_analyze_results_manager(unified_config, results_manager, logging_config)
        
        # Advanced tuning intelligence manager
        tuning_manager = create_tuning_suggestions_manager(unified_config, results_manager, analyze_manager)

        managers = {
            'unified_config': unified_config,
            'logging_config': logging_config,
            'nlp_client': nlp_client,
            'test_engine': test_engine,
            'results_manager': results_manager,
            'analyze_manager': analyze_manager,
            'tuning_manager': tuning_manager,
        }
        
        logger.info(f"All managers initialized successfully: {len(managers)} total")
        logger.info("✅ Phase 3a: Advanced Tuning Intelligence enabled")
        return managers
        
    except Exception as e:
        logger.error(f"Manager initialization failed: {e}")
        raise

# ============================================================================
# ENHANCED TEST EXECUTION FUNCTIONS WITH PHASE 3A TUNING INTELLIGENCE
# ============================================================================

def run_comprehensive_test(managers):
    """Run comprehensive test suite across all categories with integrated reporting and Phase 3a tuning intelligence"""
    logger = logging.getLogger(__name__)
    test_engine = managers['test_engine']
    results_manager = managers['results_manager']
    analyze_manager = managers['analyze_manager']
    tuning_manager = managers['tuning_manager']  # Phase 3a addition
    
    logger.info("Starting comprehensive test suite...")
    
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
                logger.info("✅ All markdown reports generated successfully:")
                logger.info("   📄 reports/latest_run_summary.md")
                logger.info("   🔧 reports/threshold_recommendations.md") 
                logger.info("   📈 reports/historical_performance.md")
            else:
                logger.warning("⚠️  Some markdown reports failed to generate")
        except Exception as e:
            logger.error(f"Failed to generate markdown reports: {e}")
        
        # Generate advanced tuning intelligence and recommendations
        try:
            logger.info("=" * 50)
            logger.info("🧠 PHASE 3A: GENERATING ADVANCED TUNING INTELLIGENCE")
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
            logger.info("🎯 TUNING INTELLIGENCE SUMMARY")
            logger.info("=" * 50)
            logger.info(f"Current ensemble mode: {tuning_analysis.ensemble_mode.value}")
            logger.info(f"Critical issues identified: {len(tuning_analysis.critical_issues)}")
            logger.info(f"Threshold recommendations: {len(tuning_analysis.recommendations)}")
            logger.info(f"Risk level: {tuning_analysis.risk_assessment.get('overall_risk_level', 'unknown')}")
            
            # Display confidence summary
            confidence_summary = tuning_analysis.confidence_summary
            if confidence_summary.get('total_recommendations', 0) > 0:
                logger.info("Recommendation confidence breakdown:")
                logger.info(f"  🟢 High confidence: {confidence_summary.get('high', 0)} recommendations")
                logger.info(f"  🟡 Medium confidence: {confidence_summary.get('medium', 0)} recommendations")
                logger.info(f"  🟠 Low confidence: {confidence_summary.get('low', 0)} recommendations")
                logger.info(f"  🔴 Uncertain: {confidence_summary.get('uncertain', 0)} recommendations")
            
            # Display critical issues
            if tuning_analysis.critical_issues:
                logger.warning("🚨 Critical issues requiring immediate attention:")
                for issue in tuning_analysis.critical_issues[:3]:  # Show first 3
                    logger.warning(f"   • {issue}")
                if len(tuning_analysis.critical_issues) > 3:
                    logger.warning(f"   • ... and {len(tuning_analysis.critical_issues) - 3} more")
            
            # Display file locations
            logger.info("📁 Analysis files generated:")
            if analysis_file:
                logger.info(f"   📊 Detailed analysis: {analysis_file}")
            if env_file:
                logger.info(f"   ⚙️  Recommended settings: {env_file}")
            
            # Show implementation order preview
            if tuning_analysis.implementation_order:
                logger.info("🔄 Implementation priority order (top 3):")
                for i, order_item in enumerate(tuning_analysis.implementation_order[:3], 1):
                    logger.info(f"   {i}. {order_item}")
                if len(tuning_analysis.implementation_order) > 3:
                    logger.info(f"   ... and {len(tuning_analysis.implementation_order) - 3} more")
            
        except Exception as e:
            logger.error(f"Phase 3a tuning intelligence failed: {e}")
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
    """Run test for specific category with integrated reporting and Phase 3a tuning intelligence"""
    logger = logging.getLogger(__name__)
    test_engine = managers['test_engine']
    results_manager = managers['results_manager']
    analyze_manager = managers['analyze_manager']
    tuning_manager = managers['tuning_manager']  # Phase 3a addition
    
    logger.info(f"Starting test for category: {category_name}")
    
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
                logger.info("✅ Markdown reports updated with category test results")
            else:
                logger.warning("⚠️  Some markdown reports failed to generate")
        except Exception as e:
            logger.error(f"Failed to generate markdown reports: {e}")
        
        # Generate targeted tuning intelligence for single category
        try:
            logger.info("=" * 50)
            logger.info("🧠 GENERATING CATEGORY-SPECIFIC TUNING ANALYSIS")
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
            logger.info(f"🎯 {category_name.upper()} TUNING ANALYSIS")
            logger.info(f"Category-specific recommendations: {len(category_specific_recs)}")
            
            if category_specific_recs:
                logger.info("Top recommendations for this category:")
                for i, rec in enumerate(category_specific_recs[:2], 1):  # Show top 2
                    logger.info(f"  {i}. {rec.variable_name}: {rec.current_value:.3f} → {rec.recommended_value:.3f}")
                    logger.info(f"     Risk: {rec.risk_level.value}, Confidence: {rec.confidence_level.value}")
            else:
                # Show general recommendations that might help
                if tuning_analysis.recommendations:
                    logger.info("General recommendations that may impact this category:")
                    for i, rec in enumerate(tuning_analysis.recommendations[:2], 1):
                        logger.info(f"  {i}. {rec.variable_name}: {rec.current_value:.3f} → {rec.recommended_value:.3f}")
                        logger.info(f"     Risk: {rec.risk_level.value}, Confidence: {rec.confidence_level.value}")
                else:
                    logger.info("No specific threshold recommendations generated for this category")
            
            # Save analysis files with category prefix
            if tuning_analysis.recommendations:
                analysis_file = tuning_manager.save_tuning_analysis(tuning_analysis)
                env_file = tuning_manager.generate_env_file_recommendations(tuning_analysis)
                
                logger.info("📁 Category analysis files:")
                if analysis_file:
                    logger.info(f"   📊 Analysis: {analysis_file}")
                if env_file:
                    logger.info(f"   ⚙️  Settings: {env_file}")
            
        except Exception as e:
            logger.error(f"Phase 3a category tuning analysis failed: {e}")
            logger.warning("Continuing with standard category reporting...")
        
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
                logger.info("✅ Category meeting target performance")
            else:
                if category_result.is_critical:
                    logger.error(f"🚨 CRITICAL: Category {category_result.pass_rate:.1f}% below {category_result.target_pass_rate}% target")
                else:
                    logger.warning(f"⚠️  Category {category_result.pass_rate:.1f}% below {category_result.target_pass_rate}% target")
        
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
        logger.debug("🔍 CONVERTING SUITE RESULT TO DICT")
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
                                    logger.debug(f"  Failed test {len(failed_tests)}: {failed_test['expected_crisis_level']} → {failed_test['actual_crisis_level']}")
                        
                        logger.debug(f"Processed test details: {passed_count} passed, {failed_count} failed")
                        
                        if failed_tests:
                            category_data['failed_tests_details'] = failed_tests
                            logger.debug(f"Added {len(failed_tests)} failed test details to category data")
                        else:
                            logger.warning(f"No failed tests found despite failed_tests count = {category_data['summary']['failed_tests']}")
                else:
                    logger.warning(f"No test details found for category {category_name}")
                
                test_results['category_results'][category_name] = category_data
        else:
            logger.warning("No category results found in suite result")
        
        logger.debug("=" * 50)
        logger.debug("🔍 FINAL CONVERTED DICTIONARY STRUCTURE")
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

    def weight_optimizer(sample_run=None):
        """Optimize model weights (Full)"""
        from managers.weight_optimizer import OptimizationConfiguration, create_weight_optimizer
        from managers.weight_data_loader import create_weight_data_loader

        generations = 50
        population_size = 20
        api_endpoint = 'http://localhost:8881/analyze'
        results_dir = './results'
        
        try:
            logger.info("🚀 Starting Ash-NLP Weight Optimization")
            logger.info(f"Configuration: {generations} generations, {population_size} population")
            logger.info("📊 Loading test dataset...")

            weight_data_loader = create_weight_data_loader(results_dir)

            if sample_run:
                logger.info("🧪 Running in sample mode with reduced dataset")
                test_dataset = weight_data_loader.create_sample_dataset(sample_size=10)
            else:
                test_dataset = weight_data_loader.load_all_test_data()
            
            validation_report = weight_data_loader.validate_dataset(test_dataset)
            if not validation_report['valid']:
                logger.error(f"Dataset validation failed: {validation_report['issues']}")
                return 1
            
            logger.info(f"✅ Dataset loaded: {validation_report['total_phrases']} total phrases")

            config = OptimizationConfiguration(
                population_size=population_size,
                generations=generations,
                api_endpoint=api_endpoint
            )
            
            if sample_run:
                # Reduce parameters for sample run
                generations = 10
                population_size = 8
                logger.info("🧪 Sample run configuration applied")
            
            # Create optimizer
            optimizer = create_weight_optimizer(test_dataset, config)
            
            # Establish baseline
            logger.info("📏 Establishing baseline performance...")
            baseline_performance = optimizer.establish_baseline_performance()
            
            # Run optimization
            logger.info("🎯 Starting optimization process...")
            best_individual, optimization_results = optimizer.optimize_weights()
            
            # Save results
            logger.info("💾 Saving optimization results...")
            results_file = optimizer.save_results(optimization_results, results_dir)
            
            # Print summary
            print("\n" + "="*80)
            print("🎉 OPTIMIZATION COMPLETE")
            print("="*80)
            
            summary = optimization_results['optimization_summary']
            print(f"📊 Improvement: {summary['improvement_percentage']:.2f}%")
            print(f"🎯 Target Met: {'YES' if summary['target_met'] else 'NO'}")
            print(f"⏱️  Total Time: {summary['total_time_minutes']:.1f} minutes")
            print(f"🔧 API Calls: {summary['total_api_calls']:,}")
            
            best_config = optimization_results['best_configuration']
            print(f"\n🏆 OPTIMAL CONFIGURATION:")
            print(f"   Ensemble Mode: {best_config['ensemble_mode']}")
            print(f"   Depression Weight: {best_config['weights']['depression']:.3f}")
            print(f"   Sentiment Weight: {best_config['weights']['sentiment']:.3f}")
            print(f"   Distress Weight: {best_config['weights']['emotional_distress']:.3f}")
            
            print(f"\n💡 Recommendation: {optimization_results['recommendation']}")
            print(f"📁 Results saved to: {results_file}")
            
            return 0 if summary['target_met'] else 2

        except KeyboardInterrupt:
            logger.info("⏹️  Optimization interrupted by user")
            return 130
        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            logger.exception("Full error details:")
            return 1

def show_usage():
    """Show usage information with Phase 3a enhancements"""
    logger = logging.getLogger(__name__)
    
    logger.info("Ash-Thrash Crisis Detection Testing Suite v3.1")
    logger.info("Phase 3a: Advanced Tuning Intelligence Enabled")
    logger.info("")
    logger.info("Usage:")
    logger.info("  python main.py                    # Run comprehensive test suite")
    logger.info("  python main.py [category]         # Run specific category test")
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
    logger.info("  📄 reports/latest_run_summary.md           # Latest test results")
    logger.info("  🔧 reports/threshold_recommendations.md    # NLP tuning suggestions")
    logger.info("  📈 reports/historical_performance.md       # Performance trends")
    logger.info("  🧠 results/tuning_analysis/*.json          # Advanced tuning intelligence")
    logger.info("  ⚙️  reports/recommended_thresholds_*.env   # Recommended threshold settings")
    logger.info("")
    logger.info("Phase 3a Features:")
    logger.info("  🎯 Intelligent threshold mapping by ensemble mode")
    logger.info("  🔍 Confidence-based recommendations with risk assessment") 
    logger.info("  📊 Boundary testing suggestions for optimal values")
    logger.info("  🚨 Safety-first analysis for LGBTQIA+ community protection")
    logger.info("  📁 Automated .env file generation with recommended settings")
    logger.info("")

# ============================================================================
# MAIN APPLICATION ENTRY POINT - PHASE 3A ENHANCED
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
        logger.info("Serving The Alphabet Cartel LGBTQIA+ Community")
        logger.info("Repository: https://github.com/the-alphabet-cartel/ash-thrash")
        logger.info("Discord: https://discord.gg/alphabetcartel")
        logger.info("Website: https://alphabetcartel.org")
        logger.info("")
        logger.info("=" * 70)
        logger.info("          ASH-THRASH STARTUP - PHASE 3A")
        logger.info("=" * 70)
        
        # Initialize all managers (including Phase 3a tuning manager)
        managers = initialize_managers()
        
        # Parse command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] in ['--help', '-h', 'help']:
                show_usage()
                sys.exit(0)
            elif sys.argv[1] in ['optimize']:
                result = weight_optimizer()
            elif sys.argv[1] in ['optimize-sample']:
                sample_run = True
                result = weight_optimizer(sample_run)
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
            logger.info("💡 Check generated tuning analysis files for intelligent threshold recommendations")
            sys.exit(2)
        else:
            logger.info("Test execution completed successfully")
            logger.info("📁 Analysis files and recommendations available in ./reports/ and ./results/ directories")
            sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)