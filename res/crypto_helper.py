"""
Crypto Helper Module - Open source full version

Utility functions for cryptographic operations and data display.
Refactored to follow PEP8 standards and modern Python best practices.
"""

import hashlib
import logging
import secrets
from typing import Dict, Any, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from res.aes_data_file import AESDataFile


class CryptoHelper:
    """
    Helper class for cryptographic operations and utilities.
    
    This class provides static methods for common cryptographic operations
    and formatting functions used throughout the AES Drive Decryptor.
    """
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes, 
                               iterations: int = 50000, key_length: int = 32) -> bytes:
        """
        Derive a cryptographic key from a password using PBKDF2.
        
        Args:
            password: User password
            salt: Random salt bytes
            iterations: Number of PBKDF2 iterations
            key_length: Desired key length in bytes
            
        Returns:
            Derived key bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=key_length,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        
        return kdf.derive(password.encode('utf-8'))
    
    @staticmethod
    def generate_file_hash(file_seed: bytes) -> bytes:
        """
        Generate SHA512 hash from file seed.
        
        Args:
            file_seed: Combined salt and derived key
            
        Returns:
            SHA512 hash bytes
        """
        return hashlib.sha512(file_seed).digest()
    
    @staticmethod
    def secure_compare(a: bytes, b: bytes) -> bool:
        """
        Securely compare two byte sequences to prevent timing attacks.
        
        Args:
            a: First byte sequence
            b: Second byte sequence
            
        Returns:
            True if sequences are equal, False otherwise
        """
        return secrets.compare_digest(a, b)
    
    @staticmethod
    def format_hex_string(data: bytes, group_size: int = 16) -> str:
        """
        Format bytes as a readable hex string with grouping.
        
        Args:
            data: Bytes to format
            group_size: Number of bytes per group
            
        Returns:
            Formatted hex string
        """
        hex_str = data.hex()
        return ' '.join(hex_str[i:i+group_size*2] for i in range(0, len(hex_str), group_size*2))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength and provide feedback.
        
        Args:
            password: Password to validate
            
        Returns:
            Dictionary with validation results and recommendations
        """
        result = {
            'is_strong': False,
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        if len(password) < 8:
            result['issues'].append('Password too short')
            result['recommendations'].append('Use at least 8 characters')
        else:
            result['score'] += 1
            
        if len(password) >= 12:
            result['score'] += 1
            
        if any(c.isupper() for c in password):
            result['score'] += 1
        else:
            result['issues'].append('No uppercase letters')
            result['recommendations'].append('Include uppercase letters')
            
        if any(c.islower() for c in password):
            result['score'] += 1
        else:
            result['issues'].append('No lowercase letters')
            result['recommendations'].append('Include lowercase letters')
            
        if any(c.isdigit() for c in password):
            result['score'] += 1
        else:
            result['issues'].append('No numbers')
            result['recommendations'].append('Include numbers')
            
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            result['score'] += 1
        else:
            result['issues'].append('No special characters')
            result['recommendations'].append('Include special characters')
        
        result['is_strong'] = result['score'] >= 4
        
        return result


class DisplayFormatter:
    """
    Helper class for formatting and displaying information.
    
    Provides methods for consistent formatting of data and progress information.
    """
    
    # ANSI color codes
    COLORS = {
        'RED': '\033[31m',
        'GREEN': '\033[32m',
        'YELLOW': '\033[33m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'RESET': '\033[0m'
    }
    
    @classmethod
    def format_parameter(cls, name: str, value: Any, max_length: int = 50) -> str:
        """
        Format a parameter name-value pair for display.
        
        Args:
            name: Parameter name
            value: Parameter value
            max_length: Maximum display length for values
            
        Returns:
            Formatted string
        """
        if isinstance(value, bytes):
            display_value = value.hex()[:max_length]
            if len(value.hex()) > max_length:
                display_value += "..."
        elif isinstance(value, (int, float)):
            display_value = str(value)
        else:
            display_value = str(value)[:max_length]
            if len(str(value)) > max_length:
                display_value += "..."
        
        # Calculate padding
        dots_length = 50 - len(name) - len(str(len(display_value)))
        dots = '.' * max(1, dots_length)
        
        return f"{name}{dots} ({len(str(value))}) {cls.COLORS['WHITE']}{display_value}{cls.COLORS['RESET']}"
    
    @classmethod
    def format_file_info(cls, data_file: AESDataFile) -> str:
        """
        Format AES data file information for display.
        
        Args:
            data_file: AESDataFile instance
            
        Returns:
            Formatted information string
        """
        info = data_file.get_info_dict()
        
        lines = [
            cls.format_parameter("File type", info['file_type']),
            cls.format_parameter("File version", info['file_type_version']),
            cls.format_parameter("CRC32 checksum", info['crc32_checksum']),
            cls.format_parameter("Global salt", info['global_salt_hex']),
            cls.format_parameter("File salt", info['file_salt_hex']),
            cls.format_parameter("Validation", "PASSED" if info['is_valid'] else "FAILED")
        ]
        
        return "\n".join(lines)
    
    @classmethod
    def format_progress_bar(cls, current: int, total: int, width: int = 50) -> str:
        """
        Create a progress bar string.
        
        Args:
            current: Current progress value
            total: Total/maximum value
            width: Width of progress bar in characters
            
        Returns:
            Progress bar string
        """
        if total == 0:
            percentage = 0
        else:
            percentage = min(100, (current / total) * 100)
        
        filled_width = int(width * percentage / 100)
        bar = '█' * filled_width + '░' * (width - filled_width)
        
        return f"{cls.COLORS['CYAN']}[{bar}]{cls.COLORS['RESET']} {percentage:6.1f}%"
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """
        Add color to text.
        
        Args:
            text: Text to colorize
            color: Color name from COLORS dict
            
        Returns:
            Colorized text
        """
        color_code = cls.COLORS.get(color.upper(), '')
        return f"{color_code}{text}{cls.COLORS['RESET']}"
    
    @classmethod
    def print_header(cls, title: str, width: int = 72) -> None:
        """
        Print a formatted header.
        
        Args:
            title: Header title
            width: Total width of header
        """
        logger = logging.getLogger(__name__)
        
        border = '=' * width
        title_line = f" {title} ".center(width, '=')
        
        logger.info(border)
        logger.info(title_line)
        logger.info(border)
    
    @classmethod
    def print_separator(cls, width: int = 72) -> None:
        """
        Print a separator line.
        
        Args:
            width: Width of separator
        """
        logger = logging.getLogger(__name__)
        logger.info('-' * width)


def setup_crypto_logging() -> None:
    """Setup logging configuration for crypto operations."""
    logging.getLogger('cryptography').setLevel(logging.WARNING)


if __name__ == '__main__':
    print('This is a module - import it rather than running directly')