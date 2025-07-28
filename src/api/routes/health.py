"""
Health check routes for Ash-Thrash API

Provides health check endpoints for monitoring service status
and dependencies.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import requests
import os
import psutil
import sys

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """
    Main health check endpoint
    
    Returns:
        JSON response with service health status
    """
    try:
        # Basic service health
        health_data = {
            'service': 'ash-thrash-api',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'uptime': _get_uptime(),
            'dependencies': _check_dependencies(),
            'system': _get_system_info()
        }
        
        # Check if any dependencies are unhealthy
        unhealthy_deps = [dep for dep, info in health_data['dependencies'].items() 
                         if info.get('status') != 'healthy']
        
        if unhealthy_deps:
            health_data['status'] = 'degraded'
            health_data['issues'] = unhealthy_deps
        
        status_code = 200 if health_data['status'] in ['healthy', 'degraded'] else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        return jsonify({
            'service': 'ash-thrash-api',
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503


@health_bp.route('/health/detailed')
def detailed_health_check():
    """
    Detailed health check with comprehensive system information
    
    Returns:
        JSON response with detailed health information
    """
    try:
        detailed_data = {
            'service': 'ash-thrash-api',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'uptime': _get_uptime(),
            'dependencies': _check_dependencies(),
            'system': _get_detailed_system_info(),
            'configuration': _get_configuration_info(),
            'storage': _check_storage_health(),
            'performance': _get_performance_metrics()
        }
        
        # Overall health assessment
        health_issues = []
        
        # Check dependencies
        for dep, info in detailed_data['dependencies'].items():
            if info.get('status') != 'healthy':
                health_issues.append(f"Dependency {dep} is {info.get('status', 'unknown')}")
        
        # Check system resources
        system = detailed_data['system']
        if system.get('cpu_percent', 0) > 90:
            health_issues.append("High CPU usage")
        if system.get('memory_percent', 0) > 90:
            health_issues.append("High memory usage")
        if system.get('disk_percent', 0) > 90:
            health_issues.append("High disk usage")
        
        # Set overall status
        if health_issues:
            detailed_data['status'] = 'degraded' if len(health_issues) < 3 else 'unhealthy'
            detailed_data['issues'] = health_issues
        
        status_code = 200 if detailed_data['status'] in ['healthy', 'degraded'] else 503
        return jsonify(detailed_data), status_code
        
    except Exception as e:
        return jsonify({
            'service': 'ash-thrash-api',
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503


@health_bp.route('/health/dependencies')
def dependencies_check():
    """
    Check health of external dependencies
    
    Returns:
        JSON response with dependency health status
    """
    dependencies = _check_dependencies()
    
    all_healthy = all(dep.get('status') == 'healthy' for dep in dependencies.values())
    overall_status = 'healthy' if all_healthy else 'degraded'
    
    return jsonify({
        'overall_status': overall_status,
        'dependencies': dependencies,
        'timestamp': datetime.now().isoformat()
    })


def _get_uptime():
    """Get service uptime information"""
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return {
            'seconds': int(uptime_seconds),
            'human_readable': f"{days}d {hours}h {minutes}m"
        }
    except Exception:
        return {'error': 'Unable to determine uptime'}


def _check_dependencies():
    """Check health of external dependencies"""
    dependencies = {}
    
    # NLP Server check
    nlp_url = current_app.config.get('GLOBAL_NLP_API_URL', 'http://10.20.30.253:8881')
    dependencies['nlp_server'] = _check_nlp_server(nlp_url)
    
    # Results directory check
    results_dir = current_app.config.get('RESULTS_DIR', 'results')
    dependencies['results_storage'] = _check_storage(results_dir)
    
    return dependencies


def _check_nlp_server(base_url):
    """Check NLP server health"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            return {
                'status': 'healthy',
                'url': base_url,
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'last_checked': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'unhealthy',
                'url': base_url,
                'error': f"HTTP {response.status_code}",
                'last_checked': datetime.now().isoformat()
            }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'unreachable',
            'url': base_url,
            'error': 'Connection failed',
            'last_checked': datetime.now().isoformat()
        }
    except requests.exceptions.Timeout:
        return {
            'status': 'timeout',
            'url': base_url,
            'error': 'Request timeout',
            'last_checked': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'url': base_url,
            'error': str(e),
            'last_checked': datetime.now().isoformat()
        }


def _check_storage(directory):
    """Check storage accessibility and space"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Check if directory is writable
        test_file = os.path.join(directory, '.health_check')
        with open(test_file, 'w') as f:
            f.write('health_check')
        os.remove(test_file)
        
        # Get disk usage
        disk_usage = psutil.disk_usage(directory)
        free_gb = disk_usage.free / (1024**3)
        
        return {
            'status': 'healthy',
            'path': os.path.abspath(directory),
            'writable': True,
            'free_space_gb': round(free_gb, 2),
            'last_checked': datetime.now().isoformat()
        }
        
    except PermissionError:
        return {
            'status': 'unhealthy',
            'path': os.path.abspath(directory),
            'error': 'Permission denied',
            'last_checked': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'path': os.path.abspath(directory),
            'error': str(e),
            'last_checked': datetime.now().isoformat()
        }


def _get_system_info():
    """Get basic system information"""
    try:
        return {
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    except Exception as e:
        return {'error': f'Unable to get system info: {e}'}


def _get_detailed_system_info():
    """Get detailed system information"""
    try:
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu': {
                'count': psutil.cpu_count(logical=True),
                'physical_count': psutil.cpu_count(logical=False),
                'percent': psutil.cpu_percent(interval=1),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total_gb': round(vm.total / (1024**3), 2),
                'available_gb': round(vm.available / (1024**3), 2),
                'used_gb': round(vm.used / (1024**3), 2),
                'percent': vm.percent
            },
            'disk': {
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'percent': round((disk.used / disk.total) * 100, 2)
            },
            'network': _get_network_info()
        }
    except Exception as e:
        return {'error': f'Unable to get detailed system info: {e}'}


def _get_network_info():
    """Get network interface information"""
    try:
        network_info = {}
        for interface, addresses in psutil.net_if_addrs().items():
            network_info[interface] = []
            for addr in addresses:
                if addr.family.name in ['AF_INET', 'AF_INET6']:
                    network_info[interface].append({
                        'family': addr.family.name,
                        'address': addr.address,
                        'netmask': addr.netmask
                    })
        return network_info
    except Exception:
        return {}


def _get_configuration_info():
    """Get current configuration information"""
    return {
        'GLOBAL_NLP_API_URL': current_app.config.get('GLOBAL_NLP_API_URL'),
        'results_dir': current_app.config.get('RESULTS_DIR'),
        'max_workers': current_app.config.get('MAX_WORKERS'),
        'testing_timeout': current_app.config.get('TESTING_TIMEOUT'),
        'debug_mode': current_app.config.get('DEBUG'),
        'host': current_app.config.get('HOST'),
        'port': current_app.config.get('PORT')
    }


def _check_storage_health():
    """Check storage health and capacity"""
    results_dir = current_app.config.get('RESULTS_DIR', 'results')
    
    try:
        # Count result files
        comprehensive_files = len(glob.glob(os.path.join(results_dir, 'comprehensive', '*.json')))
        quick_files = len(glob.glob(os.path.join(results_dir, 'quick_validation', '*.json')))
        report_files = len(glob.glob(os.path.join(results_dir, 'reports', '*')))
        
        # Calculate directory sizes
        total_size = 0
        for root, dirs, files in os.walk(results_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        
        return {
            'status': 'healthy',
            'file_counts': {
                'comprehensive_results': comprehensive_files,
                'quick_validation_results': quick_files,
                'reports': report_files,
                'total': comprehensive_files + quick_files + report_files
            },
            'total_size_mb': round(total_size / (1024**2), 2),
            'directory': os.path.abspath(results_dir)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'directory': os.path.abspath(results_dir)
        }


def _get_performance_metrics():
    """Get current performance metrics"""
    try:
        return {
            'cpu_times': psutil.cpu_times()._asdict(),
            'memory_info': psutil.virtual_memory()._asdict(),
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None,
            'process_count': len(psutil.pids()),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
    except Exception as e:
        return {'error': f'Unable to get performance metrics: {e}'}