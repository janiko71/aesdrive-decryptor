#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AES Drive Data File Module

This module provides functionality to parse and validate AES Drive encrypted file headers.
It implements the header structure according to the AES Drive file format specification.

Reference: https://cdn.nsoftware.com/help/NEH/app/nsoftware.AESDrive.htm#pg_aesdfileformat
"""

import os
import sys
import binascii as ba
from typing import Optional, Union, BinaryIO


class DataFile:
    """
    Class representing an AES Drive encrypted file.
    
    This class parses and validates the header of an AES Drive encrypted file,
    extracting the necessary information for decryption.
    """
    
    def __init__(self, header: bytes):
        """
        Initialize a DataFile object by parsing the provided header.
        
        Args:
            header: The 144-byte header from an AES Drive encrypted file
            
        Raises:
            ValueError: If the header is not 144 bytes long
            SystemExit: If the header checksum verification fails
        """
        if len(header) != 144:
            raise ValueError(f"Invalid header length: {len(header)} bytes (expected 144 bytes)")
            
        self.raw_header = header
        
        # Parse header fields
        self.file_type = header[0:4].decode("utf-8")
        self.file_type_version = header[4]
        self.reserved_1 = header[5:12]
        self.crc32_checksum = ba.hexlify(header[12:16])
        self.global_salt = header[16:32]
        self.file_salt = header[32:48]
        self.aes_gcm_header = header[48:128]
        self.aes_gcm_auth_tag = header[128:144]
        
        # Verify header checksum
        self._verify_checksum()
    
    def _verify_checksum(self) -> None:
        """
        Verify the CRC32 checksum of the header.
        
        The checksum is calculated over the entire header with the checksum field
        itself set to zero.
        
        Raises:
            SystemExit: If the checksum verification fails
        """
        # Create a copy of the header with checksum bytes set to zero
        header_copy = self.raw_header[0:12] + b'\x00\x00\x00\x00' + self.raw_header[16:144]
        
        # Calculate CRC32 checksum
        calculated_checksum = ba.crc32(header_copy)
        calculated_checksum_hex = ba.hexlify(calculated_checksum.to_bytes(4, 'big'))
        
        # Verify checksum
        if calculated_checksum_hex != self.crc32_checksum:
            raise ValueError(f"Header checksum verification failed. Expected: {self.crc32_checksum.decode()}, Got: {calculated_checksum_hex.decode()}")
    
    def __str__(self) -> str:
        """
        Return a string representation of the DataFile.
        
        Returns:
            A string containing the key properties of the DataFile
        """
        return (
            f"AES Drive Data File (v{self.file_type_version})\n"
            f"File type: {self.file_type}\n"
            f"CRC32 checksum: {self.crc32_checksum.decode()}\n"
            f"Global salt: {self.global_salt.hex()}\n"
            f"File salt: {self.file_salt.hex()}"
        )


# Module guard
if __name__ == '__main__':
    print('This is a module and should not be executed directly.')
    sys.exit(1)