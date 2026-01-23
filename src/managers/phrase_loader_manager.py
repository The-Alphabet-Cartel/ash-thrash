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
Phrase Loader Manager for Ash-Thrash Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.1-2
LAST MODIFIED: 2026-01-20
PHASE: Phase 2 - Test Execution Engine (refactored)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
============================================================================

RESPONSIBILITIES:
- Load test phrase JSON files from configuration directory
- Validate phrase JSON structure against expected schema
- Organize phrases by category and subcategory
- Calculate phrase statistics and distribution
- Provide iteration interface for test execution

PHRASE DIRECTORY STRUCTURE:
    src/config/phrases/
    ├── critical_high_priority.json   (definite high/critical)
    ├── medium_priority.json          (definite medium)
    ├── low_priority.json             (definite low)
    ├── none_priority.json            (definite none - false positive prevention)
    ├── edge_cases/
    │   ├── maybe_high_medium.json    (ambiguous high/medium)
    │   ├── maybe_medium_low.json     (ambiguous medium/low)
    │   └── maybe_low_none.json       (ambiguous low/none)
    └── specialty/
        ├── irony_sarcasm.json        (dark humor, sarcasm)
        ├── gaming_context.json       (gaming terminology)
        ├── songs_quotes.json         (quoted content)
        ├── lgbtqia_specific.json     (identity-related)
        ├── cultural_slang.json       (internet slang)
        └── language_hints.json       (code-switching)

PHRASE JSON SCHEMA:
    {
      "_metadata": { ... },
      "category_info": {
        "name": "string",
        "description": "string",
        "total_phrases": integer,
        "target_pass_rate": float,
        "critical": boolean,
        "allow_escalation": boolean,
        "allow_de-escalation": boolean
      },
      "category": {
        "name": "string",
        "expected_priority": ["string", ...],
        "subcategories": {
          "subcategory_name": [
            { "message": "string", "description": "string" },
            ...
          ]
        }
      }
    }
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Union

# Module version
__version__ = "v5.0-2-2.1-2"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default phrases directory (relative to src/config/)
DEFAULT_PHRASES_DIR = "phrases"

# Phrase category types
CATEGORY_DEFINITE = "definite"
CATEGORY_EDGE_CASE = "edge_case"
CATEGORY_SPECIALTY = "specialty"

# Known file patterns for auto-discovery
DEFINITE_FILES = [
    "critical_high_priority.json",
    "medium_priority.json",
    "low_priority.json",
    "none_priority.json",
]

EDGE_CASE_DIR = "edge_cases"
SPECIALTY_DIR = "specialty"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class TestPhrase:
    """
    A single test phrase with expected classification.
    
    Attributes:
        message: The message text to test
        description: Human-readable description of the test case
        expected_priorities: List of acceptable priority classifications
        category: Category name (e.g., "definite_high", "irony_sarcasm")
        subcategory: Subcategory name (e.g., "method_specific", "burden_thoughts")
        category_type: Type of category (definite, edge_case, specialty)
        is_critical: Whether this is a critical test case
        allow_escalation: Whether higher severity is acceptable
        allow_deescalation: Whether lower severity is acceptable
        source_file: Name of the source JSON file
    """
    message: str
    description: str
    expected_priorities: List[str]
    category: str
    subcategory: str
    category_type: str = CATEGORY_DEFINITE
    is_critical: bool = False
    allow_escalation: bool = True
    allow_deescalation: bool = False
    source_file: str = ""
    
    def get_validation_params(self) -> dict:
        """
        Get parameters for ClassificationValidator.validate().
        
        Returns:
            Dictionary with validation parameters:
                - expected_priorities: List[str]
                - allow_escalation: bool
                - allow_deescalation: bool
        
        Example:
            >>> from src.validators import create_classification_validator
            >>> validator = create_classification_validator()
            >>> result = validator.validate(
            ...     actual_severity=response.severity,
            ...     **phrase.get_validation_params()
            ... )
        """
        return {
            "expected_priorities": self.expected_priorities,
            "allow_escalation": self.allow_escalation,
            "allow_deescalation": self.allow_deescalation,
        }


@dataclass
class CategoryInfo:
    """
    Metadata about a phrase category.
    
    Attributes:
        name: Category identifier
        description: Human-readable description
        total_phrases: Number of phrases in category
        target_pass_rate: Target accuracy percentage
        is_critical: Whether this category is critical
        allow_escalation: Default escalation setting
        allow_deescalation: Default de-escalation setting
        expected_priorities: Default expected priorities
        source_file: Source JSON filename
    """
    name: str
    description: str
    total_phrases: int = 0
    target_pass_rate: float = 85.0
    is_critical: bool = False
    allow_escalation: bool = True
    allow_deescalation: bool = False
    expected_priorities: List[str] = field(default_factory=list)
    source_file: str = ""


@dataclass
class PhraseStatistics:
    """
    Statistics about loaded phrases.
    
    Attributes:
        total_phrases: Total number of phrases loaded
        by_category: Count per category
        by_category_type: Count per category type
        by_subcategory: Count per subcategory
        files_loaded: Number of files successfully loaded
        files_failed: Number of files that failed to load
        validation_errors: List of validation error messages
    """
    total_phrases: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    by_category_type: Dict[str, int] = field(default_factory=dict)
    by_subcategory: Dict[str, int] = field(default_factory=dict)
    files_loaded: int = 0
    files_failed: int = 0
    validation_errors: List[str] = field(default_factory=list)


# =============================================================================
# Phrase Loader Manager
# =============================================================================

class PhraseLoaderManager:
    """
    Loads and manages test phrases from JSON configuration files.
    
    Provides:
    - Automatic discovery and loading of phrase files
    - Schema validation with graceful error handling
    - Organization by category, subcategory, and type
    - Statistics and distribution reporting
    - Iteration interface for test execution
    
    Attributes:
        phrases_dir: Path to phrases directory
        phrases: List of all loaded TestPhrase objects
        categories: Dictionary of CategoryInfo by name
        statistics: PhraseStatistics summary
    
    Example:
        >>> loader = create_phrase_loader_manager(config_manager=config)
        >>> 
        >>> # Get statistics
        >>> stats = loader.get_statistics()
        >>> print(f"Loaded {stats.total_phrases} phrases")
        >>> 
        >>> # Iterate by category
        >>> for phrase in loader.get_phrases_by_category("definite_high"):
        ...     result = await nlp_client.analyze(phrase.message)
        ...     passed = phrase.matches_priority(result.severity)
    """
    
    def __init__(
        self,
        phrases_dir: Optional[Union[str, Path]] = None,
        logger_instance: Optional[logging.Logger] = None,
    ):
        """
        Initialize the PhraseLoaderManager.
        
        Args:
            phrases_dir: Path to phrases directory
            logger_instance: Optional custom logger
        
        Note:
            Use create_phrase_loader_manager() factory function instead.
        """
        # Set phrases directory
        if phrases_dir is None:
            # Default to src/config/phrases relative to managers directory
            self.phrases_dir = Path(__file__).parent.parent / "config" / DEFAULT_PHRASES_DIR
        else:
            self.phrases_dir = Path(phrases_dir)
        
        # Use provided logger or module logger
        self._logger = logger_instance or logger
        
        # Storage
        self._phrases: List[TestPhrase] = []
        self._categories: Dict[str, CategoryInfo] = {}
        self._statistics = PhraseStatistics()
        
        # Load phrases
        self._load_all_phrases()
        
        self._logger.info(
            f"✅ PhraseLoaderManager {__version__} initialized "
            f"({self._statistics.total_phrases} phrases from {self._statistics.files_loaded} files)"
        )
    
    def _load_all_phrases(self) -> None:
        """Load all phrase files from the phrases directory."""
        if not self.phrases_dir.exists():
            self._logger.error(f"❌ Phrases directory not found: {self.phrases_dir}")
            self._statistics.validation_errors.append(
                f"Phrases directory not found: {self.phrases_dir}"
            )
            return
        
        self._logger.debug(f"📂 Loading phrases from: {self.phrases_dir}")
        
        # Load definite classification files
        for filename in DEFINITE_FILES:
            filepath = self.phrases_dir / filename
            if filepath.exists():
                self._load_phrase_file(filepath, CATEGORY_DEFINITE)
        
        # Load edge case files
        edge_case_dir = self.phrases_dir / EDGE_CASE_DIR
        if edge_case_dir.exists():
            for filepath in edge_case_dir.glob("*.json"):
                self._load_phrase_file(filepath, CATEGORY_EDGE_CASE)
        
        # Load specialty files
        specialty_dir = self.phrases_dir / SPECIALTY_DIR
        if specialty_dir.exists():
            for filepath in specialty_dir.glob("*.json"):
                self._load_phrase_file(filepath, CATEGORY_SPECIALTY)
        
        # Update statistics
        self._update_statistics()
    
    def _load_phrase_file(self, filepath: Path, category_type: str) -> None:
        """
        Load a single phrase JSON file.
        
        Args:
            filepath: Path to JSON file
            category_type: Type of category (definite, edge_case, specialty)
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate and extract data
            if not self._validate_phrase_schema(data, filepath.name):
                self._statistics.files_failed += 1
                return
            
            # Extract category info
            category_info = self._extract_category_info(data, filepath.name)
            
            # Extract phrases
            phrases = self._extract_phrases(data, category_info, category_type, filepath.name)
            
            # Store
            self._categories[category_info.name] = category_info
            self._phrases.extend(phrases)
            self._statistics.files_loaded += 1
            
            self._logger.debug(
                f"  📄 Loaded {len(phrases)} phrases from {filepath.name}"
            )
            
        except json.JSONDecodeError as e:
            self._logger.error(f"❌ Invalid JSON in {filepath.name}: {e}")
            self._statistics.files_failed += 1
            self._statistics.validation_errors.append(
                f"Invalid JSON in {filepath.name}: {e}"
            )
        except Exception as e:
            self._logger.error(f"❌ Error loading {filepath.name}: {e}")
            self._statistics.files_failed += 1
            self._statistics.validation_errors.append(
                f"Error loading {filepath.name}: {e}"
            )
    
    def _validate_phrase_schema(self, data: Dict[str, Any], filename: str) -> bool:
        """
        Validate phrase JSON structure.
        
        Args:
            data: Parsed JSON data
            filename: Source filename for error messages
        
        Returns:
            True if valid, False otherwise
        """
        errors = []
        
        # Check required sections
        if "category_info" not in data:
            errors.append("Missing 'category_info' section")
        
        if "category" not in data:
            errors.append("Missing 'category' section")
        else:
            category = data["category"]
            if "subcategories" not in category:
                errors.append("Missing 'category.subcategories' section")
            if "expected_priority" not in category and "defaults" not in category:
                errors.append("Missing 'category.expected_priority' or defaults")
        
        # Log errors
        if errors:
            for error in errors:
                self._logger.warning(f"⚠️ {filename}: {error}")
                self._statistics.validation_errors.append(f"{filename}: {error}")
            return False
        
        return True
    
    def _extract_category_info(self, data: Dict[str, Any], filename: str) -> CategoryInfo:
        """
        Extract category metadata from phrase data.
        
        Args:
            data: Parsed JSON data
            filename: Source filename
        
        Returns:
            CategoryInfo object
        """
        cat_info = data.get("category_info", {})
        category = data.get("category", {})
        
        # Get defaults
        defaults = cat_info.get("defaults", {})
        cat_defaults = category.get("defaults", {})
        
        # Resolve expected priorities
        expected = category.get("expected_priority")
        if isinstance(expected, str) and expected.startswith("${"):
            expected = cat_defaults.get("expected_priority", ["none"])
        elif expected is None:
            expected = cat_defaults.get("expected_priority", ["none"])
        
        # Resolve other fields
        target_rate = cat_info.get("target_pass_rate")
        if isinstance(target_rate, str) and target_rate.startswith("${"):
            target_rate = defaults.get("target_pass_rate", 85.0)
        
        is_critical = cat_info.get("critical")
        if isinstance(is_critical, str) and is_critical.startswith("${"):
            is_critical = defaults.get("critical", False)
        
        allow_esc = cat_info.get("allow_escalation")
        if isinstance(allow_esc, str) and allow_esc.startswith("${"):
            allow_esc = defaults.get("allow_escalation", True)
        
        allow_deesc = cat_info.get("allow_de-escalation")
        if isinstance(allow_deesc, str) and allow_deesc.startswith("${"):
            allow_deesc = defaults.get("allow_de-escalation", False)
        
        return CategoryInfo(
            name=cat_info.get("name", category.get("name", filename.replace(".json", ""))),
            description=cat_info.get("description", ""),
            target_pass_rate=float(target_rate) if target_rate else 85.0,
            is_critical=bool(is_critical) if is_critical is not None else False,
            allow_escalation=bool(allow_esc) if allow_esc is not None else True,
            allow_deescalation=bool(allow_deesc) if allow_deesc is not None else False,
            expected_priorities=expected if isinstance(expected, list) else [expected],
            source_file=filename,
        )
    
    def _extract_phrases(
        self,
        data: Dict[str, Any],
        category_info: CategoryInfo,
        category_type: str,
        filename: str,
    ) -> List[TestPhrase]:
        """
        Extract test phrases from data.
        
        Args:
            data: Parsed JSON data
            category_info: Category metadata
            category_type: Type of category
            filename: Source filename
        
        Returns:
            List of TestPhrase objects
        """
        phrases = []
        category = data.get("category", {})
        subcategories = category.get("subcategories", {})
        
        for subcat_name, phrase_list in subcategories.items():
            if not isinstance(phrase_list, list):
                continue
            
            for phrase_data in phrase_list:
                if not isinstance(phrase_data, dict):
                    continue
                
                message = phrase_data.get("message", "")
                if not message:
                    continue
                
                phrase = TestPhrase(
                    message=message,
                    description=phrase_data.get("description", ""),
                    expected_priorities=category_info.expected_priorities.copy(),
                    category=category_info.name,
                    subcategory=subcat_name,
                    category_type=category_type,
                    is_critical=category_info.is_critical,
                    allow_escalation=category_info.allow_escalation,
                    allow_deescalation=category_info.allow_deescalation,
                    source_file=filename,
                )
                phrases.append(phrase)
        
        # Update category total
        category_info.total_phrases = len(phrases)
        
        return phrases
    
    def _update_statistics(self) -> None:
        """Update phrase statistics."""
        self._statistics.total_phrases = len(self._phrases)
        
        # Count by category
        by_cat: Dict[str, int] = {}
        by_type: Dict[str, int] = {}
        by_subcat: Dict[str, int] = {}
        
        for phrase in self._phrases:
            # By category
            by_cat[phrase.category] = by_cat.get(phrase.category, 0) + 1
            
            # By type
            by_type[phrase.category_type] = by_type.get(phrase.category_type, 0) + 1
            
            # By subcategory (full path)
            subcat_key = f"{phrase.category}.{phrase.subcategory}"
            by_subcat[subcat_key] = by_subcat.get(subcat_key, 0) + 1
        
        self._statistics.by_category = by_cat
        self._statistics.by_category_type = by_type
        self._statistics.by_subcategory = by_subcat
    
    # =========================================================================
    # Public API - Getters
    # =========================================================================
    
    def get_all_phrases(self) -> List[TestPhrase]:
        """
        Get all loaded phrases.
        
        Returns:
            List of all TestPhrase objects
        """
        return self._phrases.copy()
    
    def get_phrases_by_category(self, category: str) -> List[TestPhrase]:
        """
        Get phrases for a specific category.
        
        Args:
            category: Category name
        
        Returns:
            List of TestPhrase objects in that category
        """
        return [p for p in self._phrases if p.category == category]
    
    def get_phrases_by_type(self, category_type: str) -> List[TestPhrase]:
        """
        Get phrases by category type.
        
        Args:
            category_type: Type (definite, edge_case, specialty)
        
        Returns:
            List of TestPhrase objects of that type
        """
        return [p for p in self._phrases if p.category_type == category_type]
    
    def get_phrases_by_subcategory(self, category: str, subcategory: str) -> List[TestPhrase]:
        """
        Get phrases for a specific subcategory.
        
        Args:
            category: Category name
            subcategory: Subcategory name
        
        Returns:
            List of TestPhrase objects
        """
        return [
            p for p in self._phrases
            if p.category == category and p.subcategory == subcategory
        ]
    
    def get_critical_phrases(self) -> List[TestPhrase]:
        """
        Get all critical test phrases.
        
        Returns:
            List of critical TestPhrase objects
        """
        return [p for p in self._phrases if p.is_critical]
    
    def get_category_info(self, category: str) -> Optional[CategoryInfo]:
        """
        Get metadata for a category.
        
        Args:
            category: Category name
        
        Returns:
            CategoryInfo or None if not found
        """
        return self._categories.get(category)
    
    def get_all_categories(self) -> List[str]:
        """
        Get list of all category names.
        
        Returns:
            List of category names
        """
        return list(self._categories.keys())
    
    def get_all_subcategories(self, category: str) -> List[str]:
        """
        Get list of subcategories for a category.
        
        Args:
            category: Category name
        
        Returns:
            List of subcategory names
        """
        subcats: Set[str] = set()
        for phrase in self._phrases:
            if phrase.category == category:
                subcats.add(phrase.subcategory)
        return sorted(subcats)
    
    def get_statistics(self) -> PhraseStatistics:
        """
        Get phrase statistics.
        
        Returns:
            PhraseStatistics object
        """
        return self._statistics
    
    # =========================================================================
    # Iteration Support
    # =========================================================================
    
    def __iter__(self) -> Iterator[TestPhrase]:
        """Iterate over all phrases."""
        return iter(self._phrases)
    
    def __len__(self) -> int:
        """Return total phrase count."""
        return len(self._phrases)
    
    # =========================================================================
    # Reload Support
    # =========================================================================
    
    def reload(self) -> None:
        """Reload all phrases from disk."""
        self._phrases.clear()
        self._categories.clear()
        self._statistics = PhraseStatistics()
        self._load_all_phrases()
        self._logger.info(
            f"🔄 Reloaded {self._statistics.total_phrases} phrases"
        )
    
    # =========================================================================
    # Status and Debugging
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get loader status information.
        
        Returns:
            Dictionary with status information
        """
        return {
            "phrases_dir": str(self.phrases_dir),
            "total_phrases": self._statistics.total_phrases,
            "files_loaded": self._statistics.files_loaded,
            "files_failed": self._statistics.files_failed,
            "categories": list(self._categories.keys()),
            "by_type": self._statistics.by_category_type,
            "validation_errors": len(self._statistics.validation_errors),
        }
    
    def print_summary(self) -> None:
        """Print a summary of loaded phrases to the logger."""
        self._logger.info("=" * 60)
        self._logger.info("Phrase Loader Summary")
        self._logger.info("=" * 60)
        self._logger.info(f"Directory: {self.phrases_dir}")
        self._logger.info(f"Total Phrases: {self._statistics.total_phrases}")
        self._logger.info(f"Files Loaded: {self._statistics.files_loaded}")
        self._logger.info(f"Files Failed: {self._statistics.files_failed}")
        self._logger.info("-" * 60)
        self._logger.info("By Category Type:")
        for cat_type, count in self._statistics.by_category_type.items():
            self._logger.info(f"  {cat_type}: {count}")
        self._logger.info("-" * 60)
        self._logger.info("By Category:")
        for category, count in self._statistics.by_category.items():
            info = self._categories.get(category)
            critical_marker = " [CRITICAL]" if info and info.is_critical else ""
            self._logger.info(f"  {category}: {count}{critical_marker}")
        self._logger.info("=" * 60)


# =============================================================================
# Factory Function - Clean Architecture v5.2.1 Compliance (Rule #1)
# =============================================================================

def create_phrase_loader_manager(
    phrases_dir: Optional[Union[str, Path]] = None,
    config_manager: Optional[Any] = None,
    logging_manager: Optional[Any] = None,
) -> PhraseLoaderManager:
    """
    Factory function for PhraseLoaderManager (Clean Architecture v5.2.1 Pattern).
    
    This is the ONLY way to create a PhraseLoaderManager instance.
    Direct instantiation should be avoided in production code.
    
    Resolution order for phrases_dir:
    1. Explicit parameter (if provided)
    2. ConfigManager value (if config_manager provided)
    3. Environment variable (THRASH_PHRASES_DIR)
    4. Default value (src/config/phrases)
    
    Args:
        phrases_dir: Path to phrases directory override
        config_manager: Optional ConfigManager for loading settings
        logging_manager: Optional LoggingConfigManager for custom logger
    
    Returns:
        Configured PhraseLoaderManager instance
    
    Example:
        >>> # Simple usage
        >>> loader = create_phrase_loader_manager()
        
        >>> # With ConfigManager integration
        >>> config = create_config_manager()
        >>> loader = create_phrase_loader_manager(config_manager=config)
        
        >>> # Access phrases
        >>> for phrase in loader.get_critical_phrases():
        ...     print(f"Testing: {phrase.message[:50]}...")
    """
    import os
    
    # Resolve phrases_dir
    if phrases_dir is None:
        if config_manager:
            phrases_dir = config_manager.get("phrases", "directory")
        if phrases_dir is None:
            phrases_dir = os.environ.get("THRASH_PHRASES_DIR")
    
    # Get logger if logging_manager provided
    logger_instance = None
    if logging_manager:
        logger_instance = logging_manager.get_logger("phrase_loader")
    
    logger.debug(f"🏭 Creating PhraseLoaderManager")
    
    return PhraseLoaderManager(
        phrases_dir=phrases_dir,
        logger_instance=logger_instance,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "PhraseLoaderManager",
    "create_phrase_loader_manager",
    "TestPhrase",
    "CategoryInfo",
    "PhraseStatistics",
    "CATEGORY_DEFINITE",
    "CATEGORY_EDGE_CASE",
    "CATEGORY_SPECIALTY",
]
