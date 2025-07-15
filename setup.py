#!/usr/bin/env python3
"""
Setup script for AES Drive Decryptor - Open source full version

This setup script allows for easy installation and distribution of the
AES Drive Decryptor package.

Usage:
    pip install .                    # Install package
    pip install -e .                 # Install in development mode
    python setup.py sdist bdist_wheel # Build distribution packages
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements from requirements.txt
def read_requirements(filename):
    """Read requirements from a requirements file."""
    requirements = []
    req_file = this_directory / filename
    
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments, empty lines, and -r/-e directives
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Remove inline comments
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    requirements.append(line)
    
    return requirements

# Get version from main module (avoiding import issues)
def get_version():
    """Extract version from the main module."""
    version_file = this_directory / "aes_decryptor.py"
    if version_file.exists():
        content = version_file.read_text(encoding='utf-8')
        # Look for version in docstring or comments
        version_match = re.search(r'version["\']?\s*[:=]\s*["\']([^"\']+)["\']', content, re.I)
        if version_match:
            return version_match.group(1)
    
    # Fallback version
    return "2.0.0"

# Main requirements
install_requires = read_requirements("requirements.txt")

# Development requirements
dev_requires = read_requirements("requirements-dev.txt")

setup(
    # Basic package information
    name="aesdrive-decryptor",
    version=get_version(),
    
    # Author information
    author="Professional refactor of janiko71's work",
    author_email="",
    maintainer="Community",
    maintainer_email="",
    
    # Package description
    description="Professional AES Drive file decryptor with modern Python standards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # URLs and links
    url="https://github.com/janiko71/aesdrive-decryptor",
    project_urls={
        "Bug Reports": "https://github.com/janiko71/aesdrive-decryptor/issues",
        "Source": "https://github.com/janiko71/aesdrive-decryptor",
        "Documentation": "https://github.com/janiko71/aesdrive-decryptor/wiki",
        "Changelog": "https://github.com/janiko71/aesdrive-decryptor/blob/main/CHANGELOG.md",
    },
    
    # Package discovery
    packages=find_packages(),
    py_modules=["aes_decryptor"],
    
    # Package classification
    classifiers=[
        # Development status
        "Development Status :: 5 - Production/Stable",
        
        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        
        # Topic classification
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Python version support
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        
        # Operating system
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        
        # Environment
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
    ],
    
    # Python version requirements
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=install_requires,
    
    # Optional dependencies
    extras_require={
        "dev": dev_requires,
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
        "lint": [
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=0.18.0",
        ],
        "all": dev_requires,  # Install all optional dependencies
    },
    
    # Console scripts
    entry_points={
        "console_scripts": [
            "aesdecryptor=aes_decryptor:main",
            "aes-decrypt=aes_decryptor:main",
        ],
    },
    
    # Keywords for package discovery
    keywords=[
        "aes", "encryption", "decryption", "aesdrive", "security", 
        "cryptography", "file-decryption", "xts-aes", "nsoftware",
        "professional", "cli", "tool"
    ],
    
    # Package data
    include_package_data=True,
    zip_safe=False,
    
    # Platform compatibility
    platforms=["any"],
    
    # License
    license="MIT",
    
    # Additional metadata
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.ini"],
        "res": ["*.py"],
    },
    
    # Exclude packages (if any)
    # exclude_package_data={},
    
    # Setup requirements (only needed during setup)
    setup_requires=[
        "setuptools>=45",
        "wheel",
    ],
    
    # Test requirements
    tests_require=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
    
    # Command classes (for custom setup commands)
    # cmdclass={},
)

# Post-installation message
if __name__ == "__main__":
    print("🎉 AES Drive Decryptor installation completed!")
    print("📖 Usage: aesdecryptor --help")
    print("🔗 Documentation: https://github.com/janiko71/aesdrive-decryptor")