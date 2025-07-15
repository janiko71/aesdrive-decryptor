"""
AES Drive Decryptor - Opens source Python Implementation

A secure, efficient, and professional tool for decrypting AES Drive encrypted files.
This package provides a complete solution with modern Python best practices.

Usage:
    from aes_decryptor import AESDecryptor
    from res import Config
    
    config = Config()
    decryptor = AESDecryptor(config)
    
    success = decryptor.decrypt_file(
        input_path=Path("encrypted.aesd"),
        password="mypassword"
    )

Command Line Usage:
    python aes_decryptor.py file.aesd -p password
    
Author: Professional refactor of janiko71's original work
License: MIT
Version: 2.0.0
"""

# Package metadata
__version__ = "2.0.0"
__author__ = "Professional refactor of janiko71's work"
__license__ = "MIT"
__description__ = "Professional AES Drive file decryptor"
__url__ = "https://github.com/janiko71/aesdrive-decryptor"

# Import main classes for top-level access
try:
    from .aes_decryptor import AESDecryptor, AESDecryptorError
    from .res import Config, AESDataFile, CryptoHelper
except ImportError:
    # Handle case when modules are not yet installed
    pass

# Define public API
__all__ = [
    'AESDecryptor',
    'AESDecryptorError', 
    'Config',
    'AESDataFile',
    'CryptoHelper',
    '__version__',
    '__author__',
    '__license__',
    '__description__',
    '__url__',
]


def get_version():
    """Get the current version of the package."""
    return __version__


def get_info():
    """
    Get complete package information.
    
    Returns:
        Dictionary with package details
    """
    return {
        'name': 'aesdrive-decryptor',
        'version': __version__,
        'author': __author__, 
        'license': __license__,
        'description': __description__,
        'url': __url__,
        'python_requires': '>=3.8',
        'main_module': 'aes_decryptor',
        'resources_package': 'res',
    }