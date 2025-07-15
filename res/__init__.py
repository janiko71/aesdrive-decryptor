"""
AES Drive Decryptor - Resources Package

This package contains the core modules for the AES Drive Decryptor:
- aes_data_file: AES Drive file format parser
- config: Configuration management
- crypto_helper: Cryptographic utilities and formatters

Professional refactor of janiko71's original work.
"""

# Package metadata
__version__ = "2.0.0"
__author__ = "Professional refactor of janiko71's work"
__license__ = "MIT"
__description__ = "AES Drive Decryptor - Resources Package"

# Import main classes for easy access
from .aes_data_file import AESDataFile, AESDataFileError, load_from_file
from .config import Config, get_config, set_config
from .crypto_helper import CryptoHelper, DisplayFormatter, setup_crypto_logging

# Define what gets imported with "from res import *"
__all__ = [
    # Main classes
    'AESDataFile',
    'Config', 
    'CryptoHelper',
    'DisplayFormatter',
    
    # Exceptions
    'AESDataFileError',
    
    # Utility functions
    'load_from_file',
    'get_config',
    'set_config',
    'setup_crypto_logging',
    
    # Metadata
    '__version__',
    '__author__',
    '__license__',
    '__description__',
]

# Package-level initialization
def get_package_info():
    """
    Get package information as a dictionary.
    
    Returns:
        Dictionary containing package metadata
    """
    return {
        'name': 'aesdrive-decryptor-res',
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'description': __description__,
        'modules': [
            'aes_data_file',
            'config', 
            'crypto_helper'
        ]
    }