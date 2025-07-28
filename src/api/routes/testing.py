"""
Testing operation routes for Ash-Thrash API

Provides endpoints for triggering tests, checking test status,
and managing testing operations.
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import threading
import subprocess
import os
import json
import time
import glob

testing_bp = Blueprint('testing', __name__)

# Global variables to track running tests
_running_tests = {}
_test_lock = threading.Lock()


@testing_bp.route('/status')
def get_testing_status():
    """
    Get current testing status and latest results summary
    
    Returns:
        JSON response with testing status
    """
    try:
        results_dir = current_app.config.get('RESULTS_DIR', 'results')
        
        # Check for running tests
        with _test_lock:
            currently_running = list(_running_tests.keys())
        
        # Find latest results
        latest_results = _get_latest_results(results_dir)
        
        # Get test history summary
        history_summary = _get_test_history_summary(results_dir)
        
        status_data = {
            'service': 'ash-thrash-testing',
            'timestamp': datetime.now().isoformat(),
            'currently_running': currently_running,
            'latest_results': latest_results,
            'history_summary': history_summary,
            'configuration': {
                'GLOBAL_NLP_API_URL': current_app.config.get('GLOBAL_NLP_API_URL'),
                'max_workers': current_app.config.get('MAX_WORKERS'),
                'testing_timeout': current_app.config.get('TESTING_TIMEOUT')
            }
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get testing status',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@testing_bp.route('/run', methods=['POST'])
def run_comprehensive_test():
    """
    Trigger a comprehensive test run
    
    Returns:
        JSON response with test execution status
    """
    try:
        test_id = f"comprehensive_{int(time.time())}"
        
        # Check if test is already running
        with _test_lock:
            if any('comprehensive' in tid for tid in _running_tests):
                return jsonify({
                    'error': 'Test already running',
                    'message': 'A comprehensive test is already in progress',
                    'running_tests': list(_running_tests.keys())
                }), 409
        
        # Get request parameters
        data = request.get_json() or {}
        priority = data.get('priority', 'normal')
        notify_webhook = data.get('notify_webhook', None)
        
        # Start test in background
        test_thread = threading.Thread(
            target=_run_comprehensive_test_background,
            args=(test_id, priority, notify_webhook)
        )
        test_thread.daemon = True
        test_thread.start()
        
        # Track running test
        with _test_lock:
            _running_tests[test_id] = {
                'type': 'comprehensive',
                'started': datetime.now().isoformat(),
                'priority': priority,
                'status': 'starting'
            }
        
        return jsonify({
            'success': True,
            'test_id': test_id,
            'message': 'Comprehensive test started',
            'started_at': datetime.now().isoformat(),
            'estimated_duration': '2-5 minutes',
            'status_endpoint': f'/api/test/status/{test_id}'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to start test',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@testing_bp.route('/quick', methods=['POST'])
def run_quick_test():
    """
    Run a quick validation test (10 phrases)
    
    Returns:
        JSON response with test results
    """
    try:
        test_id = f"quick_{int(time.time())}"
        
        # Check if too many tests are running
        with _test_lock:
            if len(_running_tests) >= 3:
                return jsonify({
                    'error': 'Too many tests running',
                    'message': 'Maximum concurrent tests reached',
                    'running_tests': list(_running_tests.keys())
                }), 429
        
        # Start quick test in background
        test_thread = threading.Thread(
            target=_run_quick_test_background,
            args=(test_id,)
        )
        test_thread.daemon = True
        test_thread.start()
        
        # Track running test
        with _test_lock:
            _running_tests[test_id] = {
                'type': 'quick',
                'started': datetime.now().isoformat(),
                'status': 'running'
            }
        
        return jsonify({
            'success': True,
            'test_id': test_id,
            'message': 'Quick validation test started',
            'started_at': datetime.now().isoformat(),
            'estimated_duration': '30-60 seconds',
            'status_endpoint': f'/api/test/status/{test_id}'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to start quick test',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@testing_bp.route('/status/<test_id>')
def get_test_status(test_id):
    """
    Get status of a specific test
    
    Args:
        test_id: Test identifier
        
    Returns:
        JSON response with test status
    """
    with _test_lock:
        if test_id in _running_tests:
            test_info = _running_tests[test_id].copy()
            test_info['test_id'] = test_id
            test_info['current_status'] = 'running'
            return jsonify(test_info)
    
    # Check if test completed (look for results file)
    results_dir = current_app.config.get('RESULTS_DIR', 'results')
    
    # Look for comprehensive test results
    if test_id.startswith('comprehensive'):
        pattern = os.path.join(results_dir, 'comprehensive', f'*{test_id.split("_")[1]}*.json')
        result_files = glob.glob(pattern)
        
        if result_files:
            try:
                with open(result_files[0], 'r') as f:
                    results = json.load(f)
                
                return jsonify({
                    'test_id': test_id,
                    'current_status': 'completed',
                    'completed_at': results.get('timestamp'),
                    'results_summary': {
                        'pass_rate': results.get('overall_results', {}).get('overall_pass_rate'),
                        'total_tests': results.get('overall_results', {}).get('total_tests'),
                        'goal_achievement': results.get('goal_achievement', {}).get('summary', {}).get('achievement_rate')
                    },
                    'results_file': os.path.basename(result_files[0])
                })
            except Exception as e:
                return jsonify({
                    'test_id': test_id,
                    'current_status': 'error',
                    'error': f'Failed to read results: {e}'
                })
    
    # Look for quick test results
    elif test_id.startswith('quick'):
        pattern = os.path.join(results_dir, 'quick_validation', f'*{test_id.split("_")[1]}*.json')
        result_files = glob.glob(pattern)
        
        if result_files:
            try:
                with open(result_files[0], 'r') as f:
                    results = json.load(f)
                
                return jsonify({
                    'test_id': test_id,
                    'current_status': 'completed',
                    'completed_at': results.get('timestamp'),
                    'results_summary': {
                        'pass_rate': results.get('pass_rate'),
                        'total_tests': results.get('total_tests'),
                        'avg_response_time': results.get('avg_response_time_ms')
                    },
                    'results_file': os.path.basename(result_files[0])
                })
            except Exception as e:
                return jsonify({
                    'test_id': test_id,
                    'current_status': 'error',
                    'error': f'Failed to read results: {e}'
                })
    
    # Test not found
    return jsonify({
        'test_id': test_id,
        'current_status': 'not_found',
        'message': 'Test not found or results not available'
    }), 404


@testing_bp.route('/running')
def get_running_tests():
    """
    Get list of currently running tests
    
    Returns:
        JSON response with running tests
    """
    with _test_lock:
        running_tests = _running_tests.copy()
    
    return jsonify({
        'running_tests': running_tests,
        'count': len(running_tests),
        'timestamp': datetime.now().isoformat()
    })


@testing_bp.route('/cancel/<test_id>', methods=['POST'])
def cancel_test(test_id):
    """
    Cancel a running test (if possible)
    
    Args:
        test_id: Test identifier
        
    Returns:
        JSON response with cancellation status
    """
    with _test_lock:
        if test_id in _running_tests:
            # Mark as cancelled (the background thread should check this)
            _running_tests[test_id]['status'] = 'cancelled'
            _running_tests[test_id]['cancelled_at'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'message': f'Test {test_id} marked for cancellation',
                'test_id': test_id
            })
    
    return jsonify({
        'error': 'Test not found',
        'message': f'Test {test_id} is not currently running',
        'test_id': test_id
    }), 404


def _run_comprehensive_test_background(test_id, priority, notify_webhook):
    """Run comprehensive test in background thread"""
    try:
        with _test_lock:
            if test_id in _running_tests:
                _running_tests[test_id]['status'] = 'running'
        
        # Run the comprehensive testing script
        script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'comprehensive_testing.py')
        
        result = subprocess.run([
            'python', script_path
        ], capture_output=True, text=True, timeout=current_app.config.get('TESTING_TIMEOUT', 300))
        
        with _test_lock:
            if test_id in _running_tests:
                if result.returncode == 0:
                    _running_tests[test_id]['status'] = 'completed'
                    _running_tests[test_id]['completed_at'] = datetime.now().isoformat()
                else:
                    _running_tests[test_id]['status'] = 'failed'
                    _running_tests[test_id]['error'] = result.stderr
                    _running_tests[test_id]['failed_at'] = datetime.now().isoformat()
        
        # Send webhook notification if provided
        if notify_webhook and result.returncode == 0:
            _send_webhook_notification(notify_webhook, test_id, 'comprehensive', True)
        
    except subprocess.TimeoutExpired:
        with _test_lock:
            if test_id in _running_tests:
                _running_tests[test_id]['status'] = 'timeout'
                _running_tests[test_id]['error'] = 'Test execution timed out'
                _running_tests[test_id]['failed_at'] = datetime.now().isoformat()
    
    except Exception as e:
        with _test_lock:
            if test_id in _running_tests:
                _running_tests[test_id]['status'] = 'error'
                _running_tests[test_id]['error'] = str(e)
                _running_tests[test_id]['failed_at'] = datetime.now().isoformat()
    
    finally:
        # Clean up after 1 hour
        def cleanup():
            time.sleep(3600)  # 1 hour
            with _test_lock:
                _running_tests.pop(test_id, None)
        
        cleanup_thread = threading.Thread(target=cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()


def _run_quick_test_background(test_id):
    """Run quick test in background thread"""
    try:
        with _test_lock:
            if test_id in _running_tests:
                _running_tests[test_id]['status'] = 'running'
        
        # Run the quick validation script
        script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'quick_validation.py')
        
        result = subprocess.run([
            'python', script_path
        ], capture_output=True, text=True, timeout=60)
        
        with _test_lock:
            if test_id in _running_tests:
                if result.returncode == 0:
                    _running_tests[test_id]['status'] = 'completed'
                    _running_tests[test_id]['completed_at'] = datetime.now().isoformat()
                else:
                    _running_tests[test_id]['status'] = 'failed'
                    _running_tests[test_id]['error'] = result.stderr
                    _running_tests[test_id]['failed_at'] = datetime.now().isoformat()
    
    except Exception as e:
        with _test_lock:
            if test_id in _running_tests:
                _running_tests[test_id]['status'] = 'error'
                _running_tests[test_id]['error'] = str(e)
                _running_tests[test_id]['failed_at'] = datetime.now().isoformat()
    
    finally:
        # Clean up after 10 minutes
        def cleanup():
            time.sleep(600)  # 10 minutes
            with _test_lock:
                _running_tests.pop(test_id, None)
        
        cleanup_thread = threading.Thread(target=cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()


def _get_latest_results(results_dir):
    """Get summary of latest test results"""
    try:
        # Find latest comprehensive results
        comprehensive_files = glob.glob(os.path.join(results_dir, 'comprehensive', '*.json'))
        comprehensive_files.sort(reverse=True)
        
        if comprehensive_files:
            with open(comprehensive_files[0], 'r') as f:
                latest = json.load(f)
            
            return {
                'type': 'comprehensive',
                'timestamp': latest.get('timestamp'),
                'filename': os.path.basename(comprehensive_files[0]),
                'summary': {
                    'pass_rate': latest.get('overall_results', {}).get('overall_pass_rate'),
                    'total_tests': latest.get('overall_results', {}).get('total_tests'),
                    'goal_achievement': latest.get('goal_achievement', {}).get('summary', {}).get('achievement_rate'),
                    'avg_response_time': latest.get('overall_results', {}).get('avg_response_time')
                }
            }
        
        return None
        
    except Exception:
        return None


def _get_test_history_summary(results_dir):
    """Get summary of test history"""
    try:
        comprehensive_files = glob.glob(os.path.join(results_dir, 'comprehensive', '*.json'))
        quick_files = glob.glob(os.path.join(results_dir, 'quick_validation', '*.json'))
        
        return {
            'comprehensive_tests': len(comprehensive_files),
            'quick_tests': len(quick_files),
            'total_tests': len(comprehensive_files) + len(quick_files),
            'last_comprehensive': _get_file_timestamp(comprehensive_files[0]) if comprehensive_files else None,
            'last_quick': _get_file_timestamp(quick_files[0]) if quick_files else None
        }
        
    except Exception:
        return {'error': 'Unable to get test history'}


def _get_file_timestamp(filepath):
    """Extract timestamp from result filename"""
    try:
        basename = os.path.basename(filepath)
        if 'comprehensive_test_results_' in basename:
            timestamp_str = basename.replace('comprehensive_test_results_', '').replace('.json', '')
            return datetime.fromtimestamp(int(timestamp_str)).isoformat()
        elif 'quick_validation_' in basename:
            timestamp_str = basename.replace('quick_validation_', '').replace('.json', '')
            return datetime.fromtimestamp(int(timestamp_str)).isoformat()
    except Exception:
        pass
    return None


def _send_webhook_notification(webhook_url, test_id, test_type, success):
    """Send webhook notification for test completion"""
    try:
        import requests
        
        payload = {
            'test_id': test_id,
            'test_type': test_type,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'service': 'ash-thrash'
        }
        
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception:
        pass  # Silently ignore webhook failures