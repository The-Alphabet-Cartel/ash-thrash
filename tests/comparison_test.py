#!/usr/bin/env python3
"""
NLP Server Sentiment & Confidence Analysis Script

This script analyzes how the ash-nlp server handles sentiment and confidence
to help verify that ash-thrash evaluation logic matches ash-bot behavior.

Usage:
    python analyze_nlp_sentiment.py
"""

import requests
import json
import time
from typing import Dict, List, Tuple, Any

# Configuration
ASH_NLP_URL = "http://10.20.30.253:8881"

# Test phrases specifically designed to test sentiment + confidence handling
TEST_PHRASES = [
    {
        "phrase": "I'm feeling absolutely wonderful today, everything is amazing!",
        "expected_sentiment": "positive",
        "expected_crisis": "none",
        "description": "Strong positive sentiment - should have low crisis score"
    },
    {
        "phrase": "I hate everything, nothing matters anymore, I'm done",
        "expected_sentiment": "negative", 
        "expected_crisis": "high",
        "description": "Strong negative sentiment - should boost crisis detection"
    },
    {
        "phrase": "I'm struggling but trying to stay positive",
        "expected_sentiment": "mixed",
        "expected_crisis": "medium",
        "description": "Mixed sentiment - should moderate crisis score"
    },
    {
        "phrase": "I can't take this anymore, I'm so tired of fighting",
        "expected_sentiment": "negative",
        "expected_crisis": "high", 
        "description": "Negative sentiment with crisis language - should have high confidence"
    },
    {
        "phrase": "Gaming is frustrating but I love the challenge",
        "expected_sentiment": "mixed",
        "expected_crisis": "none",
        "description": "Gaming context with mixed sentiment - should not trigger crisis"
    }
]

def analyze_with_nlp_server(phrase: str) -> Dict[str, Any]:
    """Get raw analysis from ash-nlp server"""
    try:
        payload = {
            "message": phrase,
            "user_id": "test_verification",
            "channel_id": "test_channel",
            "timestamp": time.time()
        }
        
        response = requests.post(
            f"{ASH_NLP_URL}/analyze",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ NLP API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ NLP request failed: {e}")
        return None

def simulate_ash_bot_evaluation(nlp_result: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate how ash-bot would evaluate the NLP result"""
    
    if not nlp_result:
        return {"error": "No NLP result to evaluate"}
    
    # Extract base values
    crisis_level = nlp_result.get('crisis_level', 'none')
    base_confidence = nlp_result.get('confidence_score', 0.0)
    analysis = nlp_result.get('analysis', {})
    
    # Simulate ash-bot's sentiment adjustments
    confidence_adjustment = 0.0
    adjustment_reasons = []
    
    # Check for sentiment scores in analysis
    sentiment_scores = analysis.get('sentiment_scores', {})
    if sentiment_scores:
        # Negative sentiment boost (matches ash-bot logic)
        negative_score = sentiment_scores.get('negative', 0)
        if negative_score > 0.85:  # Very negative sentiment
            confidence_adjustment += 0.08
            adjustment_reasons.append("very_negative_sentiment (+0.08)")
        elif negative_score > 0.70:  # Moderately negative
            confidence_adjustment += 0.04
            adjustment_reasons.append("negative_sentiment (+0.04)")
        
        # Positive sentiment reduction (matches ash-bot logic)
        positive_score = sentiment_scores.get('positive', 0)
        if positive_score > 0.70:
            confidence_adjustment -= 0.10
            adjustment_reasons.append("positive_sentiment (-0.10)")
    
    # Apply adjustment and clamp to [0, 1]
    adjusted_confidence = max(0.0, min(1.0, base_confidence + confidence_adjustment))
    
    return {
        "original_crisis_level": crisis_level,
        "original_confidence": base_confidence,
        "sentiment_adjustment": confidence_adjustment,
        "adjusted_confidence": adjusted_confidence,
        "adjustment_reasons": adjustment_reasons,
        "sentiment_scores": sentiment_scores
    }

def extract_sentiment_info(nlp_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract sentiment information from NLP result"""
    analysis = nlp_result.get('analysis', {})
    
    sentiment_info = {
        'sentiment_score': analysis.get('sentiment_score', None),
        'sentiment_breakdown': {},
        'confidence_adjustments': []
    }
    
    # Look for sentiment breakdown in various formats
    if isinstance(analysis.get('sentiment_scores'), dict):
        sentiment_info['sentiment_breakdown'] = analysis['sentiment_scores']
    
    # Check for confidence adjustments or context modifications
    reasoning = nlp_result.get('reasoning', '')
    if 'sentiment' in reasoning.lower():
        sentiment_info['confidence_adjustments'].append(reasoning)
    
    return sentiment_info

def analyze_nlp_response(phrase_data: Dict[str, str]) -> Dict[str, Any]:
    """Analyze how NLP server responds and what ash-bot/ash-thrash should do with it"""
    
    phrase = phrase_data['phrase']
    print(f"\n🔍 Testing: '{phrase[:60]}...'")
    print(f"   Expected sentiment: {phrase_data['expected_sentiment']}")
    print(f"   Expected crisis: {phrase_data['expected_crisis']}")
    
    # Get NLP analysis
    nlp_result = analyze_with_nlp_server(phrase)
    if not nlp_result:
        return {"error": "Failed to get NLP analysis"}
    
    # Extract key values
    crisis_level = nlp_result.get('crisis_level', 'unknown')
    confidence = nlp_result.get('confidence_score', 0.0)
    sentiment_info = extract_sentiment_info(nlp_result)
    
    print(f"   📊 Raw NLP Result: {crisis_level} (confidence: {confidence:.3f})")
    
    # Show detailed sentiment breakdown
    if sentiment_info['sentiment_breakdown']:
        print(f"   🎭 Sentiment Breakdown:")
        for sentiment_type, score in sentiment_info['sentiment_breakdown'].items():
            print(f"      • {sentiment_type}: {score:.3f}")
    
    if sentiment_info['sentiment_score'] is not None:
        print(f"   🎭 Overall Sentiment Score: {sentiment_info['sentiment_score']:.3f}")
    
    # Simulate ash-bot processing
    ash_bot_simulation = simulate_ash_bot_evaluation(nlp_result)
    print(f"   🤖 Ash-Bot Would Process As:")
    print(f"      • Original confidence: {ash_bot_simulation['original_confidence']:.3f}")
    if ash_bot_simulation['adjustment_reasons']:
        print(f"      • Adjustments: {', '.join(ash_bot_simulation['adjustment_reasons'])}")
        print(f"      • Final confidence: {ash_bot_simulation['adjusted_confidence']:.3f}")
    else:
        print(f"      • No sentiment adjustments needed")
    
    return {
        'phrase': phrase,
        'nlp_raw': nlp_result,
        'sentiment_info': sentiment_info,
        'ash_bot_simulation': ash_bot_simulation,
        'expected': phrase_data
    }

def analyze_nlp_sentiment_handling() -> None:
    """Main analysis function for NLP server sentiment handling"""
    print("🔬 NLP Server Sentiment & Confidence Analysis")
    print("=" * 60)
    print(f"🎯 NLP Server: {ASH_NLP_URL}")
    print("🎯 Purpose: Analyze how NLP processes sentiment to guide ash-thrash logic")
    print()
    
    # Health check
    try:
        nlp_health = requests.get(f"{ASH_NLP_URL}/health", timeout=5)
        if nlp_health.status_code != 200:
            print("❌ NLP server health check failed!")
            return
        print("✅ NLP server healthy")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    print("\n" + "="*60)
    print("🧪 SENTIMENT & CONFIDENCE ANALYSIS")
    print("="*60)
    
    all_results = []
    
    for i, test_phrase in enumerate(TEST_PHRASES, 1):
        print(f"\n📝 Test {i}/{len(TEST_PHRASES)}: {test_phrase['description']}")
        
        result = analyze_nlp_response(test_phrase)
        all_results.append(result)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            continue
            
        # Check if sentiment handling makes sense
        ash_bot_sim = result['ash_bot_simulation']
        expected_sentiment = test_phrase['expected_sentiment']
        expected_crisis = test_phrase['expected_crisis']
        
        # Validate sentiment detection
        sentiment_scores = ash_bot_sim.get('sentiment_scores', {})
        if expected_sentiment == 'positive' and sentiment_scores.get('positive', 0) < 0.5:
            print("   ⚠️  Expected positive sentiment not strongly detected")
        elif expected_sentiment == 'negative' and sentiment_scores.get('negative', 0) < 0.5:
            print("   ⚠️  Expected negative sentiment not strongly detected")
        else:
            print("   ✅ Sentiment detection aligns with expectations")
            
        # Validate crisis level alignment
        actual_crisis = result['nlp_raw'].get('crisis_level', 'none')
        if actual_crisis != expected_crisis:
            print(f"   ⚠️  Crisis level mismatch: expected {expected_crisis}, got {actual_crisis}")
        else:
            print("   ✅ Crisis level aligns with expectations")
    
    # Summary and recommendations
    print("\n" + "="*60)
    print("📋 ANALYSIS SUMMARY & ASH-THRASH RECOMMENDATIONS")
    print("="*60)
    
    print("\n🔍 KEY FINDINGS:")
    sentiment_patterns = {}
    confidence_patterns = {}
    
    for result in all_results:
        if 'error' not in result:
            sim = result['ash_bot_simulation']
            expected = result['expected']['expected_sentiment']
            
            # Track sentiment patterns
            if expected not in sentiment_patterns:
                sentiment_patterns[expected] = []
            sentiment_patterns[expected].append(sim.get('sentiment_scores', {}))
            
            # Track confidence adjustments
            if sim.get('adjustment_reasons'):
                for reason in sim['adjustment_reasons']:
                    if reason not in confidence_patterns:
                        confidence_patterns[reason] = 0
                    confidence_patterns[reason] += 1
    
    print(f"   • Tested {len(TEST_PHRASES)} phrases across different sentiment types")
    print(f"   • Found {len(confidence_patterns)} types of confidence adjustments")
    
    if confidence_patterns:
        print(f"   • Most common adjustments:")
        for reason, count in sorted(confidence_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"     - {reason}: {count} times")
    
    print(f"\n🔧 ASH-THRASH IMPLEMENTATION RECOMMENDATIONS:")
    print(f"   1. Ensure ash-thrash extracts sentiment_scores from NLP analysis")
    print(f"   2. Implement the same confidence adjustments ash-bot uses:")
    print(f"      • Negative sentiment > 0.85: +0.08 confidence")
    print(f"      • Negative sentiment > 0.70: +0.04 confidence") 
    print(f"      • Positive sentiment > 0.70: -0.10 confidence")
    print(f"   3. Apply adjustments in ash_compatible_evaluation.py")
    print(f"   4. Clamp adjusted confidence to [0.0, 1.0] range")
    
    print(f"\n📊 DETAILED RESULTS FOR DEBUGGING:")
    for i, result in enumerate(all_results, 1):
        if 'error' in result:
            print(f"   Test {i}: ❌ {result['error']}")
        else:
            nlp = result['nlp_raw']
            sim = result['ash_bot_simulation']
            print(f"   Test {i}: {nlp.get('crisis_level')} (raw: {sim['original_confidence']:.3f} → final: {sim['adjusted_confidence']:.3f})")
            
            # Show sentiment breakdown
            sentiment_scores = sim.get('sentiment_scores', {})
            if sentiment_scores:
                sentiment_str = ", ".join([f"{k}:{v:.2f}" for k, v in sentiment_scores.items() if v > 0.1])
                print(f"            Sentiment: {sentiment_str}")
            
            if sim.get('adjustment_reasons'):
                print(f"            Adjustments: {', '.join(sim['adjustment_reasons'])}")

def generate_ash_thrash_code_template() -> None:
    """Generate template code for ash-thrash to handle sentiment properly"""
    
    print("\n" + "="*60)
    print("💻 ASH-THRASH CODE TEMPLATE")
    print("="*60)
    
    code_template = '''
# Add this to ash-thrash/src/utils/ash_compatible_evaluation.py

def apply_sentiment_adjustments(nlp_result: Dict[str, Any]) -> float:
    """
    Apply the same sentiment adjustments that ash-bot uses.
    This ensures ash-thrash evaluation matches ash-bot behavior.
    """
    base_confidence = nlp_result.get("confidence_score", 0.0)
    analysis = nlp_result.get('analysis', {})
    
    # Extract sentiment scores
    sentiment_scores = analysis.get('sentiment_scores', {})
    if not sentiment_scores:
        return base_confidence
    
    confidence_adjustment = 0.0
    
    # Negative sentiment boost (matches ash-bot logic)
    negative_score = sentiment_scores.get('negative', 0)
    if negative_score > 0.85:  # Very negative sentiment
        confidence_adjustment += 0.08
    elif negative_score > 0.70:  # Moderately negative
        confidence_adjustment += 0.04
    
    # Positive sentiment reduction (matches ash-bot logic) 
    positive_score = sentiment_scores.get('positive', 0)
    if positive_score > 0.70:
        confidence_adjustment -= 0.10
    
    # Apply adjustment and clamp to [0, 1]
    adjusted_confidence = max(0.0, min(1.0, base_confidence + confidence_adjustment))
    
    return adjusted_confidence

# Then modify evaluate_ash_compatible() to use this:
def evaluate_ash_compatible(phrase_data, nlp_result):
    # ... existing code ...
    
    # Instead of: confidence = nlp_result.get("confidence_score", 0)
    # Use: confidence = apply_sentiment_adjustments(nlp_result)
    
    # ... rest of function ...
'''
    
    print("📝 Add this code to your ash-thrash implementation:")
    print(code_template)
    
    print("\n🔧 Integration Steps:")
    print("   1. Add the apply_sentiment_adjustments() function")
    print("   2. Update evaluate_ash_compatible() to use it")
    print("   3. Test with sentiment-heavy phrases")
    print("   4. Verify confidence scores match expected ash-bot behavior")

if __name__ == "__main__":
    analyze_nlp_sentiment_handling()
    generate_ash_thrash_code_template()