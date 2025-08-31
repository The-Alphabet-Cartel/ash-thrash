# ash-thrash/analyze_results.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Results Analysis and Reporting Script for Ash-Thrash Service
---
FILE VERSION: v3.1-1a-1
LAST MODIFIED: 2025-08-30
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime
import colorlog

# Manager imports
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.results_manager import create_results_manager

def setup_logging(unified_config_manager):
    """Setup colorlog logging for analysis script"""
    try:
        log_level = unified_config_manager.get_config_section('logging_settings', 'global_settings.log_level', 'INFO')
        
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s%(reset)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        logging.info("Analysis logging configured successfully")
        
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to setup logging: {e}")

def display_latest_results(results_manager):
    """Display the most recent test results"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Loading latest test results...")
        
        latest_results = results_manager.get_latest_results()
        
        if not latest_results:
            print("❌ No test results found")
            return False
        
        # Extract data
        run_summary = latest_results.get('run_summary', {})
        category_summaries = latest_results.get('category_summaries', [])
        performance_analysis = latest_results.get('performance_analysis', {})
        recommendations = latest_results.get('recommendations', [])
        
        # Display run summary
        print("=" * 70)
        print("🧪 ASH-THRASH LATEST TEST RESULTS")
        print("=" * 70)
        print(f"Run ID: {run_summary.get('run_id', 'unknown')}")
        
        if run_summary.get('timestamp'):
            timestamp = datetime.fromtimestamp(run_summary['timestamp'])
            print(f"Executed: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"Server Version: {run_summary.get('server_version', 'unknown')}")
        print(f"Execution Time: {run_summary.get('execution_time_ms', 0)/1000:.1f}s")
        print()
        
        # Overall performance
        overall_pass_rate = run_summary.get('overall_pass_rate', 0)
        safety_score = run_summary.get('weighted_safety_score', 0)
        
        print("📊 OVERALL PERFORMANCE")
        print("-" * 30)
        print(f"Overall Pass Rate: {overall_pass_rate:.1f}%")
        print(f"Safety Score: {safety_score:.2f}")
        print(f"Total Phrases: {run_summary.get('total_phrases', 0)}")
        print(f"Passed: {run_summary.get('total_passed', 0)}")
        print(f"Failed: {run_summary.get('total_failed', 0)}")
        print(f"Errors: {run_summary.get('total_errors', 0)}")
        
        if run_summary.get('early_termination'):
            print(f"⚠️  Early Termination: {run_summary.get('termination_reason', 'unknown')}")
        print()
        
        # Category performance
        print("📋 CATEGORY PERFORMANCE")
        print("-" * 50)
        print(f"{'Category':<20} {'Pass Rate':<10} {'Target':<8} {'Status':<8}")
        print("-" * 50)
        
        for category in category_summaries:
            name = category.get('category_name', 'unknown')[:18]
            pass_rate = category.get('pass_rate', 0)
            target = category.get('target_pass_rate', 0)
            met_target = category.get('met_target', False)
            is_critical = category.get('is_critical', False)
            
            status = "✅ PASS" if met_target else "❌ FAIL"
            if is_critical and not met_target:
                status = "🚨 CRIT"
            
            print(f"{name:<20} {pass_rate:>6.1f}%    {target:>4}%    {status}")
        print()
        
        # Performance analysis
        if performance_analysis:
            print("🔍 PERFORMANCE ANALYSIS")
            print("-" * 30)
            overall_status = performance_analysis.get('overall_status', 'unknown')
            safety_assessment = performance_analysis.get('safety_assessment', 'unknown')
            
            print(f"Overall Status: {overall_status.upper()}")
            print(f"Safety Assessment: {safety_assessment.upper()}")
            
            # Critical failures
            critical_failures = performance_analysis.get('critical_failures', [])
            if critical_failures:
                print("\n🚨 CRITICAL FAILURES:")
                for failure in critical_failures:
                    cat = failure.get('category', 'unknown')
                    rate = failure.get('pass_rate', 0)
                    target = failure.get('target', 0)
                    false_negs = failure.get('false_negatives', 0)
                    print(f"  - {cat}: {rate:.1f}% (need {target}%), {false_negs} false negatives")
            
            # Performance issues
            performance_issues = performance_analysis.get('performance_issues', [])
            if performance_issues:
                print("\n⚠️  PERFORMANCE ISSUES:")
                for issue in performance_issues:
                    cat = issue.get('category', 'unknown')
                    issue_type = issue.get('issue_type', 'unknown')
                    if issue_type == 'significantly_below_target':
                        rate = issue.get('pass_rate', 0)
                        target = issue.get('target', 0)
                        print(f"  - {cat}: {rate:.1f}% (target {target}%)")
                    elif issue_type == 'false_negatives_detected':
                        false_negs = issue.get('false_negatives', 0)
                        print(f"  - {cat}: {false_negs} false negatives")
            
            # Strengths
            strengths = performance_analysis.get('strengths', [])
            if strengths:
                print("\n✨ STRENGTHS:")
                for strength in strengths:
                    cat = strength.get('category', 'unknown')
                    rate = strength.get('pass_rate', 0)
                    target = strength.get('target', 0)
                    print(f"  - {cat}: {rate:.1f}% (exceeds {target}% target)")
            
            print()
        
        # Recommendations
        if recommendations:
            print("🔧 TUNING RECOMMENDATIONS")
            print("-" * 40)
            
            high_priority = [r for r in recommendations if r.get('priority') == 'HIGH']
            medium_priority = [r for r in recommendations if r.get('priority') == 'MEDIUM']
            low_priority = [r for r in recommendations if r.get('priority') == 'LOW']
            
            for priority_group, title, emoji in [
                (high_priority, "HIGH PRIORITY", "🚨"),
                (medium_priority, "MEDIUM PRIORITY", "⚠️"),
                (low_priority, "LOW PRIORITY", "💡")
            ]:
                if priority_group:
                    print(f"\n{emoji} {title}:")
                    for rec in priority_group:
                        category = rec.get('category', 'unknown')
                        issue = rec.get('issue', 'unknown issue')
                        recommendation = rec.get('recommendation', 'no recommendation')
                        confidence = rec.get('confidence', 'unknown')
                        
                        print(f"  Category: {category}")
                        print(f"  Issue: {issue}")
                        print(f"  Recommendation: {recommendation}")
                        print(f"  Confidence: {confidence}")
                        print()
        
        print("=" * 70)
        return True
        
    except Exception as e:
        logger.error(f"Error displaying latest results: {e}")
        return False

def display_historical_trends(results_manager, days: int = 7):
    """Display historical performance trends"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Loading historical trends (last {days} days)...")
        
        historical_data = results_manager.get_historical_trends(days)
        test_runs = historical_data.get('test_runs', [])
        trends = historical_data.get('trends', {})
        
        if not test_runs:
            print("❌ No historical data found")
            return False
        
        print("=" * 70)
        print(f"📈 HISTORICAL PERFORMANCE TRENDS (Last {days} days)")
        print("=" * 70)
        print(f"Total Test Runs: {len(test_runs)}")
        
        if len(test_runs) >= 2:
            print("\nTrend Analysis:")
            pass_rate_trend = trends.get('overall_pass_rate_trend', 0)
            safety_trend = trends.get('safety_score_trend', 0)
            time_trend = trends.get('execution_time_trend', 0)
            
            # Pass rate trend
            if abs(pass_rate_trend) < 1.0:
                pass_icon = "➡️"
                pass_desc = "stable"
            elif pass_rate_trend > 0:
                pass_icon = "⬆️"
                pass_desc = f"improved by {pass_rate_trend:+.1f}%"
            else:
                pass_icon = "⬇️"
                pass_desc = f"declined by {pass_rate_trend:+.1f}%"
            
            print(f"  Pass Rate: {pass_icon} {pass_desc}")
            
            # Safety score trend
            if abs(safety_trend) < 0.1:
                safety_icon = "➡️"
                safety_desc = "stable"
            elif safety_trend < 0:  # Lower safety score is better
                safety_icon = "⬆️"
                safety_desc = f"improved by {-safety_trend:.2f}"
            else:
                safety_icon = "⬇️"
                safety_desc = f"worsened by {safety_trend:+.2f}"
            
            print(f"  Safety Score: {safety_icon} {safety_desc}")
            
            # Execution time trend
            if abs(time_trend) < 1000:  # Less than 1 second change
                time_icon = "➡️"
                time_desc = "stable"
            elif time_trend < 0:
                time_icon = "⚡"
                time_desc = f"faster by {-time_trend/1000:.1f}s"
            else:
                time_icon = "🐌"
                time_desc = f"slower by {time_trend/1000:.1f}s"
            
            print(f"  Execution Time: {time_icon} {time_desc}")
        
        # Recent test runs summary
        print("\nRecent Test Runs:")
        print(f"{'Date/Time':<20} {'Pass Rate':<10} {'Safety Score':<12} {'Status'}")
        print("-" * 55)
        
        for run in test_runs[-10:]:  # Show last 10 runs
            timestamp = datetime.fromtimestamp(run['timestamp'])
            date_str = timestamp.strftime('%m-%d %H:%M')
            pass_rate = run.get('overall_pass_rate', 0)
            safety_score = run.get('weighted_safety_score', 0)
            
            if run.get('early_termination'):
                status = "❌ HALT"
            elif pass_rate >= 85.0:
                status = "✅ PASS"
            else:
                status = "⚠️ FAIL"
            
            print(f"{date_str:<20} {pass_rate:>6.1f}%    {safety_score:>8.2f}    {status}")
        
        print("=" * 70)
        return True
        
    except Exception as e:
        logger.error(f"Error displaying historical trends: {e}")
        return False

def cleanup_old_results(results_manager, days: int):
    """Clean up old test results"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Cleaning up test results older than {days} days...")
        
        removed_count = results_manager.cleanup_old_results(days)
        
        if removed_count > 0:
            print(f"✅ Cleaned up {removed_count} old test result directories")
            print(f"   (moved to backup directory)")
        else:
            print("ℹ️  No old results found to clean up")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return False

def main():
    """Main analysis script entry point"""
    parser = argparse.ArgumentParser(
        description='Ash-Thrash Results Analysis and Reporting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_results.py                    # Show latest results
  python analyze_results.py --trends           # Show historical trends
  python analyze_results.py --trends --days 14 # Show 14-day trends
  python analyze_results.py --cleanup --keep 30 # Cleanup results older than 30 days
        """
    )
    
    parser.add_argument('--trends', action='store_true',
                       help='Display historical performance trends')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days for trend analysis (default: 7)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up old test results')
    parser.add_argument('--keep', type=int, default=30,
                       help='Days of results to keep during cleanup (default: 30)')
    
    args = parser.parse_args()
    
    try:
        print("Starting Ash-Thrash Results Analysis")
        print("Serving The Alphabet Cartel LGBTQIA+ Community")
        print("Repository: https://github.com/the-alphabet-cartel/ash-thrash")
        print("Discord: https://discord.gg/alphabetcartel")
        print("Website: https://alphabetcartel.org")
        print("")
        
        # Initialize managers
        unified_config = create_unified_config_manager()
        setup_logging(unified_config)
        
        logger = logging.getLogger(__name__)
        logger.info("=" * 50)
        logger.info("  ASH-THRASH RESULTS ANALYSIS")
        logger.info("=" * 50)
        
        logging_config = create_logging_config_manager(unified_config)
        results_manager = create_results_manager(unified_config)
        
        logger.info("All managers initialized successfully")
        
        # Execute requested operations
        success = True
        
        if args.cleanup:
            success = cleanup_old_results(results_manager, args.keep) and success
            print()  # Add spacing
        
        if args.trends:
            success = display_historical_trends(results_manager, args.days) and success
        else:
            # Default: show latest results
            success = display_latest_results(results_manager) and success
        
        if success:
            logger.info("Analysis completed successfully")
            sys.exit(0)
        else:
            logger.error("Analysis completed with errors")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()