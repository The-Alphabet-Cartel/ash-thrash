"""
Test Data Package for Ash-Thrash Crisis Detection Testing

This package contains all 350 test phrases organized by priority category:
- Definite High Priority: 50 phrases (100% catch rate target)
- Definite Medium Priority: 50 phrases (65% catch rate target)  
- Definite Low Priority: 50 phrases (65% catch rate target)
- Definite None Priority: 50 phrases (95% catch rate target)
- Maybe High/Medium: 50 phrases (90% catch rate target, allow escalation)
- Maybe Medium/Low: 50 phrases (80% catch rate target, allow escalation)
- Maybe Low/None: 50 phrases (90% catch rate target, allow escalation)

Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
"""

from .high_priority import get_high_priority_phrases, CATEGORY_INFO as HIGH_INFO
from .medium_priority import get_medium_priority_phrases, CATEGORY_INFO as MEDIUM_INFO
from .low_priority import get_low_priority_phrases, CATEGORY_INFO as LOW_INFO
from .none_priority import get_none_priority_phrases, CATEGORY_INFO as NONE_INFO
from .maybe_high_medium import get_maybe_high_medium_phrases, CATEGORY_INFO as MAYBE_HM_INFO
from .maybe_medium_low import get_maybe_medium_low_phrases, CATEGORY_INFO as MAYBE_ML_INFO
from .maybe_low_none import get_maybe_low_none_phrases, CATEGORY_INFO as MAYBE_LN_INFO


def get_all_test_phrases():
    """
    Returns all 350 test phrases organized by category.
    
    Returns:
        dict: Dictionary with category names as keys and phrase lists as values
    """
    return {
        "definite_high": get_high_priority_phrases(),
        "definite_medium": get_medium_priority_phrases(),
        "definite_low": get_low_priority_phrases(),
        "definite_none": get_none_priority_phrases(),
        "maybe_high_medium": get_maybe_high_medium_phrases(),
        "maybe_medium_low": get_maybe_medium_low_phrases(),
        "maybe_low_none": get_maybe_low_none_phrases()
    }


def get_category_info():
    """
    Returns metadata about each testing category.
    
    Returns:
        dict: Dictionary with category metadata including targets and settings
    """
    return {
        "definite_high": HIGH_INFO,
        "definite_medium": MEDIUM_INFO,
        "definite_low": LOW_INFO,
        "definite_none": NONE_INFO,
        "maybe_high_medium": MAYBE_HM_INFO,
        "maybe_medium_low": MAYBE_ML_INFO,
        "maybe_low_none": MAYBE_LN_INFO
    }


def get_phrase_count_summary():
    """
    Returns summary of phrase counts by category.
    
    Returns:
        dict: Dictionary with phrase counts and totals
    """
    all_phrases = get_all_test_phrases()
    
    summary = {}
    total_phrases = 0
    
    for category, phrases in all_phrases.items():
        count = len(phrases)
        summary[category] = count
        total_phrases += count
    
    summary["total"] = total_phrases
    return summary


def get_testing_goals():
    """
    Returns testing goals and targets for each category.
    
    Returns:
        dict: Dictionary with testing targets and critical status
    """
    category_info = get_category_info()
    
    goals = {}
    for category, info in category_info.items():
        goals[category] = {
            "target_pass_rate": info["target_pass_rate"],
            "critical": info["critical"],
            "allow_escalation": info["allow_escalation"],
            "description": info["description"]
        }
    
    return goals


def validate_test_data():
    """
    Validates the test data for completeness and consistency.
    
    Returns:
        dict: Validation results with any issues found
    """
    validation_results = {
        "valid": True,
        "issues": [],
        "summary": {}
    }
    
    try:
        # Check phrase counts
        phrase_counts = get_phrase_count_summary()
        expected_total = 350
        expected_per_category = 50
        
        validation_results["summary"] = phrase_counts
        
        # Validate total count
        if phrase_counts["total"] != expected_total:
            validation_results["valid"] = False
            validation_results["issues"].append(
                f"Total phrase count is {phrase_counts['total']}, expected {expected_total}"
            )
        
        # Validate per-category counts
        for category, count in phrase_counts.items():
            if category != "total" and count != expected_per_category:
                validation_results["valid"] = False
                validation_results["issues"].append(
                    f"Category '{category}' has {count} phrases, expected {expected_per_category}"
                )
        
        # Validate phrase structure
        all_phrases = get_all_test_phrases()
        for category, phrases in all_phrases.items():
            for i, phrase in enumerate(phrases):
                # Check required fields
                required_fields = ["message", "expected_priority", "subcategory", "description"]
                for field in required_fields:
                    if field not in phrase:
                        validation_results["valid"] = False
                        validation_results["issues"].append(
                            f"Category '{category}', phrase {i+1}: Missing required field '{field}'"
                        )
                
                # Check message is not empty
                if phrase.get("message", "").strip() == "":
                    validation_results["valid"] = False
                    validation_results["issues"].append(
                        f"Category '{category}', phrase {i+1}: Empty message"
                    )
        
        # Validate category metadata
        category_info = get_category_info()
        for category in all_phrases.keys():
            if category not in category_info:
                validation_results["valid"] = False
                validation_results["issues"].append(
                    f"Missing category info for '{category}'"
                )
        
    except Exception as e:
        validation_results["valid"] = False
        validation_results["issues"].append(f"Validation error: {str(e)}")
    
    return validation_results


def get_phrases_by_priority(priority_level):
    """
    Returns all phrases that should be detected at a specific priority level.
    
    Args:
        priority_level (str): Priority level ('high', 'medium', 'low', 'none')
        
    Returns:
        list: List of phrases expected to be detected at that priority
    """
    all_phrases = get_all_test_phrases()
    matching_phrases = []
    
    for category, phrases in all_phrases.items():
        for phrase in phrases:
            if phrase["expected_priority"] == priority_level:
                phrase_copy = phrase.copy()
                phrase_copy["category"] = category
                matching_phrases.append(phrase_copy)
    
    return matching_phrases


def get_critical_test_phrases():
    """
    Returns phrases from critical categories (high and none priority).
    
    Returns:
        dict: Dictionary with critical category phrases
    """
    all_phrases = get_all_test_phrases()
    category_info = get_category_info()
    
    critical_phrases = {}
    for category, info in category_info.items():
        if info["critical"]:
            critical_phrases[category] = all_phrases[category]
    
    return critical_phrases


def get_escalation_test_phrases():
    """
    Returns phrases from "maybe" categories that allow escalation.
    
    Returns:
        dict: Dictionary with escalation-allowed category phrases
    """
    all_phrases = get_all_test_phrases()
    category_info = get_category_info()
    
    escalation_phrases = {}
    for category, info in category_info.items():
        if info["allow_escalation"]:
            escalation_phrases[category] = all_phrases[category]
    
    return escalation_phrases


# Export main functions
__all__ = [
    'get_all_test_phrases',
    'get_category_info', 
    'get_phrase_count_summary',
    'get_testing_goals',
    'validate_test_data',
    'get_phrases_by_priority',
    'get_critical_test_phrases',
    'get_escalation_test_phrases'
]


# Module metadata
__version__ = "1.0.0"
__author__ = "The Alphabet Cartel"
__description__ = "Comprehensive crisis detection test phrases for Ash-Thrash"

# Quick validation on import
if __name__ == "__main__":
    validation = validate_test_data()
    if validation["valid"]:
        print("✅ Test data validation passed")
        print(f"📊 Total phrases: {validation['summary']['total']}")
        for category, count in validation["summary"].items():
            if category != "total":
                print(f"   {category}: {count} phrases")
    else:
        print("❌ Test data validation failed:")
        for issue in validation["issues"]:
            print(f"   - {issue}")