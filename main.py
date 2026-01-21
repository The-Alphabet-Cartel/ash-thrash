#!/usr/bin/env python3
"""
============================================================================
Ash-Thrash: Discord Crisis Detection Testing Suite
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Validate  → Verify crisis detection accuracy through live Ash-NLP integration testing
    Challenge → Stress test the system with edge cases and adversarial scenarios
    Guard     → Prevent regressions that could compromise detection reliability
    Protect   → Safeguard our LGBTQIA+ community through rigorous quality assurance

============================================================================
Main Entry Point for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.7-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 1 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

USAGE:
    # Run with default settings
    python main.py

    # Run with testing environment
    THRASH_ENVIRONMENT=testing python main.py

ENVIRONMENT VARIABLES:
    THRASH_ENVIRONMENT     - Environment (production, testing, development)
    THRASH_LOG_LEVEL       - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    THRASH_LOG_FORMAT      - Log format (human, json)
    See .env.template for complete list
"""

import asyncio
import signal
import sys
from typing import Optional

# Module version
__version__ = "v5.0-1-1.7-1"

# =============================================================================
# Manager Imports (Phase 1)
# =============================================================================

from src.managers import (
    create_config_manager,
    create_secrets_manager,
    create_logging_config_manager,
    create_nlp_client_manager,
    create_phrase_loader_manager,
    ConfigManager,
    SecretsManager,
    LoggingConfigManager,
    NLPClientManager,
    PhraseLoaderManager,
)


# =============================================================================
# Application Class
# =============================================================================

class AshThrash:
    """
    Main application class for Ash-Thrash testing suite.
    
    Manages lifecycle of all managers and coordinates test execution.
    
    Attributes:
        config: ConfigManager instance
        secrets: SecretsManager instance
        logging_mgr: LoggingConfigManager instance
        nlp_client: NLPClientManager instance
        phrase_loader: PhraseLoaderManager instance
    """
    
    def __init__(self):
        """Initialize the application (managers created in startup)."""
        self.config: Optional[ConfigManager] = None
        self.secrets: Optional[SecretsManager] = None
        self.logging_mgr: Optional[LoggingConfigManager] = None
        self.nlp_client: Optional[NLPClientManager] = None
        self.phrase_loader: Optional[PhraseLoaderManager] = None
        self._logger = None
        self._shutdown_event = asyncio.Event()
    
    async def startup(self) -> bool:
        """
        Initialize all managers and verify system readiness.
        
        Returns:
            True if startup successful, False otherwise
        """
        try:
            # Step 1: Configuration Manager
            self.config = create_config_manager()
            
            # Step 2: Secrets Manager
            self.secrets = create_secrets_manager()
            
            # Step 3: Logging Manager (depends on config)
            self.logging_mgr = create_logging_config_manager(
                config_manager=self.config
            )
            self._logger = self.logging_mgr.get_logger("main")
            
            # Print startup banner
            self._print_banner()
            
            # Step 4: NLP Client Manager (depends on config, logging)
            self._logger.info("Initializing NLP Client...")
            self.nlp_client = create_nlp_client_manager(
                config_manager=self.config,
                logging_manager=self.logging_mgr,
            )
            
            # Step 5: Phrase Loader Manager (depends on config, logging)
            self._logger.info("Loading test phrases...")
            self.phrase_loader = create_phrase_loader_manager(
                config_manager=self.config,
                logging_manager=self.logging_mgr,
            )
            
            # Verify Ash-NLP connectivity
            self._logger.info("Checking Ash-NLP connectivity...")
            if await self.nlp_client.is_available():
                self._logger.success("Ash-NLP server is available")
            else:
                self._logger.warning("⚠️ Ash-NLP server is not available - tests will fail")
            
            # Print summary
            self._print_startup_summary()
            
            return True
            
        except Exception as e:
            if self._logger:
                self._logger.critical(f"Startup failed: {e}")
            else:
                print(f"🚨 CRITICAL: Startup failed: {e}", file=sys.stderr)
            return False
    
    async def shutdown(self) -> None:
        """Clean shutdown of all managers."""
        if self._logger:
            self._logger.info("Shutting down Ash-Thrash...")
        
        # Close NLP client connection
        if self.nlp_client:
            await self.nlp_client.close()
        
        if self._logger:
            self._logger.success("Shutdown complete")
    
    async def run(self) -> int:
        """
        Main run loop.
        
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        # Setup signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self._handle_signal(s))
            )
        
        # Startup
        if not await self.startup():
            return 1
        
        try:
            # Phase 1: Just verify everything is working
            # Phase 2+ will add test execution here
            self._logger.info("Phase 1 Foundation Complete - Ready for test execution")
            self._logger.info("Waiting for shutdown signal (Ctrl+C)...")
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
            return 0
            
        except Exception as e:
            self._logger.error(f"Runtime error: {e}")
            return 1
            
        finally:
            await self.shutdown()
    
    async def _handle_signal(self, sig: signal.Signals) -> None:
        """Handle shutdown signals."""
        if self._logger:
            self._logger.info(f"Received signal {sig.name}, initiating shutdown...")
        self._shutdown_event.set()
    
    def _print_banner(self) -> None:
        """Print the startup banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     █████╗ ███████╗██╗  ██╗      ████████╗██╗  ██╗██████╗  █████╗ ███████╗   ║
║    ██╔══██╗██╔════╝██║  ██║      ╚══██╔══╝██║  ██║██╔══██╗██╔══██╗██╔════╝   ║
║    ███████║███████╗███████║█████╗   ██║   ███████║██████╔╝███████║███████╗   ║
║    ██╔══██║╚════██║██╔══██║╚════╝   ██║   ██╔══██║██╔══██╗██╔══██║╚════██║   ║
║    ██║  ██║███████║██║  ██║         ██║   ██║  ██║██║  ██║██║  ██║███████║   ║
║    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝         ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ║
║                                                                              ║
║                    Crisis Detection Testing Suite v5.0                       ║
║                                                                              ║
║              The Alphabet Cartel - https://discord.gg/alphabetcartel         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        # Print banner without logging (direct to console)
        print(banner)
        
        self._logger.info(f"Ash-Thrash {__version__} starting...")
        self._logger.info(f"Environment: {self.config.get_environment()}")
    
    def _print_startup_summary(self) -> None:
        """Print startup summary."""
        stats = self.phrase_loader.get_statistics()
        
        self._logger.info("=" * 60)
        self._logger.info("Startup Summary")
        self._logger.info("=" * 60)
        self._logger.info(f"  Environment:    {self.config.get_environment()}")
        self._logger.info(f"  Log Level:      {self.logging_mgr.log_level}")
        self._logger.info(f"  NLP Server:     {self.nlp_client.base_url}")
        self._logger.info(f"  Total Phrases:  {stats.total_phrases}")
        self._logger.info(f"  Files Loaded:   {stats.files_loaded}")
        
        if stats.by_category_type:
            self._logger.info("  By Type:")
            for cat_type, count in stats.by_category_type.items():
                self._logger.info(f"    - {cat_type}: {count}")
        
        webhook_status = "Configured" if self.secrets.has_discord_webhook() else "Not configured"
        self._logger.info(f"  Discord Webhook: {webhook_status}")
        self._logger.info("=" * 60)
        self._logger.success("Ash-Thrash initialized successfully")


# =============================================================================
# Entry Point
# =============================================================================

def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code
    """
    app = AshThrash()
    
    try:
        return asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        return 0


if __name__ == "__main__":
    sys.exit(main())
