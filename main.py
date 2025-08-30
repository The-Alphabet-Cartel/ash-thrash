# ash-thrash/main.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Ash-Thrash Main Application Entry Point for Ash Thrash Service
---
FILE VERSION: v3.1-1a-1
LAST MODIFIED: 2025-08-30
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import sys
import colorlog

# ============================================================================
# MANAGER IMPORTS - ALL USING FACTORY FUNCTIONS
# ============================================================================
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.nlp_client import create_nlp_client_manager
from managers.test_engine import create_test_engine_manager

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
    Initialize all managers using factory functions
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

        managers = {
            'unified_config': unified_config,
            'logging_config': logging_config,
            'nlp_client': nlp_client,
            'test_engine': test_engine,
        }
        
        logger.info(f"All managers initialized successfully: {len(managers)} total")
        return managers
        
    except Exception as e:
        logger.error(f"Manager initialization failed: {e}")
        raise

# ============================================================================
# TEST EXECUTION FUNCTIONS
# ============================================================================

def run_comprehensive_test(managers):
    """Run comprehensive test suite across all categories"""
    logger = logging.getLogger(__name__)
    test_engine = managers['test_engine']
    
    logger.info("Starting comprehensive test suite...")
    
    try:
        # Run all category tests
        suite_result = test_engine.run_test_suite()
        
        # Log summary
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
        
        return suite_result
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return None

def run_category_test(managers, category_name: str):
    """Run test for specific category"""
    logger = logging.getLogger(__name__)
    test_engine = managers['test_engine']
    
    logger.info(f"Starting test for category: {category_name}")
    
    try:
        suite_result = test_engine.run_test_suite([category_name])
        
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
        
        return suite_result
        
    except Exception as e:
        logger.error(f"Category test failed: {e}")
        return None

def show_usage():
    """Show usage information"""
    print("\nAsh-Thrash Crisis Detection Testing Suite")
    print("Usage:")
    print("  python main.py                    # Run comprehensive test suite")
    print("  python main.py [category]         # Run specific category test")
    print("\nAvailable categories:")
    print("  definite_high       # High priority crisis phrases")
    print("  definite_medium     # Medium priority crisis phrases") 
    print("  definite_low        # Low priority crisis phrases")
    print("  definite_none       # No priority crisis phrases")
    print("  maybe_high_medium   # High/medium boundary tests")
    print("  maybe_medium_low    # Medium/low boundary tests")
    print("  maybe_low_none      # Low/none boundary tests")
    print()

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    
    try:
        print("Starting Ash-Thrash Crisis Detection Testing Suite")
        print("Serving The Alphabet Cartel LGBTQIA+ Community")
        print("Repository: https://github.com/the-alphabet-cartel/ash-thrash")
        print("Discord: https://discord.gg/alphabetcartel")
        print("Website: https://alphabetcartel.org")
        print("")
        
        # Initialize unified configuration manager first
        unified_config = create_unified_config_manager()
        
        # Setup unified logging
        setup_unified_logging(unified_config)
        
        logger = logging.getLogger(__name__)
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
        
        if result is None:
            logger.error("Test execution failed")
            sys.exit(1)
        elif result.early_termination:
            logger.warning("Tests terminated early due to poor performance")
            sys.exit(2)
        else:
            logger.info("Test execution completed successfully")
            sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)