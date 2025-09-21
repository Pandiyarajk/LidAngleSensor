#!/usr/bin/env python3
"""
Webhook script to automatically check and fix isort and black issues,
then commit the changes to git.
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CodeFormatter:
    """Handles code formatting with isort and black."""
    
    def __init__(self, project_root: str, config_file: Optional[str] = None):
        self.project_root = Path(project_root)
        self.config_file = config_file
        self.changed_files = set()
        
    def run_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"Error running command {' '.join(command)}: {e}")
            return 1, "", str(e)
    
    def check_git_status(self) -> bool:
        """Check if we're in a git repository and if there are uncommitted changes."""
        exit_code, stdout, stderr = self.run_command(["git", "status", "--porcelain"])
        if exit_code != 0:
            logger.error(f"Not in a git repository or git error: {stderr}")
            return False
        
        # Check if there are any uncommitted changes
        if stdout.strip():
            logger.warning("There are uncommitted changes. Please commit or stash them first.")
            return False
        
        return True
    
    def get_python_files(self) -> List[Path]:
        """Get all Python files in the project."""
        python_files = []
        for pattern in ["*.py", "**/*.py"]:
            python_files.extend(self.project_root.glob(pattern))
        
        # Filter out __pycache__ and .git directories
        python_files = [
            f for f in python_files 
            if "__pycache__" not in str(f) and ".git" not in str(f)
        ]
        
        return python_files
    
    def run_isort_check(self, files: List[Path]) -> bool:
        """Run isort check on files."""
        logger.info("Running isort check...")
        
        file_paths = [str(f) for f in files]
        command = ["isort", "--check-only", "--diff"] + file_paths
        
        exit_code, stdout, stderr = self.run_command(command)
        
        if exit_code == 0:
            logger.info("isort check passed - no import sorting issues found")
            return True
        else:
            logger.warning("isort check failed - import sorting issues found")
            if stdout:
                logger.info(f"isort diff:\n{stdout}")
            return False
    
    def run_black_check(self, files: List[Path]) -> bool:
        """Run black check on files."""
        logger.info("Running black check...")
        
        file_paths = [str(f) for f in files]
        command = ["black", "--check", "--diff"] + file_paths
        
        exit_code, stdout, stderr = self.run_command(command)
        
        if exit_code == 0:
            logger.info("black check passed - no formatting issues found")
            return True
        else:
            logger.warning("black check failed - formatting issues found")
            if stdout:
                logger.info(f"black diff:\n{stdout}")
            return False
    
    def fix_isort(self, files: List[Path]) -> bool:
        """Fix isort issues in files."""
        logger.info("Fixing isort issues...")
        
        file_paths = [str(f) for f in files]
        command = ["isort"] + file_paths
        
        exit_code, stdout, stderr = self.run_command(command)
        
        if exit_code == 0:
            logger.info("isort fixes applied successfully")
            # Track which files were changed
            for file_path in files:
                if self.file_has_changes(file_path):
                    self.changed_files.add(file_path)
            return True
        else:
            logger.error(f"Failed to apply isort fixes: {stderr}")
            return False
    
    def fix_black(self, files: List[Path]) -> bool:
        """Fix black formatting issues in files."""
        logger.info("Fixing black formatting issues...")
        
        file_paths = [str(f) for f in files]
        command = ["black"] + file_paths
        
        exit_code, stdout, stderr = self.run_command(command)
        
        if exit_code == 0:
            logger.info("black fixes applied successfully")
            # Track which files were changed
            for file_path in files:
                if self.file_has_changes(file_path):
                    self.changed_files.add(file_path)
            return True
        else:
            logger.error(f"Failed to apply black fixes: {stderr}")
            return False
    
    def file_has_changes(self, file_path: Path) -> bool:
        """Check if a file has uncommitted changes."""
        exit_code, stdout, stderr = self.run_command(["git", "status", "--porcelain", str(file_path)])
        return bool(stdout.strip())
    
    def commit_changes(self, commit_message: str = None) -> bool:
        """Commit the changed files."""
        if not self.changed_files:
            logger.info("No files were changed, nothing to commit")
            return True
        
        logger.info(f"Committing changes to {len(self.changed_files)} files...")
        
        # Add changed files to git
        for file_path in self.changed_files:
            exit_code, stdout, stderr = self.run_command(["git", "add", str(file_path)])
            if exit_code != 0:
                logger.error(f"Failed to add {file_path} to git: {stderr}")
                return False
        
        # Create commit message
        if not commit_message:
            commit_message = f"Auto-format: Fix isort and black issues in {len(self.changed_files)} files"
        
        # Commit changes
        exit_code, stdout, stderr = self.run_command(["git", "commit", "-m", commit_message])
        if exit_code == 0:
            logger.info(f"Successfully committed changes: {commit_message}")
            return True
        else:
            logger.error(f"Failed to commit changes: {stderr}")
            return False
    
    def run_webhook(self, check_only: bool = False, commit_message: str = None) -> bool:
        """Run the complete webhook process."""
        logger.info("Starting webhook formatter...")
        
        # Check git status
        if not self.check_git_status():
            return False
        
        # Get Python files
        python_files = self.get_python_files()
        if not python_files:
            logger.warning("No Python files found in the project")
            return True
        
        logger.info(f"Found {len(python_files)} Python files to check")
        
        # Run checks
        isort_ok = self.run_isort_check(python_files)
        black_ok = self.run_black_check(python_files)
        
        if isort_ok and black_ok:
            logger.info("All checks passed - no formatting issues found")
            return True
        
        if check_only:
            logger.info("Check-only mode - not applying fixes")
            return False
        
        # Apply fixes
        success = True
        if not isort_ok:
            success &= self.fix_isort(python_files)
        
        if not black_ok:
            success &= self.fix_black(python_files)
        
        if not success:
            logger.error("Failed to apply some fixes")
            return False
        
        # Commit changes if any files were modified
        if self.changed_files:
            success &= self.commit_changes(commit_message)
        
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Webhook formatter for isort and black")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Root directory of the project (default: current directory)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for issues, don't fix them"
    )
    parser.add_argument(
        "--commit-message",
        help="Custom commit message for auto-commits"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize formatter
    formatter = CodeFormatter(args.project_root, args.config)
    
    # Run webhook
    success = formatter.run_webhook(
        check_only=args.check_only,
        commit_message=args.commit_message
    )
    
    if success:
        logger.info("Webhook completed successfully")
        sys.exit(0)
    else:
        logger.error("Webhook failed")
        sys.exit(1)


if __name__ == "__main__":
    main()