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
Logging Configuration Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.2-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 1 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Configure Python logging with colorized console output
- Support human-readable (colorized) and JSON log formats
- Implement custom SUCCESS level (25) for positive confirmations
- Provide consistent logging across all Ash-Thrash components
- Silence noisy third-party libraries

COLORIZATION SCHEME (Charter v5.2.1 Rule #9):
- CRITICAL: Bright Red Bold (🚨)
- ERROR:    Red (❌)
- WARNING:  Yellow (⚠️)
- INFO:     Cyan (ℹ️)
- DEBUG:    Gray (🔍)
- SUCCESS:  Green (✅)

ENVIRONMENT VARIABLES:
- THRASH_LOG_LEVEL:   Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- THRASH_LOG_FORMAT:  Output format (human, json)
- THRASH_LOG_FILE:    Log file path (optional)
- THRASH_LOG_CONSOLE: Enable console output (true/false)
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Module version
__version__ = "v5.0-1-1.2-1"

# =============================================================================
# Constants
# =============================================================================

# Custom SUCCESS level (between INFO=20 and WARNING=30)
SUCCESS_LEVEL = 25

# Application name for log prefixing
DEFAULT_APP_NAME = "ash-thrash"

# Noisy libraries to silence
NOISY_LIBRARIES = [
    "urllib3",
    "httpx",
    "httpcore",
    "asyncio",
    "aiohttp",
]


# =============================================================================
# ANSI Color Codes (Charter v5.2.1 Standard)
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    
    # Log level colors
    CRITICAL = "\033[1;91m"  # Bright Red Bold
    ERROR = "\033[91m"       # Bright Red
    WARNING = "\033[93m"     # Bright Yellow
    INFO = "\033[96m"        # Bright Cyan
    DEBUG = "\033[90m"       # Gray
    SUCCESS = "\033[92m"     # Bright Green
    
    # Utility
    RESET = "\033[0m"        # Reset all formatting
    BOLD = "\033[1m"         # Bold
    DIM = "\033[2m"          # Dim


class Symbols:
    """Emoji symbols for log levels."""
    
    CRITICAL = "🚨"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    DEBUG = "🔍"
    SUCCESS = "✅"


# =============================================================================
# Custom Formatters
# =============================================================================

class ColorizedFormatter(logging.Formatter):
    """
    Formatter that adds colors and symbols to log output.
    
    Output format:
    [2026-01-20 14:30:00] INFO     | ash-thrash.module        | ℹ️ Message here
    """
    
    # Map log levels to colors
    LEVEL_COLORS = {
        logging.CRITICAL: Colors.CRITICAL,
        logging.ERROR: Colors.ERROR,
        logging.WARNING: Colors.WARNING,
        logging.INFO: Colors.INFO,
        logging.DEBUG: Colors.DEBUG,
        SUCCESS_LEVEL: Colors.SUCCESS,
    }
    
    # Map log levels to symbols
    LEVEL_SYMBOLS = {
        logging.CRITICAL: Symbols.CRITICAL,
        logging.ERROR: Symbols.ERROR,
        logging.WARNING: Symbols.WARNING,
        logging.INFO: Symbols.INFO,
        logging.DEBUG: Symbols.DEBUG,
        SUCCESS_LEVEL: Symbols.SUCCESS,
    }
    
    def __init__(self, colorize: bool = True):
        """
        Initialize the formatter.
        
        Args:
            colorize: Whether to apply ANSI colors (disable for non-TTY)
        """
        super().__init__()
        self.colorize = colorize
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with colors and symbols."""
        # Get color and symbol for this level
        color = self.LEVEL_COLORS.get(record.levelno, Colors.INFO)
        symbol = self.LEVEL_SYMBOLS.get(record.levelno, Symbols.INFO)
        reset = Colors.RESET
        
        # Disable colors if not colorizing
        if not self.colorize:
            color = ""
            reset = ""
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Format level name (padded to 8 chars)
        level_name = record.levelname.ljust(8)
        
        # Format logger name (truncated/padded to 25 chars)
        logger_name = record.name[:25].ljust(25)
        
        # Build the formatted message
        formatted = (
            f"{Colors.DIM if self.colorize else ''}[{timestamp}]{reset} "
            f"{color}{level_name}{reset} | "
            f"{logger_name} | "
            f"{symbol} {record.getMessage()}"
        )
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs logs as JSON for log aggregators.
    
    No colors in JSON format - designed for machine parsing.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


class PlainFormatter(logging.Formatter):
    """
    Plain text formatter without colors (for file output).
    
    Output format:
    [2026-01-20 14:30:00] INFO     | ash-thrash.module        | Message here
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as plain text."""
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Format level name (padded to 8 chars)
        level_name = record.levelname.ljust(8)
        
        # Format logger name (truncated/padded to 25 chars)
        logger_name = record.name[:25].ljust(25)
        
        # Build the formatted message
        formatted = f"[{timestamp}] {level_name} | {logger_name} | {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


# =============================================================================
# Logging Configuration Manager
# =============================================================================

class LoggingConfigManager:
    """
    Standard logging manager for Ash-Thrash (Charter v5.2.1 Rule #9).
    
    Provides colorized console output with emoji symbols for visual debugging.
    Supports both human-readable and JSON output formats.
    
    Attributes:
        app_name: Application name prefix for loggers
        log_level: Current log level
        log_format: Output format (human or json)
        console_enabled: Whether console output is enabled
        file_path: Optional log file path
    
    Example:
        >>> logging_manager = create_logging_config_manager()
        >>> logger = logging_manager.get_logger("my_module")
        >>> logger.info("Starting process")
        >>> logger.success("Process completed!")
    """
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_format: str = "human",
        log_file: Optional[str] = None,
        console_enabled: bool = True,
        app_name: str = DEFAULT_APP_NAME,
    ):
        """
        Initialize the LoggingConfigManager.
        
        Args:
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Output format ("human" for colorized, "json" for structured)
            log_file: Optional path to log file
            console_enabled: Whether to output to console
            app_name: Application name for logger prefixing
        
        Note:
            Use create_logging_config_manager() factory function instead.
        """
        self.app_name = app_name
        self.log_level = log_level.upper()
        self.log_format = log_format.lower()
        self.console_enabled = console_enabled
        self.file_path = log_file
        
        # Track configured loggers
        self._configured_loggers: Dict[str, logging.Logger] = {}
        
        # Register custom SUCCESS level
        self._register_success_level()
        
        # Configure root logger
        self._configure_root_logger()
        
        # Silence noisy libraries
        self._silence_noisy_libraries()
    
    def _register_success_level(self) -> None:
        """Register the custom SUCCESS log level."""
        # Only register if not already registered
        if not hasattr(logging, "SUCCESS"):
            logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
            logging.SUCCESS = SUCCESS_LEVEL
    
    def _configure_root_logger(self) -> None:
        """Configure the root logger with handlers."""
        # Get numeric level
        numeric_level = getattr(logging, self.log_level, logging.INFO)
        
        # Get root logger for our app
        root_logger = logging.getLogger(self.app_name)
        root_logger.setLevel(numeric_level)
        
        # Remove any existing handlers
        root_logger.handlers.clear()
        
        # Add console handler if enabled
        if self.console_enabled:
            console_handler = self._create_console_handler()
            root_logger.addHandler(console_handler)
        
        # Add file handler if specified
        if self.file_path:
            file_handler = self._create_file_handler()
            if file_handler:
                root_logger.addHandler(file_handler)
        
        # Prevent propagation to root
        root_logger.propagate = False
    
    def _create_console_handler(self) -> logging.Handler:
        """Create a console handler with appropriate formatter."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, self.log_level, logging.INFO))
        
        # Choose formatter based on format setting
        if self.log_format == "json":
            handler.setFormatter(JSONFormatter())
        else:
            # Check if we're outputting to a TTY for color support
            is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
            # Also check FORCE_COLOR env var (for Docker)
            force_color = os.environ.get("FORCE_COLOR", "").lower() in ("1", "true", "yes")
            colorize = is_tty or force_color
            
            handler.setFormatter(ColorizedFormatter(colorize=colorize))
        
        return handler
    
    def _create_file_handler(self) -> Optional[logging.Handler]:
        """Create a file handler for log output."""
        try:
            # Ensure directory exists
            log_path = Path(self.file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            handler = logging.FileHandler(self.file_path, encoding="utf-8")
            handler.setLevel(getattr(logging, self.log_level, logging.INFO))
            
            # Always use plain formatter for files (no colors)
            handler.setFormatter(PlainFormatter())
            
            return handler
            
        except Exception as e:
            # Log to stderr since logging isn't fully configured yet
            print(f"⚠️ Failed to create log file handler: {e}", file=sys.stderr)
            return None
    
    def _silence_noisy_libraries(self) -> None:
        """Reduce log noise from third-party libraries."""
        for library in NOISY_LIBRARIES:
            logging.getLogger(library).setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with the custom success() method.
        
        Args:
            name: Logger name (will be prefixed with app_name)
        
        Returns:
            Configured logger instance with success() method
        
        Example:
            >>> logger = logging_manager.get_logger("nlp_client")
            >>> logger.info("Connecting to Ash-NLP...")
            >>> logger.success("Connected successfully!")
        """
        # Build full logger name
        full_name = f"{self.app_name}.{name}"
        
        # Return cached logger if available
        if full_name in self._configured_loggers:
            return self._configured_loggers[full_name]
        
        # Get or create logger
        logger = logging.getLogger(full_name)
        
        # Add success method
        def success(msg: str, *args, **kwargs):
            """Log a success message (custom level 25)."""
            logger.log(SUCCESS_LEVEL, msg, *args, **kwargs)
        
        logger.success = success
        
        # Cache and return
        self._configured_loggers[full_name] = logger
        return logger
    
    def set_level(self, level: str) -> None:
        """
        Change the log level at runtime.
        
        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = level.upper()
        numeric_level = getattr(logging, self.log_level, logging.INFO)
        
        # Update root logger
        root_logger = logging.getLogger(self.app_name)
        root_logger.setLevel(numeric_level)
        
        # Update all handlers
        for handler in root_logger.handlers:
            handler.setLevel(numeric_level)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get logging configuration status.
        
        Returns:
            Dictionary with current logging configuration
        """
        return {
            "app_name": self.app_name,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "console_enabled": self.console_enabled,
            "file_path": self.file_path,
            "configured_loggers": list(self._configured_loggers.keys()),
        }


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================

def create_logging_config_manager(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
    console_enabled: Optional[bool] = None,
    app_name: str = DEFAULT_APP_NAME,
    config_manager: Optional[Any] = None,
) -> LoggingConfigManager:
    """
    Factory function for LoggingConfigManager (Clean Architecture v5.2.1 Pattern).
    
    This is the ONLY way to create a LoggingConfigManager instance.
    Direct instantiation should be avoided in production code.
    
    Resolution order for each setting:
    1. Explicit parameter (if provided)
    2. ConfigManager value (if config_manager provided)
    3. Environment variable (THRASH_LOG_*)
    4. Default value
    
    Args:
        log_level: Log level override
        log_format: Output format override ("human" or "json")
        log_file: Log file path override
        console_enabled: Console output override
        app_name: Application name for logger prefixing
        config_manager: Optional ConfigManager for loading settings
    
    Returns:
        Configured LoggingConfigManager instance
    
    Example:
        >>> # Simple usage with defaults
        >>> logging_mgr = create_logging_config_manager()
        
        >>> # With ConfigManager integration
        >>> config = create_config_manager()
        >>> logging_mgr = create_logging_config_manager(config_manager=config)
        
        >>> # With explicit overrides
        >>> logging_mgr = create_logging_config_manager(log_level="DEBUG")
    """
    # Resolve log_level
    if log_level is None:
        if config_manager:
            log_level = config_manager.get("logging", "level")
        if log_level is None:
            log_level = os.environ.get("THRASH_LOG_LEVEL", "INFO")
    
    # Resolve log_format
    if log_format is None:
        if config_manager:
            log_format = config_manager.get("logging", "format")
        if log_format is None:
            log_format = os.environ.get("THRASH_LOG_FORMAT", "human")
    
    # Resolve log_file
    if log_file is None:
        if config_manager:
            log_file = config_manager.get("logging", "file")
        if log_file is None:
            log_file = os.environ.get("THRASH_LOG_FILE")
    
    # Resolve console_enabled
    if console_enabled is None:
        if config_manager:
            console_enabled = config_manager.get("logging", "console")
        if console_enabled is None:
            env_console = os.environ.get("THRASH_LOG_CONSOLE", "true")
            console_enabled = env_console.lower() in ("true", "1", "yes")
    
    return LoggingConfigManager(
        log_level=log_level,
        log_format=log_format,
        log_file=log_file,
        console_enabled=console_enabled,
        app_name=app_name,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "LoggingConfigManager",
    "create_logging_config_manager",
    "SUCCESS_LEVEL",
    "Colors",
    "Symbols",
]
