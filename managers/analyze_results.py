# ash-thrash/managers/analyze_results.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Results Analysis and Markdown Report Generation Manager for Ash-Thrash Service
---
FILE VERSION: v3.1-2a-1
LAST MODIFIED: 2025-08-31
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
    """
    
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
            overall_pass_rate = run_summary.get('overall_pass_rate', 0)
            safety_score = run_summary.get('weighted_safety_score', 0)
            
            logger.info("OVERALL PERFORMANCE")
            logger.info(f"Overall Pass Rate: {overall_pass_rate:.1f}%")
            logger.info(f"Safety Score: {safety_score:.2f}")
            logger.info(f"Total Phrases: {run_summary.get('total_phrases', 0)}")
            logger.info(f"Passed: {run_summary.get('total_passed', 0)}")
            logger.info(f"Failed: {run_summary.get('total_failed', 0)}")
            logger.info(f"Errors: {run_summary.get('total_errors', 0)}")
            
            if run_summary.get('early_termination'):
                logger.warning(f"Early Termination: {run_summary.get('termination_reason', 'unknown')}")
            
            # Category performance
            logger.info("CATEGORY PERFORMANCE")
            for category in category_summaries:
                name = category.get('category_name', 'unknown')
                pass_rate = category.get('pass_rate', 0)
                target = category.get('target_pass_rate', 0)
                met_target = category.get('met_target', False)
                is_critical = category.get('is_critical', False)
                
                status = "PASS" if met_target else "FAIL"
                log_level = logger.info
                if is_critical and not met_target:
                    status = "CRITICAL FAIL"
                    log_level = logger.error
                elif not met_target:
                    log_level = logger.warning
                
                log_level(f"{name}: {pass_rate:.1f}% (target: {target}%) - {status}")
            
            # Performance analysis
            if performance_analysis:
                logger.info("PERFORMANCE ANALYSIS")
                overall_status = performance_analysis.get('overall_status', 'unknown')
                safety_assessment = performance_analysis.get('safety_assessment', 'unknown')
                
                logger.info(f"Overall Status: {overall_status.upper()}")
                logger.info(f"Safety Assessment: {safety_assessment.upper()}")
                
                # Critical failures
                critical_failures = performance_analysis.get('critical_failures', [])
                if critical_failures:
                    logger.error("CRITICAL FAILURES DETECTED:")
                    for failure in critical_failures:
                        cat = failure.get('category', 'unknown')
                        rate = failure.get('pass_rate', 0)
                        target = failure.get('target', 0)
                        false_negs = failure.get('false_negatives', 0)
                        logger.error(f"  {cat}: {rate:.1f}% (need {target}%), {false_negs} false negatives")
                
                # Performance issues
                performance_issues = performance_analysis.get('performance_issues', [])
                if performance_issues:
                    logger.warning("PERFORMANCE ISSUES:")
                    for issue in performance_issues:
                        cat = issue.get('category', 'unknown')
                        issue_type = issue.get('issue_type', 'unknown')
                        if issue_type == 'significantly_below_target':
                            rate = issue.get('pass_rate', 0)
                            target = issue.get('target', 0)
                            logger.warning(f"  {cat}: {rate:.1f}% (target {target}%)")
                        elif issue_type == 'false_negatives_detected':
                            false_negs = issue.get('false_negatives', 0)
                            logger.warning(f"  {cat}: {false_negs} false negatives")
                
                # Strengths
                strengths = performance_analysis.get('strengths', [])
                if strengths:
                    logger.info("SYSTEM STRENGTHS:")
                    for strength in strengths:
                        cat = strength.get('category', 'unknown')
                        rate = strength.get('pass_rate', 0)
                        target = strength.get('target', 0)
                        logger.info(f"  {cat}: {rate:.1f}% (exceeds {target}% target)")
            
            # Recommendations
            if recommendations:
                logger.info("TUNING RECOMMENDATIONS")
                
                high_priority = [r for r in recommendations if r.get('priority') == 'HIGH']
                medium_priority = [r for r in recommendations if r.get('priority') == 'MEDIUM']
                low_priority = [r for r in recommendations if r.get('priority') == 'LOW']
                
                for priority_group, title, log_level in [
                    (high_priority, "HIGH PRIORITY", logger.error),
                    (medium_priority, "MEDIUM PRIORITY", logger.warning),
                    (low_priority, "LOW PRIORITY", logger.info)
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
            
            # Generate markdown content
            markdown_content = self._build_latest_run_markdown(
                run_summary, category_summaries, performance_analysis, recommendations
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
            
            # Generate historical markdown
            markdown_content = self._build_historical_performance_markdown(
                test_runs, trends, days
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
    
    def _build_latest_run_markdown(self, run_summary: Dict, category_summaries: List, 
                                  performance_analysis: Dict, recommendations: List) -> str:
        """Build markdown content for latest run summary"""
        
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
        
        # Category Performance Table
        content += """## 📋 Category Performance

| Category | Pass Rate | Target | Status | False Negatives | False Positives |
|----------|-----------|--------|---------|-----------------|-----------------|
"""
        
        for category in category_summaries:
            name = category.get('category_name', 'unknown')
            pass_rate = category.get('pass_rate', 0)
            target = category.get('target_pass_rate', 0)
            met_target = category.get('met_target', False)
            is_critical = category.get('is_critical', False)
            false_negs = category.get('false_negatives', 0)
            false_pos = category.get('false_positives', 0)
            
            if is_critical and not met_target:
                status = "🚨 **CRITICAL FAIL**"
            elif not met_target:
                status = "❌ FAIL"
            else:
                status = "✅ PASS"
            
            content += f"| {name} | {pass_rate:.1f}% | {target}% | {status} | {false_negs} | {false_pos} |\n"
        
        # Performance Analysis
        if performance_analysis:
            content += f"""
## 🔍 Performance Analysis

- **Overall Status**: {performance_analysis.get('overall_status', 'unknown').upper()}
- **Safety Assessment**: {performance_analysis.get('safety_assessment', 'unknown').upper()}
"""
            
            # Critical failures
            critical_failures = performance_analysis.get('critical_failures', [])
            if critical_failures:
                content += "\n### 🚨 Critical Failures\n\n"
                for failure in critical_failures:
                    cat = failure.get('category', 'unknown')
                    rate = failure.get('pass_rate', 0)
                    target = failure.get('target', 0)
                    false_negs = failure.get('false_negatives', 0)
                    content += f"- **{cat}**: {rate:.1f}% (need {target}%), {false_negs} false negatives\n"
            
            # Performance issues
            performance_issues = performance_analysis.get('performance_issues', [])
            if performance_issues:
                content += "\n### ⚠️ Performance Issues\n\n"
                for issue in performance_issues:
                    cat = issue.get('category', 'unknown')
                    issue_type = issue.get('issue_type', 'unknown')
                    if issue_type == 'significantly_below_target':
                        rate = issue.get('pass_rate', 0)
                        target = issue.get('target', 0)
                        content += f"- **{cat}**: {rate:.1f}% (target {target}%)\n"
                    elif issue_type == 'false_negatives_detected':
                        false_negs = issue.get('false_negatives', 0)
                        content += f"- **{cat}**: {false_negs} false negatives detected\n"
            
            # Strengths
            strengths = performance_analysis.get('strengths', [])
            if strengths:
                content += "\n### ✨ System Strengths\n\n"
                for strength in strengths:
                    cat = strength.get('category', 'unknown')
                    rate = strength.get('pass_rate', 0)
                    target = strength.get('target', 0)
                    content += f"- **{cat}**: {rate:.1f}% (exceeds {target}% target)\n"
        
        # Recommendations Summary
        if recommendations:
            content += "\n## 🔧 Tuning Recommendations Summary\n\n"
            
            high_priority = [r for r in recommendations if r.get('priority') == 'HIGH']
            medium_priority = [r for r in recommendations if r.get('priority') == 'MEDIUM']
            low_priority = [r for r in recommendations if r.get('priority') == 'LOW']
            
            content += f"- 🚨 **High Priority**: {len(high_priority)} recommendations\n"
            content += f"- ⚠️ **Medium Priority**: {len(medium_priority)} recommendations\n"
            content += f"- 💡 **Low Priority**: {len(low_priority)} recommendations\n"
            
            content += "\n> See `threshold_recommendations.md` for detailed tuning guidance.\n"
        
        content += f"""
---

**Generated by**: Ash-Thrash v3.1-2a-1  
**For**: The Alphabet Cartel LGBTQIA+ Community Mental Health Support System
"""
        
        return content
    
    def _build_threshold_recommendations_markdown(self, recommendations: List, 
                                                category_summaries: List) -> str:
        """Build markdown content for threshold recommendations"""
        
        content = f"""# NLP Threshold Tuning Recommendations

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)  
**Repository**: [ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

---

## 🎯 Executive Summary

This report provides specific threshold adjustment recommendations for the Ash-NLP crisis detection system based on comprehensive testing results.

"""
        
        if not recommendations:
            content += """
> ✅ **No tuning recommendations required** - All categories meeting performance targets.

"""
            return content
        
        # Group recommendations by priority
        high_priority = [r for r in recommendations if r.get('priority') == 'HIGH']
        medium_priority = [r for r in recommendations if r.get('priority') == 'MEDIUM']
        low_priority = [r for r in recommendations if r.get('priority') == 'LOW']
        
        # High Priority Recommendations
        if high_priority:
            content += f"""## 🚨 High Priority Recommendations ({len(high_priority)})

> **⚠️ IMMEDIATE ACTION REQUIRED** - These issues affect safety-critical crisis detection

"""
            
            for i, rec in enumerate(high_priority, 1):
                category = rec.get('category', 'unknown')
                issue = rec.get('issue', 'unknown issue')
                recommendation = rec.get('recommendation', 'no recommendation')
                confidence = rec.get('confidence', 'unknown')
                
                content += f"""### {i}. {category}

**Issue**: {issue}  
**Recommendation**: {recommendation}  
**Confidence**: {confidence}

"""
                
                # Add specific threshold suggestions based on category
                if 'definite_high' in category.lower():
                    content += """**Suggested Actions**:
- Lower `NLP_HIGH_CRISIS_THRESHOLD` from 0.8 to 0.7
- Review `NLP_CRISIS_ESCALATION_THRESHOLD` settings
- Test boundary cases between medium and high

"""
                elif 'false negatives' in issue.lower():
                    content += """**Suggested Actions**:
- Reduce detection thresholds by 0.1-0.2
- Review pattern matching sensitivity
- Consider ensemble model weight adjustments

"""
        
        # Medium Priority Recommendations
        if medium_priority:
            content += f"""## ⚠️ Medium Priority Recommendations ({len(medium_priority)})

"""
            
            for i, rec in enumerate(medium_priority, 1):
                category = rec.get('category', 'unknown')
                issue = rec.get('issue', 'unknown issue')
                recommendation = rec.get('recommendation', 'no recommendation')
                confidence = rec.get('confidence', 'unknown')
                
                content += f"""### {i}. {category}

**Issue**: {issue}  
**Recommendation**: {recommendation}  
**Confidence**: {confidence}

"""
        
        # Low Priority Recommendations
        if low_priority:
            content += f"""## 💡 Low Priority Recommendations ({len(low_priority)})

"""
            
            for i, rec in enumerate(low_priority, 1):
                category = rec.get('category', 'unknown')
                issue = rec.get('issue', 'unknown issue')
                recommendation = rec.get('recommendation', 'no recommendation')
                confidence = rec.get('confidence', 'unknown')
                
                content += f"""### {i}. {category}

**Issue**: {issue}  
**Recommendation**: {recommendation}  
**Confidence**: {confidence}

"""
        
        # Current Performance Context
        content += """## 📊 Current Performance Context

| Category | Current Pass Rate | Target | Gap | Action Priority |
|----------|------------------|--------|-----|-----------------|
"""
        
        for category in category_summaries:
            name = category.get('category_name', 'unknown')
            pass_rate = category.get('pass_rate', 0)
            target = category.get('target_pass_rate', 0)
            met_target = category.get('met_target', False)
            is_critical = category.get('is_critical', False)
            
            gap = target - pass_rate if not met_target else 0
            
            if is_critical and not met_target:
                priority = "🚨 CRITICAL"
            elif gap > 10:
                priority = "⚠️ HIGH"
            elif gap > 5:
                priority = "💡 MEDIUM"
            else:
                priority = "✅ GOOD"
            
            content += f"| {name} | {pass_rate:.1f}% | {target}% | {gap:+.1f}% | {priority} |\n"
        
        content += f"""

## 🔧 Implementation Guide

### Step 1: Backup Current Settings
```bash
# Backup current NLP configuration
cp ash-nlp/.env ash-nlp/.env.backup.$(date +%Y%m%d)
```

### Step 2: Apply High Priority Changes
Focus on safety-critical categories first. Make incremental changes and test after each adjustment.

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

**Generated by**: Ash-Thrash v3.1-2a-1  
**For**: The Alphabet Cartel LGBTQIA+ Community Mental Health Support System
"""
        
        return content
    
    def _build_historical_performance_markdown(self, test_runs: List, trends: Dict, days: int) -> str:
        """Build markdown content for historical performance"""
        
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
                safety_indicator = f"⬇️ Worsened by {safety_trend:+.2f}"
            
            if abs(time_trend) < 1000:  # Less than 1 second change
                time_indicator = "➡️ Stable"
            elif time_trend < 0:
                time_indicator = f"⚡ Faster by {-time_trend/1000:.1f}s"
            else:
                time_indicator = f"🐌 Slower by {time_trend/1000:.1f}s"
            
            content += f"""
### Trend Analysis

| Metric | Trend |
|--------|-------|
| **Pass Rate** | {pass_indicator} |
| **Safety Score** | {safety_indicator} |
| **Execution Time** | {time_indicator} |

"""
        
        # Recent test runs table
        content += """## 📊 Recent Test Runs

| Date/Time | Pass Rate | Safety Score | Total Phrases | Status | Notes |
|-----------|-----------|--------------|---------------|---------|-------|
"""
        
        # Show last 15 runs
        for run in test_runs[-15:]:
            timestamp = datetime.fromtimestamp(run['timestamp'])
            date_str = timestamp.strftime('%m-%d %H:%M')
            pass_rate = run.get('overall_pass_rate', 0)
            safety_score = run.get('weighted_safety_score', 0)
            total_phrases = run.get('total_phrases', 0)
            
            if run.get('early_termination'):
                status = "❌ HALT"
                notes = "Early termination"
            elif pass_rate >= 85.0:
                status = "✅ PASS"
                notes = ""
            else:
                status = "⚠️ FAIL"
                notes = f"Below 85% threshold"
            
            content += f"| {date_str} | {pass_rate:.1f}% | {safety_score:.2f} | {total_phrases} | {status} | {notes} |\n"
        
        # Performance insights
        if len(test_runs) >= 5:
            recent_5 = test_runs[-5:]
            avg_pass_rate = sum(r.get('overall_pass_rate', 0) for r in recent_5) / 5
            avg_safety_score = sum(r.get('weighted_safety_score', 0) for r in recent_5) / 5
            
            content += f"""
## 🔍 Performance Insights (Last 5 Runs)

- **Average Pass Rate**: {avg_pass_rate:.1f}%
- **Average Safety Score**: {avg_safety_score:.2f}
- **Performance Stability**: {"Stable" if max(r.get('overall_pass_rate', 0) for r in recent_5) - min(r.get('overall_pass_rate', 0) for r in recent_5) < 10 else "Variable"}

"""
            
            if avg_pass_rate < 70:
                content += "> 🚨 **Alert**: Average pass rate below 70% - immediate threshold review recommended\n\n"
            elif avg_pass_rate < 80:
                content += "> ⚠️ **Warning**: Average pass rate below 80% - consider threshold adjustments\n\n"
            else:
                content += "> ✅ **Good**: Average pass rate above 80% - system performing within acceptable range\n\n"
        
        content += f"""
## 📋 Historical Analysis Summary

This analysis covers {len(test_runs)} test runs over the past {days} days, providing insights into:

- **Performance Trends**: Overall system improvement or degradation patterns
- **Stability Metrics**: Consistency of results across multiple test runs  
- **Safety Evolution**: How well the system maintains crisis detection accuracy
- **Execution Efficiency**: Performance optimization tracking

### Recommendations for Historical Review

1. **Weekly Reviews**: Monitor trends weekly to catch performance degradation early
2. **Threshold Stability**: Ensure changes don't negatively impact long-term performance
3. **Safety First**: Prioritize maintaining high detection rates for critical categories
4. **Continuous Improvement**: Use historical data to guide optimization efforts

---

**Generated by**: Ash-Thrash v3.1-2a-1  
**For**: The Alphabet Cartel LGBTQIA+ Community Mental Health Support System
"""
        
        return content

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

# Export public interface
__all__ = ['AnalyzeResultsManager', 'create_analyze_results_manager']

logger.info("AnalyzeResultsManager v3.1-2a-1 loaded")