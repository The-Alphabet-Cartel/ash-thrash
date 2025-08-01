"""
Test Data Package for Ash-Thrash Crisis Detection Testing

This package contains test phrases organized by priority category for comprehensive
testing of the Ash NLP crisis detection system.

Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
Discord: https://discord.gg/alphabetcartel
"""

# Sample test phrases for basic functionality
# In a full implementation, these would be in separate files with 350 total phrases

DEFINITE_HIGH_PHRASES = [
    "I want to kill myself",
    "I'm going to end my life", 
    "I can't take it anymore, goodbye",
    "Planning to commit suicide tonight",
    "I want to die right now",
    "I'm going to hurt myself",
    "Life isn't worth living anymore",
    "I have a suicide plan",
    "I want to end it all",
    "Going to kill myself tonight"
]

DEFINITE_MEDIUM_PHRASES = [
    "I'm feeling really depressed",
    "Life feels meaningless lately",
    "I'm struggling with severe anxiety",
    "Everything feels hopeless",
    "I can't stop crying",
    "I feel so alone and empty",
    "Nothing matters anymore",
    "I hate myself so much",
    "Why do I even exist",
    "I'm broken beyond repair"
]

DEFINITE_LOW_PHRASES = [
    "Having a rough day",
    "Feeling a bit down",
    "Work is stressing me out",
    "I'm worried about my grades",
    "Feeling overwhelmed with tasks",
    "Been better, honestly",
    "Not my best week",
    "Struggling with some stuff",
    "Having some personal issues",
    "Been feeling off lately"
]

DEFINITE_NONE_PHRASES = [
    "Going to the store",
    "What's for dinner",
    "Nice weather today",
    "See you tomorrow",
    "Thanks for the help",
    "How was your day",
    "What time is the meeting",
    "Love this song",
    "Great job on the project",
    "Happy Friday everyone"
]

MAYBE_HIGH_MEDIUM_PHRASES = [
    "I don't know if I can keep going",
    "Everything is falling apart",
    "I feel like giving up",
    "Nothing I do matters",
    "I'm tired of trying",
    "What's the point anymore",
    "I can't handle this",
    "I'm losing hope",
    "Feel like I'm drowning",
    "Can't see a way forward"
]

MAYBE_MEDIUM_LOW_PHRASES = [
    "Things aren't going well",
    "I'm struggling right now",
    "Having a hard time",
    "Feel pretty low today",
    "Not doing great mentally",
    "Been better days",
    "Feeling pretty rough",
    "This is really difficult",
    "Having some tough times",
    "Not feeling myself"
]

MAYBE_LOW_NONE_PHRASES = [
    "Could be better",
    "Not bad, could be worse",
    "It's whatever",
    "Meh, okay I guess",
    "Fine, thanks for asking",
    "Not complaining",
    "Same old, same old",
    "Getting by",
    "Can't complain too much",
    "Doing alright"
]

def get_high_priority_phrases():
    """Get high priority crisis phrases."""
    return [{"phrase": p, "expected_priority": "high", "category": "definite_high"} 
            for p in DEFINITE_HIGH_PHRASES]

def get_medium_priority_phrases():
    """Get medium priority crisis phrases."""
    return [{"phrase": p, "expected_priority": "medium", "category": "definite_medium"} 
            for p in DEFINITE_MEDIUM_PHRASES]

def get_low_priority_phrases():
    """Get low priority crisis phrases."""
    return [{"phrase": p, "expected_priority": "low", "category": "definite_low"} 
            for p in DEFINITE_LOW_PHRASES]

def get_none_priority_phrases():
    """Get no priority phrases."""
    return [{"phrase": p, "expected_priority": "none", "category": "definite_none"} 
            for p in DEFINITE_NONE_PHRASES]

def get_maybe_high_medium_phrases():
    """Get maybe high/medium priority phrases."""
    return [{"phrase": p, "expected_priority": "medium", "category": "maybe_high_medium"} 
            for p in MAYBE_HIGH_MEDIUM_PHRASES]

def get_maybe_medium_low_phrases():
    """Get maybe medium/low priority phrases."""
    return [{"phrase": p, "expected_priority": "low", "category": "maybe_medium_low"} 
            for p in MAYBE_MEDIUM_LOW_PHRASES]

def get_maybe_low_none_phrases():
    """Get maybe low/none priority phrases."""
    return [{"phrase": p, "expected_priority": "none", "category": "maybe_low_none"} 
            for p in MAYBE_LOW_NONE_PHRASES]

def get_all_test_phrases():
    """
    Returns all test phrases organized by category.
    
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
        "definite_high": {
            "target_pass_rate": 90.0,
            "description": "High Priority Crisis (Must Catch All)",
            "critical": True,
            "allow_escalation": False,
            "min_confidence": 0.8
        },
        "definite_medium": {
            "target_pass_rate": 65.0,
            "description": "Medium Priority Crisis",
            "critical": False,
            "allow_escalation": False,
            "min_confidence": 0.5
        },
        "definite_low": {
            "target_pass_rate": 65.0,
            "description": "Low Priority Crisis",
            "critical": False,
            "allow_escalation": False,
            "min_confidence": 0.3
        },
        "definite_none": {
            "target_pass_rate": 95.0,
            "description": "No Priority Crisis (Prevent False Positives)",
            "critical": True,
            "allow_escalation": False,
            "min_confidence": 0.0
        },
        "maybe_high_medium": {
            "target_pass_rate": 90.0,
            "description": "Maybe High/Medium (No Priority Drops)",
            "critical": False,
            "allow_escalation": True,
            "min_confidence": 0.4
        },
        "maybe_medium_low": {
            "target_pass_rate": 80.0,
            "description": "Maybe Medium/Low (No Priority Drops)",
            "critical": False,
            "allow_escalation": True,
            "min_confidence": 0.3
        },
        "maybe_low_none": {
            "target_pass_rate": 90.0,
            "description": "Maybe Low/None (Prevent False Positives)",
            "critical": True,
            "allow_escalation": True,
            "min_confidence": 0.2
        }
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

# Category info for backward compatibility
CATEGORY_INFO = get_category_info()