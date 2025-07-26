"""
Report Generator for Ash-Thrash Testing

Generates various types of reports from test results including
HTML reports, performance summaries, and trend analysis.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import glob


class ReportGenerator:
    """Generates reports from test results"""
    
    def __init__(self, results_dir: str = "results"):
        """
        Initialize report generator
        
        Args:
            results_dir: Directory containing test results
        """
        self.results_dir = results_dir
    
    def generate_performance_summary(self, results: Dict[str, Any]) -> str:
        """
        Generate a text-based performance summary
        
        Args:
            results: Processed test results
            
        Returns:
            str: Formatted performance summary
        """
        overall = results.get('overall_results', {})
        goals = results.get('goal_achievement', {})
        categories = results.get('category_results', {})
        
        report = []
        report.append("=" * 80)
        report.append("🧪 ASH-THRASH COMPREHENSIVE TESTING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall Performance
        report.append("📊 OVERALL PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Total Tests: {overall.get('total_tests', 0)}")
        report.append(f"Passed: {overall.get('total_passed', 0)}")
        report.append(f"Failed: {overall.get('total_failed', 0)}")
        report.append(f"Errors: {overall.get('total_errors', 0)}")
        report.append(f"Pass Rate: {overall.get('overall_pass_rate', 0):.1f}%")
        report.append(f"Avg Response Time: {overall.get('avg_response_time', 0):.1f}ms")
        
        if overall.get('execution_time', 0) > 0:
            report.append(f"Total Execution Time: {overall['execution_time']:.1f}s")
        
        report.append("")
        
        # Goal Achievement
        goal_summary = goals.get('summary', {})
        report.append("🎯 GOAL ACHIEVEMENT")
        report.append("-" * 40)
        report.append(f"Goals Achieved: {goal_summary.get('goals_achieved', 0)}/{goal_summary.get('total_goals', 0)}")
        report.append(f"Achievement Rate: {goal_summary.get('achievement_rate', 0):.1f}%")
        report.append(f"Status: {goal_summary.get('overall_status', 'Unknown')}")
        report.append("")
        
        # Category Performance
        report.append("📋 CATEGORY PERFORMANCE")
        report.append("-" * 40)
        
        for category, data in categories.items():
            status_icon = "✅" if data.get('goal_met', False) else "❌"
            report.append(f"{status_icon} {category}")
            report.append(f"   Pass Rate: {data.get('pass_rate', 0):.1f}% (Target: {data.get('target_rate', 0):.1f}%)")
            report.append(f"   Tests: {data.get('passed_tests', 0)}/{data.get('total_tests', 0)}")
            report.append(f"   Avg Confidence: {data.get('avg_confidence', 0):.3f}")
            
            failures = data.get('failures', [])
            if failures:
                report.append(f"   Failures: {len(failures)}")
                # Show first few failures
                for failure in failures[:3]:
                    report.append(f"     - '{failure.get('message', '')[:50]}...' → {failure.get('detected', 'unknown')}")
                if len(failures) > 3:
                    report.append(f"     ... and {len(failures) - 3} more")
            report.append("")
        
        # Performance Metrics
        perf = results.get('performance_metrics', {})
        if perf and 'response_time' in perf:
            report.append("⚡ PERFORMANCE METRICS")
            report.append("-" * 40)
            
            rt = perf['response_time']
            report.append(f"Response Time - Min: {rt.get('min', 0):.1f}ms, Max: {rt.get('max', 0):.1f}ms, Avg: {rt.get('mean', 0):.1f}ms")
            
            conf = perf.get('confidence', {})
            if conf:
                report.append(f"Confidence - Min: {conf.get('min', 0):.3f}, Max: {conf.get('max', 0):.3f}, Avg: {conf.get('mean', 0):.3f}")
            
            error_rate = perf.get('error_rate', 0)
            if error_rate > 0:
                report.append(f"Error Rate: {error_rate:.1f}%")
            report.append("")
        
        # Summary and Recommendations
        summary = results.get('summary', {})
        if summary:
            report.append("💡 SUMMARY & RECOMMENDATIONS")
            report.append("-" * 40)
            report.append(f"Status: {summary.get('overall_status', 'Unknown')}")
            
            findings = summary.get('key_findings', [])
            if findings:
                report.append("\nKey Findings:")
                for finding in findings:
                    report.append(f"  • {finding}")
            
            recommendations = summary.get('recommendations', [])
            if recommendations:
                report.append("\nRecommendations:")
                for rec in recommendations:
                    report.append(f"  • {rec}")
            report.append("")
        
        report.append("=" * 80)
        report.append("Generated by Ash-Thrash Testing Suite")
        report.append("Repository: https://github.com/The-Alphabet-Cartel/ash-thrash")
        
        return "\n".join(report)
    
    def generate_html_report(self, results: Dict[str, Any]) -> str:
        """
        Generate an HTML report with charts and detailed analysis
        
        Args:
            results: Processed test results
            
        Returns:
            str: HTML report content
        """
        overall = results.get('overall_results', {})
        goals = results.get('goal_achievement', {})
        categories = results.get('category_results', {})
        confidence_dist = results.get('confidence_distribution', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ash-Thrash Testing Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .metric-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .metric-label {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .category-card {{
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
        }}
        .category-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .status-pass {{ color: #28a745; }}
        .status-fail {{ color: #dc3545; }}
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
        .failure-item {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 10px;
            margin: 5px 0;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            color: #6c757d;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Ash-Thrash Testing Report</h1>
        <p>Comprehensive Crisis Detection Testing Results</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="card">
        <h2>📊 Overall Performance</h2>
        <div class="metrics-grid">
            <div class="metric-box">
                <div class="metric-number">{overall.get('total_tests', 0)}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-box">
                <div class="metric-number">{overall.get('overall_pass_rate', 0):.1f}%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric-box">
                <div class="metric-number">{overall.get('avg_response_time', 0):.0f}ms</div>
                <div class="metric-label">Avg Response Time</div>
            </div>
            <div class="metric-box">
                <div class="metric-number">{goals.get('summary', {}).get('goals_achieved', 0)}/{goals.get('summary', {}).get('total_goals', 0)}</div>
                <div class="metric-label">Goals Achieved</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>🎯 Goal Achievement</h2>
        <div class="chart-container">
            <canvas id="goalChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2>📋 Category Performance</h2>
        <div class="category-grid">
"""
        
        # Add category cards
        for category, data in categories.items():
            status_class = "status-pass" if data.get('goal_met', False) else "status-fail"
            status_icon = "✅" if data.get('goal_met', False) else "❌"
            
            html += f"""
            <div class="category-card">
                <div class="category-header">
                    <strong>{category.replace('_', ' ').title()}</strong>
                    <span class="{status_class}">{status_icon} {data.get('pass_rate', 0):.1f}%</span>
                </div>
                <div>Target: {data.get('target_rate', 0):.1f}%</div>
                <div>Tests: {data.get('passed_tests', 0)}/{data.get('total_tests', 0)}</div>
                <div>Avg Confidence: {data.get('avg_confidence', 0):.3f}</div>
                <div>Avg Response: {data.get('avg_response_time', 0):.1f}ms</div>
            </div>
"""
        
        html += """
        </div>
    </div>
"""
        
        # Add failures section if there are any
        failure_analysis = results.get('failure_analysis', {})
        critical_failures = failure_analysis.get('critical_failure_details', [])
        
        if critical_failures:
            html += f"""
    <div class="card">
        <h2>🚨 Critical Failures</h2>
        <p>Found {len(critical_failures)} critical failures that require immediate attention:</p>
"""
            for failure in critical_failures[:10]:  # Show first 10
                html += f"""
        <div class="failure-item">
            <strong>{failure.get('type', 'Unknown').replace('_', ' ').title()}:</strong>
            "{failure.get('message', '')[:100]}..."<br>
            Expected: {failure.get('expected', 'unknown')}, Detected: {failure.get('detected', 'unknown')}
            (Confidence: {failure.get('confidence', 0):.3f})
        </div>
"""
            html += "    </div>\n"
        
        # Add confidence distribution chart
        if confidence_dist and 'distribution_ranges' in confidence_dist:
            html += """
    <div class="card">
        <h2>📈 Confidence Distribution</h2>
        <div class="chart-container">
            <canvas id="confidenceChart"></canvas>
        </div>
    </div>
"""
        
        # JavaScript for charts
        html += """
    <script>
        // Goal Achievement Chart
        const goalCtx = document.getElementById('goalChart').getContext('2d');
        new Chart(goalCtx, {
            type: 'bar',
            data: {
                labels: ["""
        
        # Add goal chart data
        goal_labels = []
        goal_data = []
        goal_colors = []
        
        for category, goal_info in goals.items():
            if category != 'summary':
                goal_labels.append(f"'{category.replace('_', ' ').title()}'")
                goal_data.append(goal_info.get('actual_rate', 0))
                color = "'#28a745'" if goal_info.get('goal_met', False) else "'#dc3545'"
                goal_colors.append(color)
        
        html += ", ".join(goal_labels)
        html += f"""],
                datasets: [{{
                    label: 'Pass Rate (%)',
                    data: [{", ".join(map(str, goal_data))}],
                    backgroundColor: [{", ".join(goal_colors)}],
                    borderColor: [{", ".join(goal_colors)}],
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
"""
        
        # Add confidence distribution chart if data exists
        if confidence_dist and 'distribution_ranges' in confidence_dist:
            ranges = confidence_dist['distribution_ranges']
            html += f"""
        // Confidence Distribution Chart
        const confCtx = document.getElementById('confidenceChart').getContext('2d');
        new Chart(confCtx, {{
            type: 'pie',
            data: {{
                labels: {list(ranges.keys())},
                datasets: [{{
                    data: {list(ranges.values())},
                    backgroundColor: [
                        '#ff6384',
                        '#36a2eb', 
                        '#cc65fe',
                        '#ffce56',
                        '#4bc0c0'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
"""
        
        html += """
    </script>

    <div class="footer">
        <p>Generated by <strong>Ash-Thrash Testing Suite</strong></p>
        <p><a href="https://github.com/The-Alphabet-Cartel/ash-thrash">github.com/The-Alphabet-Cartel/ash-thrash</a></p>
        <p><a href="https://discord.gg/alphabetcartel">Join The Alphabet Cartel Discord</a></p>
    </div>
</body>
</html>
"""
        
        return html
    
    def generate_trend_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate trend analysis from historical results
        
        Args:
            days: Number of days to analyze
            
        Returns:
            dict: Trend analysis data
        """
        # Find result files from the last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        result_files = glob.glob(os.path.join(self.results_dir, "comprehensive", "*.json"))
        
        historical_data = []
        for file_path in result_files:
            try:
                # Extract timestamp from filename
                filename = os.path.basename(file_path)
                if "comprehensive_test_results_" in filename:
                    timestamp_str = filename.replace("comprehensive_test_results_", "").replace(".json", "")
                    try:
                        timestamp = datetime.fromtimestamp(int(timestamp_str))
                        if timestamp >= cutoff_date:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                historical_data.append({
                                    'timestamp': timestamp,
                                    'data': data
                                })
                    except ValueError:
                        continue
            except Exception:
                continue
        
        # Sort by timestamp
        historical_data.sort(key=lambda x: x['timestamp'])
        
        if not historical_data:
            return {'error': f'No test results found in the last {days} days'}
        
        # Extract trend data
        trends = []
        for entry in historical_data:
            data = entry['data']
            overall = data.get('overall_results', {})
            goals = data.get('goal_achievement', {}).get('summary', {})
            
            trends.append({
                'timestamp': entry['timestamp'].isoformat(),
                'pass_rate': overall.get('overall_pass_rate', 0),
                'goal_achievement_rate': goals.get('achievement_rate', 0),
                'avg_response_time': overall.get('avg_response_time', 0),
                'total_tests': overall.get('total_tests', 0)
            })
        
        # Calculate trend statistics
        if len(trends) > 1:
            first = trends[0]
            last = trends[-1]
            
            trend_analysis = {
                'timespan': f"{first['timestamp']} to {last['timestamp']}",
                'total_data_points': len(trends),
                'pass_rate_trend': last['pass_rate'] - first['pass_rate'],
                'goal_achievement_trend': last['goal_achievement_rate'] - first['goal_achievement_rate'],
                'response_time_trend': last['avg_response_time'] - first['avg_response_time'],
                'trends': trends
            }
            
            # Add trend interpretation
            if trend_analysis['pass_rate_trend'] > 2:
                trend_analysis['pass_rate_status'] = 'Improving'
            elif trend_analysis['pass_rate_trend'] < -2:
                trend_analysis['pass_rate_status'] = 'Declining'
            else:
                trend_analysis['pass_rate_status'] = 'Stable'
            
            return trend_analysis
        else:
            return {
                'timespan': trends[0]['timestamp'] if trends else 'No data',
                'total_data_points': len(trends),
                'message': 'Insufficient data for trend analysis',
                'trends': trends
            }
    
    def save_report(self, content: str, filename: str, report_type: str = "html") -> str:
        """
        Save report to file
        
        Args:
            content: Report content
            filename: Output filename
            report_type: Type of report (html, txt, json)
            
        Returns:
            str: Full path of saved file
        """
        reports_dir = os.path.join(self.results_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Add extension if not present
        if not filename.endswith(f".{report_type}"):
            filename = f"{filename}.{report_type}"
        
        file_path = os.path.join(reports_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path


def generate_quick_report(results_file: str, output_format: str = "txt") -> str:
    """
    Quick report generation from results file
    
    Args:
        results_file: Path to results JSON file
        output_format: Output format (txt, html)
        
    Returns:
        str: Generated report content
    """
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    generator = ReportGenerator()
    
    if output_format.lower() == "html":
        return generator.generate_html_report(results)
    else:
        return generator.generate_performance_summary(results)