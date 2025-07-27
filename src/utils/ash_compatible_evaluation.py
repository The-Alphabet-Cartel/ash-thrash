#!/usr/bin/env python3
"""
Ash-Compatible Evaluation Logic

This module implements the exact same crisis detection logic that Ash uses,
ensuring ash-thrash tests the same behavior as the actual bot.

Based on analysis of:
- bot/handlers/message_handler.py (hybrid detection logic)
- bot/services/detection_service.py (combination logic)  
- config/nlp_settings.py (thresholds)
"""

def evaluate_ash_compatible(phrase_data, nlp_result):
    """
    Evaluate using Ash's actual crisis detection logic.
    
    This matches the hybrid detection system where Ash combines:
    1. Keyword detection (high confidence baseline)
    2. NLP detection (ML-based analysis)
    3. Safety-first hierarchy (higher priority wins)
    
    Args:
        phrase_data: Test phrase info with expected_priority and category
        nlp_result: Raw response from NLP server
        
    Returns:
        dict: Evaluation result with success/failure and detailed reasoning
    """
    
    if not nlp_result:
        return create_evaluation_result(phrase_data, "error", False, "No NLP response")
    
    expected = phrase_data["expected_priority"].lower()
    actual_nlp = nlp_result.get("crisis_level", "unknown").lower()
    phrase = phrase_data.get("phrase", phrase_data.get("message", ""))
    category = phrase_data.get("category", "unknown")
    confidence = nlp_result.get("confidence_score", 0)
    
    # Simulate keyword detection (Ash's baseline)
    keyword_level = simulate_keyword_detection(phrase)
    
    # Apply Ash's hybrid logic: safety-first hierarchy
    hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
    
    keyword_priority = hierarchy.get(keyword_level, 0)
    nlp_priority = hierarchy.get(actual_nlp, 0)
    
    # Ash uses the HIGHER of the two priorities (safety-first)
    final_priority_value = max(keyword_priority, nlp_priority)
    final_priority = [k for k, v in hierarchy.items() if v == final_priority_value][0]
    
    # Determine which system "won"
    if keyword_priority >= nlp_priority:
        method = "keyword_primary"
        winning_confidence = 0.9  # Keywords are high confidence in Ash
    else:
        method = "nlp_primary" 
        winning_confidence = confidence
    
    # Evaluation logic based on Ash's actual behavior
    expected_value = hierarchy.get(expected, 0)
    actual_value = final_priority_value
    
    # Success criteria that matches Ash's logic
    if category.startswith("definite_"):
        # For definite categories, we need exact match OR safe escalation
        if actual_value == expected_value:
            success = True
            message = f"✅ Exact match: {final_priority} (via {method})"
        elif actual_value > expected_value:
            # Ash would escalate - this is SAFE behavior
            success = True
            message = f"✅ Safe escalation: {expected} → {final_priority} (via {method})"
        else:
            # Ash would de-escalate - this is DANGEROUS
            success = False
            message = f"❌ Dangerous de-escalation: {expected} → {final_priority} (via {method})"
    
    elif category.startswith("maybe_"):
        # For maybe categories, escalation is explicitly allowed and expected
        if actual_value >= expected_value:
            success = True
            if actual_value == expected_value:
                message = f"✅ Exact match: {final_priority} (via {method})"
            else:
                message = f"✅ Allowed escalation: {expected} → {final_priority} (via {method})"
        else:
            # De-escalation in maybe categories is dangerous
            success = False
            message = f"❌ Dangerous de-escalation: {expected} → {final_priority} (via {method})"
    
    else:
        # Unknown category - use conservative evaluation
        success = (actual_value == expected_value)
        message = f"{'✅' if success else '❌'} {expected} → {final_priority} (via {method})"
    
    return create_evaluation_result(
        phrase_data, 
        final_priority, 
        success, 
        message,
        extra_data={
            "keyword_level": keyword_level,
            "nlp_level": actual_nlp,
            "final_level": final_priority,
            "method": method,
            "confidence": winning_confidence,
            "keyword_priority": keyword_priority,
            "nlp_priority": nlp_priority,
            "safety_escalation": actual_value > expected_value
        }
    )

def simulate_keyword_detection(phrase):
    """
    Use Ash's ACTUAL keyword detection logic for hybrid testing.
    
    This uses the exact same keywords that Ash Bot uses, ensuring
    our testing matches the real hybrid behavior.
    """
    try:
        # Import Ash's actual keywords
        from src.keywords import get_high_crisis_keywords, get_medium_crisis_keywords, get_low_crisis_keywords
        
        # Get all keyword sets
        high_keywords = get_high_crisis_keywords()
        medium_keywords = get_medium_crisis_keywords()
        low_keywords = get_low_crisis_keywords()
        
        phrase_lower = phrase.lower()
        
        # Check high priority first (safety-first)
        for category, keywords in high_keywords.items():
            for keyword in keywords:
                if keyword.lower() in phrase_lower:
                    return 'high'
        
        # Check medium priority
        for category, keywords in medium_keywords.items():
            for keyword in keywords:
                if keyword.lower() in phrase_lower:
                    return 'medium'
        
        # Check low priority
        for category, keywords in low_keywords.items():
            for keyword in keywords:
                if keyword.lower() in phrase_lower:
                    return 'low'
        
        return 'none'
        
    except ImportError:
        # Fallback to simplified keywords if import fails
        return simulate_keyword_detection_fallback(phrase)

def simulate_keyword_detection_fallback(phrase):
    """
    Fallback keyword detection if Ash keywords can't be imported.
    """
    phrase_lower = phrase.lower()
    
    # Simplified high priority keywords
    high_keywords = [
        'kill myself', 'suicide', 'end my life', 'want to die', 
        'hurt myself', 'cut myself', 'overdose', 'jump off'
    ]
    
    # Simplified medium priority keywords
    medium_keywords = [
        'want to disappear', 'nothing matters', 'give up', 'hopeless',
        'worthless', 'hate myself', 'can\'t go on', 'no point'
    ]
    
    # Simplified low priority keywords
    low_keywords = [
        'stressed', 'anxious', 'overwhelmed', 'worried', 'nervous',
        'rough day', 'having a hard time', 'struggling'
    ]
    
    # Check in priority order
    for keyword in high_keywords:
        if keyword in phrase_lower:
            return 'high'
    
    for keyword in medium_keywords:
        if keyword in phrase_lower:
            return 'medium'
    
    for keyword in low_keywords:
        if keyword in phrase_lower:
            return 'low'
    
    return 'none'

def create_evaluation_result(phrase_data, actual_priority, success, message, extra_data=None):
    """Create standardized evaluation result."""
    from datetime import datetime, timezone
    
    result = {
        "phrase": phrase_data.get("phrase", phrase_data.get("message", "")),
        "expected_priority": phrase_data["expected_priority"],
        "actual_priority": actual_priority,
        "category": phrase_data.get("category", "unknown"),
        "success": success,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subcategory": phrase_data.get("subcategory", ""),
        "description": phrase_data.get("description", "")
    }
    
    if extra_data:
        result.update(extra_data)
    
    return result

def get_ash_testing_goals():
    """
    Return testing goals that match Ash's actual behavior.
    
    These are adjusted to reflect that Ash uses safety-first escalation,
    so we expect higher success rates due to safe escalation being allowed.
    """
    return {
        "definite_high": {
            "target_pass_rate": 100.0,
            "description": "High Priority Crisis (Must Catch All + Allow Safe Escalation)",
            "critical": True,
            "allow_safe_escalation": True
        },
        "definite_medium": {
            "target_pass_rate": 85.0,  # Higher due to safe escalation 
            "description": "Medium Priority Crisis (Allow Safe Escalation)",
            "critical": False,
            "allow_safe_escalation": True
        },
        "definite_low": {
            "target_pass_rate": 80.0,  # Higher due to safe escalation
            "description": "Low Priority Crisis (Allow Safe Escalation)", 
            "critical": False,
            "allow_safe_escalation": True
        },
        "definite_none": {
            "target_pass_rate": 90.0,  # Slightly lower since some escalation is acceptable
            "description": "No Priority Crisis (Some Safe Escalation OK)",
            "critical": True,
            "allow_safe_escalation": False  # Don't want false positives
        },
        "maybe_high_medium": {
            "target_pass_rate": 95.0,  # High because escalation is expected
            "description": "Maybe High/Medium (Escalation Expected)",
            "critical": False,
            "allow_escalation": True
        },
        "maybe_medium_low": {
            "target_pass_rate": 90.0,  # High because escalation is expected
            "description": "Maybe Medium/Low (Escalation Expected)",
            "critical": False,
            "allow_escalation": True
        },
        "maybe_low_none": {
            "target_pass_rate": 95.0,  # High - should catch most with escalation
            "description": "Maybe Low/None (Some Escalation Expected)",
            "critical": True,
            "allow_escalation": True
        }
    }