"""
Utility functions and classes for AES Drive Decryptor.

This module provides various utility functions for file operations,
formatting, validation, and logging support.
"""

import os
import sys
import logging
import hashlib
from pathlib import Path
from typing import Optional, Union, Any, Dict
from contextlib import contextmanager

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False


class SecureMemory:
    """Utility class for secure memory operations."""
    
    @staticmethod
    def secure_zero(data: bytearray) -> None:
        """Securely zero out memory."""
        if isinstance(data, bytearray):
            for i in range(len(data)):
                data[i] = 0
    
    @staticmethod
    @contextmanager
    def secure_bytes(size: int):
        """Context manager for secure byte arrays."""
        data = bytearray(size)
        try:
            yield data
        finally:
            SecureMemory.secure_zero(data)


class ColorFormatter:
    """Utility class for colored console output."""
    
    def __init__(self, use_color: bool = True):
        """
        Initialize color formatter.
        
        Args:
            use_color: Whether to use colors (auto-detected if colorama available)
        """
        self.use_color = use_color and HAS_COLORAMA
    
    def colorize(self, text: str, color: str = "white") -> str:
        """
        Colorize text if colors are enabled.
        
        Args:
            text: Text to colorize
            color: Color name (red, green, yellow, blue, cyan, white)
            
        Returns:
            Colorized text or plain text if colors disabled
        """
        if not self.use_color:
            return text
        
        color_map = {
            "red": Fore.RED,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "cyan": Fore.CYAN,
            "white": Fore.WHITE,
            "lightwhite": Fore.LIGHTWHITE_EX,
            "reset": Style.RESET_ALL
        }
        
        color_code = color_map.get(color.lower(), "")
        return f"{color_code}{text}{Style.RESET_ALL}"
    
    def success(self, text: str) -> str:
        """Format success message."""
        return self.colorize(f"✓ {text}", "green")
    
    def error(self, text: str) -> str:
        """Format error message."""
        return self.colorize(f"❌ {text}", "red")
    
    def warning(self, text: str) -> str:
        """Format warning message."""
        return self.colorize(f"⚠️ {text}", "yellow")
    
    def info(self, text: str) -> str:
        """Format info message."""
        return self.colorize(f"ℹ️ {text}", "blue")


class ParameterFormatter:
    """Utility class for formatting parameter output."""
    
    def __init__(self, color_formatter: Optional[ColorFormatter] = None):
        """
        Initialize parameter formatter.
        
        Args:
            color_formatter: Color formatter instance
        """
        self.color_formatter = color_formatter or ColorFormatter()
    
    def format_parameter(self, name: str, value: Any, max_width: int = 50) -> str:
        """
        Format a parameter for display.
        
        Args:
            name: Parameter name
            value: Parameter value
            max_width: Maximum width for formatting
            
        Returns:
            Formatted parameter string
        """
        # Convert value to string
        if isinstance(value, bytes):
            str_value = value.hex()
        elif isinstance(value, int):
            str_value = str(value)
        else:
            str_value = str(value)
        
        # Calculate padding
        value_len = len(str_value)
        dots_len = max_width - len(name) - len(str(value_len)) - 3  # 3 for " () "
        dots = "." * max(dots_len, 1)
        
        # Format with colors
        name_colored = self.color_formatter.colorize(name, "white")
        value_colored = self.color_formatter.colorize(str_value, "lightwhite")
        length_info = self.color_formatter.colorize(f"({value_len})", "cyan")
        
        return f"{name_colored}{dots} {length_info} {value_colored}"
    
    def print_parameter(self, name: str, value: Any, max_width: int = 50) -> None:
        """
        Print a formatted parameter.
        
        Args:
            name: Parameter name
            value: Parameter value
            max_width: Maximum width for formatting
        """
        print(self.format_parameter(name, value, max_width))
    
    def print_separator(self, char: str = "-", length: int = 72) -> None:
        """
        Print a separator line.
        
        Args:
            char: Character to use for separator
            length: Length of separator
        """
        print(char * length)
    
    def print_header(self, title: str, char: str = "=", length: int = 72) -> None:
        """
        Print a header with title.
        
        Args:
            title: Header title
            char: Character to use for header
            length: Length of header
        """
        title_colored = self.color_formatter.colorize(title, "lightwhite")
        print(char * length)
        print(title_colored.center(length))
        print(char * length)


class FileValidator:
    """Utility class for file validation."""
    
    @staticmethod
    def validate_path(path: Union[str, Path], must_exist: bool = True) -> Path:
        """
        Validate and convert path to Path object.
        
        Args:
            path: Path to validate
            must_exist: Whether path must exist
            
        Returns:
            Validated Path object
            
        Raises:
            FileNotFoundError: If file doesn't exist and must_exist is True
            ValueError: If path is invalid
        """
        path_obj = Path(path)
        
        if must_exist and not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path_obj}")
        
        return path_obj
    
    @staticmethod
    def validate_file_extension(path: Path, allowed_extensions: set) -> bool:
        """
        Validate file extension.
        
        Args:
            path: File path
            allowed_extensions: Set of allowed extensions (including dot)
            
        Returns:
            True if extension is valid
        """
        return path.suffix.lower() in allowed_extensions
    
    @staticmethod
    def validate_file_size(path: Path, min_size: int = 0, max_size: Optional[int] = None) -> bool:
        """
        Validate file size.
        
        Args:
            path: File path
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes (None for no limit)
            
        Returns:
            True if size is valid
        """
        if not path.exists():
            return False
        
        size = path.stat().st_size
        
        if size < min_size:
            return False
        
        if max_size is not None and size > max_size:
            return False
        
        return True


class SecureUtils:
    """Utility class for security-related operations."""
    
    @staticmethod
    def secure_delete_file(path: Path, passes: int = 3) -> bool:
        """
        Securely delete a file by overwriting it multiple times.
        
        Args:
            path: File path to delete
            passes: Number of overwrite passes
            
        Returns:
            True if successful
        """
        try:
            if not path.exists():
                return True
            
            file_size = path.stat().st_size
            
            with open(path, "r+b") as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            path.unlink()
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def calculate_file_hash(path: Path, algorithm: str = "sha256", chunk_size: int = 8192) -> str:
        """
        Calculate file hash.
        
        Args:
            path: File path
            algorithm: Hash algorithm (sha256, sha512, md5)
            chunk_size: Chunk size for reading
            
        Returns:
            Hexadecimal hash string
        """
        hash_obj = hashlib.new(algorithm)
        
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    @contextmanager
    def temporary_file_permissions(path: Path, permissions: int):
        """
        Temporarily change file permissions.
        
        Args:
            path: File path
            permissions: Temporary permissions (octal)
        """
        original_permissions = path.stat().st_mode
        try:
            path.chmod(permissions)
            yield
        finally:
            path.chmod(original_permissions)


class LoggingUtils:
    """Utility class for logging setup and management."""
    
    @staticmethod
    def setup_logger(name: str, level: int = logging.INFO, 
                    format_string: Optional[str] = None) -> logging.Logger:
        """
        Setup a logger with standard configuration.
        
        Args:
            name: Logger name
            level: Logging level
            format_string: Custom format string
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            
            if format_string is None:
                format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            
            formatter = logging.Formatter(format_string)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.setLevel(level)
        return logger
    
    @staticmethod
    def setup_file_logger(name: str, log_file: Path, level: int = logging.INFO) -> logging.Logger:
        """
        Setup a file logger.
        
        Args:
            name: Logger name
            log_file: Path to log file
            level: Logging level
            
        Returns:
            Configured file logger
        """
        logger = logging.getLogger(name)
        
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(level)
        
        return logger


class ProgressReporter:
    """Simple progress reporter when tqdm is not available."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize progress reporter.
        
        Args:
            total: Total number of items
            description: Description text
        """
        self.total = total
        self.description = description
        self.current = 0
        self.last_percent = -1
    
    def update(self, increment: int = 1) -> None:
        """
        Update progress.
        
        Args:
            increment: Number to increment by
        """
        self.current += increment
        percent = int((self.current / self.total) * 100)
        
        if percent > self.last_percent and percent % 10 == 0:
            print(f"{self.description}: {percent}% ({self.current}/{self.total})")
            self.last_percent = percent
    
    def close(self) -> None:
        """Close progress reporter."""
        if self.current >= self.total:
            print(f"{self.description}: 100% completed!")


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes in human-readable format.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def get_terminal_width() -> int:
    """
    Get terminal width with fallback.
    
    Returns:
        Terminal width in characters
    """
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80  # Default fallback


# Configuration helper
class ConfigManager:
    """Simple configuration manager."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        
        if config_file and config_file.exists():
            self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file and self.config_file.exists():
            import json
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_config(self) -> None:
        """Save configuration to file."""
        if self.config_file:
            import json
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value


if __name__ == '__main__':
    print('This is a utility module - do not execute directly')