"""
AES Data File Module - Open source full version


This module contains the AESDataFile class for parsing AES Drive encrypted file headers.
Refactored to follow PEP8 standards and modern Python best practices.

Reference: https://cdn.nsoftware.com/help/NEH/app/nsoftware.AESDrive.htm#pg_aesdfileformat
"""

import binascii
import logging
import sys
from typing import Optional
from pathlib import Path


class AESDataFileError(Exception):
    """Custom exception for AES Data File parsing errors."""
    pass


class AESDataFile:
    """
    Represents an AES Drive encrypted file with parsed header information.
    
    The AES Drive file format contains a 144-byte header with cryptographic
    information needed for decryption.
    
    Header Structure (144 bytes):
    - Bytes 0-3: File type ("AESD")
    - Byte 4: File type version
    - Bytes 5-11: Reserved
    - Bytes 12-15: CRC32 checksum
    - Bytes 16-31: Global salt (16 bytes)
    - Bytes 32-47: File salt (16 bytes)  
    - Bytes 48-127: AES-GCM encrypted header (80 bytes)
    - Bytes 128-143: AES-GCM authentication tag (16 bytes)
    """
    
    EXPECTED_FILE_TYPE = "AESD"
    HEADER_LENGTH = 144
    
    def __init__(self, header: bytes, file_path: Optional[Path] = None):
        """
        Initialize AESDataFile from header bytes.
        
        Args:
            header: 144-byte header from AES Drive file
            file_path: Optional path to the source file (for logging)
            
        Raises:
            AESDataFileError: If header is invalid or corrupted
        """
        self.logger = logging.getLogger(__name__)
        self._file_path = file_path
        
        if len(header) != self.HEADER_LENGTH:
            raise AESDataFileError(
                f"Invalid header length: expected {self.HEADER_LENGTH}, got {len(header)}"
            )
        
        self.raw_header = header
        self._parse_header()
        self._validate_checksum()
        
        self.logger.debug(f"Successfully parsed AES data file header")
    
    def _parse_header(self) -> None:
        """Parse the header bytes into individual components."""
        header = self.raw_header
        
        # Basic file information
        self.file_type = header[0:4].decode("utf-8")
        self.file_type_version = header[4]
        self.reserved_1 = header[5:12]
        
        # Checksum and salts
        self.crc32_checksum = binascii.hexlify(header[12:16])
        self.global_salt = header[16:32]
        self.file_salt = header[32:48]
        
        # Encrypted content
        self.aes_gcm_header = header[48:128]
        self.aes_gcm_auth_tag = header[128:144]
        
        # Validate file type
        if self.file_type != self.EXPECTED_FILE_TYPE:
            raise AESDataFileError(
                f"Invalid file type: expected '{self.EXPECTED_FILE_TYPE}', got '{self.file_type}'"
            )
        
        self.logger.debug(f"File type: {self.file_type}, version: {self.file_type_version}")
    
    def _validate_checksum(self) -> None:
        """Validate the CRC32 checksum of the header."""
        # Create header copy with zeroed checksum field for validation
        header_for_checksum = (
            self.raw_header[0:12] + 
            b'\x00\x00\x00\x00' + 
            self.raw_header[16:144]
        )
        
        # Calculate CRC32
        calculated_crc = binascii.crc32(header_for_checksum)
        calculated_hex = binascii.hexlify(calculated_crc.to_bytes(4, 'big'))
        
        if calculated_hex != self.crc32_checksum:
            raise AESDataFileError(
                f"Checksum mismatch: expected {self.crc32_checksum.decode()}, "
                f"calculated {calculated_hex.decode()}"
            )
        
        self.logger.debug("Header checksum validation passed")
    
    @property
    def is_valid(self) -> bool:
        """Check if the data file appears to be valid."""
        try:
            return (
                self.file_type == self.EXPECTED_FILE_TYPE and
                len(self.global_salt) == 16 and
                len(self.file_salt) == 16 and
                len(self.aes_gcm_header) == 80 and
                len(self.aes_gcm_auth_tag) == 16
            )
        except AttributeError:
            return False
    
    def get_info_dict(self) -> dict:
        """
        Get file information as a dictionary.
        
        Returns:
            Dictionary containing parsed file information
        """
        return {
            'file_type': self.file_type,
            'file_type_version': self.file_type_version,
            'crc32_checksum': self.crc32_checksum.decode(),
            'global_salt_hex': self.global_salt.hex(),
            'file_salt_hex': self.file_salt.hex(),
            'header_length': len(self.aes_gcm_header),
            'auth_tag_length': len(self.aes_gcm_auth_tag),
            'is_valid': self.is_valid
        }
    
    def __str__(self) -> str:
        """String representation of the AES data file."""
        info = self.get_info_dict()
        return (
            f"AESDataFile(type={info['file_type']}, "
            f"version={info['file_type_version']}, "
            f"valid={info['is_valid']})"
        )
    
    def __repr__(self) -> str:
        """Detailed representation of the AES data file."""
        return f"AESDataFile(file_path={self._file_path}, valid={self.is_valid})"


def load_from_file(file_path: Path) -> AESDataFile:
    """
    Load an AESDataFile from a file path.
    
    Args:
        file_path: Path to the AES Drive encrypted file
        
    Returns:
        Parsed AESDataFile object
        
    Raises:
        AESDataFileError: If file cannot be read or parsed
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(AESDataFile.HEADER_LENGTH)
        
        return AESDataFile(header, file_path)
        
    except IOError as e:
        raise AESDataFileError(f"Cannot read file {file_path}: {e}") from e
    except Exception as e:
        raise AESDataFileError(f"Failed to parse file {file_path}: {e}") from e


if __name__ == '__main__':
    print('This is a module - import it rather than running directly')
    sys.exit(1)