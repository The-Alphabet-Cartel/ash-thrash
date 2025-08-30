# ash-thrash/main.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Ash-Thrash Main Application Entry Point for Ash Thrash Service
---
FILE VERSION: v3.1-1
LAST MODIFIED: 2025-08-29
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-nlp
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import colorlog

# ============================================================================
# MANAGER IMPORTS - ALL USING FACTORY FUNCTIONS
# ============================================================================
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager

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
        log_file = unified_config_manager.get_config_section('logging_settings', 'global_settings.log_file', 'nlp_service.log')
        
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
                logging.info(f"📁 File logging enabled: {log_file}")
            except Exception as e:
                logging.warning(f"⚠️ Could not setup file logging: {e}")
        
        logging.info("🎨 Unified colorlog logging configured successfully")
        logging.info(f"📊 Log level: {log_level}")
        
    except Exception as e:
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)
        logging.error(f"❌ Failed to setup unified logging: {e}")
        logging.info("🔄 Using fallback basic logging configuration")

# ============================================================================
# UNIFIED MANAGER INITIALIZATION
# ============================================================================

def initialize_unified_managers():
    """
    Initialize all managers using UnifiedConfigManager
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("🚀 Initializing unified configuration management system...")
    logger.info("=" * 70)
    
    try:
        logger.info("=" * 70)
        logger.info("🏗️ Creating UnifiedConfigManager...")
        logger.info("=" * 70)
        unified_config = create_unified_config_manager()
        logger.info("=" * 70)
        logger.info("✅ UnifiedConfigManager created successfully")
        logger.info("=" * 70)

        logger.info("=" * 70)
        logger.info("🔧 Initializing logging config manager...")
        logger.info("=" * 70)
        logging_config = create_logging_config_manager(unified_config)
        logger.info("=" * 70)
        logger.info("✅ Logging config manager initialized...")
        logger.info("=" * 70)

        managers = {
            'unified_config': unified_config,
            'logging_config': logging_config,
        }
        
        logger.info("🎉 ======================================================== 🎉")
        logger.info("🎉 All managers initialized successfully with unified configuration 🎉")
        logger.info(f"📊 Total managers created: {len(managers)}")
        logger.info("🎉 ======================================================== 🎉")
        
        return managers
        
    except Exception as e:
        logger.error(f"❌ Manager initialization failed: {e}")
        raise

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    
    try:
        print("🎉 Starting Ash-Thrash Crisis Detection Testing Suite")
        print("🏳️‍🌈 Serving The Alphabet Cartel LGBTQIA+ Community")
        print("🏛️ Repository: https://github.com/the-alphabet-cartel/ash-nlp")
        print("💬 Discord: https://discord.gg/alphabetcartel")
        print("🌐 Website: https://alphabetcartel.org")
        print("")
        
        # Initialize unified configuration manager first
        unified_config = create_unified_config_manager()
        
        # Setup unified logging
        setup_unified_logging(unified_config)
        
        logger = logging.getLogger(__name__)
        logger.info("=" * 70)
        logger.info("          🚀 ASH-THRASH STARTUP")
        logger.info("=" * 70)
        
        # Clear cache first to ensure validation applies
        try:
            cache_cleared = unified_config.clear_configuration_cache()
            logger.info(f"🧹 Cleared {cache_cleared} cache entries to ensure validation applies")
        except Exception as e:
            logger.warning(f"⚠️ Could not clear cache: {e}")
        
        logger.info("=" * 70)
        logger.info("🏳️‍🌈 Ready to serve The Alphabet Cartel community!")
        logger.info("=" * 70)
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise