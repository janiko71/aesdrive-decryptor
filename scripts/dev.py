#!/usr/bin/env python3
"""Development utility script for AES Drive Decryptor."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        return None


def format_code():
    """Format code using black and isort."""
    print("🎨 Formatting code...")
    run_command("black .", "Running black formatter")
    run_command("isort .", "Running isort import sorter")


def lint_code():
    """Lint code using flake8 and mypy."""
    print("🔍 Linting code...")
    run_command("flake8 .", "Running flake8 linter")
    run_command("mypy .", "Running mypy type checker")


def run_tests():
    """Run tests using pytest."""
    print("🧪 Running tests...")
    run_command("pytest --cov=. --cov-report=html", "Running pytest with coverage")


def install_dev_deps():
    """Install development dependencies."""
    print("📦 Installing development dependencies...")
    run_command("pip install -r requirements-dev.txt", "Installing dev dependencies")


def clean():
    """Clean build artifacts and cache files."""
    print("🧹 Cleaning build artifacts...")
    
    patterns = [
        "build/",
        "dist/",
        "*.egg-info/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        ".mypy_cache/"
    ]
    
    for pattern in patterns:
        if sys.platform == "win32":
            run_command(f'for /d /r . %d in ({pattern}) do @if exist "%d" rd /s /q "%d"', f"Removing {pattern}")
            run_command(f'del /s /q {pattern} 2>nul', f"Removing {pattern} files")
        else:
            run_command(f'find . -name "{pattern}" -exec rm -rf {{}} +', f"Removing {pattern}")


def build_package():
    """Build the package."""
    print("📦 Building package...")
    run_command("python -m build", "Building package")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Development utility for AES Drive Decryptor")
    parser.add_argument("command", choices=[
        "format", "lint", "test", "install-dev", "clean", "build", "all"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "format":
        format_code()
    elif args.command == "lint":
        lint_code()
    elif args.command == "test":
        run_tests()
    elif args.command == "install-dev":
        install_dev_deps()
    elif args.command == "clean":
        clean()
    elif args.command == "build":
        build_package()
    elif args.command == "all":
        install_dev_deps()
        format_code()
        lint_code()
        run_tests()
        build_package()
    
    print("🎉 Development task completed!")


if __name__ == "__main__":
    main()