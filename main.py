#!/usr/bin/env python3
"""
Ash-Thrash Management Scripts v3.0
Standard Python-based management and deployment utilities

Repository: https://github.com/the-alphabet-cartel/ash-thrash
Discord: https://discord.gg/alphabetcartel
Website: http://alphabetcartel.org

Usage:
    python manage.py setup        # Initial setup and validation
    python manage.py start        # Start services with Docker Compose  
    python manage.py test-all     # Run comprehensive tests
    python manage.py status       # Check service status
    python manage.py logs         # View service logs
    python manage.py stop         # Stop all services
"""

import os
import sys
import subprocess
import json
import time
import argparse
from pathlib import Path
from typing import Optional

# Project configuration
PROJECT_NAME = "ash-thrash"
COMPOSE_FILE = "docker-compose.yml"
ENV_FILE = ".env"
ENV_TEMPLATE = "config/.env.template"

def print_header(title: str, width: int = 40):
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
# COMMAND FUNCTIONS
# =============================================================================

def setup_command(args):
    """Initial setup and configuration"""
    print("🔧 Setting up Ash-Thrash v3.0")
    print_header("Initial Setup")
    
    # 1. Check Docker and Docker Compose
    if not check_docker():
        sys.exit(1)
    
    # 2. Create environment file if it doesn't exist
    setup_environment()
    
    # 3. Create required directories
    create_directories()
    
    # 4. Validate configuration
    validate_configuration()
    
    print_success("Setup completed successfully!")
    print("\nNext steps:")
    print("  1. Review and update .env file with your settings")
    print("  2. Run 'python manage.py start' to start services")
    print("  3. Run 'python manage.py test-all' to run tests")

def start_command(args):
    """Start Ash-Thrash services"""
    print("🚀 Starting Ash-Thrash Services")
    print_header("Service Startup")
    
    # Build command
    cmd = ["docker-compose", "-f", COMPOSE_FILE]
    
    if args.build:
        print("🔨 Building images...")
        run_command(cmd + ["build"])
    
    # Start services
    start_cmd = cmd + ["up"]
    if args.detach:
        start_cmd.append("-d")
    
    print("🌟 Starting services...")
    run_command(start_cmd)
    
    if args.detach:
        # Wait a moment and check health
        time.sleep(5)
        check_services_health()

def stop_command(args):
    """Stop all services"""
    print("🛑 Stopping Ash-Thrash Services")
    print_header("Service Shutdown")
    
    run_command(["docker-compose", "-f", COMPOSE_FILE, "down"])
    print_success("All services stopped")

def logs_command(args):
    """View service logs"""
    cmd = ["docker-compose", "-f", COMPOSE_FILE, "logs"]
    
    if args.follow:
        cmd.append("-f")
    
    if args.service:
        cmd.append(args.service)
    
    run_command(cmd)

def status_command(args):
    """Check service status"""
    print("📊 Ash-Thrash Service Status")
    print_header("Service Status")
    
    # Check Docker Compose services
    try:
        result = subprocess.run(
            ["docker-compose", "-f", COMPOSE_FILE, "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        services = json.loads(result.stdout) if result.stdout.strip() else []
        
        if not services:
            print("🔍 No services running")
            return
        
        for service in services:
            name = service.get('Name', 'Unknown')
            state = service.get('State', 'Unknown')
            status_text = service.get('Status', '')
            
            if state == 'running':
                status_emoji = "✅"
            elif state == 'exited':
                status_emoji = "❌" if '(0)' not in status_text else "⏹️"
            else:
                status_emoji = "⚠️"
            
            print(f"{status_emoji} {name}: {state} {status_text}")
        
        # Check API health if running
        check_api_health()
        
    except subprocess.CalledProcessError:
        print_error("Error checking service status")
    except json.JSONDecodeError:
        print_warning("Could not parse service status")

def test_all_command(args):
    """Run tests using Docker Compose"""
    print(f"🧪 Running {args.test_type} tests")
    print_header("Test Execution")
    
    # Ensure services are running
    if not check_api_running():
        print_warning("API service not running, starting it...")
        run_command(["docker-compose", "-f", COMPOSE_FILE, "up", "-d", "ash-thrash-api"])
        time.sleep(10)  # Wait for startup
    
    # Run tests using CLI container
    cmd = [
        "docker-compose", "-f", COMPOSE_FILE, "run", "--rm",
        "ash-thrash-cli", "test", args.test_type
    ]
    
    run_command(cmd)

def cli_command(args):
    """Run CLI commands in container"""
    cmd = [
        "docker-compose", "-f", COMPOSE_FILE, "run", "--rm",
        "ash-thrash-cli"
    ] + args.command
    
    run_command(cmd)

def validate_command(args):
    """Validate configuration and setup"""
    print("🔍 Validating Ash-Thrash Configuration")
    print_header("Configuration Validation")
    
    issues = []
    
    # Check required files
    required_files = [
        COMPOSE_FILE,
        ENV_FILE,
        "src/ash_thrash_core.py",
        "src/ash_thrash_api.py",
        "src/test_data.py",
        "cli.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} missing")
            issues.append(f"Missing {file_path}")
    
    # Check Docker
    if not check_docker():
        issues.append("Docker not available")
    
    # Check environment variables
    env_vars = load_env_file()
    required_env_vars = ["GLOBAL_NLP_API_URL"]
    
    for var in required_env_vars:
        if var in env_vars:
            print_success(f"{var} configured")
        else:
            print_warning(f"{var} not configured (using default)")
    
    # Summary
    if not issues:
        print_success("All validation checks passed!")
    else:
        print_error(f"{len(issues)} issues found:")
        for issue in issues:
            print(f"  • {issue}")

def clean_command(args):
    """Clean up containers, images, and volumes"""
    print("🧹 Cleaning up Ash-Thrash resources")
    print_header("Resource Cleanup")
    
    if not args.force:
        response = input("This will remove containers, images, and volumes. Continue? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Cleanup cancelled")
            return
    
    # Stop services
    run_command(["docker-compose", "-f", COMPOSE_FILE, "down", "-v"])
    
    # Remove images
    try:
        run_command(["docker", "rmi", f"ghcr.io/the-alphabet-cartel/{PROJECT_NAME}:v3.0"])
    except subprocess.CalledProcessError:
        pass  # Image might not exist
    
    # Clean up build cache
    run_command(["docker", "system", "prune", "-f"])
    
    print_success("Cleanup completed")

def build_command(args):
    """Build Docker images"""
    print("🔨 Building Ash-Thrash Images")
    print_header("Image Build")
    
    run_command(["docker-compose", "-f", COMPOSE_FILE, "build"])
    print_success("Build completed")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def check_docker() -> bool:
    """Check if Docker and Docker Compose are available"""
    try:
        # Check Docker
        subprocess.run(["docker", "--version"], 
                      capture_output=True, check=True)
        print_success("Docker is available")
        
        # Check Docker Compose
        subprocess.run(["docker-compose", "--version"], 
                      capture_output=True, check=True)
        print_success("Docker Compose is available")
        
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Docker or Docker Compose not found")
        print("Please install Docker and Docker Compose:")
        print("  https://docs.docker.com/get-docker/")
        return False

def setup_environment():
    """Setup environment file from template"""
    env_path = Path(ENV_FILE)
    template_path = Path(ENV_TEMPLATE)
    
    if env_path.exists():
        print_success(f"Environment file exists: {ENV_FILE}")
        return
    
    if template_path.exists():
        # Copy template to .env
        import shutil
        shutil.copy(template_path, env_path)
        print_success(f"Created {ENV_FILE} from template")
        print_warning("Please review and update the .env file with your settings")
    else:
        # Create basic .env file
        basic_env = """# Ash-Thrash Configuration
GLOBAL_NLP_API_URL=http://10.20.30.253:8881
GLOBAL_LOG_LEVEL=INFO
DISCORD_WEBHOOK_URL=
DISCORD_NOTIFICATIONS_ENABLED=true
"""
        env_path.write_text(basic_env)
        print_success(f"Created basic {ENV_FILE}")

def create_directories():
    """Create required directories"""
    directories = ["results", "logs", "reports", "config"]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print_success(f"Created directory: {directory}")

def validate_configuration():
    """Validate configuration files"""
    # Check if key files exist and are valid
    try:
        # Validate docker-compose.yml
        subprocess.run(
            ["docker-compose", "-f", COMPOSE_FILE, "config"],
            capture_output=True,
            check=True
        )
        print_success("Docker Compose configuration is valid")
        
    except subprocess.CalledProcessError:
        print_error("Docker Compose configuration is invalid")

def load_env_file() -> dict:
    """Load environment variables from .env file"""
    env_vars = {}
    env_path = Path(ENV_FILE)
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    return env_vars

def check_services_health():
    """Check health of running services"""
    print("\n🏥 Checking service health...")
    check_api_health()

def check_api_health():
    """Check API service health"""
    try:
        import requests
        response = requests.get("http://localhost:8884/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            status = health_data.get('status', 'unknown')
            
            if status == 'healthy':
                print_success("API service is healthy")
            else:
                print_warning(f"API service status: {status}")
        else:
            print_error(f"API service returned {response.status_code}")
            
    except Exception as e:
        print_error(f"API service unreachable: {str(e)}")

def check_api_running() -> bool:
    """Check if API service is running"""
    try:
        result = subprocess.run(
            ["docker-compose", "-f", COMPOSE_FILE, "ps", "-q", "ash-thrash-api"],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False

def run_command(cmd: list):
    """Run a subprocess command with proper error handling"""
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        sys.exit(1)

# =============================================================================
# ARGUMENT PARSING
# =============================================================================

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Ash-Thrash v3.0 Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage.py setup
  python manage.py start --detach
  python manage.py test-all comprehensive
  python manage.py status
  python manage.py logs --follow
  python manage.py stop
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    subparsers.add_parser('setup', help='Initial setup and configuration')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start services')
    start_parser.add_argument('--build', action='store_true', help='Force rebuild images')
    start_parser.add_argument('--detach', action='store_true', default=True, help='Run in background')
    start_parser.add_argument('--no-detach', dest='detach', action='store_false', help='Run in foreground')
    
    # Stop command
    subparsers.add_parser('stop', help='Stop all services')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='View service logs')
    logs_parser.add_argument('--follow', '-f', action='store_true', help='Follow logs')
    logs_parser.add_argument('--service', help='Show logs for specific service')
    
    # Status command
    subparsers.add_parser('status', help='Check service status')
    
    # Test command
    test_parser = subparsers.add_parser('test-all', help='Run tests')
    test_parser.add_argument('test_type', default='comprehensive', nargs='?',
                            help='Test type to run')
    
    # CLI command
    cli_parser = subparsers.add_parser('cli', help='Run CLI commands in container')
    cli_parser.add_argument('command', nargs='+', help='CLI command to run')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate configuration')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean up resources')
    clean_parser.add_argument('--force', action='store_true', help='Force cleanup without confirmation')
    
    # Build command
    subparsers.add_parser('build', help='Build Docker images')
    
    return parser

def main():
    """Main management entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        command_map = {
            'setup': setup_command,
            'start': start_command,
            'stop': stop_command,
            'logs': logs_command,
            'status': status_command,
            'test-all': test_all_command,
            'cli': cli_command,
            'validate': validate_command,
            'clean': clean_command,
            'build': build_command
        }
        
        if args.command in command_map:
            command_map[args.command](args)
        else:
            print_error(f"Unknown command: {args.command}")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()