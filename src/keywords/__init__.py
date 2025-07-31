"""
Keywords package for Ash-Thrash Testing - Mirrors Ash Bot's Keyword Structure

This package contains the EXACT same keyword files that Ash Bot uses for crisis detection.
This ensures ash-thrash tests the same hybrid detection logic as the actual bot.

Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
Based on: https://github.com/The-Alphabet-Cartel/ash/bot/keywords/
"""

from .high_crisis import get_high_crisis_keywords
from .medium_crisis import get_medium_crisis_keywords  
from .low_crisis import get_low_crisis_keywords

__all__ = [
    'get_high_crisis_keywords',
    'get_medium_crisis_keywords', 
    'get_low_crisis_keywords'
]

def get_all_keywords():
    """
    Get all keywords from all crisis levels.
    
    Returns:
        dict: Complete keyword structure matching Ash Bot
    """
    return {
        'high_crisis': get_high_crisis_keywords(),
        'medium_crisis': get_medium_crisis_keywords(),
        'low_crisis': get_low_crisis_keywords()
    }

def get_keyword_counts():
    """
    Get counts of keywords by crisis level and category.
    
    Returns:
        dict: Keyword counts for validation
    """
    all_keywords = get_all_keywords()
    
    counts = {}
    total = 0
    
    for crisis_level, categories in all_keywords.items():
        level_total = 0
        counts[crisis_level] = {}
        
        for category, keywords in categories.items():
            count = len(keywords)
            counts[crisis_level][category] = count
            level_total += count
            total += count
        
        counts[crisis_level]['total'] = level_total
    
    counts['grand_total'] = total
    return counts

def validate_keyword_structure():
    """
    Validate that our keyword structure matches Ash's expected format.
    
    Returns:
        dict: Validation results
    """
    try:
        all_keywords = get_all_keywords()
        counts = get_keyword_counts()
        
        # Expected structure validation
        required_levels = ['high_crisis', 'medium_crisis', 'low_crisis']
        missing_levels = [level for level in required_levels if level not in all_keywords]
        
        # Check for minimum keyword counts (based on Ash's actual counts)
        expected_minimums = {
            'high_crisis': 50,  # Should have substantial high-priority keywords
            'medium_crisis': 80,  # Largest category in Ash
            'low_crisis': 100   # Most diverse category
        }
        
        insufficient_counts = {}
        for level, min_count in expected_minimums.items():
            actual_count = counts.get(level, {}).get('total', 0)
            if actual_count < min_count:
                insufficient_counts[level] = {'expected': min_count, 'actual': actual_count}
        
        return {
            'valid': len(missing_levels) == 0 and len(insufficient_counts) == 0,
            'missing_levels': missing_levels,
            'insufficient_counts': insufficient_counts,
            'total_keywords': counts['grand_total'],
            'level_counts': {level: counts[level]['total'] for level in required_levels if level in counts}
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'missing_levels': [],
            'insufficient_counts': {},
            'total_keywords': 0,
            'level_counts': {}
        }