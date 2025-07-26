#!/usr/bin/env python3
"""
Comprehensive Crisis Detection Testing Suite

This script runs the full 350-phrase test suite against the Ash NLP server
to validate crisis detection accuracy across all priority categories.

Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
Discord: https://discord.gg/alphabetcartel
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test data (we'll create these modules next)
try:
    from src.test_data import get_all_test_phrases, get_category_info
except ImportError:
    print("⚠️  Test data modules not found, using basic test set")
    
    # Fallback basic test data
    def get_all_test_phrases():
        return {
            "definite_high": [
                "I want to kill myself",
                "I'm going to end my life", 
                "I can't take it anymore, goodbye",
                "Planning to commit suicide tonight",
                "I want to die right now"
            ],
            "definite_medium": [
                "I'm feeling really depressed",
                "Life feels meaningless lately",
                "I'm struggling with severe anxiety",
                "Everything feels hopeless",
                "I can't stop crying"
            ],
            "definite_low": [
                "Having a rough day",
                "Feeling a bit down",
                "Work is stressing me out",
                "I'm worried about my grades",
                "Feeling overwhelmed with tasks"
            ],
            "definite_none": [
                "Going to the store",
                "What's for dinner",
                "Nice weather today",
                "See you tomorrow",
                "Thanks for the help"
            ]
        }
    
    def get_category_info():
        return {
            "definite_high": {"target_pass_rate": 100.0, "critical": True},
            "definite_medium": {"target_pass_rate": 65.0, "critical": False},
            "definite_low": {"target_pass_rate": 65.0, "critical": False},
            "definite_none": {"target_pass_rate": 95.0, "critical": True}
        }

def get_nlp_server_url():
    """Get NLP server URL from environment variables."""
    return os.getenv('NLP_SERVER_URL', 'http://10.20.30.16:8881')

def get_max_concurrent_tests():
    """Get maximum concurrent tests from environment."""
    return int(os.getenv('MAX_CONCURRENT_TESTS', '5'))

def test_nlp_server_health(url):
    """Test if NLP server is responding."""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def analyze_phrase(phrase_data, test_id=None):
    """Send a phrase to the NLP server for analysis."""
    phrase = phrase_data["phrase"]
    expected = phrase_data["expected_priority"]
    category = phrase_data["category"]
    
    url = get_nlp_server_url()
    
    try:
        start_time = time.time()
        
        payload = {
            "message": phrase,
            "user_id": f"test_user_{test_id}" if test_id else "test_user",
            "channel_id": "comprehensive_test_channel",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = requests.post(
            f"{url}/analyze",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            result = response.json()
            result["response_time_ms"] = response_time
            return evaluate_result(phrase_data, result)
        else:
            return create_error_result(phrase_data, f"API error: {response.status_code}")
            
    except Exception as e:
        return create_error_result(phrase_data, f"Request failed: {str(e)}")

def create_error_result(phrase_data, error_message):
    """Create an error result for failed requests."""
    return {
        "phrase": phrase_data["phrase"],
        "expected_priority": phrase_data["expected_priority"],
        "actual_priority": "error",
        "category": phrase_data["category"],
        "success": False,
        "message": f"❌ {error_message}",
        "response_time_ms": 0,
        "confidence": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": error_message
    }

def evaluate_result(phrase_data, result):
    """Evaluate if the NLP result matches expected priority."""
    if not result:
        return create_error_result(phrase_data, "No response from server")
    
    expected = phrase_data["expected_priority"]
    actual = result.get("priority", "unknown").lower()
    phrase = phrase_data["phrase"]
    category = phrase_data["category"]
    
    # Define priority mappings
    priority_map = {"high": 3, "medium": 2, "low": 1, "none": 0}
    expected_val = priority_map.get(expected, 0)
    actual_val = priority_map.get(actual, 0)
    
    # Exact match is always correct
    if expected == actual:
        success = True
        message = f"✅ Exact match: {actual}"
    # For "maybe" categories, allow escalation but not de-escalation
    elif "maybe" in category:
        if actual_val >= expected_val:
            success = True
            message = f"✅ Escalation allowed: {expected} → {actual}"
        else:
            success = False
            message = f"❌ Dangerous de-escalation: {expected} → {actual}"
    # For definite categories, require exact match
    else:
        success = False
        message = f"❌ Priority mismatch: expected {expected}, got {actual}"
    
    return {
        "phrase": phrase,
        "expected_priority": expected,
        "actual_priority": actual,
        "category": category,
        "success": success,
        "message": message,
        "response_time_ms": result.get("response_time_ms", 0),
        "confidence": result.get("confidence", 0),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def run_category_tests(category_name, phrases, max_workers=5):
    """Run tests for a specific category with concurrent execution."""
    print(f"\n🧪 Testing Category: {category_name.upper()}")
    print(f"   📝 {len(phrases)} phrases")
    
    # Prepare phrase data
    phrase_data_list = []
    for phrase in phrases:
        if isinstance(phrase, str):
            # Convert string to full phrase data
            priority = "high" if "definite_high" in category_name else \
                      "medium" if "medium" in category_name else \
                      "low" if "low" in category_name else "none"
            phrase_data_list.append({
                "phrase": phrase,
                "expected_priority": priority,
                "category": category_name
            })
        else:
            phrase_data_list.append(phrase)
    
    results = []
    
    # Use ThreadPoolExecutor for concurrent testing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_phrase = {
            executor.submit(analyze_phrase, phrase_data, i): phrase_data 
            for i, phrase_data in enumerate(phrase_data_list)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_phrase):
            result = future.result()
            results.append(result)
            
            # Show progress
            if result["success"]:
                print(f"   ✅ {len(results)}/{len(phrase_data_list)}")
            else:
                print(f"   ❌ {len(results)}/{len(phrase_data_list)}: {result['message']}")
    
    return results

def calculate_category_metrics(results, category_info):
    """Calculate metrics for a category."""
    if not results:
        return {"pass_rate": 0, "avg_response_time": 0, "total": 0, "passed": 0, "failed": 0}
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    pass_rate = (passed / total) * 100
    avg_response_time = sum(r["response_time_ms"] for r in results) / total
    
    return {
        "pass_rate": pass_rate,
        "avg_response_time": avg_response_time,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "target_pass_rate": category_info.get("target_pass_rate", 0),
        "meets_target": pass_rate >= category_info.get("target_pass_rate", 0)
    }

def run_comprehensive_test(categories=None):
    """Run the comprehensive test suite."""
    print("🧪 Ash-Thrash Comprehensive Crisis Detection Test")
    print("=" * 60)
    print(f"Repository: https://github.com/The-Alphabet-Cartel/ash-thrash")
    print(f"Discord: https://discord.gg/alphabetcartel")
    print()
    
    start_time = time.time()
    nlp_url = get_nlp_server_url()
    max_workers = get_max_concurrent_tests()
    
    print(f"🎯 Testing NLP Server: {nlp_url}")
    print(f"⚙️  Max Concurrent Tests: {max_workers}")
    print()
    
    # Health check first
    print("🔍 Running health check...")
    if not test_nlp_server_health(nlp_url):
        print("❌ NLP server health check failed!")
        return False
    
    print("✅ NLP server health check passed")
    
    # Get test data
    all_phrases = get_all_test_phrases()
    category_info = get_category_info()
    
    # Filter categories if specified
    if categories:
        all_phrases = {k: v for k, v in all_phrases.items() if k in categories}
    
    total_phrases = sum(len(phrases) for phrases in all_phrases.values())
    print(f"📝 Total test phrases: {total_phrases}")
    print(f"📂 Categories: {list(all_phrases.keys())}")
    
    # Run tests by category
    all_results = {}
    category_metrics = {}
    
    for category_name, phrases in all_phrases.items():
        category_results = run_category_tests(category_name, phrases, max_workers)
        all_results[category_name] = category_results
        
        # Calculate metrics
        cat_info = category_info.get(category_name, {})
        metrics = calculate_category_metrics(category_results, cat_info)
        category_metrics[category_name] = metrics
        
        # Show category summary
        print(f"   📊 {category_name}: {metrics['passed']}/{metrics['total']} ({metrics['pass_rate']:.1f}%)")
        if metrics['meets_target']:
            print(f"   ✅ Meets target: {metrics['target_pass_rate']:.1f}%")
        else:
            print(f"   ❌ Below target: {metrics['target_pass_rate']:.1f}%")
    
    # Calculate overall metrics
    end_time = time.time()
    total_time = end_time - start_time
    
    all_test_results = []
    for results in all_results.values():
        all_test_results.extend(results)
    
    total_passed = sum(1 for r in all_test_results if r["success"])
    total_tests = len(all_test_results)
    overall_pass_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    avg_response_time = sum(r["response_time_ms"] for r in all_test_results) / total_tests if total_tests > 0 else 0
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    print(f"✅ Overall Pass Rate: {total_passed}/{total_tests} ({overall_pass_rate:.1f}%)")
    print(f"⏱️  Total Time: {total_time:.1f}s")
    print(f"📈 Avg Response Time: {avg_response_time:.0f}ms")
    print(f"🔧 Tests per Second: {total_tests/total_time:.1f}")
    print()
    
    # Category breakdown
    print("📂 CATEGORY BREAKDOWN:")
    for category, metrics in category_metrics.items():
        status = "✅" if metrics['meets_target'] else "❌"
        print(f"{status} {category}: {metrics['pass_rate']:.1f}% (target: {metrics['target_pass_rate']:.1f}%)")
    
    print()
    
    # Save results
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results_dir = Path("results/comprehensive")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    summary = {
        "test_type": "comprehensive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nlp_server_url": nlp_url,
        "total_phrases": total_tests,
        "passed": total_passed,
        "failed": total_tests - total_passed,
        "overall_pass_rate_percent": overall_pass_rate,
        "total_time_seconds": total_time,
        "avg_response_time_ms": avg_response_time,
        "tests_per_second": total_tests / total_time,
        "category_metrics": category_metrics,
        "all_results": all_results
    }
    
    results_file = results_dir / f"comprehensive_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📁 Results saved to: {results_file}")
    
    # Determine success
    critical_categories_pass = all(
        metrics['meets_target'] for category, metrics in category_metrics.items()
        if category_info.get(category, {}).get('critical', False)
    )
    
    overall_success = overall_pass_rate >= 85.0 and critical_categories_pass
    
    if overall_success:
        print("🎉 COMPREHENSIVE TEST PASSED!")
    else:
        print("🚨 COMPREHENSIVE TEST FAILED!")
    
    return overall_success

def main():
    """Main function with command line argument handling."""
    parser = argparse.ArgumentParser(description="Ash-Thrash Comprehensive Testing")
    parser.add_argument("--category", help="Test specific category only")
    parser.add_argument("--categories", help="Test specific categories (comma-separated)")
    parser.add_argument("--server", help="Override NLP server URL")
    
    args = parser.parse_args()
    
    # Override server URL if provided
    if args.server:
        os.environ['NLP_SERVER_URL'] = args.server
    
    # Determine categories to test
    categories = None
    if args.category:
        categories = [args.category]
    elif args.categories:
        categories = [c.strip() for c in args.categories.split(',')]
    
    try:
        success = run_comprehensive_test(categories)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()