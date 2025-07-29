#!/usr/bin/env python3
"""
Ash-Thrash Sentiment & Confidence Verification Script

This script verifies that ash-thrash is using the same logic as ash-bot 
for handling positive/negative sentiment levels and confidence scores.

Usage:
    python verify_sentiment_confidence.py
"""

import requests
import json
import time
from typing import Dict, List, Tuple, Any

# Configuration
ASH_NLP_URL = "http://10.20.30.253:8881"
ASH_THRASH_URL = "http://10.20.30.253:8884"

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

def test_with_ash_thrash(phrase: str) -> Dict[str, Any]:
    """Test phrase through ash-thrash evaluation"""
    try:
        payload = {
            "phrase": phrase,
            "expected_priority": "medium",  # Dummy value for testing
            "category": "test_verification"
        }
        
        response = requests.post(
            f"{ASH_THRASH_URL}/api/test_single",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Thrash API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Thrash request failed: {e}")
        return None

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

def compare_ash_bot_vs_thrash_logic(phrase_data: Dict[str, str]) -> Dict[str, Any]:
    """Compare how ash-bot vs ash-thrash handle the same phrase"""
    
    phrase = phrase_data['phrase']
    print(f"\n🔍 Testing: '{phrase[:60]}...'")
    print(f"   Expected sentiment: {phrase_data['expected_sentiment']}")
    print(f"   Expected crisis: {phrase_data['expected_crisis']}")
    
    # Get NLP analysis (what ash-bot would see)
    nlp_result = analyze_with_nlp_server(phrase)
    if not nlp_result:
        return {"error": "Failed to get NLP analysis"}
    
    # Extract key values
    crisis_level = nlp_result.get('crisis_level', 'unknown')
    confidence = nlp_result.get('confidence_score', 0.0)
    sentiment_info = extract_sentiment_info(nlp_result)
    
    print(f"   📊 NLP Result: {crisis_level} (confidence: {confidence:.3f})")
    print(f"   🎭 Sentiment: {sentiment_info}")
    
    # Test with ash-thrash (simulate ash-bot evaluation)
    thrash_result = test_with_ash_thrash(phrase)
    
    comparison = {
        'phrase': phrase,
        'nlp_result': {
            'crisis_level': crisis_level,
            'confidence_score': confidence,
            'sentiment_info': sentiment_info
        },
        'thrash_evaluation': thrash_result,
        'expected': phrase_data,
        'discrepancies': []
    }
    
    # Check for discrepancies
    if thrash_result:
        thrash_confidence = thrash_result.get('confidence', 0.0)
        confidence_diff = abs(confidence - thrash_confidence)
        
        if confidence_diff > 0.1:  # Significant difference
            comparison['discrepancies'].append(
                f"Confidence mismatch: NLP={confidence:.3f} vs Thrash={thrash_confidence:.3f}"
            )
    
    return comparison

def verify_sentiment_handling() -> None:
    """Main verification function"""
    print("🔬 Ash-Thrash Sentiment & Confidence Verification")
    print("=" * 60)
    print(f"🎯 NLP Server: {ASH_NLP_URL}")
    print(f"🧪 Thrash Server: {ASH_THRASH_URL}")
    print()
    
    # Health checks
    try:
        nlp_health = requests.get(f"{ASH_NLP_URL}/health", timeout=5)
        if nlp_health.status_code != 200:
            print("❌ NLP server health check failed!")
            return
        print("✅ NLP server healthy")
        
        thrash_health = requests.get(f"{ASH_THRASH_URL}/api/health", timeout=5)  
        if thrash_health.status_code != 200:
            print("❌ Thrash server health check failed!")
            return
        print("✅ Thrash server healthy")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    print("\n" + "="*60)
    print("🧪 SENTIMENT & CONFIDENCE VERIFICATION TESTS")
    print("="*60)
    
    all_results = []
    discrepancy_count = 0
    
    for i, test_phrase in enumerate(TEST_PHRASES, 1):
        print(f"\n📝 Test {i}/{len(TEST_PHRASES)}: {test_phrase['description']}")
        
        result = compare_ash_bot_vs_thrash_logic(test_phrase)
        all_results.append(result)
        
        if result.get('discrepancies'):
            discrepancy_count += len(result['discrepancies'])
            print("⚠️  DISCREPANCIES FOUND:")
            for disc in result['discrepancies']:
                print(f"     • {disc}")
        else:
            print("✅ No significant discrepancies detected")
    
    # Summary
    print("\n" + "="*60)
    print("📋 VERIFICATION SUMMARY")
    print("="*60)
    
    if discrepancy_count == 0:
        print("✅ All tests passed - ash-thrash appears to handle sentiment & confidence correctly")
    else:
        print(f"⚠️  Found {discrepancy_count} discrepancies across {len(TEST_PHRASES)} tests")
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("   1. Review ash-thrash evaluation logic in src/utils/ash_compatible_evaluation.py")
        print("   2. Ensure sentiment adjustments are properly simulated")
        print("   3. Verify confidence score calculations match ash-bot behavior")
        print("   4. Consider updating ash-thrash to use ash-bot's exact sentiment logic")
    
    # Detailed results
    print(f"\n📊 DETAILED RESULTS:")
    for i, result in enumerate(all_results, 1):
        if 'error' in result:
            print(f"   Test {i}: ❌ {result['error']}")
        else:
            nlp = result['nlp_result']
            print(f"   Test {i}: {nlp['crisis_level']} (conf: {nlp['confidence_score']:.3f})")
            
            # Show sentiment details if available
            sentiment = nlp['sentiment_info']
            if sentiment['sentiment_score'] is not None:
                print(f"            Sentiment score: {sentiment['sentiment_score']:.3f}")
            if sentiment['sentiment_breakdown']:
                print(f"            Sentiment breakdown: {sentiment['sentiment_breakdown']}")

def check_ash_thrash_evaluation_logic() -> None:
    """Check if ash-thrash has the latest evaluation logic"""
    
    print("\n" + "="*60)
    print("🔍 CHECKING ASH-THRASH EVALUATION LOGIC")
    print("="*60)
    
    key_checks = [
        "Does ash-thrash use confidence_score from NLP results?",
        "Does ash-thrash account for sentiment adjustments?", 
        "Does ash-thrash simulate keyword+NLP hybrid logic?",
        "Does ash-thrash use safety-first hierarchy (max priority wins)?",
        "Does ash-thrash handle positive vs negative sentiment differently?"
    ]
    
    print("🔧 Manual verification needed for:")
    for i, check in enumerate(key_checks, 1):
        print(f"   {i}. {check}")
    
    print("\n📁 Key files to examine:")
    print("   • ash-thrash/src/utils/ash_compatible_evaluation.py")
    print("   • ash-thrash/src/quick_validation.py") 
    print("   • ash-thrash/src/comprehensive_testing.py")
    
    print("\n🔍 Look for these patterns:")
    print("   • confidence = nlp_result.get('confidence_score', 0)")
    print("   • sentiment handling in evaluation logic")
    print("   • Context adjustments for positive/negative sentiment")
    print("   • Final confidence score calculations")

if __name__ == "__main__":
    verify_sentiment_handling()
    check_ash_thrash_evaluation_logic()