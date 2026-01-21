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
Secrets Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.3-1
LAST MODIFIED: 2026-01-20
PHASE: Phase 1 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Read secrets from Docker Secrets (/run/secrets/)
- Fallback to local secrets directory for development
- Provide secure access to Discord webhook credentials
- Never log or expose secret values

DOCKER SECRETS LOCATIONS:
- Production (Docker): /run/secrets/<secret_name>
- Development (Local): ./secrets/<secret_name>

SUPPORTED SECRETS:
- ash_thrash_discord_alert_token: Discord webhook URL for test result notifications
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional

# Module version
__version__ = "v5.0-1-1.3-1"

# Initialize logger
logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

# Docker Secrets mount path (standard Docker location)
DOCKER_SECRETS_PATH = Path("/run/secrets")

# Local development secrets path (relative to project root)
LOCAL_SECRETS_PATH = Path("secrets")

# Known secret names and their descriptions for Ash-Thrash
KNOWN_SECRETS = {
    "ash_thrash_discord_alert_token": "Discord webhook URL for test result notifications",
}


# =============================================================================
# Secrets Manager Class
# =============================================================================


class SecretsManager:
    """
    Manages access to Docker Secrets and local development secrets.

    Reads secrets from:
    1. Docker Secrets path (/run/secrets/) - Production
    2. Local secrets directory (./secrets/) - Development fallback
    3. Environment variables - Last resort fallback

    Attributes:
        docker_path: Path to Docker secrets directory
        local_path: Path to local secrets directory
        _cache: Cached secret values (read once)

    Example:
        >>> secrets = create_secrets_manager()
        >>> webhook_url = secrets.get_discord_alert_token()
        >>> if webhook_url:
        ...     print("Discord webhook configured")
    """

    def __init__(
        self,
        docker_path: Optional[Path] = None,
        local_path: Optional[Path] = None,
    ):
        """
        Initialize the SecretsManager.

        Args:
            docker_path: Custom Docker secrets path (default: /run/secrets)
            local_path: Custom local secrets path (default: ./secrets)

        Note:
            Use create_secrets_manager() factory function instead of direct instantiation.
        """
        self.docker_path = docker_path or DOCKER_SECRETS_PATH
        self.local_path = local_path or self._find_local_secrets_path()
        self._cache: Dict[str, Optional[str]] = {}

        # Log initialization (without revealing paths that might hint at secrets)
        logger.debug(f"SecretsManager {__version__} initialized")

    def _find_local_secrets_path(self) -> Path:
        """
        Find the local secrets directory.

        Searches in order:
        1. ./secrets (current directory)
        2. ../secrets (parent directory)
        3. Project root /secrets

        Returns:
            Path to secrets directory
        """
        # Try current directory
        if LOCAL_SECRETS_PATH.exists():
            return LOCAL_SECRETS_PATH

        # Try relative to this file's location (project_root/secrets)
        module_path = Path(__file__).parent.parent.parent / "secrets"
        if module_path.exists():
            return module_path

        # Default to standard path
        return LOCAL_SECRETS_PATH

    def get(
        self,
        secret_name: str,
        default: Optional[str] = None,
        required: bool = False,
    ) -> Optional[str]:
        """
        Get a secret value.

        Lookup order:
        1. Cache (if previously loaded)
        2. Docker Secrets (/run/secrets/<secret_name>)
        3. Local secrets file (./secrets/<secret_name>)
        4. Environment variable (uppercase, prefixed with THRASH_SECRET_)
        5. Default value

        Args:
            secret_name: Name of the secret (e.g., "ash_thrash_discord_alert_token")
            default: Default value if secret not found
            required: If True, raise error when secret not found

        Returns:
            Secret value or default

        Raises:
            SecretNotFoundError: If required=True and secret not found
        """
        # Check cache first
        if secret_name in self._cache:
            return self._cache[secret_name]

        value = None
        source = None

        # 1. Try Docker Secrets path
        docker_secret_path = self.docker_path / secret_name
        if docker_secret_path.exists() and docker_secret_path.is_file():
            try:
                value = docker_secret_path.read_text().strip()
                source = "docker_secrets"
            except Exception as e:
                logger.warning(f"Failed to read Docker secret '{secret_name}': {e}")

        # 2. Try local secrets path
        if value is None:
            local_secret_path = self.local_path / secret_name
            if local_secret_path.exists() and local_secret_path.is_file():
                try:
                    value = local_secret_path.read_text().strip()
                    source = "local_file"
                except Exception as e:
                    logger.warning(f"Failed to read local secret '{secret_name}': {e}")

        # 3. Try environment variable
        if value is None:
            env_var_name = self._get_env_var_name(secret_name)
            value = os.environ.get(env_var_name)
            if value:
                source = "environment"

        # 4. Use default
        if value is None:
            value = default
            source = "default" if default else None

        # Handle required secrets
        if value is None and required:
            raise SecretNotFoundError(
                f"Required secret '{secret_name}' not found. "
                f"Checked: Docker Secrets, local file, environment variable."
            )

        # Cache the value
        self._cache[secret_name] = value

        # Log (without revealing the value)
        if value is not None and source:
            logger.debug(f"Secret '{secret_name}' loaded from {source}")
        elif value is None:
            logger.debug(f"Secret '{secret_name}' not found")

        return value

    def _get_env_var_name(self, secret_name: str) -> str:
        """
        Convert secret name to environment variable name.

        Examples:
            ash_thrash_discord_alert_token -> THRASH_SECRET_ASH_THRASH_DISCORD_ALERT_TOKEN

        Args:
            secret_name: Secret name

        Returns:
            Environment variable name
        """
        return f"THRASH_SECRET_{secret_name.upper()}"

    def get_discord_alert_token(self) -> Optional[str]:
        """
        Get Discord alert webhook token/URL.

        This is the primary secret for Ash-Thrash, used to send
        test result notifications to Discord.

        Also checks DISCORD_ALERT_TOKEN environment variable as fallback.

        Returns:
            Discord webhook URL or None
        """
        # Try our secrets system first
        token = self.get("ash_thrash_discord_alert_token")

        # Fallback to generic Discord env var
        if token is None:
            token = os.environ.get("DISCORD_ALERT_TOKEN")

        return token

    def has_secret(self, secret_name: str) -> bool:
        """
        Check if a secret exists (without loading it).

        Args:
            secret_name: Name of the secret

        Returns:
            True if secret exists
        """
        # Check Docker path
        if (self.docker_path / secret_name).exists():
            return True

        # Check local path
        if (self.local_path / secret_name).exists():
            return True

        # Check environment
        if os.environ.get(self._get_env_var_name(secret_name)):
            return True

        return False

    def has_discord_webhook(self) -> bool:
        """
        Check if Discord webhook is configured.

        Returns:
            True if Discord alert token is available
        """
        return self.get_discord_alert_token() is not None

    def list_available(self) -> Dict[str, bool]:
        """
        List all known secrets and their availability.

        Returns:
            Dict mapping secret name to availability
        """
        return {name: self.has_secret(name) for name in KNOWN_SECRETS}

    def get_status(self) -> Dict[str, any]:
        """
        Get secrets manager status.

        Returns:
            Status dictionary (safe for logging - no secret values)
        """
        return {
            "docker_secrets_path": str(self.docker_path),
            "docker_secrets_available": self.docker_path.exists(),
            "local_secrets_path": str(self.local_path),
            "local_secrets_available": self.local_path.exists(),
            "secrets_available": self.list_available(),
            "discord_webhook_configured": self.has_discord_webhook(),
            "cached_count": len(self._cache),
        }

    def clear_cache(self) -> None:
        """Clear the secrets cache."""
        self._cache.clear()
        logger.debug("Secrets cache cleared")


# =============================================================================
# Exceptions
# =============================================================================


class SecretNotFoundError(Exception):
    """Raised when a required secret is not found."""

    pass


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================


def create_secrets_manager(
    docker_path: Optional[Path] = None,
    local_path: Optional[Path] = None,
) -> SecretsManager:
    """
    Factory function to create a SecretsManager instance.

    This is the ONLY way to create a SecretsManager instance.
    Direct instantiation should be avoided in production code.

    Args:
        docker_path: Custom Docker secrets path (default: /run/secrets)
        local_path: Custom local secrets path (default: ./secrets)

    Returns:
        Configured SecretsManager instance

    Example:
        >>> secrets = create_secrets_manager()
        >>> webhook = secrets.get_discord_alert_token()
    """
    logger.debug("🏭 Creating SecretsManager")

    return SecretsManager(
        docker_path=docker_path,
        local_path=local_path,
    )


# =============================================================================
# Module-level convenience functions
# =============================================================================

# Global instance (lazy initialization)
_global_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """
    Get the global SecretsManager instance.

    Creates instance on first call (lazy initialization).

    Returns:
        Global SecretsManager instance
    """
    global _global_secrets_manager

    if _global_secrets_manager is None:
        _global_secrets_manager = create_secrets_manager()

    return _global_secrets_manager


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get a secret value.

    Args:
        secret_name: Name of the secret
        default: Default value if not found

    Returns:
        Secret value or default
    """
    return get_secrets_manager().get(secret_name, default)


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "SecretsManager",
    "create_secrets_manager",
    "get_secrets_manager",
    "get_secret",
    "SecretNotFoundError",
    "KNOWN_SECRETS",
]
