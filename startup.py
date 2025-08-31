# ash-thrash/startup.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Container Startup and Warm-up Script for Ash-Thrash Service
---
FILE VERSION: v3.1-1a-1
LAST MODIFIED: 2025-08-30
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import time
import signal
import sys
from pathlib import Path
import colorlog

# Manager imports
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.nlp_client import create_nlp_client_manager
from managers.test_engine import create_test_engine_manager

def setup_logging(unified_config_manager):
    """Setup colorlog logging for startup"""
    try:
        log_level = unified_config_manager.get_config_section('logging_settings', 'global_settings.log_level', 'INFO')
        
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s: %(message)s',
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
        
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Optional file logging
        enable_file_logging = unified_config_manager.get_config_section('logging_settings', 'global_settings.enable_file_output', False)
        if enable_file_logging:
            log_file = unified_config_manager.get_config_section('logging_settings', 'global_settings.log_file', 'ash-thrash.log')
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
        
        logging.info("Startup logging configured successfully")
        
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to setup startup logging: {e}")

def initialize_and_warm_managers():
    """Initialize all managers and warm up the system"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("           ASH-THRASH CONTAINER STARTUP")
    logger.info("=" * 70)
    
    try:
        # Initialize all managers
        logger.info("Initializing all Ash-Thrash managers...")
        
        unified_config = create_unified_config_manager()
        logging_config = create_logging_config_manager(unified_config)
        nlp_client = create_nlp_client_manager(unified_config)
        test_engine = create_test_engine_manager(unified_config, nlp_client)
        
        managers = {
            'unified_config': unified_config,
            'logging_config': logging_config,
            'nlp_client': nlp_client,
            'test_engine': test_engine,
        }
        
        logger.info(f"All managers initialized successfully: {len(managers)} total")
        
        # Warm up NLP server connection
        logger.info("Warming up NLP server connection...")
        is_ready, status = nlp_client.verify_server_ready()
        if is_ready:
            logger.info(f"NLP server connection verified: {status}")
            
            # Test analysis to warm up models
            logger.info("Warming up NLP models...")
            result = nlp_client.analyze_message("System warmup test", "warmup_user", "warmup_channel")
            if result:
                logger.info(f"Model warmup successful: {result.crisis_level} in {result.processing_time_ms:.1f}ms")
            else:
                logger.warning("Model warmup failed, but system will continue")
        else:
            logger.error(f"NLP server not ready: {status}")
            logger.error("System will continue but tests may fail")
        
        # Pre-load configuration cache
        logger.info("Pre-loading configuration cache...")
        test_categories = unified_config.get_config_section('test_settings', 'test_categories', {})
        logger.info(f"Cached {len(test_categories)} test categories")
        
        # Verify directories exist
        logger.info("Verifying storage directories...")
        storage_config = unified_config.get_config_section('test_settings', 'storage', {})
        for dir_name, dir_path in [
            ('results', storage_config.get('results_directory', './results')),
            ('reports', storage_config.get('reports_directory', './reports')),
            ('logs', storage_config.get('log_directory', './logs'))
        ]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory verified: {dir_name} -> {dir_path}")
        
        # Get cache statistics if caching is enabled
        cache_stats = unified_config.get_cache_statistics()
        if cache_stats.get('enabled'):
            logger.info(f"Configuration cache ready: {cache_stats.get('cache_entries', 0)} entries, "
                       f"{cache_stats.get('memory_usage_mb', 0):.1f}MB")
        
        logger.info("=" * 70)
        logger.info("           SYSTEM READY FOR TESTING")
        logger.info("=" * 70)
        logger.info("Available commands:")
        logger.info("  docker compose exec ash-thrash python main.py                    # Full test suite")
        logger.info("  docker compose exec ash-thrash python main.py [category]        # Single category")
        logger.info("  docker compose exec ash-thrash python analyze_results.py       # Analyze results")
        logger.info("=" * 70)
        
        return managers
        
    except Exception as e:
        logger.error(f"Manager initialization failed: {e}")
        raise

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger = logging.getLogger(__name__)
    logger.info("Received shutdown signal, cleaning up...")
    sys.exit(0)

def main():
    """Main startup daemon"""
    print("Starting Ash-Thrash Crisis Detection Testing Suite")
    print("Serving The Alphabet Cartel LGBTQIA+ Community")
    print("Repository: https://github.com/the-alphabet-cartel/ash-thrash")
    print("Discord: https://discord.gg/alphabetcartel")
    print("Website: https://alphabetcartel.org")
    print("")
    
    try:
        # Setup signal handling
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize configuration first (minimal logging)
        unified_config = create_unified_config_manager()
        
        # Setup full logging
        setup_logging(unified_config)
        
        # Initialize and warm up all managers
        managers = initialize_and_warm_managers()
        
        # Keep container running
        logger = logging.getLogger(__name__)
        logger.info("Container startup complete - entering daemon mode...")
        logger.info("System is warm and ready for immediate testing")
        
        # Keep alive loop
        while True:
            time.sleep(60)  # Check every minute
            
            # Optional: Periodic health check
            try:
                nlp_client = managers['nlp_client']
                health_result = nlp_client.check_health()
                if health_result.status.value != 'healthy':
                    logger.warning(f"NLP server health check failed: {health_result.error_message}")
            except Exception as e:
                logger.warning(f"Health check error: {e}")
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()