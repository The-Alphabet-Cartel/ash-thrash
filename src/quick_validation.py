#!/usr/bin/env python3
"""
Quick Validation Test for Ash Crisis Detection System

This script runs a quick 10-phrase validation test to verify the NLP server
is responding and functioning correctly. Designed for health checks and 
rapid validation.

Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
Discord: https://discord.gg/alphabetcartel
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Ash-compatible evaluation
try:
    from src.utils.ash_compatible_evaluation import evaluate_ash_compatible, get_ash_testing_goals
    USE_ASH_COMPATIBLE = True
except ImportError:
    USE_ASH_COMPATIBLE = False
    print("⚠️  Using basic evaluation - ash_compatible_evaluation not found")

# Quick validation test phrases (10 phrases)
QUICK_TEST_PHRASES = [
    {"phrase": "I want to end it all", "expected_priority": "high", "category": "definite_high"},
    {"phrase": "I'm having thoughts of suicide", "expected_priority": "high", "category": "definite_high"},
    {"phrase": "Going to the store later", "expected_priority": "none", "category": "definite_none"},
    {"phrase": "What's for dinner tonight", "expected_priority": "none", "category": "definite_none"},
    {"phrase": "I've been feeling really down lately", "expected_priority": "medium", "category": "definite_medium"},
    {"phrase": "Life feels overwhelming right now", "expected_priority": "medium", "category": "definite_medium"},
    {"phrase": "I'm a bit stressed about work", "expected_priority": "low", "category": "definite_low"},
    {"phrase": "Having a rough day", "expected_priority": "low", "category": "definite_low"},
    {"phrase": "I don't know if I can keep going", "expected_priority": "high", "category": "maybe_high_medium"},
    {"phrase": "Everything is fine", "expected_priority": "none", "category": "definite_none"}
]

def get_nlp_server_url():
    """Get NLP server URL from environment variables."""
    return os.getenv('NLP_SERVER_URL', 'http://10.20.30.16:8881')

def test_nlp_server_health(url):
    """Test if NLP server is responding."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def analyze_phrase(phrase, user_id="test_user", channel_id="test_channel"):
    """Send a phrase to the NLP server for analysis."""
    url = get_nlp_server_url()
    
    try:
        payload = {
            "message": phrase,
            "user_id": user_id,
            "channel_id": channel_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = requests.post(
            f"{url}/analyze",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def evaluate_result_ash_compatible(phrase_data, result):
    """Evaluate using Ash-compatible logic if available."""
    if USE_ASH_COMPATIBLE:
        # Use full Ash-compatible evaluation
        evaluation = evaluate_ash_compatible(phrase_data, result)
        return evaluation["success"], evaluation["message"]
    else:
        # Fallback to basic evaluation
        return evaluate_result_basic(phrase_data, result)

def evaluate_result_basic(phrase_data, result):
    """Basic evaluation logic with permissive range-based testing."""
    if not result:
        return False, "No response from server"
    
    expected = phrase_data["expected_priority"]
    # Try both 'priority' and 'crisis_level' fields (NLP server might use either)
    actual = result.get("priority", result.get("crisis_level", "unknown")).lower()
    phrase = phrase_data.get("phrase", phrase_data.get("message", ""))
    category = phrase_data.get("category", "unknown")
    
    # Define priority mappings
    priority_map = {"high": 3, "medium": 2, "low": 1, "none": 0}
    expected_val = priority_map.get(expected, 0)
    actual_val = priority_map.get(actual, 0)
    
    # Exact match is always correct
    if expected == actual:
        return True, f"✅ Exact match: {actual}"
    
    # For "maybe" categories, use permissive range-based evaluation
    if "maybe" in category:
        # Define category-specific acceptable ranges
        if category == "maybe_high_medium":
            # Should be low, medium or high (1-3), avoid none (0)
            if actual_val >= 1:
                return True, f"✅ Appropriate range: {expected} → {actual}"
            else:
                return False, f"❌ Underdetection: {expected} → {actual} (too low for crisis-level phrase)"
                
        elif category == "maybe_medium_low":
            # Should be none, low, medium, or high (0-3), accept anything!
            return True, f"✅ Appropriate range: {expected} → {actual}"
                
        elif category == "maybe_low_none":
            # Should be none or low (0-1), avoid medium/high (2-3)
            if actual_val <= 1:
                return True, f"✅ Appropriate range: {expected} → {actual}"
            else:
                return False, f"❌ Overdetection: {expected} → {actual} (false positive)"
        else:
            # Generic maybe handling - allow one step in either direction
            priority_diff = abs(actual_val - expected_val)
            if priority_diff <= 1:
                if actual_val > expected_val:
                    return True, f"✅ Escalation: {expected} → {actual}"
                elif actual_val < expected_val:
                    return True, f"✅ Descalation: {expected} → {actual}"
                else:
                    return True, f"✅ Exact match: {actual}"
            else:
                return False, f"❌ Too far off: {expected} → {actual}"
    
    # For definite categories, allow exact match or escalation/de-escalation by one level
    else:
        priority_diff = abs(expected_val - actual_val)  # Absolute difference
        
        if priority_diff == 0:
            # Exact match
            return True, f"✅ Exact match: {actual}"
        elif priority_diff == 1:
            # One level difference in either direction (allowed)
            if actual_val > expected_val:
                return True, f"✅ Escalation allowed: {expected} → {actual}"
            else:
                return True, f"✅ De-escalation allowed: {expected} → {actual}"
        else:
            # More than one level difference (not allowed)
            if actual_val > expected_val:
                return False, f"❌ Excessive escalation: {expected} → {actual} (too far up)"
            else:
                return False, f"❌ Excessive de-escalation: {expected} → {actual} (too far down)"

# Legacy function for backward compatibility
def evaluate_result(phrase_data, result):
    """Legacy function - redirects to ash_compatible evaluation."""
    return evaluate_result_ash_compatible(phrase_data, result)

def run_quick_validation():
    """Run the quick validation test."""
    print("🔍 Ash-Thrash Quick Validation Test")
    print("=" * 50)
    print(f"Repository: https://github.com/The-Alphabet-Cartel/ash-thrash")
    print(f"Discord: https://discord.gg/alphabetcartel")
    print()
    
    if USE_ASH_COMPATIBLE:
        print("✅ Using Ash-compatible evaluation logic")
    else:
        print("⚠️  Using permissive evaluation logic")
        print("🔄 Definite tests allow one-level movement in either direction")
        print("🔄 Maybe tests use permissive range-based evaluation")
    
    print()
    
    start_time = time.time()
    nlp_url = get_nlp_server_url()
    
    print(f"🎯 Testing NLP Server: {nlp_url}")
    print(f"📝 Running {len(QUICK_TEST_PHRASES)} validation phrases")
    print()
    
    # Health check first
    if not test_nlp_server_health(nlp_url):
        print("❌ NLP server health check failed!")
        return False
    
    print("✅ NLP server health check passed")
    print()
    
    # Test results
    results = []
    passed = 0
    failed = 0
    
    for i, phrase_data in enumerate(QUICK_TEST_PHRASES, 1):
        phrase = phrase_data["phrase"]
        expected = phrase_data["expected_priority"]
        category = phrase_data["category"]
        
        print(f"🧪 Test {i}/{len(QUICK_TEST_PHRASES)}: {phrase[:50]}..." if len(phrase) > 50 else f"🧪 Test {i}/{len(QUICK_TEST_PHRASES)}: {phrase}")
        
        # Analyze phrase
        result = analyze_phrase(phrase)
        success, message = evaluate_result(phrase_data, result)
        
        # Record result
        test_result = {
            "phrase": phrase,
            "expected_priority": expected,
            "actual_priority": result.get("priority", result.get("crisis_level", "error")) if result else "error",
            "category": category,
            "success": success,
            "message": message,
            "response_time_ms": result.get("response_time_ms", 0) if result else 0,
            "confidence": result.get("confidence_score", result.get("confidence", 0)) if result else 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        results.append(test_result)
        
        if success:
            passed += 1
            print(f"   {message}")
        else:
            failed += 1
            print(f"   {message}")
        
        print()
    
    # Calculate metrics
    end_time = time.time()
    total_time = end_time - start_time
    pass_rate = (passed / len(QUICK_TEST_PHRASES)) * 100
    avg_response_time = sum(r["response_time_ms"] for r in results) / len(results)
    
    # Results summary
    print("📊 QUICK VALIDATION RESULTS")
    print("=" * 30)
    print(f"✅ Passed: {passed}/{len(QUICK_TEST_PHRASES)} ({pass_rate:.1f}%)")
    print(f"❌ Failed: {failed}/{len(QUICK_TEST_PHRASES)}")
    print(f"⏱️  Total Time: {total_time:.2f}s")
    print(f"📈 Avg Response: {avg_response_time:.0f}ms")
    print()
    
    # Health assessment with updated thresholds (more permissive now)
    if USE_ASH_COMPATIBLE:
        # Use realistic thresholds for Ash-compatible mode
        if pass_rate >= 70:
            print("🎉 VALIDATION PASSED - System is healthy!")
            health_status = "healthy"
        elif pass_rate >= 50:
            print("⚠️  VALIDATION WARNING - System has minor issues")
            health_status = "warning"
        else:
            print("🚨 VALIDATION FAILED - System needs attention!")
            health_status = "critical"
    else:
        # More permissive thresholds for basic mode (since we're now more flexible)
        if pass_rate >= 70:
            print("🎉 VALIDATION PASSED - System is healthy!")
            health_status = "healthy"
        elif pass_rate >= 50:
            print("⚠️  VALIDATION WARNING - System has issues")
            health_status = "warning"
        else:
            print("🚨 VALIDATION FAILED - System needs attention!")
            health_status = "critical"
    
    # Save results
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results_dir = Path("results/quick_validation")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    summary = {
        "test_type": "quick_validation",
        "ash_compatible": USE_ASH_COMPATIBLE,
        "permissive_evaluation": True,
        "definite_bidirectional_allowed": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nlp_server_url": nlp_url,
        "total_phrases": len(QUICK_TEST_PHRASES),
        "passed": passed,
        "failed": failed,
        "pass_rate_percent": pass_rate,
        "total_time_seconds": total_time,
        "avg_response_time_ms": avg_response_time,
        "health_status": health_status,
        "details": results
    }
    
    results_file = results_dir / f"quick_validation_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📁 Results saved to: {results_file}")
    
    # Show additional insights for Ash-compatible mode
    if USE_ASH_COMPATIBLE and any(r.get("method") for r in results):
        print()
        print("🎯 ASH-COMPATIBLE INSIGHTS:")
        
        # Count detection methods
        keyword_primary = sum(1 for r in results if r.get("method") == "keyword_primary")
        nlp_primary = sum(1 for r in results if r.get("method") == "nlp_primary")
        safety_escalations = sum(1 for r in results if r.get("safety_escalation", False))
        
        print(f"   🔑 Keyword-driven decisions: {keyword_primary}/{len(results)}")
        print(f"   🧠 NLP-driven decisions: {nlp_primary}/{len(results)}")
        print(f"   🛡️ Safety escalations: {safety_escalations}/{len(results)}")
        
        if safety_escalations > 0:
            print(f"   ✅ Safety-first behavior working correctly")
    
    print()
    
    return pass_rate >= (70 if USE_ASH_COMPATIBLE else 70)

if __name__ == "__main__":
    try:
        success = run_quick_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)