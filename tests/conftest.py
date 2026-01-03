"""
Ash-Thrash: Crisis Detection Testing Framework for The Alphabet Cartel Discord Community
CORE PRINCIPLE:
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Thrash is a CRISIS DETECTION TESTING FRAMEWORK that:
1. PRIMARY:
2. CONTEXTUAL:
3. HISTORICAL:
5. **PURPOSE**:
********************************************************************************
Ash-Thrash Test Fixtures
---
FILE VERSION: v5.0
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

Shared pytest fixtures for the Ash-Thrash test suite.
"""

import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment
os.environ["BOT_ENVIRONMENT"] = "testing"


# =============================================================================
# Configuration Fixtures
# =============================================================================
