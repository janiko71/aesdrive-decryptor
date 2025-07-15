"""
Test Suite for AES Drive Decryptor

This package contains comprehensive tests for the AES Drive Decryptor:
- Unit tests for individual components
- Integration tests for complete workflows  
- Security tests for cryptographic functions
- Performance tests for large files

Run tests with: pytest tests/
"""

__version__ = "2.0.0"
__description__ = "Test suite for AES Drive Decryptor"

# Test configuration
TEST_DATA_DIR = "test_data"
SAMPLE_FILES = {
    'small_encrypted': 'sample_small.aesd',
    'large_encrypted': 'sample_large.aesd',
    'invalid_file': 'invalid.aesd',
    'test_password': 'test_password_123'
}

# Import test utilities if available
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

__all__ = [
    'TEST_DATA_DIR',
    'SAMPLE_FILES', 
    'PYTEST_AVAILABLE',
    '__version__',
    '__description__',
]


def run_tests():
    """
    Run the complete test suite.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    if not PYTEST_AVAILABLE:
        print("pytest is required to run tests. Install with: pip install pytest")
        return 1
        
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', '-v', '--tb=short'
        ], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode


if __name__ == '__main__':
    # Allow running tests directly with: python -m tests
    exit_code = run_tests()
    exit(exit_code)