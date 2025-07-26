"""
Results retrieval routes for Ash-Thrash API

Provides endpoints for retrieving test results, downloading files,
and accessing historical data.
"""

from flask import Blueprint, jsonify, request, send_file, current_app
from datetime import datetime, timedelta
import os
import json
import glob
from typing import Dict, List, Any

results_bp = Blueprint('results', __name__)


@results_bp.route('/latest')
def get_latest_results():
    """
    Get the latest comprehensive test results
    
    Returns:
        JSON response with latest results
    """
    try:
        results_dir = current_app.config.get('RESULTS_DIR', 'results')
        comprehensive_dir = os.path.join(results_dir, 'comprehensive')
        
        # Find latest results file
        result_files = glob.glob(os.path.join(comprehensive_dir, 'comprehensive_test_results_*.json'))
        
        if not result_files:
            return jsonify({
                'error': 'No test results found',
                'message': 'No comprehensive test results are available',
                'suggestion': 'Run a comprehensive test first using POST /api/test/run'
            }), 404
        
        # Sort by filename (timestamp) and get latest
        result_files.sort(reverse=True)
        latest_file = result_files[0]
        
        with open(latest_file, 'r') as f:
            results = json.load(f)
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(latest_file),
            'file_path': latest_file,
            'retrieved_at': datetime.now().isoformat(),
            'results': results
        })
        
    except FileNotFoundError:
        return jsonify({
            'error': 'Results file not found',
            'message': 'The results file could not be located'
        }), 404
    except json.JSONDecodeError as e:
        return jsonify({
            'error': 'Invalid results file',
            'message': f'Results file contains invalid JSON: {e}'
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve results',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@results_bp.route('/history')
def get_results_history():
    """
    Get historical test results summary
    
    Query parameters:
        - days: Number of days to look back (default: 7)
        - limit: Maximum number of results (default: 20)
        - type: Test type filter (comprehensive, quick, all)
        
    Returns:
        JSON response with historical results
    """
    try:
        # Parse query parameters
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 20, type=int)
        test_type = request.args.get('type', 'all')
        
        results_dir = current_app.config.get('RESULTS_DIR', 'results')
        cutoff_date = datetime.now() - timedelta(days=days)
        
        historical_results = []
        
        # Get comprehensive results if requested
        if test_type in ['comprehensive', 'all']:
            comprehensive_files = glob.glob(os.path.join(results_dir, 'comprehensive', '*.json'))
            for file_path in comprehensive_files:
                file_info = _get_file_info(file_path, 'comprehensive', cutoff_date)
                if file_info:
                    historical_results.append(file_info)
        
        # Get quick validation results if requested
        if test_type in ['quick', 'all']:
            quick_files = glob.glob(os.path.join(results_dir, 'quick_validation', '*.json'))
            for file_path in quick_files:
                file_info = _get_file_info(file_path, 'quick', cutoff_date)
                if file_info:
                    historical_results.append(file_info)
        
        # Sort by timestamp (newest first) and limit
        historical_results.sort(key=lambda x: x['timestamp'], reverse=True)
        historical_results = historical_results[:limit]
        
        return jsonify({
            'success': True,
            'query_parameters': {
                'days': days,
                'limit': limit,
                'type': test_type
            },
            'date_range': {
                'from': cutoff_date.isoformat(),
                'to': datetime.now().isoformat()
            },
            'total_results': len(historical_results),
            'results': historical_results
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve history',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@results_bp.route('/summary')
def get_results_summary():
    """
    Get summary statistics of all test results
    
    Returns:
        JSON response with summary statistics
    """
    try:
        results_dir = current_app.config.get('RESULTS_DIR', 'results')
        
        # Count files
        comprehensive_files = glob.glob(os.path.join(results_dir, 'comprehensive', '*.json'))
        quick_files = glob.glob(os.path.join(results_dir, 'quick_validation', '*.json'))
        report_files = glob.glob(os.path.join(results_dir, 'reports', '*'))
        
        # Calculate directory sizes
        total_size = _calculate_directory_size(results_dir)
        
        # Get latest results summary
        latest_comprehensive = _get_latest_file_summary(comprehensive_files, 'comprehensive')
        latest_quick = _get_latest_file_summary(quick_files, 'quick')
        
        # Calculate trends if enough data
        trends = _calculate_trends(comprehensive_files)
        
        summary = {
            'file_counts': {
                'comprehensive_tests': len(comprehensive_files),
                'quick_validations': len(quick_files),
                'reports': len(report_files),
                'total_files': len(comprehensive_files) + len(quick_files) + len(report_files)
            },
            'storage': {
                'total_size_mb': round(total_size / (1024**2), 2),
                'results_directory': os.path.abspath(results_dir)
            },
            'latest_results': {
                'comprehensive': latest_comprehensive,
                'quick_validation': latest_quick
            },
            'trends': trends,
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate summary',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@results_bp.route('/download/<filename>')
def download_results_file(filename):
    """
    Download a specific results file
    
    Args:
        filename: Name of the file to download
        
    Returns:
        File download response
    """
    try:
        results_dir = current_app.config.get('RESULTS_DIR', 'results')
        
        # Security check - only allow files in results directory
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({
                'error': 'Invalid filename',
                'message': 'Filename contains invalid characters'
            }), 400
        
        # Look for file in different subdirectories
        possible_paths = [
            os.path.join(results_dir, 'comprehensive', filename),
            os.path.join(results_dir, 'quick_validation', filename),
            os.path.join(results_dir, 'reports', filename),
            os.path.join(results_dir, filename)
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            return jsonify({
                'error': 'File not found',
                'message': f'File {filename} not found in results directory',
                'searched_locations': [os.path.dirname(p) for p in possible_paths]
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json' if filename.endswith('.json') else None
        )
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to download file',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@results_bp.route('/files')
def list_results_files():
    """
    List all available results files
    
    Query parameters:
        - type: File type filter (comprehensive, quick, reports, all)
        - format: Response format (simple, detailed)
        
    Returns:
        JSON response with file list
    """
    try:
        results_dir = current_app.config.get('RESULTS_DIR', 'results')
        file_type = request.args.get('type', 'all')
        response_format = request.args.get('format', 'simple')
        
        files_info = {}
        
        # Get comprehensive test files
        if file_type in ['comprehensive', 'all']:
            comprehensive_files = glob.glob(os.path.join(results_dir, 'comprehensive', '*.json'))
            files_info['comprehensive'] = _process_file_list(comprehensive_files, response_format)
        
        # Get quick validation files
        if file_type in ['quick', 'all']:
            quick_files = glob.glob(os.path.join(results_dir, 'quick_validation', '*.json'))
            files_info['quick_validation'] = _process_file_list(quick_files, response_format)
        
        # Get report files
        if file_type in ['reports', 'all']:
            report_files = glob.glob(os.path.join(results_dir, 'reports', '*'))
            files_info['reports'] = _process_file_list(report_files, response_format)
        
        # Calculate totals
        total_files = sum(len(files) for files in files_info.values())
        
        return jsonify({
            'success': True,
            'query_parameters': {
                'type': file_type,
                'format': response_format
            },
            'total_files': total_files,
            'files': files_info,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to list files',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@results_bp.route('/analyze/<filename>')
def analyze_results_file(filename):
    """
    Analyze a specific results file and return detailed insights
    
    Args:
        filename: Name of the results file to analyze
        
    Returns:
        JSON response with analysis results
    """
    try:
        results_dir = current_app.config.get('RESULTS_DIR', 'results')
        
        # Find the file
        file_path = None
        for subdir in ['comprehensive', 'quick_validation']:
            potential_path = os.path.join(results_dir, subdir, filename)
            if os.path.exists(potential_path):
                file_path = potential_path
                break
        
        if not file_path:
            return jsonify({
                'error': 'File not found',
                'message': f'Results file {filename} not found'
            }), 404
        
        # Load and analyze the results
        with open(file_path, 'r') as f:
            results = json.load(f)
        
        # Generate analysis
        analysis = _analyze_results_file(results, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'file_path': file_path,
            'analysis': analysis,
            'analyzed_at': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError as e:
        return jsonify({
            'error': 'Invalid JSON file',
            'message': f'File contains invalid JSON: {e}'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze file',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@results_bp.route('/compare')
def compare_results():
    """
    Compare multiple test results
    
    Query parameters:
        - files: Comma-separated list of filenames to compare
        - metric: Metric to compare (pass_rate, response_time, goal_achievement)
        
    Returns:
        JSON response with comparison results
    """
    try:
        files_param = request.args.get('files', '')
        metric = request.args.get('metric', 'pass_rate')
        
        if not files_param:
            return jsonify({
                'error': 'No files specified',
                'message': 'Provide comma-separated filenames in the files parameter'
            }), 400
        
        filenames = [f.strip() for f in files_param.split(',')]
        results_dir = current_app.config.get('RESULTS_DIR', 'results')
        
        comparison_data = []
        
        for filename in filenames:
            # Find and load the file
            file_data = _load_results_file(results_dir, filename)
            if file_data:
                comparison_data.append(file_data)
        
        if len(comparison_data) < 2:
            return jsonify({
                'error': 'Insufficient data',
                'message': 'At least 2 valid files are required for comparison',
                'found_files': len(comparison_data)
            }), 400
        
        # Generate comparison
        comparison = _generate_comparison(comparison_data, metric)
        
        return jsonify({
            'success': True,
            'comparison_metric': metric,
            'files_compared': len(comparison_data),
            'comparison': comparison,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to compare results',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def _get_file_info(file_path: str, test_type: str, cutoff_date: datetime) -> Dict[str, Any]:
    """Get information about a results file"""
    try:
        # Extract timestamp from filename
        filename = os.path.basename(file_path)
        
        if test_type == 'comprehensive' and 'comprehensive_test_results_' in filename:
            timestamp_str = filename.replace('comprehensive_test_results_', '').replace('.json', '')
        elif test_type == 'quick' and 'quick_validation_' in filename:
            timestamp_str = filename.replace('quick_validation_', '').replace('.json', '')
        else:
            return None
        
        try:
            file_timestamp = datetime.fromtimestamp(int(timestamp_str))
        except ValueError:
            return None
        
        # Check if file is within date range
        if file_timestamp < cutoff_date:
            return None
        
        # Load basic file info
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract summary information
        if test_type == 'comprehensive':
            overall = data.get('overall_results', {})
            goals = data.get('goal_achievement', {}).get('summary', {})
            
            return {
                'filename': filename,
                'timestamp': file_timestamp.isoformat(),
                'type': 'comprehensive',
                'summary': {
                    'total_tests': overall.get('total_tests'),
                    'pass_rate': overall.get('overall_pass_rate'),
                    'goal_achievement_rate': goals.get('achievement_rate'),
                    'avg_response_time': overall.get('avg_response_time'),
                    'execution_time': data.get('test_metadata', {}).get('total_execution_time_seconds')
                }
            }
        else:  # quick validation
            return {
                'filename': filename,
                'timestamp': file_timestamp.isoformat(),
                'type': 'quick_validation',
                'summary': {
                    'total_tests': data.get('total_tests'),
                    'pass_rate': data.get('pass_rate'),
                    'avg_response_time': data.get('avg_response_time_ms')
                }
            }
        
    except Exception:
        return None


def _calculate_directory_size(directory: str) -> int:
    """Calculate total size of directory"""
    total_size = 0
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception:
        pass
    return total_size


def _get_latest_file_summary(files: List[str], test_type: str) -> Dict[str, Any]:
    """Get summary of the latest file"""
    if not files:
        return None
    
    try:
        # Sort files and get latest
        files.sort(reverse=True)
        latest_file = files[0]
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        filename = os.path.basename(latest_file)
        
        if test_type == 'comprehensive':
            overall = data.get('overall_results', {})
            return {
                'filename': filename,
                'timestamp': data.get('timestamp'),
                'total_tests': overall.get('total_tests'),
                'pass_rate': overall.get('overall_pass_rate'),
                'avg_response_time': overall.get('avg_response_time')
            }
        else:  # quick
            return {
                'filename': filename,
                'timestamp': data.get('timestamp'),
                'total_tests': data.get('total_tests'),
                'pass_rate': data.get('pass_rate'),
                'avg_response_time': data.get('avg_response_time_ms')
            }
            
    except Exception:
        return None


def _calculate_trends(files: List[str]) -> Dict[str, Any]:
    """Calculate performance trends from historical data"""
    if len(files) < 2:
        return {'insufficient_data': True}
    
    try:
        # Sort files chronologically
        files.sort()
        
        # Take last 5 files for trend calculation
        recent_files = files[-5:]
        trend_data = []
        
        for file_path in recent_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                overall = data.get('overall_results', {})
                goals = data.get('goal_achievement', {}).get('summary', {})
                
                trend_data.append({
                    'timestamp': data.get('timestamp'),
                    'pass_rate': overall.get('overall_pass_rate', 0),
                    'goal_achievement': goals.get('achievement_rate', 0),
                    'response_time': overall.get('avg_response_time', 0)
                })
            except Exception:
                continue
        
        if len(trend_data) < 2:
            return {'insufficient_data': True}
        
        # Calculate trends
        first = trend_data[0]
        last = trend_data[-1]
        
        return {
            'data_points': len(trend_data),
            'timespan': {
                'from': first['timestamp'],
                'to': last['timestamp']
            },
            'trends': {
                'pass_rate': {
                    'change': last['pass_rate'] - first['pass_rate'],
                    'direction': 'improving' if last['pass_rate'] > first['pass_rate'] else 'declining' if last['pass_rate'] < first['pass_rate'] else 'stable'
                },
                'goal_achievement': {
                    'change': last['goal_achievement'] - first['goal_achievement'],
                    'direction': 'improving' if last['goal_achievement'] > first['goal_achievement'] else 'declining' if last['goal_achievement'] < first['goal_achievement'] else 'stable'
                },
                'response_time': {
                    'change': last['response_time'] - first['response_time'],
                    'direction': 'improving' if last['response_time'] < first['response_time'] else 'declining' if last['response_time'] > first['response_time'] else 'stable'
                }
            }
        }
        
    except Exception:
        return {'error': 'Failed to calculate trends'}


def _process_file_list(files: List[str], response_format: str) -> List[Dict[str, Any]]:
    """Process list of files based on response format"""
    processed_files = []
    
    for file_path in files:
        filename = os.path.basename(file_path)
        
        if response_format == 'simple':
            processed_files.append({
                'filename': filename,
                'size_kb': round(os.path.getsize(file_path) / 1024, 2) if os.path.exists(file_path) else 0
            })
        else:  # detailed
            try:
                stat = os.stat(file_path)
                processed_files.append({
                    'filename': filename,
                    'size_kb': round(stat.st_size / 1024, 2),
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception:
                processed_files.append({
                    'filename': filename,
                    'error': 'Unable to get file details'
                })
    
    # Sort by filename (reverse chronological)
    processed_files.sort(key=lambda x: x['filename'], reverse=True)
    return processed_files


def _analyze_results_file(results: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """Analyze a results file and provide insights"""
    analysis = {
        'file_type': 'comprehensive' if 'overall_results' in results else 'quick_validation',
        'test_metadata': results.get('test_metadata', {}),
        'performance_analysis': {},
        'issues_found': [],
        'recommendations': []
    }
    
    if analysis['file_type'] == 'comprehensive':
        overall = results.get('overall_results', {})
        goals = results.get('goal_achievement', {})
        categories = results.get('category_results', {})
        
        # Performance analysis
        analysis['performance_analysis'] = {
            'overall_pass_rate': overall.get('overall_pass_rate', 0),
            'goal_achievement_rate': goals.get('summary', {}).get('achievement_rate', 0),
            'avg_response_time': overall.get('avg_response_time', 0),
            'total_tests': overall.get('total_tests', 0),
            'error_rate': (overall.get('total_errors', 0) / overall.get('total_tests', 1)) * 100
        }
        
        # Identify issues
        if overall.get('overall_pass_rate', 0) < 80:
            analysis['issues_found'].append('Overall pass rate below 80%')
        
        if goals.get('summary', {}).get('achievement_rate', 0) < 70:
            analysis['issues_found'].append('Goal achievement rate below 70%')
        
        if overall.get('avg_response_time', 0) > 200:
            analysis['issues_found'].append('Average response time exceeds 200ms')
        
        # Check critical categories
        high_priority = categories.get('definite_high', {})
        if high_priority.get('pass_rate', 100) < 100:
            analysis['issues_found'].append(f"High priority detection at {high_priority.get('pass_rate', 0):.1f}% (critical)")
        
        none_priority = categories.get('definite_none', {})
        false_positive_rate = 100 - none_priority.get('pass_rate', 100)
        if false_positive_rate > 10:
            analysis['issues_found'].append(f"False positive rate at {false_positive_rate:.1f}%")
        
        # Generate recommendations
        if analysis['issues_found']:
            if 'High priority detection' in str(analysis['issues_found']):
                analysis['recommendations'].append('Immediately review high priority detection failures')
            if 'response time' in str(analysis['issues_found']):
                analysis['recommendations'].append('Consider performance optimization')
            if 'False positive' in str(analysis['issues_found']):
                analysis['recommendations'].append('Tune detection sensitivity to reduce false positives')
        else:
            analysis['recommendations'].append('System performing within acceptable parameters')
    
    else:  # quick validation
        analysis['performance_analysis'] = {
            'pass_rate': results.get('pass_rate', 0),
            'total_tests': results.get('total_tests', 0),
            'avg_response_time': results.get('avg_response_time_ms', 0)
        }
        
        if results.get('pass_rate', 0) < 80:
            analysis['issues_found'].append('Quick validation pass rate below 80%')
            analysis['recommendations'].append('Run comprehensive test to identify issues')
    
    return analysis


def _load_results_file(results_dir: str, filename: str) -> Dict[str, Any]:
    """Load a results file and extract basic info"""
    try:
        # Find the file
        for subdir in ['comprehensive', 'quick_validation']:
            file_path = os.path.join(results_dir, subdir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                return {
                    'filename': filename,
                    'type': subdir,
                    'data': data
                }
        return None
    except Exception:
        return None


def _generate_comparison(comparison_data: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
    """Generate comparison between multiple results"""
    comparison = {
        'metric': metric,
        'files': [],
        'summary': {}
    }
    
    values = []
    
    for file_data in comparison_data:
        filename = file_data['filename']
        data = file_data['data']
        file_type = file_data['type']
        
        # Extract metric value based on file type and metric
        if file_type == 'comprehensive':
            if metric == 'pass_rate':
                value = data.get('overall_results', {}).get('overall_pass_rate', 0)
            elif metric == 'response_time':
                value = data.get('overall_results', {}).get('avg_response_time', 0)
            elif metric == 'goal_achievement':
                value = data.get('goal_achievement', {}).get('summary', {}).get('achievement_rate', 0)
            else:
                value = 0
        else:  # quick validation
            if metric == 'pass_rate':
                value = data.get('pass_rate', 0)
            elif metric == 'response_time':
                value = data.get('avg_response_time_ms', 0)
            else:
                value = 0
        
        comparison['files'].append({
            'filename': filename,
            'type': file_type,
            'timestamp': data.get('timestamp'),
            'metric_value': value
        })
        values.append(value)
    
    # Calculate summary statistics
    if values:
        comparison['summary'] = {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'range': max(values) - min(values),
            'best_file': comparison['files'][values.index(max(values) if metric != 'response_time' else min(values))]['filename'],
            'worst_file': comparison['files'][values.index(min(values) if metric != 'response_time' else max(values))]['filename']
        }
    
    return comparison