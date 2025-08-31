# ash-thrash/analyze.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Standalone Results Analysis Script for Ash-Thrash Service
---
FILE VERSION: v3.1-2a-1
LAST MODIFIED: 2025-08-31
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

# Manager imports following Clean Architecture
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.results_manager import create_results_manager
from managers.analyze_results import create_analyze_results_manager

def setup_logging(unified_config_manager):
    """Setup colorlog logging for standalone analysis script"""
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

def display_latest_results(analyze_manager):
    """Display the most recent test results using the manager"""
    logger = logging.getLogger(__name__)
    
    try:
        success = analyze_manager.display_latest_results()
        return success
        
    except Exception as e:
        logger.error(f"Error displaying latest results: {e}")
        return False

def display_historical_trends(results_manager, days: int = 7):
    """Display historical performance trends (console only)"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Loading historical trends (last {days} days)...")
        
        historical_data = results_manager.get_historical_trends(days)
        test_runs = historical_data.get('test_runs', [])
        trends = historical_data.get('trends', {})
        
        if not test_runs:
            logger.error("No historical data found")
            return False
        
        logger.info("=" * 70)
        logger.info(f"HISTORICAL PERFORMANCE TRENDS (Last {days} days)")
        logger.info("=" * 70)
        logger.info(f"Total Test Runs: {len(test_runs)}")
        
        if len(test_runs) >= 2:
            logger.info("Trend Analysis:")
            pass_rate_trend = trends.get('overall_pass_rate_trend', 0)
            safety_trend = trends.get('safety_score_trend', 0)
            time_trend = trends.get('execution_time_trend', 0)
            
            # Pass rate trend
            if abs(pass_rate_trend) < 1.0:
                pass_desc = "stable"
            elif pass_rate_trend > 0:
                pass_desc = f"improved by {pass_rate_trend:+.1f}%"
            else:
                pass_desc = f"declined by {pass_rate_trend:+.1f}%"
            
            logger.info(f"  Pass Rate: {pass_desc}")
            
            # Safety score trend
            if abs(safety_trend) < 0.1:
                safety_desc = "stable"
            elif safety_trend < 0:  # Lower safety score is better
                safety_desc = f"improved by {-safety_trend:.2f}"
            else:
                safety_desc = f"worsened by {safety_trend:+.2f}"
            
            logger.info(f"  Safety Score: {safety_desc}")
            
            # Execution time trend
            if abs(time_trend) < 1000:  # Less than 1 second change
                time_desc = "stable"
            elif time_trend < 0:
                time_desc = f"faster by {-time_trend/1000:.1f}s"
            else:
                time_desc = f"slower by {time_trend/1000:.1f}s"
            
            logger.info(f"  Execution Time: {time_desc}")
        
        # Recent test runs summary
        logger.info("Recent Test Runs:")
        logger.info(f"{'Date/Time':<20} {'Pass Rate':<10} {'Safety Score':<12} {'Status'}")
        logger.info("-" * 55)
        
        for run in test_runs[-10:]:  # Show last 10 runs
            timestamp = datetime.fromtimestamp(run['timestamp'])
            date_str = timestamp.strftime('%m-%d %H:%M')
            pass_rate = run.get('overall_pass_rate', 0)
            safety_score = run.get('weighted_safety_score', 0)
            
            if run.get('early_termination'):
                status = "HALT"
                log_level = logger.error
            elif pass_rate >= 85.0:
                status = "PASS"
                log_level = logger.info
            else:
                status = "FAIL"
                log_level = logger.warning
            
            log_level(f"{date_str:<20} {pass_rate:>6.1f}%    {safety_score:>8.2f}    {status}")
        
        logger.info("=" * 70)
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
            logger.info(f"Cleaned up {removed_count} old test result directories (moved to backup)")
        else:
            logger.info("No old results found to clean up")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return False

def generate_reports(analyze_manager):
    """Generate all markdown reports"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Generating all markdown reports...")
        success = analyze_manager.generate_all_reports()
        
        if success:
            logger.info("All markdown reports generated successfully")
        else:
            logger.warning("Some markdown reports failed to generate")
        
        return success
        
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        return False

def main():
    """Main analysis script entry point"""
    parser = argparse.ArgumentParser(
        description='Ash-Thrash Results Analysis and Reporting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_results.py                         # Show latest results
  python analyze_results.py --trends                # Show historical trends  
  python analyze_results.py --trends --days 14      # Show 14-day trends
  python analyze_results.py --cleanup --keep 30     # Cleanup results older than 30 days
  python analyze_results.py --reports               # Generate markdown reports
  python analyze_results.py --reports --display     # Generate reports AND display results
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
    parser.add_argument('--reports', action='store_true',
                       help='Generate markdown reports')
    parser.add_argument('--display', action='store_true',
                       help='Display latest results (used with --reports)')
    
    args = parser.parse_args()
    
    try:
        logger = logging.getLogger(__name__)
        logger.info("Starting Ash-Thrash Results Analysis")
        logger.info("Serving The Alphabet Cartel LGBTQIA+ Community")
        logger.info("Repository: https://github.com/the-alphabet-cartel/ash-thrash")
        logger.info("Discord: https://discord.gg/alphabetcartel")
        logger.info("Website: https://alphabetcartel.org")
        logger.info("")
        
        # Initialize managers following Clean Architecture
        unified_config = create_unified_config_manager()
        setup_logging(unified_config)
        
        logger.info("=" * 50)
        logger.info("  ASH-THRASH RESULTS ANALYSIS")
        logger.info("=" * 50)
        
        logging_config = create_logging_config_manager(unified_config)
        results_manager = create_results_manager(unified_config)
        analyze_manager = create_analyze_results_manager(unified_config, results_manager, logging_config)
        
        logger.info("All managers initialized successfully")
        
        # Execute requested operations
        success = True
        
        if args.cleanup:
            success = cleanup_old_results(results_manager, args.keep) and success
        
        if args.reports:
            success = generate_reports(analyze_manager) and success
            if args.display:  # Generate reports AND display
                success = display_latest_results(analyze_manager) and success
        elif args.trends:
            success = display_historical_trends(results_manager, args.days) and success
        else:
            # Default: show latest results
            success = display_latest_results(analyze_manager) and success
        
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
    # Setup basic logging first
    logging.basicConfig(level=logging.INFO)
    main()