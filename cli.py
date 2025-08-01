#!/usr/bin/env python3
"""
Ash-Thrash CLI Management Tool v3.0
Standard Python command interface for all testing operations

Repository: https://github.com/the-alphabet-cartel/ash-thrash
Discord: https://discord.gg/alphabetcartel
Website: http://alphabetcartel.org

Usage:
    python cli.py test comprehensive
    python cli.py test quick
    python cli.py test category definite_high
    python cli.py api start
    python cli.py validate setup
    python cli.py api trigger comprehensive
"""

import asyncio
import json
import os
import sys
import time
import argparse
from pathlib import Path
from typing import Optional
import requests
from datetime import datetime

# Import our core modules
from src.ash_thrash_core import AshThrashTester
from src.test_data import validate_test_data, get_category_info
from src.ash_thrash_api import app

def print_header(title: str, width: int = 60):
    """Print a formatted header"""
    print("=" * width)
    print(title)
    print("=" * width)

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️ {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️ {message}")

# =============================================================================
# TESTING COMMANDS
# =============================================================================

async def run_comprehensive_test(args):
    """Run comprehensive test suite (350 phrases)"""
    print("🧪 Starting Comprehensive Crisis Detection Test")
    print_header("Ash-Thrash Comprehensive Testing")
    print(f"Repository: https://github.com/the-alphabet-cartel/ash-thrash")
    print(f"Discord: https://discord.gg/alphabetcartel")
    print()
    
    tester = AshThrashTester()
    results = await tester.run_comprehensive_test()
    
    if args.output == 'json':
        print(json.dumps(results, default=str, indent=2))
    elif args.output == 'file':
        results_file = Path("results") / f"{results.test_id}_results.json"
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, default=str, indent=2)
        print_success(f"Results saved to: {results_file}")
    else:
        # Console output (default)
        print_test_results(results)
    
    if getattr(args, 'save_results', True) and args.output != 'file':
        results_file = Path("results") / f"{results.test_id}_results.json"
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, default=str, indent=2)
        print(f"\n💾 Results also saved to: {results_file}")

async def run_quick_test(args):
    """Run quick validation test (subset of phrases)"""
    print(f"⚡ Starting Quick Validation Test (sample size: {args.sample_size})")
    print_header("Ash-Thrash Quick Testing")
    
    tester = AshThrashTester()
    results = await tester.run_quick_validation(args.sample_size)
    
    if args.output == 'json':
        print(json.dumps(results, default=str, indent=2))
    else:
        print_test_results(results)

async def run_category_test(args):
    """Run category-specific test"""
    available_categories = list(get_category_info().keys())
    
    if args.category_name not in available_categories:
        print_error(f"Invalid category: {args.category_name}")
        print(f"Available categories: {', '.join(available_categories)}")
        sys.exit(1)
    
    print(f"🎯 Starting Category-Specific Test: {args.category_name}")
    print_header("Ash-Thrash Category Testing")
    
    tester = AshThrashTester()
    results = await tester.run_category_specific_test(args.category_name)
    
    if args.output == 'json':
        print(json.dumps(results, default=str, indent=2))
    else:
        print_test_results(results)

# =============================================================================
# API COMMANDS
# =============================================================================

def start_api_server(args):
    """Start the API server"""
    print("🚀 Starting Ash-Thrash API Server")
    print_header("API Server Startup")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"API Docs: http://{args.host}:{args.port}/docs")
    print()
    
    import uvicorn
    uvicorn.run(
        "src.ash_thrash_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
        access_log=True
    )

def trigger_api_test(args):
    """Trigger a test via API"""
    print(f"🧪 Triggering {args.test_type} test via API")
    print(f"API URL: {args.api_url}")
    print()
    
    # Trigger test
    try:
        response = requests.post(
            f"{args.api_url}/api/test/trigger",
            json={
                "test_type": args.test_type,
                "triggered_by": "cli"
            },
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        test_id = result['test_id']
        
        print_success("Test triggered successfully!")
        print(f"Test ID: {test_id}")
        print(f"Estimated duration: {result['estimated_duration_seconds']}s")
        
        if args.wait:
            print("\n⏳ Waiting for test completion...")
            wait_for_test_completion(args.api_url, test_id)
        else:
            print(f"\n📊 Monitor status: {args.api_url}/api/test/status/{test_id}")
            print(f"📊 Get results: {args.api_url}/api/test/results/{test_id}")
            
    except requests.exceptions.RequestException as e:
        print_error(f"API request failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)

def check_api_health(args):
    """Check API server health"""
    try:
        response = requests.get(f"{args.api_url}/health", timeout=5)
        response.raise_for_status()
        
        health_data = response.json()
        
        print("🏥 API Server Health Check")
        print_header("Health Status")
        print(f"Status: {'✅' if health_data['status'] == 'healthy' else '❌'} {health_data['status']}")
        print(f"Version: {health_data['version']}")
        print(f"NLP Server: {'✅' if health_data['nlp_server_status'] == 'healthy' else '❌'} {health_data['nlp_server_status']}")
        print(f"NLP URL: {health_data['nlp_server_url']}")
        print(f"Test Data: {'✅' if health_data['test_data_status'] == 'valid' else '❌'} {health_data['test_data_status']}")
        print(f"Total Phrases: {health_data['total_phrases']}")
        print(f"Uptime: {health_data['uptime_seconds']:.1f}s")
        
    except requests.exceptions.RequestException as e:
        print_error(f"Health check failed: {str(e)}")
        sys.exit(1)

# =============================================================================
# VALIDATION COMMANDS
# =============================================================================

def validate_setup(args):
    """Validate ash-thrash setup and configuration"""
    print("🔍 Validating Ash-Thrash Setup")
    print_header("Setup Validation")
    
    issues = []
    
    # 1. Check Python version
    print("1. Checking Python version...")
    python_version = sys.version_info
    print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 8):
        issues.append("Python 3.8+ required")
        print_error("   Python 3.8+ required")
    else:
        print_success("   Python version OK")
    
    # 2. Check directory structure
    print("\n2. Checking directory structure...")
    required_files = [
        "src/ash_thrash_core.py",
        "src/test_data.py", 
        "src/ash_thrash_api.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"   {file_path} found")
        else:
            print_error(f"   {file_path} missing")
            issues.append(f"Missing {file_path}")
    
    # 3. Check environment variables
    print("\n3. Checking environment configuration...")
    nlp_url = os.getenv('GLOBAL_NLP_API_URL')
    if nlp_url:
        print_success(f"   GLOBAL_NLP_API_URL: {nlp_url}")
    else:
        print_warning("   GLOBAL_NLP_API_URL not set (using default)")
    
    # 4. Validate test data
    print("\n4. Validating test data...")
    try:
        validation = validate_test_data()
        if validation["correct_total"] and validation["all_categories_have_50"]:
            print_success(f"   Test data validated: {validation['total_phrases']} phrases")
        else:
            print_error(f"   Test data validation failed: {validation['total_phrases']} phrases")
            issues.append("Invalid test data structure")
    except Exception as e:
        print_error(f"   Test data validation error: {str(e)}")
        issues.append(f"Test data error: {str(e)}")
    
    # 5. Test NLP connectivity
    print("\n5. Testing NLP server connectivity...")
    nlp_url = nlp_url or "http://10.20.30.253:8881"
    try:
        response = requests.get(f"{nlp_url}/health", timeout=5)
        if response.status_code == 200:
            print_success("   NLP server is reachable")
        else:
            print_error(f"   NLP server returned {response.status_code}")
            issues.append(f"NLP server unhealthy: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print_error(f"   NLP server unreachable: {str(e)}")
        issues.append(f"NLP server unreachable: {str(e)}")
    
    # Summary
    print("\n🎯 Setup Validation Results")
    print_header("Validation Summary")
    if not issues:
        print_success("All validation checks passed!")
        print("🚀 Ash-Thrash is ready for testing!")
    else:
        print_error(f"{len(issues)} issues found:")
        for issue in issues:
            print(f"  • {issue}")
        sys.exit(1)

def validate_test_data(args):
    """Validate test data structure and phrase counts"""
    print("🧪 Validating Test Data")
    print_header("Test Data Validation")
    
    try:
        validation = validate_test_data()
        category_info = get_category_info()
        
        print(f"Total phrases: {validation['total_phrases']}")
        print(f"Expected: {validation['expected_total']}")
        print_success(f"Correct total: {validation['correct_total']}")
        print(f"Categories with 50 phrases: {validation['categories_with_50']}/7")
        print_success(f"All categories have 50: {validation['all_categories_have_50']}")
        
        print("\nCategory breakdown:")
        for category, count in validation['category_counts'].items():
            info = category_info.get(category, {})
            target = info.get('target_pass_rate', 0)
            print(f"  {category}: {count} phrases (target: {target}%)")
            
        if validation['correct_total'] and validation['all_categories_have_50']:
            print("\n🎉 Test data validation PASSED!")
        else:
            print("\n❌ Test data validation FAILED")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Validation error: {str(e)}")
        sys.exit(1)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def print_test_results(results):
    """Print test results in a nice console format"""
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
    
    # Category breakdown
    if len(results.category_results) > 1:
        print("\n📊 CATEGORY RESULTS:")
        for category, result in results.category_results.items():
            status = "✅" if result.goal_met else "❌"
            print(f"  {status} {category}: {result.pass_rate:.1f}% ({result.passed_tests}/{result.total_tests})")
    
    # Tuning suggestions
    if results.suggestions:
        print("\n🔧 TUNING SUGGESTIONS:")
        for suggestion in results.suggestions:
            print(f"  {suggestion}")

def wait_for_test_completion(api_url: str, test_id: str, max_wait: int = 300):
    """Wait for test completion with progress updates"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{api_url}/api/test/status/{test_id}", timeout=5)
            response.raise_for_status()
            
            status_data = response.json()
            status = status_data['status']
            
            if status == 'completed':
                print_success("Test completed successfully!")
                
                # Get and display results
                results_response = requests.get(f"{api_url}/api/test/results/{test_id}")
                if results_response.status_code == 200:
                    results = results_response.json()
                    print(f"\n📊 Overall Pass Rate: {results['overall_pass_rate']:.1f}%")
                    print(f"🎯 Goal Achievement: {results['goal_achievement_rate']:.1f}%")
                    
                    # Show category results
                    if 'category_results' in results:
                        print("\n📋 Category Results:")
                        for category, result in results['category_results'].items():
                            status_emoji = "✅" if result['goal_met'] else "❌"
                            print(f"  {status_emoji} {category}: {result['pass_rate']:.1f}%")
                
                return
                
            elif status == 'failed':
                error = status_data.get('error', 'Unknown error')
                print_error(f"Test failed: {error}")
                sys.exit(1)
                
            elif status == 'running':
                progress = status_data.get('progress', {})
                current_category = progress.get('current_category', 'running')
                percent = progress.get('percent_complete', 0)
                print(f"⏳ Test running... {current_category} ({percent}%)")
                
            time.sleep(10)  # Wait 10 seconds before checking again
            
        except requests.exceptions.RequestException as e:
            print_warning(f"Error checking status: {str(e)}")
            time.sleep(5)
    
    print("⏰ Test is taking longer than expected. Check status manually:")
    print(f"   {api_url}/api/test/status/{test_id}")

# =============================================================================
# ARGUMENT PARSING
# =============================================================================

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Ash-Thrash v3.0 - Crisis Detection Testing Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py test comprehensive
  python cli.py test quick --sample-size 30
  python cli.py test category definite_high
  python cli.py api start --port 8884
  python cli.py api trigger comprehensive --wait
  python cli.py validate setup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test commands
    test_parser = subparsers.add_parser('test', help='Run testing operations')
    test_subparsers = test_parser.add_subparsers(dest='test_command', help='Test types')
    
    # Comprehensive test
    comp_parser = test_subparsers.add_parser('comprehensive', help='Run comprehensive test (350 phrases)')
    comp_parser.add_argument('--output', choices=['console', 'json', 'file'], default='console',
                            help='Output format')
    comp_parser.add_argument('--save-results', action='store_true', default=True,
                            help='Save results to file')
    
    # Quick test
    quick_parser = test_subparsers.add_parser('quick', help='Run quick validation test')
    quick_parser.add_argument('--sample-size', type=int, default=50,
                             help='Number of phrases to test')
    quick_parser.add_argument('--output', choices=['console', 'json', 'file'], default='console',
                             help='Output format')
    
    # Category test
    cat_parser = test_subparsers.add_parser('category', help='Run category-specific test')
    cat_parser.add_argument('category_name', help='Category name to test')
    cat_parser.add_argument('--output', choices=['console', 'json', 'file'], default='console',
                           help='Output format')
    
    # API commands
    api_parser = subparsers.add_parser('api', help='API server operations')
    api_subparsers = api_parser.add_subparsers(dest='api_command', help='API operations')
    
    # Start API
    start_parser = api_subparsers.add_parser('start', help='Start API server')
    start_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    start_parser.add_argument('--port', type=int, default=8884, help='Port to bind to')
    start_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    # Trigger test via API
    trigger_parser = api_subparsers.add_parser('trigger', help='Trigger test via API')
    trigger_parser.add_argument('test_type', default='comprehensive', nargs='?',
                               help='Test type to trigger')
    trigger_parser.add_argument('--api-url', default='http://localhost:8884',
                               help='API server URL')
    trigger_parser.add_argument('--wait', action='store_true', help='Wait for completion')
    
    # API health check
    health_parser = api_subparsers.add_parser('health', help='Check API health')
    health_parser.add_argument('--api-url', default='http://localhost:8884',
                              help='API server URL')
    
    # Validation commands
    validate_parser = subparsers.add_parser('validate', help='Validation operations')
    validate_subparsers = validate_parser.add_subparsers(dest='validate_command', help='Validation types')
    
    validate_subparsers.add_parser('setup', help='Validate setup and configuration')
    validate_subparsers.add_parser('data', help='Validate test data')
    
    return parser

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'test':
            if args.test_command == 'comprehensive':
                asyncio.run(run_comprehensive_test(args))
            elif args.test_command == 'quick':
                asyncio.run(run_quick_test(args))
            elif args.test_command == 'category':
                asyncio.run(run_category_test(args))
            else:
                print_error("Invalid test command")
                parser.print_help()
                
        elif args.command == 'api':
            if args.api_command == 'start':
                start_api_server(args)
            elif args.api_command == 'trigger':
                trigger_api_test(args)
            elif args.api_command == 'health':
                check_api_health(args)
            else:
                print_error("Invalid API command")
                parser.print_help()
                
        elif args.command == 'validate':
            if args.validate_command == 'setup':
                validate_setup(args)
            elif args.validate_command == 'data':
                validate_test_data(args)
            else:
                print_error("Invalid validate command")
                parser.print_help()
        else:
            print_error("Invalid command")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()