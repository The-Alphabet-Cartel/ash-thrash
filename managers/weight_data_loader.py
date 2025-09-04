# ash-nlp/optimization/weight_data_loader.py
"""
Ash-NLP: Crisis Detection Backend for The Alphabet Cartel Discord Community
CORE PRINCIPLE: Zero-Shot AI Models → Pattern Enhancement → Crisis Classification
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-NLP is a CRISIS DETECTION BACKEND that:
1. FIRST: Uses Zero-Shot AI models for primary semantic classification
2. SECOND: Enhances AI results with contextual pattern analysis  
3. FALLBACK: Uses pattern-only classification if AI models fail
4. PURPOSE: Detect crisis messages in Discord community communications
********************************************************************************
Test Data Loader for Weight Optimization
---
FILE VERSION: v3.1-wo-1-1
LAST MODIFIED: 2025-09-01
PHASE: Weight Optimization Implementation
CLEAN ARCHITECTURE: v3.1 Compliant
Repository: https://github.com/the-alphabet-cartel/ash-nlp
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class WeightDataLoader:
    """
    Load and parse test data from JSON configuration files
    
    Handles the 345 human-classified phrases across 7 categories:
    - high_priority.json (50 phrases)
    - medium_priority.json (50 phrases) 
    - low_priority.json (50 phrases)
    - none_priority.json (50 phrases)
    - maybe_high_medium.json (50 phrases)
    - maybe_medium_low.json (50 phrases)
    - maybe_low_none.json (45 phrases)
    """
    
    def __init__(self, unified_config, test_data_dir: str = "./optimization/phrases"):
        """
        Initialize test data loader
        
        Args:
            test_data_dir: Directory containing test data JSON files
        """
        self.test_data_dir = Path(test_data_dir)
        self.file_mappings = {
            'high_priority': 'high_priority.json',
            'medium_priority': 'medium_priority.json', 
            'low_priority': 'low_priority.json',
            'none_priority': 'none_priority.json'
            'maybe_high_medium': 'maybe_high_medium.json',
            'maybe_medium_low': 'maybe_medium_low.json',
            'maybe_low_none': 'maybe_low_none.json'
        }
        
        logger.info(f"WeightDataLoader initialized for directory: {self.test_data_dir}")
    
    def load_all_test_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all test data from JSON files
        
        Returns:
            Dictionary mapping category names to lists of test phrases
        """
        test_dataset = {}
        total_phrases = 0
        
        for category, filename in self.file_mappings.items():
            file_path = self.test_data_dir / filename
            
            if not file_path.exists():
                logger.warning(f"Test data file not found: {file_path}")
                test_dataset[category] = []
                continue
            
            try:
                phrases = self._load_category_file(file_path, category)
                test_dataset[category] = phrases
                total_phrases += len(phrases)
                
                logger.info(f"Loaded {len(phrases)} phrases from {category}")
                
            except Exception as e:
                logger.error(f"Failed to load {filename}: {e}")
                test_dataset[category] = []
        
        logger.info(f"Total phrases loaded: {total_phrases} across {len(test_dataset)} categories")
        
        # Validate expected total
        if total_phrases != 200:  # 4 categories × 50 phrases each
            logger.warning(f"Expected 200 phrases, loaded {total_phrases}")
        
        return test_dataset
    
    def _load_category_file(self, file_path: Path, category: str) -> List[Dict[str, Any]]:
        """
        Load phrases from a single category JSON file
        
        Args:
            file_path: Path to JSON file
            category: Category name for context
            
        Returns:
            List of phrase dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract phrases from JSON structure
            phrases = []
            
            # Navigate to the category data structure
            category_section = data.get('category', {})
            if not category_section:
                logger.warning(f"No 'category' section found in {file_path}")
                return phrases
            
            subcategories = category_section.get('subcategories', {})
            if not subcategories:
                logger.warning(f"No 'subcategories' found in {file_path}")
                return phrases
            
            # Extract phrases from all subcategories
            for subcategory_name, subcategory_phrases in subcategories.items():
                if isinstance(subcategory_phrases, list):
                    for phrase_data in subcategory_phrases:
                        if isinstance(phrase_data, dict):
                            # Extract message and description
                            message = phrase_data.get('message', '')
                            description = phrase_data.get('description', '')
                            
                            if message:  # Only add if we have a message
                                phrases.append({
                                    'message': message,
                                    'description': description,
                                    'subcategory': subcategory_name,
                                    'category': category
                                })
                            else:
                                logger.warning(f"Empty message in {file_path}, subcategory {subcategory_name}")
                        else:
                            logger.warning(f"Invalid phrase format in {file_path}, subcategory {subcategory_name}")
                else:
                    logger.warning(f"Invalid subcategory format in {file_path}: {subcategory_name}")
            
            logger.debug(f"Extracted {len(phrases)} phrases from {len(subcategories)} subcategories in {file_path}")
            return phrases
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def get_category_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about each category
        
        Returns:
            Dictionary with category information and expected performance targets
        """
        return {
            'high_priority': {
                'description': 'High Priority Crisis - immediate intervention required',
                'expected_levels': ['high', 'critical'],
                'target_accuracy': 0.98,
                'phrase_count': 50,
                'critical_for_safety': True
            },
            'medium_priority': {
                'description': 'Medium Priority Crisis - significant distress requiring attention',
                'expected_levels': ['medium'],
                'target_accuracy': 0.85,
                'phrase_count': 50,
                'critical_for_safety': False
            },
            'low_priority': {
                'description': 'Low Priority Crisis - mild distress benefiting from support',
                'expected_levels': ['low'],
                'target_accuracy': 0.85,
                'phrase_count': 50,
                'critical_for_safety': False
            },
            'none_priority': {
                'description': 'No Crisis - positive/neutral content (prevent false positives)',
                'expected_levels': ['none'],
                'target_accuracy': 0.95,
                'phrase_count': 50,
                'critical_for_safety': True  # Critical for preventing false alarms
            }#,
            'maybe_high_medium': {
                'description': 'Borderline High/Medium - should detect as medium or high',
                'expected_levels': ['medium', 'high'],
                'target_accuracy': 0.90,
                'phrase_count': 50,
                'critical_for_safety': False
            },
            'maybe_medium_low': {
                'description': 'Borderline Medium/Low - should detect as low or medium',
                'expected_levels': ['low', 'medium'],
                'target_accuracy': 0.85,
                'phrase_count': 50,
                'critical_for_safety': False
            },
            'maybe_low_none': {
                'description': 'Borderline Low/None - should detect as none or low',
                'expected_levels': ['none', 'low'],
                'target_accuracy': 0.90,
                'phrase_count': 50,
                'critical_for_safety': False
            }
        }
    
    def validate_dataset(self, dataset: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Validate the loaded dataset for completeness and correctness
        
        Args:
            dataset: Loaded test dataset
            
        Returns:
            Validation report
        """
        validation_report = {
            'valid': True,
            'total_phrases': 0,
            'category_counts': {},
            'issues': []
        }
        
        category_info = self.get_category_info()
        
        for category, expected_info in category_info.items():
            if category not in dataset:
                validation_report['valid'] = False
                validation_report['issues'].append(f"Missing category: {category}")
                continue
            
            phrases = dataset[category]
            phrase_count = len(phrases)
            validation_report['category_counts'][category] = phrase_count
            validation_report['total_phrases'] += phrase_count
            
            # Check expected count
            expected_count = expected_info['phrase_count']
            if phrase_count != expected_count:
                validation_report['issues'].append(
                    f"Category {category}: expected {expected_count} phrases, got {phrase_count}"
                )
            
            # Check for empty messages
            empty_messages = sum(1 for p in phrases if not p.get('message', '').strip())
            if empty_messages > 0:
                validation_report['valid'] = False
                validation_report['issues'].append(
                    f"Category {category}: {empty_messages} phrases with empty messages"
                )
        
        # Overall validation
        expected_total = sum(info['phrase_count'] for info in category_info.values())
        if validation_report['total_phrases'] != expected_total:
            validation_report['issues'].append(
                f"Total phrases: expected {expected_total}, got {validation_report['total_phrases']}"
            )
        
        if validation_report['issues']:
            logger.warning(f"Dataset validation issues found: {validation_report['issues']}")
        else:
            logger.info("Dataset validation passed successfully")
        
        return validation_report
    
    def create_sample_dataset(self, sample_size: int = 50) -> Dict[str, List[Dict]]:
        """
        Create a smaller sample dataset for testing
        
        Args:
            sample_size: Number of phrases per category (max available)
            
        Returns:
            Sample dataset
        """
        full_dataset = self.load_all_test_data()
        sample_dataset = {}
        
        for category, phrases in full_dataset.items():
            # Take up to sample_size phrases from each category
            sample_count = min(sample_size, len(phrases))
            sample_dataset[category] = phrases[:sample_count]
            
            logger.info(f"Sample dataset - {category}: {sample_count} phrases")
        
        total_sample_phrases = sum(len(phrases) for phrases in sample_dataset.values())
        logger.info(f"Sample dataset created: {total_sample_phrases} total phrases")
        
        return sample_dataset

def create_weight_data_loader(unified_config, test_data_dir: str = "./optimization/phrases") -> WeightDataLoader:
    """
    Factory function to create WeightDataLoader instance
    
    Args:
        test_data_dir: Directory containing test data JSON files
        
    Returns:
        WeightDataLoader instance
    """
    return WeightDataLoader(unified_config, test_data_dir)

__all__ = [
    'WeightDataLoader',
    'create_weight_data_loader'
]

logger.info("✅ Test Data Loader v3.1-wo-1 loaded")