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

def evaluate_result(phrase_data, result):
    """Evaluate if the NLP result matches expected priority."""
    if not result:
        return False, "No response from server"
    
    expected = phrase_data["expected_priority"]
    # Try both 'priority' and 'crisis_level' fields (NLP server might use either)
    actual = result.get("priority", result.get("crisis_level", "unknown")).lower()
    phrase = phrase_data["phrase"]
    category = phrase_data["category"]
    
    # Define priority mappings
    priority_map = {"high": 3, "medium": 2, "low": 1, "none": 0}
    expected_val = priority_map.get(expected, 0)
    actual_val = priority_map.get(actual, 0)
    
    # Exact match is always correct
    if expected == actual:
        return True, f"✅ Exact match: {actual}"
    
    # For "maybe" categories, allow escalation but not de-escalation
    if "maybe" in category:
        if actual_val >= expected_val:
            return True, f"✅ Escalation allowed: {expected} → {actual}"
        else:
            return False, f"❌ Dangerous de-escalation: {expected} → {actual}"
    
    # For definite categories, require exact match
    return False, f"❌ Priority mismatch: expected {expected}, got {actual}"

def run_quick_validation():
    """Run the quick validation test."""
    print("🔍 Ash-Thrash Quick Validation Test")
    print("=" * 50)
    print(f"Repository: https://github.com/The-Alphabet-Cartel/ash-thrash")
    print(f"Discord: https://discord.gg/alphabetcartel")
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
    
    # Health assessment
    if pass_rate >= 80:
        print("🎉 VALIDATION PASSED - System is healthy!")
        health_status = "healthy"
    elif pass_rate >= 60:
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
    print()
    
    return pass_rate >= 80

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