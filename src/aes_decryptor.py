#!/usr/bin/env python3
"""
AES Drive Decryptor - Expert Open Source Edition

A robust, professional-grade tool for decrypting AES Drive encrypted files.
Supports .aesd and .aesf file formats with comprehensive error handling,
logging, and security features.

Author: Jean GEBAROWSKI (janiko71)
License: MIT
Version: 2.0.0
"""

import os
import sys
import logging
import argparse
import time
import hashlib
import getpass
import mmap
from pathlib import Path
from typing import Optional, Tuple, BinaryIO
from dataclasses import dataclass
from contextlib import contextmanager

# Crypto imports
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag

# Third-party imports
# Local imports
from utils import (
    ColorFormatter, ParameterFormatter, FileValidator, 
    SecureUtils, LoggingUtils, format_bytes, format_duration,
    SecureMemory
)

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


# Constants
class Config:
    """Configuration constants for AES Drive decryption."""
    
    # File format constants
    HEADER_LENGTH = 144
    SECTOR_LENGTH = 512
    EXPECTED_FILE_TYPE = "AESD"
    SUPPORTED_EXTENSIONS = {".aesd", ".aesf"}
    
    # Cryptographic constants
    KDF_ITERATIONS = 50000
    PWD_ENCODING = "utf-8"
    AES_KEY_SIZE = 32
    XTS_KEY_SIZE = 64
    INIT_VECTOR_SIZE = 12
    
    # Default values
    DEFAULT_PASSWORD = "aesdformatguide"
    
    # Security
    SECURE_DELETE_PASSES = 3


@dataclass
class DecryptionStats:
    """Statistics for decryption operation."""
    
    file_size: int = 0
    decrypted_size: int = 0
    sectors_processed: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    
    @property
    def duration(self) -> float:
        """Get decryption duration in seconds."""
        return self.end_time - self.start_time
    
    @property
    def throughput_mb_s(self) -> float:
        """Get throughput in MB/s."""
        if self.duration <= 0:
            return 0.0
        return (self.decrypted_size / (1024 * 1024)) / self.duration


class AESDataFile:
    """Represents an AES Drive encrypted file with parsing capabilities."""
    
    def __init__(self, header_data: bytes):
        """
        Initialize AES data file from header.
        
        Args:
            header_data: Raw header bytes (144 bytes expected)
            
        Raises:
            ValueError: If header is invalid
        """
        if len(header_data) != Config.HEADER_LENGTH:
            raise ValueError(f"Invalid header length: {len(header_data)}, expected {Config.HEADER_LENGTH}")
        
        self.raw_header = header_data
        self._parse_header()
        self._verify_checksum()
    
    def _parse_header(self) -> None:
        """Parse the file header into components."""
        h = self.raw_header
        
        # Parse header fields
        self.file_type = h[0:4].decode("utf-8")
        self.file_type_version = h[4]
        self.reserved_1 = h[5:12]
        self.crc32_checksum = h[12:16]
        self.global_salt = h[16:32]
        self.file_salt = h[32:48]
        self.aes_gcm_header = h[48:128]
        self.aes_gcm_auth_tag = h[128:144]
        
        # Validate file type
        if self.file_type != Config.EXPECTED_FILE_TYPE:
            raise ValueError(f"Invalid file type: {self.file_type}, expected {Config.EXPECTED_FILE_TYPE}")
    
    def _verify_checksum(self) -> None:
        """Verify header CRC32 checksum."""
        import binascii
        
        # Create header copy with zeroed checksum for verification
        header_copy = (self.raw_header[0:12] + 
                      b'\x00\x00\x00\x00' + 
                      self.raw_header[16:144])
        
        calculated_crc = binascii.crc32(header_copy)
        expected_crc = int.from_bytes(self.crc32_checksum, 'big', signed=True)
        
        if calculated_crc != expected_crc:
            raise ValueError("Header CRC32 checksum verification failed")


# SecureMemory is now imported from utils


class AESDecryptorError(Exception):
    """Base exception for AES Decryptor errors."""
    pass


class InvalidPasswordError(AESDecryptorError):
    """Raised when password is incorrect."""
    pass


class FileFormatError(AESDecryptorError):
    """Raised when file format is invalid."""
    pass


class AESDecryptor:
    """Professional AES Drive decryptor with comprehensive error handling."""
    
    def __init__(self, verbose: bool = False, progress: bool = True):
        """
        Initialize AES Decryptor.
        
        Args:
            verbose: Enable verbose logging
            progress: Show progress bar during decryption
        """
        self.verbose = verbose
        self.progress = progress and HAS_TQDM
        self.logger = LoggingUtils.setup_logger(__name__, 
                                              logging.DEBUG if verbose else logging.INFO)
        self.color_formatter = ColorFormatter()
        self.param_formatter = ParameterFormatter(self.color_formatter)
    
    def _validate_input_file(self, filepath: Path) -> None:
        """
        Validate input file.
        
        Args:
            filepath: Path to input file
            
        Raises:
            FileFormatError: If file format is invalid
            FileNotFoundError: If file doesn't exist
        """
        FileValidator.validate_path(filepath, must_exist=True)
        
        if not FileValidator.validate_file_extension(filepath, Config.SUPPORTED_EXTENSIONS):
            raise FileFormatError(
                f"Unsupported file extension: {filepath.suffix}. "
                f"Supported: {', '.join(Config.SUPPORTED_EXTENSIONS)}"
            )
        
        if not FileValidator.validate_file_size(filepath, min_size=Config.HEADER_LENGTH):
            raise FileFormatError("File too small to contain valid header")
    
    def _derive_keys(self, password: str, data_file: AESDataFile) -> Tuple[bytes, bytes]:
        """
        Derive encryption keys from password and file salts.
        
        Args:
            password: User password
            data_file: Parsed AES data file
            
        Returns:
            Tuple of (header_encryption_key, init_vector)
        """
        self.logger.debug("Deriving keys from password")
        
        # Derive password-based key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=Config.AES_KEY_SIZE,
            salt=data_file.global_salt,
            iterations=Config.KDF_ITERATIONS,
            backend=default_backend()
        )
        
        pwd_derived_key = kdf.derive(password.encode(Config.PWD_ENCODING))
        
        # Create file seed (salt + derived key)
        file_seed = data_file.file_salt + pwd_derived_key
        
        # Generate file key hash
        file_key_hash = hashlib.sha512(file_seed).digest()
        
        # Extract keys
        header_encryption_key = file_key_hash[:Config.AES_KEY_SIZE]
        init_vector = file_key_hash[Config.AES_KEY_SIZE:Config.AES_KEY_SIZE + Config.INIT_VECTOR_SIZE]
        
        return header_encryption_key, init_vector
    
    def _decrypt_header(self, data_file: AESDataFile, header_key: bytes, iv: bytes) -> bytes:
        """
        Decrypt the file header.
        
        Args:
            data_file: Parsed AES data file
            header_key: Header encryption key
            iv: Initialization vector
            
        Returns:
            Decrypted header data
            
        Raises:
            InvalidPasswordError: If password is incorrect
        """
        self.logger.debug("Decrypting file header")
        
        try:
            aesgcm = AESGCM(header_key)
            encrypted_msg = data_file.aes_gcm_header + data_file.aes_gcm_auth_tag
            return aesgcm.decrypt(iv, encrypted_msg, None)
        except InvalidTag:
            raise InvalidPasswordError("Invalid password or corrupted file")
    
    def _extract_xts_keys(self, decrypted_header: bytes) -> Tuple[bytes, int]:
        """
        Extract XTS keys and padding length from decrypted header.
        
        Args:
            decrypted_header: Decrypted header data
            
        Returns:
            Tuple of (combined_xts_key, padding_length)
        """
        padding_length = int.from_bytes(decrypted_header[0:2], 'big')
        xts_key1 = decrypted_header[16:48]
        xts_key2 = decrypted_header[48:80]
        
        combined_xts_key = xts_key1 + xts_key2
        
        self.logger.debug(f"Extracted XTS keys, padding length: {padding_length}")
        return combined_xts_key, padding_length
    
    def _decrypt_file_data(self, input_file: BinaryIO, output_file: BinaryIO, 
                          xts_key: bytes, file_length: int) -> DecryptionStats:
        """
        Decrypt file data using XTS-AES.
        
        Args:
            input_file: Input file handle
            output_file: Output file handle  
            xts_key: XTS encryption key
            file_length: Expected decrypted file length
            
        Returns:
            Decryption statistics
        """
        stats = DecryptionStats()
        stats.start_time = time.time()
        
        # Calculate total sectors for progress bar
        total_sectors = (file_length + Config.SECTOR_LENGTH - 1) // Config.SECTOR_LENGTH
        
        # Setup progress bar if available
        progress_bar = None
        if self.progress:
            progress_bar = tqdm(
                total=total_sectors,
                unit='sectors',
                desc='Decrypting',
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} sectors [{elapsed}<{remaining}, {rate_fmt}]'
            )
        
        current_sector = 0
        bytes_written = 0
        
        try:
            while bytes_written < file_length:
                # Read sector
                chunk = input_file.read(Config.SECTOR_LENGTH)
                if not chunk:
                    break
                
                # Prepare tweak for XTS mode
                tweak = current_sector.to_bytes(16, 'little')
                
                # Decrypt sector
                decryptor = Cipher(
                    algorithms.AES(xts_key), 
                    modes.XTS(tweak)
                ).decryptor()
                
                decrypted_chunk = decryptor.update(chunk) + decryptor.finalize()
                
                # Write appropriate amount of data
                remaining_bytes = file_length - bytes_written
                bytes_to_write = min(len(decrypted_chunk), remaining_bytes)
                
                output_file.write(decrypted_chunk[:bytes_to_write])
                bytes_written += bytes_to_write
                
                # Update statistics
                stats.sectors_processed += 1
                current_sector += 1
                
                # Update progress bar
                if progress_bar:
                    progress_bar.update(1)
        
        finally:
            if progress_bar:
                progress_bar.close()
        
        stats.end_time = time.time()
        stats.decrypted_size = bytes_written
        
        return stats
    
    def decrypt_file(self, input_path: Path, output_path: Optional[Path] = None, 
                    password: Optional[str] = None) -> DecryptionStats:
        """
        Decrypt an AES Drive encrypted file.
        
        Args:
            input_path: Path to encrypted file
            output_path: Path for decrypted file (auto-generated if None)
            password: Decryption password (prompted if None)
            
        Returns:
            Decryption statistics
            
        Raises:
            Various AESDecryptorError subclasses for different error conditions
        """
        # Validate input
        self._validate_input_file(input_path)
        
        # Determine output path
        if output_path is None:
            output_path = input_path.with_suffix('')
        
        # Get password if not provided
        if password is None:
            password = getpass.getpass("AES Drive password: ") or Config.DEFAULT_PASSWORD
        
        self.logger.info(f"Decrypting {input_path} -> {output_path}")
        
        try:
            with open(input_path, 'rb') as input_file:
                # Read and parse header
                header_data = input_file.read(Config.HEADER_LENGTH)
                data_file = AESDataFile(header_data)
                
                # Derive keys
                header_key, iv = self._derive_keys(password, data_file)
                
                # Clear password from memory
                password = None
                
                # Decrypt header
                decrypted_header = self._decrypt_header(data_file, header_key, iv)
                
                # Extract XTS keys
                xts_key, padding_length = self._extract_xts_keys(decrypted_header)
                
                # Calculate actual file length
                file_size = input_path.stat().st_size
                file_length = file_size - Config.HEADER_LENGTH - padding_length
                
                self.logger.info(f"File size: {file_size}, Data length: {file_length}")
                
                # Decrypt file data
                with open(output_path, 'wb') as output_file:
                    stats = self._decrypt_file_data(input_file, output_file, xts_key, file_length)
                
                stats.file_size = file_size
                
                # Log completion
                self.logger.info(
                    f"Decryption completed in {stats.duration:.2f}s "
                    f"({stats.throughput_mb_s:.2f} MB/s)"
                )
                
                return stats
                
        except Exception as e:
            # Clean up output file on error
            if output_path.exists():
                try:
                    output_path.unlink()
                except OSError:
                    pass
            raise


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Professional AES Drive Decryptor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf.aesd
  %(prog)s file.aesd -o decrypted.pdf -p mypassword
  %(prog)s file.aesd --verbose --no-progress
        """
    )
    
    parser.add_argument(
        'input_file',
        type=Path,
        help='Encrypted file to decrypt (.aesd or .aesf)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path (auto-generated if not specified)'
    )
    
    parser.add_argument(
        '-p', '--password',
        help='Decryption password (prompted if not provided)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bar'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AES Drive Decryptor 2.0.0'
    )
    
    return parser


def main() -> int:
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Create decryptor
    decryptor = AESDecryptor(
        verbose=args.verbose,
        progress=not args.no_progress
    )
    
    try:
        # Perform decryption
        stats = decryptor.decrypt_file(
            input_path=args.input_file,
            output_path=args.output,
            password=args.password
        )
        
        # Print summary
        print(f"\n{self.color_formatter.success('Decryption completed successfully!')}")
        print(f"File size: {format_bytes(stats.file_size)}")
        print(f"Decrypted: {format_bytes(stats.decrypted_size)}")
        print(f"Duration: {format_duration(stats.duration)}")
        print(f"Throughput: {stats.throughput_mb_s:.2f} MB/s")
        
        return 0
        
    except KeyboardInterrupt:
        color_formatter = ColorFormatter()
        print(f"\n{color_formatter.warning('Operation cancelled by user')}")
        return 1
        
    except AESDecryptorError as e:
        color_formatter = ColorFormatter()
        print(f"{color_formatter.error(str(e))}")
        return 1
        
    except Exception as e:
        color_formatter = ColorFormatter()
        print(f"{color_formatter.error(f'Unexpected error: {e}')}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())