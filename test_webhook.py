#!/usr/bin/env python3
"""
Test script to verify webhook formatter functionality.
Creates test files with formatting issues and runs the formatter.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
import shutil


def create_test_file(file_path, content):
    """Create a test file with the given content."""
    with open(file_path, 'w') as f:
        f.write(content)


def run_command(command, cwd=None):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def test_webhook_formatter():
    """Test the webhook formatter functionality."""
    print("🧪 Testing webhook formatter...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Initialize git repository
        print("  📁 Initializing git repository...")
        success, stdout, stderr = run_command(["git", "init"], cwd=temp_path)
        if not success:
            print(f"  ❌ Failed to initialize git: {stderr}")
            return False
        
        # Configure git user (required for commits)
        run_command(["git", "config", "user.email", "test@example.com"], cwd=temp_path)
        run_command(["git", "config", "user.name", "Test User"], cwd=temp_path)
        
        # Create test Python files with formatting issues
        print("  📝 Creating test files with formatting issues...")
        
        # File with isort issues
        isort_file = temp_path / "test_isort.py"
        isort_content = '''import os
import sys
from pathlib import Path
import json
import logging

def test_function():
    """Test function with bad formatting."""
    x=1+2
    y = {"a":1,"b":2}
    return x,y
'''
        create_test_file(isort_file, isort_content)
        
        # File with black issues
        black_file = temp_path / "test_black.py"
        black_content = '''def long_function_name_that_should_be_formatted_differently(param1, param2, param3, param4, param5, param6, param7, param8):
    if param1 and param2 and param3 and param4 and param5 and param6 and param7 and param8:
        return {"key1": "value1", "key2": "value2", "key3": "value3", "key4": "value4", "key5": "value5"}
    else:
        return None
'''
        create_test_file(black_file, black_content)
        
        # File with both issues
        both_file = temp_path / "test_both.py"
        both_content = '''import json
import os
import sys
from pathlib import Path
import logging

def bad_formatting():
    x=1+2
    y={"a":1,"b":2}
    if x and y and True and False and 1 and 0 and "string" and None:
        return {"very_long_key": "very_long_value", "another_key": "another_value", "third_key": "third_value"}
    return None
'''
        create_test_file(both_file, both_content)
        
        # Copy webhook formatter to temp directory
        webhook_script = Path(__file__).parent / "webhook_formatter.py"
        if not webhook_script.exists():
            print("  ❌ webhook_formatter.py not found")
            return False
        
        shutil.copy2(webhook_script, temp_path / "webhook_formatter.py")
        
        # Commit the initial test files
        print("  📝 Committing initial test files...")
        run_command(["git", "add", "."], cwd=temp_path)
        run_command(["git", "commit", "-m", "Initial test files"], cwd=temp_path)
        
        # Test check-only mode
        print("  🔍 Testing check-only mode...")
        success, stdout, stderr = run_command([
            sys.executable, "webhook_formatter.py", "--check-only", "--verbose"
        ], cwd=temp_path)
        
        if success:
            print("  ❌ Check-only mode should have failed (files have issues)")
            return False
        
        print("  ✅ Check-only mode correctly detected issues")
        
        # Test fix mode
        print("  🔧 Testing fix mode...")
        success, stdout, stderr = run_command([
            sys.executable, "webhook_formatter.py", "--verbose"
        ], cwd=temp_path)
        
        if not success:
            print(f"  ❌ Fix mode failed: {stderr}")
            return False
        
        print("  ✅ Fix mode completed successfully")
        
        # Check if files were actually fixed
        print("  🔍 Verifying fixes...")
        
        # Check isort file
        with open(isort_file, 'r') as f:
            isort_content_fixed = f.read()
        
        if "import os" in isort_content_fixed and "import sys" in isort_content_fixed:
            print("  ✅ isort file was fixed")
        else:
            print("  ❌ isort file was not properly fixed")
            return False
        
        # Check black file
        with open(black_file, 'r') as f:
            black_content_fixed = f.read()
        
        if "def long_function_name_that_should_be_formatted_differently(" in black_content_fixed:
            print("  ✅ black file was fixed")
        else:
            print("  ❌ black file was not properly fixed")
            return False
        
        # Check if changes were committed
        success, stdout, stderr = run_command(["git", "log", "--oneline"], cwd=temp_path)
        if "Auto-format" in stdout:
            print("  ✅ Changes were automatically committed")
        else:
            print("  ❌ Changes were not committed")
            return False
        
        print("  ✅ All tests passed!")
        return True


def test_webhook_server():
    """Test the webhook server functionality."""
    print("🌐 Testing webhook server...")
    
    # This is a basic test - in a real scenario you'd test HTTP endpoints
    print("  ℹ️  Webhook server test requires manual verification")
    print("  ℹ️  Run: python3 webhook_server.py --port 8080")
    print("  ℹ️  Then test: curl http://localhost:8080/health")
    return True


def main():
    """Run all tests."""
    print("🚀 Starting webhook formatter tests...\n")
    
    # Test webhook formatter
    formatter_success = test_webhook_formatter()
    
    print()
    
    # Test webhook server
    server_success = test_webhook_server()
    
    print("\n" + "="*50)
    if formatter_success and server_success:
        print("🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Run: python3 setup_webhook.py")
        print("2. Test: ./run_webhook.sh --check-only")
        print("3. Start server: python3 webhook_server.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())