# managers/label_data_loader.py
"""
Ash-Thrash: Crisis Detection Testing Suite for The Alphabet Cartel Discord Community
CORE PRINCIPLE: Zero-Shot AI Models → Pattern Enhancement → Crisis Classification
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Thrash is a TESTING SUITE that validates crisis detection accuracy of Ash-NLP:
1. FIRST: Uses test phrases with known expected outcomes
2. SECOND: Evaluates detection accuracy across label sets  
3. THIRD: Optimizes label set selection via evolutionary algorithm
4. PURPOSE: Ensure optimal crisis detection for Discord community communications
********************************************************************************
Test Data Loader for Label Set Optimization
---
FILE VERSION: v3.1-lo-1-1
LAST MODIFIED: 2025-09-03
PHASE: Label Set Optimization Implementation
CLEAN ARCHITECTURE: v3.1 Compliant
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class LabelDataLoader:
    """
    Load and parse test data from JSON configuration files for label set optimization
    
    Handles the test phrases across priority categories:
    - high_priority.json
    - medium_priority.json 
    - low_priority.json
    - none_priority.json
    - maybe_high_medium.json (if available)
    - maybe_medium_low.json (if available)
    - maybe_low_none.json (if available)
    """
    
    def __init__(self, unified_config, test_data_dir: str = "./config/phrases"):
        """
        Initialize label test data loader
        
        Args:
            unified_config: Unified configuration manager
            test_data_dir: Directory containing test data JSON files
        """
        self.unified_config = unified_config
        self.test_data_dir = Path(test_data_dir)
        
        # Map category names to files (similar to weight optimizer but for labels)
        self.file_mappings = {
            'definite_high': 'high_priority.json',
            'definite_medium': 'medium_priority.json', 
            'definite_low': 'low_priority.json',
            'definite_none': 'none_priority.json',
            'maybe_high_medium': 'maybe_high_medium.json',
            'maybe_medium_low': 'maybe_medium_low.json',
            'maybe_low_none': 'maybe_low_none.json'
        }
        
        logger.info(f"LabelDataLoader initialized for directory: {self.test_data_dir}")
    
    def load_all_test_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all test data from JSON files for label optimization
        
        Returns:
            Dictionary mapping category names to lists of test phrases
        """
        all_data = {}
        
        for category_name, filename in self.file_mappings.items():
            file_path = self.test_data_dir / filename
            
            if file_path.exists():
                try:
                    category_data = self._load_category_file(file_path, category_name)
                    if category_data:
                        all_data[category_name] = category_data
                        logger.info(f"✅ Loaded {len(category_data)} phrases from {filename}")
                    else:
                        logger.warning(f"⚠️ No valid phrases found in {filename}")
                
                except Exception as e:
                    logger.error(f"❌ Error loading {filename}: {e}")
            else:
                logger.info(f"ℹ️ Optional file not found: {filename}")
        
        total_phrases = sum(len(phrases) for phrases in all_data.values())
        logger.info(f"📊 Total test data loaded: {total_phrases} phrases across {len(all_data)} categories")
        
        return all_data
    
    def _load_category_file(self, file_path: Path, category_name: str) -> List[Dict[str, Any]]:
        """
        Load and process a single category file
        
        Args:
            file_path: Path to the JSON file
            category_name: Name of the category
            
        Returns:
            List of processed test phrases
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract category information
            category_info = data.get('category', {})
            expected_priority = category_info.get('expected_priority', ['none'])
            subcategories = category_info.get('subcategories', {})
            
            test_phrases = []
            
            # Process all subcategories
            for subcategory_name, phrases in subcategories.items():
                for phrase_data in phrases:
                    if isinstance(phrase_data, dict) and 'message' in phrase_data:
                        processed_phrase = {
                            'message': phrase_data['message'],
                            'expected_priority': expected_priority,
                            'category': category_name,
                            'subcategory': subcategory_name,
                            'description': phrase_data.get('description', ''),
                            'file_source': file_path.name
                        }
                        test_phrases.append(processed_phrase)
            
            logger.debug(f"Processed {len(test_phrases)} phrases from {file_path.name}")
            return test_phrases
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error in {file_path}: {e}")
            return []
        except KeyError as e:
            logger.error(f"❌ Missing required key in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error loading {file_path}: {e}")
            return []
    
    def get_category_statistics(self, test_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Get statistics about the loaded test data
        
        Args:
            test_data: Dictionary of test data by category
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_categories': len(test_data),
            'total_phrases': sum(len(phrases) for phrases in test_data.values()),
            'category_breakdown': {},
            'priority_distribution': {},
            'file_sources': set()
        }
        
        for category, phrases in test_data.items():
            # Category breakdown
            stats['category_breakdown'][category] = {
                'count': len(phrases),
                'subcategories': len(set(p.get('subcategory', '') for p in phrases))
            }
            
            # Priority distribution
            for phrase in phrases:
                for priority in phrase.get('expected_priority', ['none']):
                    if priority not in stats['priority_distribution']:
                        stats['priority_distribution'][priority] = 0
                    stats['priority_distribution'][priority] += 1
                
                # File sources
                if 'file_source' in phrase:
                    stats['file_sources'].add(phrase['file_source'])
        
        stats['file_sources'] = list(stats['file_sources'])
        
        return stats
    
    def validate_test_data(self, test_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Validate loaded test data for completeness and consistency
        
        Args:
            test_data: Dictionary of test data by category
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        if not test_data:
            validation_result['valid'] = False
            validation_result['errors'].append("No test data loaded")
            return validation_result
        
        # Check minimum requirements
        total_phrases = sum(len(phrases) for phrases in test_data.values())
        if total_phrases < 50:
            validation_result['warnings'].append(f"Low phrase count: {total_phrases} (recommended: >100)")
        
        # Check required categories
        required_categories = ['definite_high', 'definite_medium', 'definite_low', 'definite_none']
        missing_categories = [cat for cat in required_categories if cat not in test_data]
        
        if missing_categories:
            validation_result['errors'].extend([f"Missing required category: {cat}" for cat in missing_categories])
            validation_result['valid'] = False
        
        # Check phrase completeness
        for category, phrases in test_data.items():
            category_errors = []
            
            for i, phrase in enumerate(phrases):
                phrase_id = f"{category}[{i}]"
                
                if not phrase.get('message'):
                    category_errors.append(f"{phrase_id}: Missing message")
                
                if not phrase.get('expected_priority'):
                    category_errors.append(f"{phrase_id}: Missing expected_priority")
                
                # Check message length
                message = phrase.get('message', '')
                if len(message) < 5:
                    category_errors.append(f"{phrase_id}: Message too short")
                elif len(message) > 500:
                    validation_result['warnings'].append(f"{phrase_id}: Very long message ({len(message)} chars)")
            
            if category_errors:
                validation_result['errors'].extend(category_errors)
                validation_result['valid'] = False
        
        # Summary
        validation_result['summary'] = {
            'total_categories': len(test_data),
            'total_phrases': total_phrases,
            'error_count': len(validation_result['errors']),
            'warning_count': len(validation_result['warnings'])
        }
        
        return validation_result
    
    def create_balanced_subset(self, test_data: Dict[str, List[Dict[str, Any]]], 
                              max_phrases_per_category: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create a balanced subset of test data for faster optimization
        
        Args:
            test_data: Full test data dictionary
            max_phrases_per_category: Maximum phrases per category in subset
            
        Returns:
            Balanced subset of test data
        """
        import random
        
        balanced_data = {}
        
        for category, phrases in test_data.items():
            if len(phrases) <= max_phrases_per_category:
                # Use all phrases if we have few enough
                balanced_data[category] = phrases.copy()
            else:
                # Random sample from the category
                balanced_data[category] = random.sample(phrases, max_phrases_per_category)
            
            logger.debug(f"Category {category}: {len(balanced_data[category])} phrases selected")
        
        total_original = sum(len(phrases) for phrases in test_data.values())
        total_balanced = sum(len(phrases) for phrases in balanced_data.values())
        
        logger.info(f"🔄 Created balanced subset: {total_balanced}/{total_original} phrases")
        
        return balanced_data


def create_label_data_loader(unified_config, test_data_dir: str = "./config/phrases") -> LabelDataLoader:
    """
    Factory function to create LabelDataLoader following Clean Architecture patterns
    
    Args:
        unified_config: Unified configuration manager
        test_data_dir: Directory containing test phrase files
        
    Returns:
        LabelDataLoader instance
    """
    logger.info("🏗️ Creating LabelDataLoader with clean architecture patterns...")
    
    try:
        loader = LabelDataLoader(unified_config, test_data_dir)
        logger.info("✅ LabelDataLoader created successfully")
        return loader
        
    except Exception as e:
        logger.error(f"❌ Failed to create LabelDataLoader: {e}")
        raise


# Export key classes and functions
__all__ = [
    'LabelDataLoader',
    'create_label_data_loader'
]