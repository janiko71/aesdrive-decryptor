#!/usr/bin/env python3
"""Script to setup virtual environment for AES Drive Decryptor."""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def main():
    """Setup virtual environment and install dependencies."""
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    print("🚀 Setting up AES Drive Decryptor development environment")
    print(f"📁 Project root: {project_root}")
    print(f"📁 Virtual environment: {venv_path}")
    
    # Change to project directory
    os.chdir(project_root)
    
    # Create virtual environment
    if venv_path.exists():
        print("⚠️ Virtual environment already exists. Removing...")
        if sys.platform == "win32":
            run_command(f'rmdir /s /q "{venv_path}"', "Removing existing venv")
        else:
            run_command(f'rm -rf "{venv_path}"', "Removing existing venv")
    
    run_command(f'python -m venv "{venv_path}"', "Creating virtual environment")
    
    # Determine activation script path
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_path = venv_path / "bin" / "pip"
    
    # Install dependencies
    run_command(f'"{pip_path}" install --upgrade pip', "Upgrading pip")
    run_command(f'"{pip_path}" install -r requirements.txt', "Installing dependencies")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    if sys.platform == "win32":
        print(f"   1. Activate the virtual environment: {activate_script}")
        print("   2. Run the decryptor: python aesdecryptor.py [file] [options]")
    else:
        print(f"   1. Activate the virtual environment: source {activate_script}")
        print("   2. Run the decryptor: python aesdecryptor.py [file] [options]")
    
    print("\n💡 To deactivate the virtual environment later, just run: deactivate")


if __name__ == "__main__":
    main()