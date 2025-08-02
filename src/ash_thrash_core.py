#!/usr/bin/env python3
"""
Ash-Thrash Core Testing Engine v3.0
Comprehensive testing suite for Ash NLP crisis detection system

Repository: https://github.com/the-alphabet-cartel/ash-thrash
Discord: https://discord.gg/alphabetcartel
Website: http://alphabetcartel.org
"""

import os
import json
import time
import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Load test data
from src.test_data import get_all_test_phrases, get_category_info, get_testing_goals

@dataclass
class TestResult:
    """Individual test result"""
    phrase: str
    expected_category: str
    detected_level: str
    confidence: float
    processing_time_ms: float
    passed: bool
    gap_detected: bool = False
    requires_staff_review: bool = False
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

@dataclass
class CategoryResults:
    """Results for a specific test category"""
    category_name: str
    target_pass_rate: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    goal_met: bool
    avg_confidence: float
    avg_processing_time: float
    failed_phrases: List[str]
    bidirectional_acceptable: bool = False
    acceptable_levels: List[str] = None

@dataclass
class ComprehensiveTestResults:
    """Complete test run results"""
    test_id: str
    test_type: str
    started_at: str
    completed_at: str
    total_duration_seconds: float
    nlp_server_url: str
    category_results: Dict[str, CategoryResults]
    overall_pass_rate: float
    goal_achievement_rate: float
    total_tests: int
    total_passed: int
    total_failed: int
    suggestions: List[str]

class NLPClient:
    """Enhanced NLP client that mimics ash-bot integration"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> bool:
        """Check if NLP server is healthy"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("status") == "healthy"
                return False
        except Exception:
            return False
    
    async def analyze_message(self, message: str, user_id: str = "test_user", 
                            channel_id: str = "test_channel") -> Dict:
        """Analyze message using the same format as ash-bot"""
        payload = {
            "message": message,
            "user_id": user_id,
            "channel_id": channel_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        async with self.session.post(
            f"{self.base_url}/analyze",
            json=payload,
            headers={'Content-Type': 'application/json'}
        ) as response:
            if response.status != 200:
                raise Exception(f"NLP API Error {response.status}: {await response.text()}")
            
            return await response.json()

class AshThrashTester:
    """Main testing engine for Ash-Thrash"""
    
    def __init__(self, nlp_url: str = None):
        self.nlp_url = nlp_url or os.getenv('GLOBAL_NLP_API_URL', 'http://10.20.30.253:8881')
        self.test_phrases = get_all_test_phrases()
        self.category_info = get_category_info()
        self.testing_goals = get_testing_goals()
        
    def _determine_test_pass(self, expected_category: str, detected_level: str) -> bool:
        """Determine if test passed based on expected vs detected levels"""
        goals = self.testing_goals.get(expected_category, {})
        
        # Handle bidirectional "maybe" categories
        if goals.get('allow_escalation') and goals.get('allow_descalation'):
            acceptable_range = goals.get('acceptable_range', [])
            return detected_level in acceptable_range
        
        # Handle definite categories - exact match required
        expected_mapping = {
            'definite_high': ['high'],
            'definite_medium': ['medium'], 
            'definite_low': ['low'],
            'definite_none': ['none']
        }
        
        if expected_category in expected_mapping:
            return detected_level in expected_mapping[expected_category]
        
        # Fallback - exact category name match
        return expected_category == detected_level
    
    async def run_category_test(self, category_name: str, phrases: List[str]) -> CategoryResults:
        """Run tests for a specific category"""
        print(f"🧪 Testing category: {category_name}")
        
        category_goal = self.testing_goals.get(category_name, {})
        target_pass_rate = category_goal.get('target_pass_rate', 0.0)
        
        results = []
        failed_phrases = []
        total_confidence = 0.0
        total_processing_time = 0.0
        
        async with NLPClient(self.nlp_url) as client:
            for i, phrase in enumerate(phrases, 1):
                print(f"   [{i:2}/{len(phrases)}] Testing: '{phrase[:50]}{'...' if len(phrase) > 50 else ''}'", end=" ")
                
                try:
                    start_time = time.time()
                    response = await client.analyze_message(phrase)
                    processing_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    # Extract crisis level from response (handle different possible field names)
                    detected_level = (
                        response.get('crisis_level') or 
                        response.get('priority') or 
                        response.get('level') or 
                        'none'
                    )
                    
                    confidence = response.get('confidence_score', response.get('confidence', 0.0))
                    gap_detected = response.get('gaps_detected', False)
                    requires_review = response.get('requires_staff_review', False)
                    
                    passed = self._determine_test_pass(category_name, detected_level)
                    
                    result = TestResult(
                        phrase=phrase,
                        expected_category=category_name,
                        detected_level=detected_level,
                        confidence=confidence,
                        processing_time_ms=processing_time,
                        passed=passed,
                        gap_detected=gap_detected,
                        requires_staff_review=requires_review
                    )
                    
                    results.append(result)
                    total_confidence += confidence
                    total_processing_time += processing_time
                    
                    if not passed:
                        failed_phrases.append(phrase)
                    
                    status = "✅ PASS" if passed else "❌ FAIL"
                    print(f"{status} (detected: {detected_level}, confidence: {confidence:.3f})")
                    
                except Exception as e:
                    print(f"❌ ERROR: {str(e)}")
                    failed_phrases.append(phrase)
                    results.append(TestResult(
                        phrase=phrase,
                        expected_category=category_name,
                        detected_level="error",
                        confidence=0.0,
                        processing_time_ms=0.0,
                        passed=False
                    ))
        
        # Calculate category results
        total_tests = len(phrases)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
        goal_met = pass_rate >= target_pass_rate
        avg_confidence = total_confidence / total_tests if total_tests > 0 else 0.0
        avg_processing_time = total_processing_time / total_tests if total_tests > 0 else 0.0
        
        return CategoryResults(
            category_name=category_name,
            target_pass_rate=target_pass_rate,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            pass_rate=pass_rate,
            goal_met=goal_met,
            avg_confidence=avg_confidence,
            avg_processing_time=avg_processing_time,
            failed_phrases=failed_phrases,
            bidirectional_acceptable=category_goal.get('allow_escalation', False),
            acceptable_levels=category_goal.get('acceptable_range', [])
        )
    
    async def run_comprehensive_test(self) -> ComprehensiveTestResults:
        """Run the full 350 phrase comprehensive test"""
        test_id = f"comprehensive_{int(time.time())}"
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()
        
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        print(f"Test ID: {test_id}")
        print(f"NLP Server: {self.nlp_url}")
        print(f"Total phrases: {sum(len(phrases) for phrases in self.test_phrases.values())}")
        print(f"Started: {started_at}")
        print()
        
        # Check NLP server health
        async with NLPClient(self.nlp_url) as client:
            if not await client.health_check():
                raise Exception(f"NLP server at {self.nlp_url} is not healthy")
        
        print("✅ NLP server health check passed")
        print()
        
        # Run tests for each category
        category_results = {}
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for category_name, phrases in self.test_phrases.items():
            result = await self.run_category_test(category_name, phrases)
            category_results[category_name] = result
            
            total_tests += result.total_tests
            total_passed += result.passed_tests
            total_failed += result.failed_tests
            
            print(f"📊 {category_name}: {result.pass_rate:.1f}% pass rate ({result.passed_tests}/{result.total_tests})")
            print()
        
        # Calculate overall metrics
        end_time = time.time()
        completed_at = datetime.now(timezone.utc).isoformat()
        total_duration = end_time - start_time
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0.0
        
        # Calculate goal achievement rate
        goals_met = sum(1 for result in category_results.values() if result.goal_met)
        goal_achievement_rate = (goals_met / len(category_results) * 100) if category_results else 0.0
        
        # Generate tuning suggestions
        suggestions = self._generate_tuning_suggestions(category_results)
        
        return ComprehensiveTestResults(
            test_id=test_id,
            test_type="comprehensive",
            started_at=started_at,
            completed_at=completed_at,
            total_duration_seconds=total_duration,
            nlp_server_url=self.nlp_url,
            category_results=category_results,
            overall_pass_rate=overall_pass_rate,
            goal_achievement_rate=goal_achievement_rate,
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            suggestions=suggestions
        )
    
    async def run_quick_validation(self, sample_size: int = 50) -> ComprehensiveTestResults:
        """Run a quick validation test with a subset of phrases"""
        test_id = f"quick_{int(time.time())}"
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()
        
        print(f"⚡ Starting Quick Validation Test (sample size: {sample_size})")
        print("=" * 60)
        
        # Sample phrases from each category
        sampled_phrases = {}
        for category, phrases in self.test_phrases.items():
            sample_count = min(sample_size // len(self.test_phrases), len(phrases))
            sampled_phrases[category] = phrases[:sample_count]
        
        # Temporarily replace test phrases with sample
        original_phrases = self.test_phrases
        self.test_phrases = sampled_phrases
        
        try:
            # Run the test with sampled phrases
            result = await self.run_comprehensive_test()
            result.test_type = "quick_validation"
            result.test_id = test_id
            return result
        finally:
            # Restore original phrases
            self.test_phrases = original_phrases
    
    async def run_category_specific_test(self, category_name: str) -> ComprehensiveTestResults:
        """Run tests for a specific category only"""
        if category_name not in self.test_phrases:
            raise ValueError(f"Category '{category_name}' not found. Available: {list(self.test_phrases.keys())}")
        
        test_id = f"category_{category_name}_{int(time.time())}"
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()
        
        print(f"🎯 Starting Category-Specific Test: {category_name}")
        print("=" * 60)
        
        # Run test for single category
        result = await self.run_category_test(category_name, self.test_phrases[category_name])
        
        end_time = time.time()
        completed_at = datetime.now(timezone.utc).isoformat()
        total_duration = end_time - start_time
        
        # Generate suggestions for this category
        suggestions = self._generate_category_suggestions(category_name, result)
        
        return ComprehensiveTestResults(
            test_id=test_id,
            test_type=f"category_{category_name}",
            started_at=started_at,
            completed_at=completed_at,
            total_duration_seconds=total_duration,
            nlp_server_url=self.nlp_url,
            category_results={category_name: result},
            overall_pass_rate=result.pass_rate,
            goal_achievement_rate=100.0 if result.goal_met else 0.0,
            total_tests=result.total_tests,
            total_passed=result.passed_tests,
            total_failed=result.failed_tests,
            suggestions=suggestions
        )
    
    def _generate_tuning_suggestions(self, category_results: Dict[str, CategoryResults]) -> List[str]:
        """Generate NLP tuning suggestions based on test results"""
        suggestions = []
        
        for category, result in category_results.items():
            if not result.goal_met:
                goal = self.testing_goals.get(category, {})
                current_rate = result.pass_rate
                target_rate = result.target_pass_rate
                gap = target_rate - current_rate
                
                if gap > 20:  # Large gap
                    if category.startswith('definite_high'):
                        suggestions.append(f"🚨 HIGH PRIORITY: {category} only {current_rate:.1f}% (need {target_rate}%). Consider lowering NLP_HIGH_CRISIS_THRESHOLD from 0.8 to 0.7")
                    elif category.startswith('definite_none'):
                        suggestions.append(f"⚠️  FALSE POSITIVE ISSUE: {category} only {current_rate:.1f}% (need {target_rate}%). Consider raising NLP_NONE_THRESHOLD from 0.3 to 0.4")
                    else:
                        suggestions.append(f"📈 TUNING NEEDED: {category} only {current_rate:.1f}% (need {target_rate}%). Review threshold settings")
                elif gap > 10:  # Medium gap
                    suggestions.append(f"🔧 MINOR TUNING: {category} at {current_rate:.1f}% (need {target_rate}%). Small threshold adjustment may help")
        
        # Overall suggestions
        overall_achievement = sum(1 for r in category_results.values() if r.goal_met) / len(category_results) * 100
        if overall_achievement < 85:
            suggestions.append("🎯 OVERALL: Consider running learning system feedback to improve model performance")
        
        return suggestions
    
    def _generate_category_suggestions(self, category_name: str, result: CategoryResults) -> List[str]:
        """Generate suggestions for a specific category"""
        suggestions = []
        
        if not result.goal_met:
            gap = result.target_pass_rate - result.pass_rate
            suggestions.append(f"Category {category_name} is {gap:.1f}% below target ({result.pass_rate:.1f}% vs {result.target_pass_rate}%)")
            
            if result.failed_phrases:
                suggestions.append(f"Failed phrases: {len(result.failed_phrases)} out of {result.total_tests}")
                if len(result.failed_phrases) <= 5:
                    for phrase in result.failed_phrases:
                        suggestions.append(f"  • '{phrase[:60]}{'...' if len(phrase) > 60 else ''}'")
        
        return suggestions

# Main execution functions
async def main():
    """Main testing function"""
    import sys
    
    # Parse command line arguments
    test_type = sys.argv[1] if len(sys.argv) > 1 else "comprehensive"
    
    tester = AshThrashTester()
    
    try:
        if test_type == "comprehensive":
            results = await tester.run_comprehensive_test()
        elif test_type == "quick":
            results = await tester.run_quick_validation()
        elif test_type.startswith("category_"):
            category_name = test_type.replace("category_", "")
            results = await tester.run_category_specific_test(category_name)
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("Available types: comprehensive, quick, category_<name>")
            return
        
        # Print results
        print("\n" + "=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Test ID: {results.test_id}")
        print(f"Test Type: {results.test_type}")
        print(f"Duration: {results.total_duration_seconds:.2f} seconds")
        print(f"Overall Pass Rate: {results.overall_pass_rate:.1f}%")
        print(f"Goal Achievement: {results.goal_achievement_rate:.1f}%")
        print(f"Total Tests: {results.total_tests}")
        print(f"Passed: {results.total_passed}")
        print(f"Failed: {results.total_failed}")
        
        if results.suggestions:
            print("\n🔧 TUNING SUGGESTIONS:")
            for suggestion in results.suggestions:
                print(f"  {suggestion}")
        
        # Save results to file
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f"{results.test_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())