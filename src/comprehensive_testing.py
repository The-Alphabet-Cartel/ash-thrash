#!/usr/bin/env python3
"""
Comprehensive Crisis Detection Testing Suite

This script runs the full test suite against the Ash NLP server
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

# Import test data with fallback
def get_all_test_phrases():
    """Get test phrases - tries to import from test_data module, falls back to basic set."""
    try:
        from src.test_data import get_all_test_phrases as import_phrases
        print("✅ Test data modules imported successfully")
        return import_phrases()
    except ImportError:
        print("⚠️  Test data modules not found, using basic test set")
        return {
            "definite_high": [
                {"message": "I want to kill myself", "expected_priority": "high", "category": "definite_high"},
                {"message": "I'm going to end my life", "expected_priority": "high", "category": "definite_high"}, 
                {"message": "I can't take it anymore, goodbye", "expected_priority": "high", "category": "definite_high"},
                {"message": "Planning to commit suicide tonight", "expected_priority": "high", "category": "definite_high"},
                {"message": "I want to die right now", "expected_priority": "high", "category": "definite_high"}
            ],
            "definite_medium": [
                {"message": "I'm feeling really depressed", "expected_priority": "medium", "category": "definite_medium"},
                {"message": "Life feels meaningless lately", "expected_priority": "medium", "category": "definite_medium"},
                {"message": "I'm struggling with severe anxiety", "expected_priority": "medium", "category": "definite_medium"},
                {"message": "Everything feels hopeless", "expected_priority": "medium", "category": "definite_medium"},
                {"message": "I can't stop crying", "expected_priority": "medium", "category": "definite_medium"}
            ],
            "definite_low": [
                {"message": "Having a rough day", "expected_priority": "low", "category": "definite_low"},
                {"message": "Feeling a bit down", "expected_priority": "low", "category": "definite_low"},
                {"message": "Work is stressing me out", "expected_priority": "low", "category": "definite_low"},
                {"message": "I'm worried about my grades", "expected_priority": "low", "category": "definite_low"},
                {"message": "Feeling overwhelmed with tasks", "expected_priority": "low", "category": "definite_low"}
            ],
            "definite_none": [
                {"message": "Going to the store", "expected_priority": "none", "category": "definite_none"},
                {"message": "What's for dinner", "expected_priority": "none", "category": "definite_none"},
                {"message": "Nice weather today", "expected_priority": "none", "category": "definite_none"},
                {"message": "See you tomorrow", "expected_priority": "none", "category": "definite_none"},
                {"message": "Thanks for the help", "expected_priority": "none", "category": "definite_none"}
            ]
        }

def get_category_info():
    """Get category info - tries to import from test_data module, falls back to basic set."""
    try:
        from src.test_data import get_category_info as import_info
        return import_info()
    except ImportError:
        return {
            "definite_high": {"target_pass_rate": 100.0, "critical": True},
            "definite_medium": {"target_pass_rate": 65.0, "critical": False},
            "definite_low": {"target_pass_rate": 65.0, "critical": False},
            "definite_none": {"target_pass_rate": 95.0, "critical": True}
        }

# Import Ash-compatible evaluation
USE_ASH_COMPATIBLE = False
try:
    from src.utils.ash_compatible_evaluation import evaluate_ash_compatible, get_ash_testing_goals
    USE_ASH_COMPATIBLE = True
    print("✅ Ash-compatible evaluation imported successfully")
    print("✅ Sentiment adjustments will be applied during evaluation")
except ImportError:
    print("⚠️  Using basic evaluation - ash_compatible_evaluation not found")

def get_GLOBAL_NLP_API_URL():
    """Get NLP server URL from environment variables."""
    return os.getenv('GLOBAL_NLP_API_URL', 'http://10.20.30.253:8881')

def get_max_concurrent_tests():
    """Get maximum concurrent tests from environment."""
    return int(os.getenv('THRASH_MAX_CONCURRENT_TESTS', '5'))

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
    # Handle the actual data format from our test data module
    phrase = phrase_data.get("phrase", phrase_data.get("message", ""))
    expected = phrase_data["expected_priority"]
    # Category might not be in the data, so we'll pass it from the calling function
    category = phrase_data.get("category", "unknown")
    
    url = get_GLOBAL_NLP_API_URL()
    
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
            
            # Use Ash-compatible evaluation if available
            if USE_ASH_COMPATIBLE:
                return evaluate_ash_compatible(phrase_data, result)
            else:
                return evaluate_single_phrase(phrase_data, result)
        else:
            return create_error_result(phrase_data, f"API error: {response.status_code}")
            
    except Exception as e:
        return create_error_result(phrase_data, f"Request failed: {str(e)}")

def create_error_result(phrase_data, error_message):
    """Create an error result for failed requests."""
    return {
        "phrase": phrase_data.get("phrase", phrase_data.get("message", "")),
        "expected_priority": phrase_data["expected_priority"],
        "actual_priority": "error",
        "category": phrase_data.get("category", "unknown"),
        "success": False,
        "message": f"❌ {error_message}",
        "response_time_ms": 0,
        "confidence": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": error_message,
        "subcategory": phrase_data.get("subcategory", ""),
        "description": phrase_data.get("description", "")
    }

def evaluate_single_phrase(phrase_data, result):
    """Evaluate a single phrase result with sentiment-aware logic"""
    if USE_ASH_COMPATIBLE:
        # Use Ash-compatible evaluation with sentiment adjustments
        evaluation = evaluate_ash_compatible(phrase_data, result)
        return evaluation["success"], evaluation["message"], evaluation.get("extra_data", {})
    else:
        # Fallback to basic evaluation
        success, message = evaluate_result(phrase_data, result)
        return success, message, {}

def evaluate_result(phrase_data, result):
    """Evaluate if the NLP result matches expected priority - uses permissive range-based logic."""
    if not result:
        return create_error_result(phrase_data, "No response from server")
    
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
        success = True
        message = f"✅ Exact match: {actual}"
    
    # For "maybe" categories, use permissive range-based evaluation
    elif "maybe" in category:
        # Define category-specific acceptable ranges
        if category == "maybe_high_medium":
            # Should be low, medium or high (1-3), avoid none (0)
            if actual_val >= 1:
                success = True
                message = f"✅ Appropriate range: {expected} → {actual}"
            else:
                success = False
                message = f"❌ Underdetection: {expected} → {actual} (too low for crisis-level phrase)"
                
        elif category == "maybe_medium_low":
            # Should be none, low, medium, or high (0-3), accept anything!
            success = True
            message = f"✅ Appropriate range: {expected} → {actual}"
                
        elif category == "maybe_low_none":
            # Should be none or low (0-1), avoid medium/high (2-3)
            if actual_val <= 1:
                success = True
                message = f"✅ Appropriate range: {expected} → {actual}"
            else:
                success = False
                message = f"❌ Overdetection: {expected} → {actual} (false positive)"
        else:
            # Generic maybe handling - allow one step in either direction
            priority_diff = abs(actual_val - expected_val)
            if priority_diff <= 1:
                success = True
                if actual_val > expected_val:
                    message = f"✅ Escalation: {expected} → {actual}"
                elif actual_val < expected_val:
                    message = f"✅ Descalation: {expected} → {actual}"
                else:
                    message = f"✅ Exact match: {actual}"
            else:
                success = False
                message = f"❌ Too far off: {expected} → {actual}"
    
    # For definite categories, allow exact match or escalation/de-escalation by one level
    else:
        priority_diff = abs(expected_val - actual_val)  # Absolute difference
        
        if priority_diff == 0:
            # Exact match
            success = True
            message = f"✅ Exact match: {actual}"
        elif priority_diff == 1:
            # One level difference in either direction (allowed)
            if actual_val > expected_val:
                success = True
                message = f"✅ Escalation allowed: {expected} → {actual}"
            else:
                success = True
                message = f"✅ De-escalation allowed: {expected} → {actual}"
        else:
            # More than one level difference (not allowed)
            if actual_val > expected_val:
                success = False
                message = f"❌ Excessive escalation: {expected} → {actual} (too far up)"
            else:
                success = False
                message = f"❌ Excessive de-escalation: {expected} → {actual} (too far down)"
    
    return {
        "phrase": phrase,
        "expected_priority": expected,
        "actual_priority": actual,
        "category": category,
        "success": success,
        "message": message,
        "response_time_ms": result.get("response_time_ms", 0),
        "confidence": result.get("confidence_score", result.get("confidence", 0)),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subcategory": phrase_data.get("subcategory", ""),
        "description": phrase_data.get("description", "")
    }

def run_category_tests(category_name, phrases, max_workers=5):
    """Run tests for a specific category with concurrent execution."""
    print(f"\n🧪 Testing Category: {category_name.upper()}")
    print(f"   📝 {len(phrases)} phrases")
    
    # Add category info to each phrase data
    phrase_data_list = []
    for phrase_data in phrases:
        # Create a copy and ensure it has the category field
        updated_phrase_data = phrase_data.copy()
        updated_phrase_data["category"] = category_name
        phrase_data_list.append(updated_phrase_data)
    
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
            
            # Show detailed progress with phrase text and confidence
            phrase_text = result["phrase"]
            # Truncate long phrases for cleaner display
            display_phrase = phrase_text[:50] + "..." if len(phrase_text) > 50 else phrase_text
            confidence = result.get("confidence", 0)
            
            if result["success"]:
                print(f"   ✅ {len(results)}/{len(phrase_data_list)}: \"{display_phrase}\" → {result['actual_priority']} (conf: {confidence:.3f})")
            else:
                print(f"   ❌ {len(results)}/{len(phrase_data_list)}: \"{display_phrase}\" → {result['actual_priority']} (conf: {confidence:.3f}) - {result['message']}")
        
        return results

def calculate_category_metrics(results, category_info):
    """Calculate metrics for a category."""
    if not results:
        return {"pass_rate": 0, "avg_response_time": 0, "total": 0, "passed": 0, "failed": 0}
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    pass_rate = (passed / total) * 100
    
    # Safely calculate average response time
    response_times = [r.get("response_time_ms", 0) for r in results]
    avg_response_time = sum(response_times) / total if total > 0 else 0
    
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
    nlp_url = get_GLOBAL_NLP_API_URL()
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
    
    # Use Ash-compatible goals if available
    if USE_ASH_COMPATIBLE:
        category_info = get_ash_testing_goals()
        print("✅ Using Ash-compatible evaluation logic")
    else:
        category_info = get_category_info()
        print("⚠️  Using basic evaluation logic")
    
    # Filter categories if specified
    if categories:
        all_phrases = {k: v for k, v in all_phrases.items() if k in categories}
    
    total_phrases = sum(len(phrases) for phrases in all_phrases.values())
    print(f"📝 Total test phrases: {total_phrases}")
    print(f"📂 Categories: {list(all_phrases.keys())}")
    print(f"🔄 Maybe tests use permissive range-based evaluation (more flexible)")
    print(f"   📈 maybe_high_medium: accepts low, medium OR high")
    print(f"   📊 maybe_medium_low: accepts ANY priority (none, low, medium, high)") 
    print(f"   📉 maybe_low_none: accepts none OR low")
    print()
    
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
        
        # Show examples of failures for debugging
        failures = [r for r in category_results if not r["success"]]
        if failures:
            print(f"   🔍 Sample failures:")
            for i, failure in enumerate(failures[:3]):  # Show first 3 failures
                phrase_text = failure["phrase"][:45] + "..." if len(failure["phrase"]) > 45 else failure["phrase"]
                confidence = failure.get("confidence", 0)
                expected = failure["expected_priority"]
                actual = failure["actual_priority"]
                print(f"      {i+1}. \"{phrase_text}\"")
                print(f"         Expected: {expected} | Got: {actual} | Confidence: {confidence:.3f}")
            if len(failures) > 3:
                print(f"      ... and {len(failures) - 3} more failures")
        
        # Show confidence distribution for this category
        confidences = [r.get("confidence", 0) for r in category_results if r.get("confidence", 0) > 0]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            min_confidence = min(confidences)
            max_confidence = max(confidences)
            print(f"   📈 Confidence stats: avg={avg_confidence:.3f}, min={min_confidence:.3f}, max={max_confidence:.3f}")
        
        print()  # Add spacing between categories
    
    # Calculate overall metrics
    end_time = time.time()
    total_time = end_time - start_time
    
    all_test_results = []
    for results in all_results.values():
        all_test_results.extend(results)
    
    total_passed = sum(1 for r in all_test_results if r["success"])
    total_tests = len(all_test_results)
    overall_pass_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    # Safely calculate average response time
    response_times = [r.get("response_time_ms", 0) for r in all_test_results]
    avg_response_time = sum(response_times) / total_tests if total_tests > 0 else 0
    
    # Calculate confidence statistics
    all_confidences = [r.get("confidence", 0) for r in all_test_results if r.get("confidence", 0) > 0]
    avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
    
    # Confidence by success/failure
    success_confidences = [r.get("confidence", 0) for r in all_test_results if r["success"] and r.get("confidence", 0) > 0]
    failure_confidences = [r.get("confidence", 0) for r in all_test_results if not r["success"] and r.get("confidence", 0) > 0]
    
    avg_success_confidence = sum(success_confidences) / len(success_confidences) if success_confidences else 0
    avg_failure_confidence = sum(failure_confidences) / len(failure_confidences) if failure_confidences else 0
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    print(f"✅ Overall Pass Rate: {total_passed}/{total_tests} ({overall_pass_rate:.1f}%)")
    print(f"⏱️  Total Time: {total_time:.1f}s")
    print(f"📈 Avg Response Time: {avg_response_time:.0f}ms")
    print(f"🔧 Tests per Second: {total_tests/total_time:.1f}")
    print(f"🎯 Overall Confidence: {avg_confidence:.3f}")
    print(f"   ✅ Success Confidence: {avg_success_confidence:.3f}")
    print(f"   ❌ Failure Confidence: {avg_failure_confidence:.3f}")
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
        "ash_compatible": USE_ASH_COMPATIBLE,
        "definite_bidirectional_allowed": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "GLOBAL_NLP_API_URL": nlp_url,
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
    
    # Determine success using appropriate criteria
    if USE_ASH_COMPATIBLE:
        # Ash-compatible success: critical categories must meet targets + overall 80%+
        critical_categories = ['definite_high', 'definite_none', 'maybe_low_none']
        critical_success = all(
            category_metrics.get(cat, {}).get('meets_target', False) 
            for cat in critical_categories if cat in category_metrics
        )
        overall_success = overall_pass_rate >= 80.0 and critical_success
        
        print("🎯 Using Ash-Compatible Success Criteria:")
        print(f"   Critical categories: {critical_categories}")
        print(f"   Critical success: {critical_success}")
        print(f"   Overall threshold: 80%")
    else:
        # Original success criteria
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
        os.environ['GLOBAL_NLP_API_URL'] = args.server
    
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