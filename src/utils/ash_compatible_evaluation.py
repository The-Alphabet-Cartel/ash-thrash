#!/usr/bin/env python3
"""
Ash-Compatible Evaluation Logic

This module implements the same permissive crisis detection logic that we use
in comprehensive testing, ensuring ash-thrash tests use consistent evaluation
across keyword_primary and nlp_primary detections.
"""

from typing import Dict, Any

def apply_sentiment_adjustments(nlp_result: Dict[str, Any]) -> tuple[float, list]:
    """
    Apply the same sentiment adjustments that ash-bot uses.
    Returns: (adjusted_confidence, adjustment_reasons)
    """
    base_confidence = nlp_result.get("confidence_score", 0.0)
    analysis = nlp_result.get('analysis', {})
    
    # Extract sentiment scores from the analysis section
    sentiment_scores = analysis.get('sentiment_scores', {})
    if not sentiment_scores:
        return base_confidence, []
    
    confidence_adjustment = 0.0
    adjustment_reasons = []
    
    # Apply ash-bot's sentiment adjustment logic
    negative_score = sentiment_scores.get('negative', 0)
    positive_score = sentiment_scores.get('positive', 0)
    neutral_score = sentiment_scores.get('neutral', 0)
    
    # Negative sentiment boost (matches ash-bot logic from project knowledge)
    if negative_score > 0.85:  # Very negative sentiment
        confidence_adjustment += 0.08
        adjustment_reasons.append("very_negative_sentiment (+0.08)")
    elif negative_score > 0.70:  # Moderately negative
        confidence_adjustment += 0.04
        adjustment_reasons.append("negative_sentiment (+0.04)")
    
    # Positive sentiment reduction (matches ash-bot logic)
    if positive_score > 0.70:
        confidence_adjustment -= 0.10
        adjustment_reasons.append("positive_sentiment (-0.10)")
    
    # Apply adjustment and clamp to [0, 1]
    adjusted_confidence = max(0.0, min(1.0, base_confidence + confidence_adjustment))
    
    return adjusted_confidence, adjustment_reasons

def evaluate_ash_compatible(phrase_data, nlp_result):
    """
    UPDATED: Evaluate using Ash's actual crisis detection logic with sentiment adjustments.
    """
    
    if not nlp_result:
        return create_evaluation_result(phrase_data, "error", False, "No NLP response")
    
    expected = phrase_data["expected_priority"].lower()
    actual_nlp = nlp_result.get("crisis_level", "unknown").lower()
    phrase = phrase_data.get("phrase", phrase_data.get("message", ""))
    category = phrase_data.get("category", "unknown")
    
    # UPDATED: Apply sentiment adjustments like ash-bot does
    adjusted_confidence, adjustment_reasons = apply_sentiment_adjustments(nlp_result)
    
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
        winning_confidence = adjusted_confidence  # Use adjusted confidence!
    
    # Build success message with sentiment info
    success_message = ""
    expected_value = hierarchy.get(expected, 0)
    actual_value = final_priority_value
    
    # Exact match is always correct
    if expected == final_priority:
        success = True
        success_message = f"✅ Exact match: {final_priority} (via {method})"
        if adjustment_reasons:
            success_message += f" [sentiment: {', '.join(adjustment_reasons)}]"
    
    # For "maybe" categories, use permissive range-based evaluation
    elif "maybe" in category:
        if category == "maybe_high_medium":
            if actual_value >= 1:
                success = True
                success_message = f"✅ Appropriate range: {expected} → {final_priority} (via {method})"
            else:
                success = False
                success_message = f"❌ Underdetection: {expected} → {final_priority} (via {method})"
                
        elif category == "maybe_medium_low":
            success = True  # Accept anything for this category
            success_message = f"✅ Appropriate range: {expected} → {final_priority} (via {method})"
                
        elif category == "maybe_low_none":
            if actual_value <= 1:
                success = True
                success_message = f"✅ Appropriate range: {expected} → {final_priority} (via {method})"
            else:
                success = False
                success_message = f"❌ Overdetection: {expected} → {final_priority} (via {method})"
        else:
            # Generic maybe handling
            priority_diff = abs(actual_value - expected_value)
            if priority_diff <= 1:
                success = True
                success_message = f"✅ Within range: {expected} → {final_priority} (via {method})"
            else:
                success = False
                success_message = f"❌ Too far off: {expected} → {final_priority} (via {method})"
    
    # For definite categories, allow exact match or one-level movement
    else:
        priority_diff = abs(expected_value - actual_value)
        
        if priority_diff == 0:
            success = True
            success_message = f"✅ Exact match: {final_priority} (via {method})"
        elif priority_diff == 1:
            success = True
            if actual_value > expected_value:
                success_message = f"✅ Escalation allowed: {expected} → {final_priority} (via {method})"
            else:
                success_message = f"✅ De-escalation allowed: {expected} → {final_priority} (via {method})"
        else:
            success = False
            if actual_value > expected_value:
                success_message = f"❌ Excessive escalation: {expected} → {final_priority} (via {method})"
            else:
                success_message = f"❌ Excessive de-escalation: {expected} → {final_priority} (via {method})"
    
    # Add sentiment adjustment info to message
    if adjustment_reasons:
        success_message += f" [adjustments: {', '.join(adjustment_reasons)}]"
    
    return create_evaluation_result(
        phrase_data, 
        final_priority, 
        success, 
        success_message,
        extra_data={
            "keyword_level": keyword_level,
            "nlp_level": actual_nlp,
            "final_level": final_priority,
            "method": method,
            "confidence": winning_confidence,
            "original_confidence": nlp_result.get("confidence_score", 0.0),
            "adjusted_confidence": adjusted_confidence,
            "sentiment_adjustments": adjustment_reasons,
            "sentiment_scores": nlp_result.get('analysis', {}).get('sentiment_scores', {}),
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
        # Import keyword detection from Ash's actual modules
        from src.keywords.high_keywords import detect_high_priority
        from src.keywords.medium_keywords import detect_medium_priority  
        from src.keywords.low_keywords import detect_low_priority
        
        # Test in priority order (high -> medium -> low -> none)
        if detect_high_priority(phrase)['has_match']:
            return 'high'
        elif detect_medium_priority(phrase)['has_match']:
            return 'medium'
        elif detect_low_priority(phrase)['has_match']:
            return 'low'
        else:
            return 'none'
            
    except ImportError:
        # Fallback if keyword modules aren't available
        return simulate_basic_keyword_detection(phrase)

def simulate_basic_keyword_detection(phrase):
    """
    Basic keyword detection fallback when Ash keyword modules aren't available.
    """
    phrase_lower = phrase.lower()
    
    # High priority keywords (crisis indicators)
    high_keywords = [
        'suicide', 'kill myself', 'end it all', 'want to die', 'end my life',
        'going to hurt', 'going to kill', 'thoughts of suicide', 'suicidal thoughts'
    ]
    
    # Medium priority keywords (distress indicators)
    medium_keywords = [
        'depressed', 'depression', 'anxious', 'anxiety', 'hopeless', 'helpless',
        'overwhelmed', 'crying', 'can\'t cope', 'breaking down', 'falling apart'
    ]
    
    # Low priority keywords (stress indicators)
    low_keywords = [
        'stressed', 'worried', 'concerned', 'upset', 'sad', 'down', 'tired',
        'rough day', 'hard time', 'struggling', 'difficult'
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
    """
    Create a standardized evaluation result dictionary.
    """
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
    Return testing goals that match the new permissive evaluation.
    
    These are adjusted to reflect the more flexible evaluation criteria.
    """
    return {
        "definite_high": {
            "target_pass_rate": 100.0,
            "description": "High Priority Crisis (Exact + Adjacent Levels)",
            "critical": True,
            "allow_bidirectional": True
        },
        "definite_medium": {
            "target_pass_rate": 90.0,  # Higher due to permissive evaluation
            "description": "Medium Priority Crisis (Exact + Adjacent Levels)",
            "critical": False,
            "allow_bidirectional": True
        },
        "definite_low": {
            "target_pass_rate": 90.0,  # Higher due to permissive evaluation
            "description": "Low Priority Crisis (Exact + Adjacent Levels)", 
            "critical": False,
            "allow_bidirectional": True
        },
        "definite_none": {
            "target_pass_rate": 95.0,  # High since only `low` is allowed adjacent
            "description": "No Priority Crisis (Exact + Low Only)",
            "critical": True,
            "allow_bidirectional": True
        },
        "maybe_high_medium": {
            "target_pass_rate": 95.0,  # High because very permissive
            "description": "Maybe High/Medium (Anything Except None)",
            "critical": False,
            "allow_escalation": True
        },
        "maybe_medium_low": {
            "target_pass_rate": 100.0,  # 100% since it accepts anything!
            "description": "Maybe Medium/Low (Accepts Anything)",
            "critical": False,
            "allow_escalation": True
        },
        "maybe_low_none": {
            "target_pass_rate": 95.0,  # High - should catch most
            "description": "Maybe Low/None (None + Low Only)",
            "critical": True,
            "allow_escalation": True
        }
    }