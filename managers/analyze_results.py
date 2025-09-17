# ash-thrash/managers/analyze_results.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Results Analysis and Markdown Report Generation Manager for Ash-Thrash Service
---
FILE VERSION: v3.1-2a-2
LAST MODIFIED: 2025-09-17
PHASE: 2a Step 2 - Enhanced Failed Phrase Details in Reports
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AnalyzeResultsManager:
    """
    Results Analysis and Markdown Report Generation Manager
    
    Handles analysis display, markdown report generation, and integration
    with the main test workflow for persistent reporting following Clean Architecture.
    
    Enhanced with detailed failed phrase analysis for improved debugging and tuning.
    """
    
    # ========================================================================
    # INITIALIZE
    # ========================================================================
    def __init__(self, unified_config_manager, results_manager, logging_config_manager):
        """
        Initialize AnalyzeResults Manager
        
        Args:
            unified_config_manager: UnifiedConfigManager instance for configuration
            results_manager: ResultsManager instance for data access
            logging_config_manager: LoggingConfigManager instance for proper logging
        """
        self.unified_config = unified_config_manager
        self.results_manager = results_manager
        self.logging_config = logging_config_manager
        
        try:
            # Load reporting configuration
            self.storage_config = self.unified_config.get_config_section('test_settings', 'storage', {})
            
            self.reports_dir = Path(self.storage_config.get('reports_directory', './reports'))
            
            # Create reports directory if it doesn't exist
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"AnalyzeResultsManager initialized: reports_dir={self.reports_dir}")
            
        except Exception as e:
            logger.error(f"Error initializing AnalyzeResultsManager: {e}")
            raise
    # ========================================================================
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    def display_latest_results(self) -> bool:
        """Display the most recent test results using proper logging"""
        try:
            logger.info("Loading latest test results...")
            
            latest_results = self.results_manager.get_latest_results()
            
            if not latest_results:
                logger.error("No test results found")
                return False
            
            # Extract data
            run_summary = latest_results.get('run_summary', {})
            category_summaries = latest_results.get('category_summaries', [])
            performance_analysis = latest_results.get('performance_analysis', {})
            recommendations = latest_results.get('recommendations', [])
            
            # Log run summary using proper logging
            logger.info("=" * 70)
            logger.info("ASH-THRASH LATEST TEST RESULTS")
            logger.info("=" * 70)
            logger.info(f"Run ID: {run_summary.get('run_id', 'unknown')}")
            
            if run_summary.get('timestamp'):
                timestamp = datetime.fromtimestamp(run_summary['timestamp'])
                logger.info(f"Executed: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            logger.info(f"Server Version: {run_summary.get('server_version', 'unknown')}")
            logger.info(f"Execution Time: {run_summary.get('execution_time_ms', 0)/1000:.1f}s")
            
            # Overall performance
            logger.info("")
            logger.info("OVERALL PERFORMANCE:")
            logger.info(f"   Pass Rate: {run_summary.get('overall_pass_rate', 0):.1f}%")
            logger.info(f"   Safety Score: {run_summary.get('weighted_safety_score', 0):.2f}")
            logger.info(f"   Total Phrases: {run_summary.get('total_phrases', 0)}")
            logger.info(f"   Passed: {run_summary.get('total_passed', 0)}")
            logger.info(f"   Failed: {run_summary.get('total_failed', 0)}")
            logger.info(f"   Errors: {run_summary.get('total_errors', 0)}")
            
            if run_summary.get('early_termination'):
                logger.warning(f"EARLY TERMINATION: {run_summary.get('termination_reason', 'unknown')}")
            
            # Category breakdown
            logger.info("")
            logger.info("CATEGORY BREAKDOWN:")
            if category_summaries:
                for category in category_summaries:
                    status = "PASS" if category.get('met_target', False) else "FAIL"
                    critical = " [CRITICAL]" if category.get('is_critical', False) else ""
                    
                    logger.info(f"   {category.get('category_name', 'unknown')}: {category.get('pass_rate', 0):.1f}% "
                               f"(target: {category.get('target_pass_rate', 0)}%) - {status}{critical}")
                    
                    if category.get('false_negatives', 0) > 0:
                        logger.info(f"      False Negatives: {category.get('false_negatives', 0)}")
                    if category.get('false_positives', 0) > 0:
                        logger.info(f"      False Positives: {category.get('false_positives', 0)}")
            else:
                logger.warning("   No category data available")
            
            # Display recommendations by priority
            logger.info("")
            logger.info("RECOMMENDATIONS BY PRIORITY:")
            
            if recommendations:
                # Group by priority (handle both string and int formats)
                def get_priority_level(rec):
                    priority = rec.get('priority', 'UNKNOWN')
                    if isinstance(priority, str):
                        priority_upper = priority.upper()
                        if priority_upper in ['HIGH', 'CRITICAL']:
                            return 1
                        elif priority_upper == 'MEDIUM':
                            return 2
                        elif priority_upper == 'LOW':
                            return 3
                        else:
                            return 99
                    elif isinstance(priority, int):
                        return priority
                    else:
                        return 99
                
                critical_recs = [r for r in recommendations if get_priority_level(r) == 1]
                high_recs = [r for r in recommendations if get_priority_level(r) == 2]
                medium_recs = [r for r in recommendations if get_priority_level(r) == 3]
                low_recs = [r for r in recommendations if get_priority_level(r) > 3]
                
                for title, priority_group, log_level in [
                    ("CRITICAL PRIORITY", critical_recs, logger.error),
                    ("HIGH PRIORITY", high_recs, logger.warning), 
                    ("MEDIUM PRIORITY", medium_recs, logger.info),
                    ("LOW PRIORITY", low_recs, logger.info)
                ]:
                    if priority_group:
                        log_level(f"{title} RECOMMENDATIONS:")
                        for rec in priority_group:
                            category = rec.get('category', 'unknown')
                            issue = rec.get('issue', 'unknown issue')
                            recommendation = rec.get('recommendation', 'no recommendation')
                            confidence = rec.get('confidence', 'unknown')
                            
                            log_level(f"  Category: {category}")
                            log_level(f"  Issue: {issue}")
                            log_level(f"  Recommendation: {recommendation}")
                            log_level(f"  Confidence: {confidence}")
            
            logger.info("=" * 70)
            return True
            
        except Exception as e:
            logger.error(f"Error displaying latest results: {e}")
            return False
    # ========================================================================
    
    # ========================================================================
    # GENERATE MARKDOWN FILES
    # ========================================================================
    def generate_latest_run_summary_markdown(self) -> bool:
        """Generate markdown report for latest test run"""
        try:
            logger.info("Generating latest run summary markdown report...")
            
            latest_results = self.results_manager.get_latest_results()
            if not latest_results:
                logger.error("No test results found for markdown generation")
                return False
            
            # Extract data
            run_summary = latest_results.get('run_summary', {})
            category_summaries = latest_results.get('category_summaries', [])
            performance_analysis = latest_results.get('performance_analysis', {})
            recommendations = latest_results.get('recommendations', [])
            
            # NEW: Get the raw results to extract failed phrase details
            raw_results = self._get_latest_raw_results()
            
            # Generate markdown content
            markdown_content = self._build_latest_run_markdown(
                run_summary, category_summaries, performance_analysis, recommendations, raw_results
            )
            
            # Write to file
            report_path = self.reports_dir / 'latest_run_summary.md'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Latest run summary markdown generated: {report_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating latest run summary markdown: {e}")
            return False
    
    def generate_threshold_recommendations_markdown(self) -> bool:
        """Generate markdown report for threshold tuning recommendations"""
        try:
            logger.info("Generating threshold recommendations markdown report...")
            
            latest_results = self.results_manager.get_latest_results()
            if not latest_results:
                logger.error("No test results found for threshold recommendations")
                return False
            
            recommendations = latest_results.get('recommendations', [])
            category_summaries = latest_results.get('category_summaries', [])
            
            # Generate threshold-specific markdown
            markdown_content = self._build_threshold_recommendations_markdown(
                recommendations, category_summaries
            )
            
            # Write to file
            report_path = self.reports_dir / 'threshold_recommendations.md'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Threshold recommendations markdown generated: {report_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating threshold recommendations markdown: {e}")
            return False
    
    def generate_historical_performance_markdown(self, days: int = 30) -> bool:
        """Generate markdown report for historical performance trends"""
        try:
            logger.info(f"Generating historical performance markdown report (last {days} days)...")
            
            historical_data = self.results_manager.get_historical_trends(days)
            test_runs = historical_data.get('test_runs', [])
            trends = historical_data.get('trends', {})
            
            if not test_runs:
                logger.warning("No historical data found for markdown generation")
                return False
            
            # NEW: Get failed phrase details for historical analysis
            historical_failed_phrases = self._extract_historical_failed_phrases(test_runs)
            
            # Generate historical markdown
            markdown_content = self._build_historical_performance_markdown(
                test_runs, trends, days, historical_failed_phrases
            )
            
            # Write to file
            report_path = self.reports_dir / 'historical_performance.md'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Historical performance markdown generated: {report_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating historical performance markdown: {e}")
            return False
    # ========================================================================
    
    # ========================================================================
    # GENERATE REPORTS
    # ========================================================================
    def generate_all_reports(self) -> bool:
        """Generate all markdown reports"""
        try:
            logger.info("Generating all markdown reports...")
            
            success = True
            success = self.generate_latest_run_summary_markdown() and success
            success = self.generate_threshold_recommendations_markdown() and success
            success = self.generate_historical_performance_markdown() and success
            
            if success:
                logger.info("All markdown reports generated successfully")
            else:
                logger.warning("Some markdown reports failed to generate")
            
            return success
            
        except Exception as e:
            logger.error(f"Error generating all reports: {e}")
            return False
    # ========================================================================
    
    # ========================================================================
    # ENHANCED MARKDOWN GENERATION WITH FAILED PHRASE DETAILS
    # ========================================================================
    def _get_latest_raw_results(self) -> Optional[Dict[str, Any]]:
        """Get the latest raw results with full phrase details"""
        try:
            test_runs_dir = self.results_manager.results_dir / 'test_runs'
            
            if not test_runs_dir.exists():
                return None
            
            # Find most recent test run directory
            run_dirs = [d for d in test_runs_dir.iterdir() if d.is_dir()]
            if not run_dirs:
                return None
            
            latest_dir = max(run_dirs, key=lambda d: d.stat().st_mtime)
            raw_results_file = latest_dir / 'raw_results.json'
            
            if raw_results_file.exists():
                with open(raw_results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest raw results: {e}")
            return None
    
    def _extract_historical_failed_phrases(self, test_runs: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract failed phrases from historical test runs for trend analysis"""
        try:
            historical_failures = {}
            
            for run in test_runs[-5:]:  # Last 5 runs
                run_id = run.get('run_id', 'unknown')
                category_performance = run.get('category_performance', {})
                
                for category, performance in category_performance.items():
                    if performance.get('false_negatives', 0) > 0 or performance.get('false_positives', 0) > 0:
                        if category not in historical_failures:
                            historical_failures[category] = []
                        
                        historical_failures[category].append({
                            'run_id': run_id,
                            'timestamp': run.get('timestamp', 0),
                            'false_negatives': performance.get('false_negatives', 0),
                            'false_positives': performance.get('false_positives', 0),
                            'pass_rate': performance.get('pass_rate', 0)
                        })
            
            return historical_failures
            
        except Exception as e:
            logger.error(f"Error extracting historical failed phrases: {e}")
            return {}
    # ========================================================================
    
    # ========================================================================
    # BUILD MARKDOWN
    # ========================================================================
    def _build_latest_run_markdown(self, run_summary: Dict, category_summaries: List, performance_analysis: Dict, recommendations: List, raw_results: Optional[Dict] = None) -> str:
        """Build markdown content for latest run summary with enhanced failed phrase details"""
        
        timestamp_str = "Unknown"
        if run_summary.get('timestamp'):
            timestamp = datetime.fromtimestamp(run_summary['timestamp'])
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""# Latest Test Run Summary

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)  
**Repository**: [ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

---

## 🧪 Test Run Information

- **Run ID**: `{run_summary.get('run_id', 'unknown')}`
- **Executed**: {timestamp_str}
- **Server Version**: {run_summary.get('server_version', 'unknown')}
- **Execution Time**: {run_summary.get('execution_time_ms', 0)/1000:.1f}s

## 📊 Overall Performance

| Metric | Value |
|--------|-------|
| **Overall Pass Rate** | **{run_summary.get('overall_pass_rate', 0):.1f}%** |
| **Safety Score** | {run_summary.get('weighted_safety_score', 0):.2f} |
| **Total Phrases** | {run_summary.get('total_phrases', 0)} |
| **Passed** | {run_summary.get('total_passed', 0)} |
| **Failed** | {run_summary.get('total_failed', 0)} |
| **Errors** | {run_summary.get('total_errors', 0)} |

"""
        
        if run_summary.get('early_termination'):
            content += f"""
> ⚠️ **Early Termination**: {run_summary.get('termination_reason', 'unknown')}

"""
        
        # Category breakdown with status indicators
        content += """## 📋 Category Performance

| Category | Pass Rate | Target | Status | False Neg | False Pos |
|----------|-----------|--------|---------|-----------|-----------|
"""
        
        if category_summaries:
            for category in category_summaries:
                status_icon = "✅" if category.get('met_target', False) else "❌"
                critical_marker = "🚨" if category.get('is_critical', False) else ""
                
                content += f"| **{category.get('category_name', 'unknown')}** {critical_marker} | "
                content += f"{category.get('pass_rate', 0):.1f}% | "
                content += f"{category.get('target_pass_rate', 0)}% | "
                content += f"{status_icon} | "
                content += f"{category.get('false_negatives', 0)} | "
                content += f"{category.get('false_positives', 0)} |\n"
        
        # NEW: Detailed Failed Phrase Analysis
        if raw_results and raw_results.get('category_results'):
            content += self._build_failed_phrase_analysis_section(raw_results['category_results'])
        
        # Performance insights
        if performance_analysis:
            content += f"""
## 🎯 Performance Insights

"""
            insights = performance_analysis.get('insights', [])
            if insights:
                for insight in insights[:5]:  # Top 5 insights
                    content += f"- {insight}\n"
            
            critical_issues = performance_analysis.get('critical_issues', [])
            if critical_issues:
                content += f"""
### 🚨 Critical Issues

"""
                for issue in critical_issues:
                    content += f"- **{issue.get('category', 'Unknown')}**: {issue.get('description', 'No description')}\n"
        
        # Recommendations
        if recommendations:
            content += f"""
## 🔧 Tuning Recommendations

"""
            # Group by priority
            critical_recs = [r for r in recommendations if r.get('priority', 99) == 1]
            high_recs = [r for r in recommendations if r.get('priority', 99) == 2]
            medium_recs = [r for r in recommendations if r.get('priority', 99) == 3]
            
            if critical_recs:
                content += f"""
### 🚨 Critical Priority

"""
                for rec in critical_recs:
                    content += f"- **{rec.get('category', 'Unknown')}**: {rec.get('recommendation', 'No recommendation')} (Confidence: {rec.get('confidence', 'unknown')})\n"
            
            if high_recs:
                content += f"""
### ⚠️ High Priority

"""
                for rec in high_recs:
                    content += f"- **{rec.get('category', 'Unknown')}**: {rec.get('recommendation', 'No recommendation')} (Confidence: {rec.get('confidence', 'unknown')})\n"
            
            if medium_recs:
                content += f"""
### 📋 Medium Priority

"""
                for rec in medium_recs:
                    content += f"- **{rec.get('category', 'Unknown')}**: {rec.get('recommendation', 'No recommendation')} (Confidence: {rec.get('confidence', 'unknown')})\n"
        
        # Footer
        content += f"""
---

**Generated by**: Ash-Thrash v3.1-2a-2  
**For**: The Alphabet Cartel LGBTQIA+ Community Mental Health Support System  
**Next Steps**: Review failed phrases and apply threshold adjustments as recommended
"""
        
        return content
    
    def _build_failed_phrase_analysis_section(self, category_results: List[Dict]) -> str:
        """Build detailed failed phrase analysis section for markdown"""
        content = """
## 🔍 Detailed Failed Phrase Analysis

This section shows exactly which phrases failed and how they were misclassified to help with debugging and threshold tuning.

"""
        
        total_failed_phrases = 0
        
        for category_data in category_results:
            category_name = category_data.get('category_name', 'unknown')
            phrase_results = category_data.get('phrase_results', [])
            
            # Filter to only failed phrases
            failed_phrases = [
                phrase for phrase in phrase_results
                if phrase.get('is_false_negative') or phrase.get('is_false_positive')
            ]
            
            if not failed_phrases:
                continue
            
            total_failed_phrases += len(failed_phrases)
            
            # Category header
            is_critical = category_data.get('is_critical', False)
            critical_marker = "🚨 " if is_critical else ""
            
            content += f"""
### {critical_marker}Category: {category_name}

**Failed Phrases**: {len(failed_phrases)} out of {len(phrase_results)}

| # | Phrase | Expected | Actual | Error Type | Direction |
|---|--------|----------|---------|-------------|-----------|
"""
            
            # Sort by severity: false negatives first (more dangerous)
            failed_phrases.sort(key=lambda p: (not p.get('is_false_negative', False), p.get('failure_severity', 0)))
            
            for i, phrase in enumerate(failed_phrases[:10], 1):  # Show max 10 per category
                expected = phrase.get('expected_priorities', ['unknown'])[0]
                actual = phrase.get('actual_priority', 'unknown')
                
                # Determine error type and direction
                is_false_neg = phrase.get('is_false_negative', False)
                is_false_pos = phrase.get('is_false_positive', False)
                
                if is_false_neg:
                    error_type = "❌ False Negative"
                    direction = "Too Low (Dangerous)"
                elif is_false_pos:
                    error_type = "⚠️ False Positive"
                    direction = "Too High (Over-sensitive)"
                else:
                    error_type = "❓ Unknown"
                    direction = "Unknown"
                
                # Truncate long phrases for readability
                phrase_text = phrase.get('message', 'No message')
                if len(phrase_text) > 60:
                    phrase_text = phrase_text[:57] + "..."
                
                content += f"| {i} | {phrase_text} | **{expected}** | **{actual}** | {error_type} | {direction} |\n"
            
            if len(failed_phrases) > 10:
                content += f"\n*... and {len(failed_phrases) - 10} more failed phrases in this category*\n"
        
        if total_failed_phrases == 0:
            content += """
🎉 **No failed phrases found!** All test phrases were classified correctly.

"""
        else:
            content += f"""
### 📈 Failure Analysis Summary

- **Total Failed Phrases**: {total_failed_phrases}
- **False Negatives**: More dangerous - classified as less severe than expected
- **False Positives**: Over-sensitive - classified as more severe than expected

**Key Insights**:
- False negatives in crisis categories are weighted heavily due to safety implications
- Review threshold settings to reduce false negatives while maintaining acceptable false positive rates
- Pay special attention to critical categories (marked with 🚨)

"""
        
        return content
    
    def _build_historical_performance_markdown(self, test_runs: List, trends: Dict, days: int, historical_failed_phrases: Dict[str, List[Dict]]) -> str:
        """Build markdown content for historical performance with failed phrase trends"""
        
        content = f"""# Historical Performance Analysis

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Period**: Last {days} days  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)  
**Repository**: [ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

---

## 📈 Performance Trends Summary

**Total Test Runs**: {len(test_runs)}
"""
        
        if len(test_runs) >= 2:
            pass_rate_trend = trends.get('overall_pass_rate_trend', 0)
            safety_trend = trends.get('safety_score_trend', 0)
            time_trend = trends.get('execution_time_trend', 0)
            
            # Trend indicators
            if abs(pass_rate_trend) < 1.0:
                pass_indicator = "➡️ Stable"
            elif pass_rate_trend > 0:
                pass_indicator = f"⬆️ Improved by {pass_rate_trend:+.1f}%"
            else:
                pass_indicator = f"⬇️ Declined by {pass_rate_trend:+.1f}%"
            
            if abs(safety_trend) < 0.1:
                safety_indicator = "➡️ Stable"
            elif safety_trend < 0:  # Lower safety score is better
                safety_indicator = f"⬆️ Improved by {-safety_trend:.2f}"
            else:
                safety_indicator = f"⬇️ Worsened by {safety_trend:.2f}"
            
            if abs(time_trend) < 100:
                time_indicator = "➡️ Stable"
            elif time_trend < 0:
                time_indicator = f"⚡ Faster by {-time_trend:.0f}ms"
            else:
                time_indicator = f"⏳ Slower by {time_trend:.0f}ms"
            
            content += f"""
| Metric | Trend | Change |
|--------|-------|---------|
| **Pass Rate** | {pass_indicator} | {pass_rate_trend:+.1f}% |
| **Safety Score** | {safety_indicator} | {safety_trend:+.2f} |
| **Execution Time** | {time_indicator} | {time_trend:+.0f}ms |

"""
        
        # Test run history table
        content += f"""
## 📊 Test Run History

| Run ID | Date | Pass Rate | Safety Score | Failed Phrases | Notes |
|--------|------|-----------|--------------|-----------------|-------|
"""
        
        for run in reversed(test_runs[-10:]):  # Last 10 runs, newest first
            timestamp = datetime.fromtimestamp(run.get('timestamp', 0))
            date_str = timestamp.strftime('%m-%d %H:%M')
            
            # Get meaningful run ID - extract timestamp or use last part
            full_run_id = run.get('run_id', 'unknown')
            if '_' in full_run_id:
                # Extract the timestamp part after the last underscore
                run_id = full_run_id.split('_')[-1][:10]  # Get timestamp, limit to 10 chars
            else:
                run_id = full_run_id[:10]  # Fallback truncation
            pass_rate = run.get('overall_pass_rate', 0)
            safety_score = run.get('weighted_safety_score', 0)
            
            # Calculate total failed phrases
            failed_count = 0
            category_performance = run.get('category_performance', {})
            for category, perf in category_performance.items():
                failed_count += perf.get('false_negatives', 0) + perf.get('false_positives', 0)
            
            # Status indicators
            status_notes = []
            if run.get('early_termination', False):
                status_notes.append("⚠️ Early term")
            if pass_rate < 80:
                status_notes.append("❌ Low pass rate")
            
            notes = " ".join(status_notes) if status_notes else "✅"
            
            content += f"| `{run_id}` | {date_str} | {pass_rate:.1f}% | {safety_score:.2f} | {failed_count} | {notes} |\n"
        
        # NEW: Historical failed phrase trend analysis
        if historical_failed_phrases:
            content += self._build_historical_failure_trends_section(historical_failed_phrases)
        
        # Weekly review recommendations
        content += f"""
## 📋 Historical Analysis Insights

### 🔍 Key Observations

"""
        
        # Generate insights based on trends
        if len(test_runs) >= 3:
            recent_runs = test_runs[-3:]
            pass_rates = [run.get('overall_pass_rate', 0) for run in recent_runs]
            
            if all(rate >= 85 for rate in pass_rates):
                content += "- ✅ **Consistent Performance**: Pass rates have been stable above 85%\n"
            elif any(rate < 75 for rate in pass_rates):
                content += "- ⚠️ **Performance Concern**: Some runs below 75% pass rate detected\n"
            
            # Check for improvement or decline
            if pass_rates[-1] > pass_rates[0] + 5:
                content += "- 📈 **Improving Trend**: Recent performance shows significant improvement\n"
            elif pass_rates[-1] < pass_rates[0] - 5:
                content += "- 📉 **Declining Trend**: Recent performance shows concerning decline\n"
        
        content += f"""
### 🎯 Recommendations

1. **Weekly Reviews**: Monitor trends weekly to catch performance degradation early
2. **Threshold Stability**: Ensure changes don't negatively impact long-term performance  
3. **Safety First**: Prioritize maintaining high detection rates for critical categories
4. **Continuous Improvement**: Use historical data to guide optimization efforts

---

**Generated by**: Ash-Thrash v3.1-2a-2  
**For**: The Alphabet Cartel LGBTQIA+ Community Mental Health Support System
"""
        
        return content
    
    def _build_historical_failure_trends_section(self, historical_failed_phrases: Dict[str, List[Dict]]) -> str:
        """Build section showing historical trends in failed phrases by category"""
        content = """
## 📉 Historical Failure Trends by Category

This section shows patterns in failed phrases over recent test runs to identify persistent issues.

"""
        
        for category, failure_history in historical_failed_phrases.items():
            if not failure_history:
                continue
            
            content += f"""
### Category: {category}

| Run | Date | False Negatives | False Positives | Pass Rate | Trend |
|-----|------|------------------|------------------|-----------|--------|
"""
            
            for i, failure_data in enumerate(failure_history):
                timestamp = datetime.fromtimestamp(failure_data.get('timestamp', 0))
                date_str = timestamp.strftime('%m-%d %H:%M')
                
                false_negs = failure_data.get('false_negatives', 0)
                false_pos = failure_data.get('false_positives', 0)
                pass_rate = failure_data.get('pass_rate', 0)
                
                # Determine trend
                if i > 0:
                    prev_pass_rate = failure_history[i-1].get('pass_rate', 0)
                    if pass_rate > prev_pass_rate + 2:
                        trend = "⬆️ Improving"
                    elif pass_rate < prev_pass_rate - 2:
                        trend = "⬇️ Declining" 
                    else:
                        trend = "➡️ Stable"
                else:
                    trend = "➡️ Baseline"
                
                # Get meaningful run ID - extract timestamp or use last part
                full_run_id = failure_data.get('run_id', 'unknown')
                if '_' in full_run_id:
                    # Extract the timestamp part after the last underscore
                    run_id = full_run_id.split('_')[-1][:8]  # Get timestamp, limit to 8 chars for table
                else:
                    run_id = full_run_id[:8]  # Fallback truncation
                content += f"| `{run_id}` | {date_str} | {false_negs} | {false_pos} | {pass_rate:.1f}% | {trend} |\n"
            
            # Analysis for this category
            latest = failure_history[-1]
            total_failures = latest.get('false_negatives', 0) + latest.get('false_positives', 0)
            
            if latest.get('false_negatives', 0) > latest.get('false_positives', 0):
                primary_issue = "false negatives (under-classification)"
            else:
                primary_issue = "false positives (over-classification)"
            
            content += f"""
**Analysis**: This category shows {total_failures} total failures in the latest run, primarily {primary_issue}.

"""
        
        return content
    
    def _build_threshold_recommendations_markdown(self, recommendations: List, category_summaries: List) -> str:
        """Build markdown content for threshold tuning recommendations"""
        
        content = f"""# Threshold Tuning Recommendations

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)  
**Repository**: [ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

---

## 🎯 Executive Summary

This report provides specific threshold adjustment recommendations based on the latest test results.
Focus on high-confidence recommendations first, especially for critical categories.

"""
        
        if not recommendations:
            content += """
## ✅ No Threshold Adjustments Needed

Current threshold settings are performing well across all categories. 
Continue monitoring for any performance changes.

"""
            return content
        
        # Group recommendations by priority and confidence (handle mixed data types)
        def get_priority_level(rec):
            priority = rec.get('priority', 'UNKNOWN')
            if isinstance(priority, str):
                priority_upper = priority.upper()
                if priority_upper in ['HIGH', 'CRITICAL']:
                    return 1
                elif priority_upper == 'MEDIUM':
                    return 2
                elif priority_upper == 'LOW':
                    return 3
                else:
                    return 99
            elif isinstance(priority, int):
                return priority
            else:
                return 99
        
        critical_recs = [r for r in recommendations if get_priority_level(r) == 1]
        high_recs = [r for r in recommendations if get_priority_level(r) == 2]
        medium_recs = [r for r in recommendations if get_priority_level(r) == 3]
        
        # High confidence recommendations
        high_confidence = [r for r in recommendations if r.get('confidence', '').lower() == 'high']
        
        if critical_recs:
            content += f"""
## 🚨 Critical Priority Recommendations

These issues require immediate attention due to safety implications.

"""
            for i, rec in enumerate(critical_recs, 1):
                content += f"""
### {i}. {rec.get('category', 'Unknown Category')}

- **Issue**: {rec.get('issue', 'No issue description')}
- **Recommendation**: {rec.get('recommendation', 'No recommendation')}
- **Confidence**: {rec.get('confidence', 'Unknown')}
- **Risk Level**: {rec.get('risk_level', 'Unknown')}

"""
        
        if high_recs:
            content += f"""
## ⚠️ High Priority Recommendations

Important optimizations that will improve performance.

"""
            for i, rec in enumerate(high_recs, 1):
                content += f"""
### {i}. {rec.get('category', 'Unknown Category')}

- **Issue**: {rec.get('issue', 'No issue description')}
- **Recommendation**: {rec.get('recommendation', 'No recommendation')}
- **Confidence**: {rec.get('confidence', 'Unknown')}
- **Expected Improvement**: {rec.get('expected_improvement', 'Unknown')}

"""
        
        if high_confidence:
            content += f"""
## 💡 High Confidence Recommendations

These recommendations have strong statistical backing and should be prioritized.

"""
            for rec in high_confidence:
                if get_priority_level(rec) <= 2:  # Don't duplicate critical/high priority ones
                    continue
                    
                content += f"""
- **{rec.get('category', 'Unknown')}**: {rec.get('recommendation', 'No recommendation')}

"""
        
        # Implementation guidance
        content += f"""
## 🔧 Implementation Guidance

### Step 1: Backup Current Settings
```bash
# Save current NLP server configuration
cp ash-nlp/.env ash-nlp/.env.backup
```

### Step 2: Apply Critical Changes First
Make incremental changes and test after each adjustment.

### Step 3: Validate Changes  
```bash
# Run focused tests on modified categories
docker compose exec ash-thrash python main.py definite_high
docker compose exec ash-thrash python main.py definite_medium
```

### Step 4: Full System Validation
```bash
# Run comprehensive test suite
docker compose exec ash-thrash python main.py
```

### Step 5: Monitor and Iterate
Review results and make additional adjustments as needed. Safety-first approach - err on the side of sensitivity for crisis detection.

---

**Generated by**: Ash-Thrash v3.1-2a-2  
**For**: The Alphabet Cartel LGBTQIA+ Community Mental Health Support System
"""
        
        return content
    # ========================================================================

# ========================================================================
# FACTORY FUNCTION
# ========================================================================
def create_analyze_results_manager(unified_config_manager, results_manager, logging_config_manager) -> AnalyzeResultsManager:
    """
    Factory function for AnalyzeResultsManager (Clean v3.1 Pattern)
    
    Args:
        unified_config_manager: UnifiedConfigManager instance
        results_manager: ResultsManager instance  
        logging_config_manager: LoggingConfigManager instance
        
    Returns:
        Initialized AnalyzeResultsManager instance
        
    Raises:
        ValueError: If required managers are None or invalid
    """
    logger.debug("Creating AnalyzeResultsManager with Clean v3.1 architecture")
    
    if not unified_config_manager:
        raise ValueError("UnifiedConfigManager is required for AnalyzeResultsManager factory")
    
    if not results_manager:
        raise ValueError("ResultsManager is required for AnalyzeResultsManager factory")
    
    if not logging_config_manager:
        raise ValueError("LoggingConfigManager is required for AnalyzeResultsManager factory")
    
    return AnalyzeResultsManager(unified_config_manager, results_manager, logging_config_manager)

# ========================================================================
# PUBLIC INTERFACE
# ========================================================================
__all__ = [
    'AnalyzeResultsManager',
    'create_analyze_results_manager'
]

logger.info("AnalyzeResultsManager loaded with enhanced failed phrase analysis")
# ========================================================================