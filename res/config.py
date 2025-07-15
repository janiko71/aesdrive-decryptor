"""
Configuration Module - Open source full version

Centralized configuration management for the AES Drive Decryptor.
Contains all constants and configurable parameters.
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """
    Configuration class containing all application constants and settings.
    
    This class centralizes all configuration parameters and makes them
    easily accessible throughout the application.
    """
    
    # File format constants
    HEADER_LENGTH: int = 144
    SECTOR_LENGTH: int = 512
    DEFAULT_FILE_EXTENSION: str = ".aesd"
    
    # Cryptographic constants  
    KDF_ITERATIONS: int = 50000
    PWD_ENCODING: str = "UTF-8"
    
    # Default values
    DEFAULT_PASSWORD: str = "aesdformatguide"  # Only for testing
    DEFAULT_TEST_FILE: str = "test.png.aesd"
    
    # Application metadata
    APP_NAME: str = "AES Drive Decryptor"
    APP_VERSION: str = "2.0.0"
    APP_AUTHOR: str = "Professional refactor of janiko71's work"
    
    # Logging configuration
    DEFAULT_LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file (future enhancement)
        """
        self.config_file = config_file
        self._load_environment_overrides()
    
    def _load_environment_overrides(self) -> None:
        """Load configuration overrides from environment variables."""
        # Allow environment variable overrides
        self.KDF_ITERATIONS = int(os.getenv('AES_KDF_ITERATIONS', self.KDF_ITERATIONS))
        self.PWD_ENCODING = os.getenv('AES_PWD_ENCODING', self.PWD_ENCODING)
        self.DEFAULT_LOG_LEVEL = os.getenv('AES_LOG_LEVEL', self.DEFAULT_LOG_LEVEL)
    
    @property
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return os.getenv('AES_DEBUG', '').lower() in ('1', 'true', 'yes')
    
    def get_temp_dir(self) -> Path:
        """Get temporary directory for intermediate files."""
        temp_dir = Path(os.getenv('AES_TEMP_DIR', '/tmp'))
        temp_dir.mkdir(exist_ok=True)
        return temp_dir
    
    def validate(self) -> bool:
        """
        Validate configuration parameters.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if self.KDF_ITERATIONS < 1000:
            return False
            
        if self.HEADER_LENGTH < 1:
            return False
            
        if self.SECTOR_LENGTH < 1:
            return False
            
        return True
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return (
            f"Config(kdf_iterations={self.KDF_ITERATIONS}, "
            f"header_length={self.HEADER_LENGTH}, "
            f"sector_length={self.SECTOR_LENGTH})"
        )


# Global configuration instance (can be overridden)
default_config = Config()


def get_config() -> Config:
    """Get the current configuration instance."""
    return default_config


def set_config(config: Config) -> None:
    """Set a new configuration instance."""
    global default_config
    default_config = config