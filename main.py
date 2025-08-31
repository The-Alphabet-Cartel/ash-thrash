# ash-thrash/main.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Ash-Thrash Main Application Entry Point for Ash Thrash Service
---
FILE VERSION: v3.1-2a-1
LAST MODIFIED: 2025-08-31
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import sys
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
# UNIFIED MANAGER INITIALIZATION
# ============================================================================

def initialize_managers():
    """
    Initialize all managers using factory functions (Clean Architecture v3.1)
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

        managers = {
            'unified_config': unified_config,
            'logging_config': logging_config,
            'nlp_client': nlp_client,
            'test_engine': test_engine,
            'results_manager': results_manager,
            'analyze_manager': analyze_manager,
        }
        
        logger.info(f"All managers initialized successfully: {len(managers)} total")
        return managers
        
    except Exception as e:
        logger.error(f"Manager initialization failed: {e}")
        raise

# ============================================================================
# ENHANCED TEST EXECUTION FUNCTIONS WITH INTEGRATED REPORTING
# ============================================================================

def run_comprehensive_test(managers):
    """Run comprehensive test suite across all categories with integrated reporting"""
    logger = logging.getLogger(__name__)
    test_engine = managers['test_engine']
    results_manager = managers['results_manager']
    analyze_manager = managers['analyze_manager']
    
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
        
        # PHASE 2A ENHANCEMENT: Generate markdown reports automatically
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
        
        # PHASE 2A ENHANCEMENT: Display quick analysis summary using the manager
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
    """Run test for specific category with integrated reporting"""
    logger = logging.getLogger(__name__)
    test_engine = managers['test_engine']
    results_manager = managers['results_manager']
    analyze_manager = managers['analyze_manager']
    
    logger.info(f"Starting test for category: {category_name}")
    
    try:
        suite_result = test_engine.run_test_suite([category_name])
        
        # Store test results to disk
        try:
            result_path = results_manager.store_test_results(suite_result)
            logger.info(f"Test results saved to: {result_path}")
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
        
        # PHASE 2A ENHANCEMENT: Generate reports for single category tests too
        try:
            logger.info("Generating markdown reports for category test...")
            report_success = analyze_manager.generate_all_reports()
            if report_success:
                logger.info("✅ Markdown reports updated with category test results")
            else:
                logger.warning("⚠️  Some markdown reports failed to generate")
        except Exception as e:
            logger.error(f"Failed to generate markdown reports: {e}")
        
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

def show_usage():
    """Show usage information"""
    logger = logging.getLogger(__name__)
    
    logger.info("Ash-Thrash Crisis Detection Testing Suite")
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
    logger.info("Reports generated:")
    logger.info("  reports/latest_run_summary.md      # Latest test results")
    logger.info("  reports/threshold_recommendations.md # NLP tuning suggestions")
    logger.info("  reports/historical_performance.md   # Performance trends")
    logger.info("")

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    
    try:
        # Initialize unified configuration manager first
        unified_config = create_unified_config_manager()
        
        # Setup unified logging
        setup_unified_logging(unified_config)
        
        logger = logging.getLogger(__name__)
        logger.info("Starting Ash-Thrash Crisis Detection Testing Suite")
        logger.info("Serving The Alphabet Cartel LGBTQIA+ Community")
        logger.info("Repository: https://github.com/the-alphabet-cartel/ash-thrash")
        logger.info("Discord: https://discord.gg/alphabetcartel")
        logger.info("Website: https://alphabetcartel.org")
        logger.info("")
        logger.info("=" * 70)
        logger.info("          ASH-THRASH STARTUP")
        logger.info("=" * 70)
        
        # Initialize all managers
        managers = initialize_managers()
        
        # Parse command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] in ['--help', '-h', 'help']:
                show_usage()
                sys.exit(0)
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
            logger.info("Check generated reports for detailed analysis and recommendations")
            sys.exit(2)
        else:
            logger.info("Test execution completed successfully")
            logger.info("Markdown reports available in ./reports/ directory")
            sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)