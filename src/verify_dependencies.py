#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  VERIFY_DEPENDENCIES.PY — Check all required dependencies
# ═══════════════════════════════════════════════════════════════

import sys
import shutil
import platform
from pathlib import Path

def check_executables():
    """Check if system executables are available."""
    executables = {
        'ffmpeg': {
            'install_windows': 'winget install ffmpeg',
            'install_mac': 'brew install ffmpeg',
            'install_linux': 'sudo apt install ffmpeg'
        },
        'ffprobe': {
            'install_windows': 'winget install ffmpeg',
            'install_mac': 'brew install ffmpeg',
            'install_linux': 'sudo apt install ffmpeg'
        }
    }
    
    missing = []
    for exe, instructions in executables.items():
        if not shutil.which(exe):
            missing.append((exe, instructions))
    
    return missing


def check_python_packages():
    """Check if required Python packages are installed."""
    packages = {
        'edge_tts': 'edge-tts>=6.1.0',
        'PIL': 'Pillow>=9.0.0',
        'librosa': 'librosa>=0.10.0',
        'requests': 'requests>=2.28.0',
        'dotenv': 'python-dotenv>=0.19.0',
        'docx': 'python-docx>=0.8.11',
    }
    
    missing = []
    for module_name, package_spec in packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append((module_name, package_spec))
    
    return missing


def check_env_file():
    """Check if .env file exists with API keys."""
    env_path = Path(__file__).parent.parent / '.env'
    
    required_keys = [
        'PEXELS_API_KEY',  # For background videos
        # Add more as needed
    ]
    
    if not env_path.exists():
        return {
            'exists': False,
            'missing_keys': required_keys,
            'path': str(env_path)
        }
    
    # Read .env and check keys
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        missing_keys = []
        for key in required_keys:
            if key not in content:
                missing_keys.append(key)
        
        return {
            'exists': True,
            'missing_keys': missing_keys,
            'path': str(env_path)
        }
    except Exception as e:
        return {
            'exists': True,
            'error': str(e),
            'path': str(env_path)
        }


def verify_all_dependencies(verbose=False):
    """
    Comprehensive dependency check.
    
    Returns: {
        'status': 'OK' | 'WARNING' | 'ERROR',
        'issues': [list of problems],
        'warnings': [list of warnings]
    }
    """
    issues = []
    warnings = []
    
    print("\n" + "="*70)
    print("🔍 DEPENDENCY VERIFICATION")
    print("="*70 + "\n")
    
    # Check executables
    print("📦 Checking system executables...")
    missing_exes = check_executables()
    if missing_exes:
        for exe, instructions in missing_exes:
            issues.append(f"❌ {exe} not found")
            if verbose:
                os_type = platform.system()
                if os_type == 'Windows':
                    print(f"   Install: {instructions['install_windows']}")
                elif os_type == 'Darwin':
                    print(f"   Install: {instructions['install_mac']}")
                else:
                    print(f"   Install: {instructions['install_linux']}")
    else:
        print("   ✅ FFmpeg and ffprobe found")
    
    # Check Python packages
    print("\n📦 Checking Python packages...")
    missing_packages = check_python_packages()
    
    if missing_packages:
        # Separate required vs optional
        required = {'edge_tts', 'PIL'}
        
        for module_name, package_spec in missing_packages:
            if module_name in required:
                issues.append(f"❌ {package_spec} not installed")
            else:
                warnings.append(f"⚠️  {package_spec} not installed (optional)")
        
        if verbose:
            print("   Install with: pip install -r requirements.txt")
    else:
        print("   ✅ All Python packages found")
    
    # Check .env file
    print("\n📦 Checking environment variables...")
    env_status = check_env_file()
    
    if not env_status['exists']:
        warnings.append(f"⚠️  .env file not found (needed for Pexels API key)")
        if verbose:
            print(f"   Create at: {env_status['path']}")
            print("   Add: PEXELS_API_KEY=your_api_key_here")
    elif env_status.get('missing_keys'):
        for key in env_status['missing_keys']:
            warnings.append(f"⚠️  {key} not configured in .env")
    else:
        print("   ✅ Environment variables configured")
    
    # Determine status
    if issues:
        status = 'ERROR'
    elif warnings:
        status = 'WARNING'
    else:
        status = 'OK'
    
    # Print summary
    print("\n" + "="*70)
    if status == 'OK':
        print("✅ ALL CHECKS PASSED - System ready!")
    elif status == 'WARNING':
        print("⚠️  WARNINGS FOUND - Some features may not work")
    else:
        print("❌ CRITICAL ISSUES - Cannot proceed")
    print("="*70 + "\n")
    
    if issues:
        print("Critical Issues:")
        for issue in issues:
            print(f"  {issue}")
        print()
    
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    return {
        'status': status,
        'issues': issues,
        'warnings': warnings
    }


def quick_check():
    """Quick dependency check without printing."""
    result = verify_all_dependencies(verbose=False)
    return result['status'] in ['OK', 'WARNING']


if __name__ == "__main__":
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    result = verify_all_dependencies(verbose=verbose)
    
    sys.exit(0 if result['status'] != 'ERROR' else 1)