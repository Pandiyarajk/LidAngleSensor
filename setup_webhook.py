#!/usr/bin/env python3
"""
Setup script to install the webhook formatter as a git pre-commit hook.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return False, "", str(e)


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("Warning: Not in a virtual environment. Consider using one for better dependency management.")
    
    # Install from requirements.txt
    success, stdout, stderr = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    if not success:
        print(f"Failed to install dependencies: {stderr}")
        return False
    
    print("Dependencies installed successfully")
    return True


def setup_git_hooks():
    """Set up git hooks."""
    print("Setting up git hooks...")
    
    # Check if we're in a git repository
    success, stdout, stderr = run_command(["git", "rev-parse", "--git-dir"])
    if not success:
        print("Error: Not in a git repository. Please initialize git first.")
        return False
    
    # Get git hooks directory
    success, stdout, stderr = run_command(["git", "rev-parse", "--git-path", "hooks"])
    if not success:
        print(f"Failed to get git hooks directory: {stderr}")
        return False
    
    hooks_dir = Path(stdout.strip())
    hooks_dir.mkdir(exist_ok=True)
    
    # Create pre-commit hook
    pre_commit_hook = hooks_dir / "pre-commit"
    webhook_script = Path(__file__).parent / "webhook_formatter.py"
    
    hook_content = f"""#!/bin/bash
# Pre-commit hook for code formatting
python3 "{webhook_script.absolute()}" --project-root "$(git rev-parse --show-toplevel)" --check-only
"""
    
    with open(pre_commit_hook, 'w') as f:
        f.write(hook_content)
    
    # Make it executable
    os.chmod(pre_commit_hook, 0o755)
    
    print(f"Pre-commit hook installed at: {pre_commit_hook}")
    return True


def create_webhook_script():
    """Create a standalone webhook script."""
    print("Creating webhook script...")
    
    webhook_script = Path(__file__).parent / "run_webhook.sh"
    
    script_content = f"""#!/bin/bash
# Webhook script to run code formatting and auto-commit

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
WEBHOOK_SCRIPT="{Path(__file__).parent.absolute()}/webhook_formatter.py"

cd "$PROJECT_ROOT"
python3 "$WEBHOOK_SCRIPT" --project-root "$PROJECT_ROOT" "$@"
"""
    
    with open(webhook_script, 'w') as f:
        f.write(script_content)
    
    os.chmod(webhook_script, 0o755)
    
    print(f"Webhook script created at: {webhook_script}")
    return True


def create_pyproject_toml():
    """Create pyproject.toml for isort and black configuration."""
    print("Creating pyproject.toml...")
    
    pyproject_content = """[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = [
    "**/migrations/**",
    "**/node_modules/**",
    "**/.git/**",
    "**/__pycache__/**"
]

[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\\.pyi?$'
exclude = '''
/(
    migrations
  | node_modules
  | \\.git
  | __pycache__
)/
'''
"""
    
    pyproject_file = Path(__file__).parent / "pyproject.toml"
    with open(pyproject_file, 'w') as f:
        f.write(pyproject_content)
    
    print(f"pyproject.toml created at: {pyproject_file}")
    return True


def main():
    """Main setup function."""
    print("Setting up webhook formatter...")
    
    # Check if we're in the right directory
    if not Path("webhook_formatter.py").exists():
        print("Error: webhook_formatter.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    success = True
    
    # Install dependencies
    success &= install_dependencies()
    
    # Create pyproject.toml
    success &= create_pyproject_toml()
    
    # Set up git hooks
    success &= setup_git_hooks()
    
    # Create webhook script
    success &= create_webhook_script()
    
    if success:
        print("\n✅ Webhook formatter setup completed successfully!")
        print("\nUsage:")
        print("  ./run_webhook.sh                    # Run formatter and auto-commit")
        print("  ./run_webhook.sh --check-only       # Only check for issues")
        print("  python3 webhook_formatter.py --help # See all options")
        print("\nThe pre-commit hook will now run automatically on git commits.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()