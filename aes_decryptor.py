#!/usr/bin/env python3
"""
AES Drive Decryptor - Open source full version

A completely documented tool for decrypting AES Drive encrypted files.
This implementation follows PEP8 standards and modern Python best practices.

Author: Refactored from original by janiko71
License: MIT
"""

import argparse
import hashlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from res.aes_data_file import AESDataFile
from res.crypto_helper import CryptoHelper
from res.config import Config


class AESDecryptorError(Exception):
    """Custom exception for AES Decryptor errors."""
    pass


class AESDecryptor:
    """
    Professional AES Drive file decryptor.
    
    This class handles the decryption of AES Drive encrypted files using
    XTS-AES encryption with proper error handling and logging.
    """

    def __init__(self, config: Config):
        """
        Initialize the AES Decryptor.
        
        Args:
            config: Configuration object containing decryption parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.backend = default_backend()
        
    def decrypt_file(self, input_path: Path, password: str, 
                    output_path: Optional[Path] = None) -> bool:
        """
        Decrypt an AES Drive encrypted file.
        
        Args:
            input_path: Path to the encrypted file
            password: Decryption password
            output_path: Optional output path (defaults to input without .aesd)
            
        Returns:
            True if decryption was successful, False otherwise
            
        Raises:
            AESDecryptorError: If decryption fails
        """
        try:
            # Validate input file
            if not self._validate_input_file(input_path):
                return False
                
            # Determine output path
            if output_path is None:
                output_path = self._get_output_path(input_path)
                
            self.logger.info(f"Starting decryption of {input_path}")
            self.logger.info(f"Output will be saved to {output_path}")
            
            # Load and parse the encrypted file
            data_file = self._load_data_file(input_path)
            
            # Derive encryption keys from password
            header_key, init_vector = self._derive_keys(password, data_file)
            
            # Decrypt the file header
            xts_key, file_length = self._decrypt_header(
                data_file, header_key, init_vector
            )
            
            # Decrypt the file content
            self._decrypt_content(
                input_path, output_path, xts_key, file_length, data_file
            )
            
            self.logger.info(f"Successfully decrypted file to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise AESDecryptorError(f"Failed to decrypt file: {e}") from e
    
    def _validate_input_file(self, input_path: Path) -> bool:
        """Validate the input file exists and has correct extension."""
        if not input_path.exists():
            self.logger.error(f"Input file not found: {input_path}")
            return False
            
        if input_path.suffix.lower() != '.aesd':
            self.logger.error(f"Invalid file extension: {input_path.suffix}")
            return False
            
        return True
    
    def _get_output_path(self, input_path: Path) -> Path:
        """Generate output path by removing .aesd extension."""
        return input_path.with_suffix('')
    
    def _load_data_file(self, input_path: Path) -> AESDataFile:
        """Load and parse the AES data file."""
        with open(input_path, 'rb') as f:
            header = f.read(self.config.HEADER_LENGTH)
            
        data_file = AESDataFile(header)
        self.logger.debug(f"Loaded data file with version {data_file.file_type_version}")
        
        return data_file
    
    def _derive_keys(self, password: str, data_file: AESDataFile) -> Tuple[bytes, bytes]:
        """
        Derive encryption keys from password and salts.
        
        Returns:
            Tuple of (header_encryption_key, init_vector)
        """
        # Derive password key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=data_file.global_salt,
            iterations=self.config.KDF_ITERATIONS,
            backend=self.backend
        )
        
        pwd_derived_key = kdf.derive(password.encode(self.config.PWD_ENCODING))
        self.logger.debug("Password key derived successfully")
        
        # Generate file seed and hash
        file_seed = data_file.file_salt + pwd_derived_key
        file_key_hash = hashlib.sha512(file_seed).digest()
        
        header_encryption_key = file_key_hash[:32]
        init_vector = file_key_hash[32:44]
        
        self.logger.debug("Header encryption key and IV generated")
        
        return header_encryption_key, init_vector
    
    def _decrypt_header(self, data_file: AESDataFile, 
                       header_key: bytes, init_vector: bytes) -> Tuple[bytes, int]:
        """
        Decrypt the file header to extract XTS keys.
        
        Returns:
            Tuple of (xts_key, file_length)
        """
        aesgcm = AESGCM(header_key)
        encrypted_msg = data_file.aes_gcm_header + data_file.aes_gcm_auth_tag
        
        try:
            decrypted_header = aesgcm.decrypt(init_vector, encrypted_msg, None)
            self.logger.debug("Header decrypted successfully")
        except InvalidTag as e:
            raise AESDecryptorError("Invalid authentication tag - wrong password?") from e
        
        # Parse decrypted header
        padding_length = int.from_bytes(decrypted_header[0:2], 'big')
        xts_key1 = decrypted_header[16:48]
        xts_key2 = decrypted_header[48:80]
        xts_key = xts_key1 + xts_key2
        
        # Calculate actual file length
        file_stats = os.stat(data_file._file_path) if hasattr(data_file, '_file_path') else None
        if file_stats:
            file_length = file_stats.st_size - self.config.HEADER_LENGTH - padding_length
        else:
            # Fallback calculation
            file_length = len(data_file.raw_header) - self.config.HEADER_LENGTH - padding_length
        
        self.logger.debug(f"XTS keys extracted, file length: {file_length}")
        
        return xts_key, file_length
    
    def _decrypt_content(self, input_path: Path, output_path: Path, 
                        xts_key: bytes, file_length: int, data_file: AESDataFile) -> None:
        """Decrypt the file content using XTS-AES."""
        start_time = time.time()
        
        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            # Skip header
            f_in.read(self.config.HEADER_LENGTH)
            
            current_sector = 0
            bytes_processed = 0
            
            while bytes_processed < file_length:
                chunk = f_in.read(self.config.SECTOR_LENGTH)
                if not chunk:
                    break
                
                # Create XTS tweak
                tweak = current_sector.to_bytes(16, 'little')
                
                # Decrypt chunk
                cipher = Cipher(algorithms.AES(xts_key), modes.XTS(tweak))
                decryptor = cipher.decryptor()
                decrypted_chunk = decryptor.update(chunk)
                
                # Handle last block
                remaining_bytes = file_length - bytes_processed
                if remaining_bytes < self.config.SECTOR_LENGTH:
                    f_out.write(decrypted_chunk[:remaining_bytes])
                    break
                else:
                    f_out.write(decrypted_chunk)
                
                bytes_processed += self.config.SECTOR_LENGTH
                current_sector += 1
                
                # Progress logging
                if current_sector % 100 == 0:
                    progress = (bytes_processed / file_length) * 100
                    self.logger.debug(f"Decryption progress: {progress:.1f}%")
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"File content decrypted in {elapsed_time:.2f} seconds")


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='AES Drive Decryptor - Professional Python implementation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.aesd                          # Interactive password prompt
  %(prog)s file.aesd -p mypassword           # Password from command line
  %(prog)s file.aesd -o decrypted.txt       # Custom output file
  %(prog)s file.aesd -v                     # Verbose logging
        """
    )
    
    parser.add_argument(
        'input_file',
        type=Path,
        help='Path to the AES Drive encrypted file (.aesd)'
    )
    
    parser.add_argument(
        '-p', '--password',
        type=str,
        help='Decryption password (will prompt if not provided)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path (default: input file without .aesd extension)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AES Drive Decryptor 2.0.0'
    )
    
    return parser.parse_args()


def get_password() -> str:
    """Get password from user input securely."""
    import getpass
    return getpass.getpass("AES Drive password: ")


def main() -> int:
    """Main entry point of the application."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)
        
        # Get password
        password = args.password or get_password()
        
        # Initialize configuration and decryptor
        config = Config()
        decryptor = AESDecryptor(config)
        
        # Perform decryption
        success = decryptor.decrypt_file(
            input_path=args.input_file,
            password=password,
            output_path=args.output
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except AESDecryptorError as e:
        logging.getLogger(__name__).error(f"Decryption error: {e}")
        return 1
    except Exception as e:
        logging.getLogger(__name__).error(f"Unexpected error: {e}")
        return 1
    finally:
        # Secure cleanup
        if 'password' in locals():
            password = None


if __name__ == '__main__':
    sys.exit(main())