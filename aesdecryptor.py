#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AES Drive Decryptor

This module provides functionality to decrypt files encrypted with the AES Drive solution.
It implements the decryption algorithm according to the AES Drive file format specification.

Usage:
    python aesdecryptor.py [file] [options]
    
    Options:
        -p, --pwd PASSWORD    Specify the AES Drive password
        -h, --help            Show help message and exit
"""

import os
import sys
import hashlib
import time
import getpass
import logging
from typing import Dict, Optional, Union, BinaryIO

# Cryptography imports
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# Local imports
import res.aesdatafile as aesdatafile
import res.fnhelper as helper

# Constants
DEFAULT_FILE = "test.png.aesd"
KDF_ITERATIONS = 50000
DEFAULT_PWD = "aesdformatguide"
PWD_ENCODING = "UTF8"
HEADER_LENGTH = 144
SECTOR_LENGTH = 512


class AESDecryptor:
    """
    A class that handles the decryption of AES Drive encrypted files.
    
    This class encapsulates the logic for decrypting files that have been
    encrypted using the AES Drive solution.
    """
    
    def __init__(self, data_filepath: str, password: str):
        """
        Initialize the AESDecryptor with a file path and password.
        
        Args:
            data_filepath: Path to the encrypted file
            password: Password for decryption
        
        Raises:
            FileNotFoundError: If the specified file does not exist
            ValueError: If the file does not have the correct extension
        """
        self.data_filepath = data_filepath
        self.password = password
        self.backend = default_backend()
        
        # Validate file
        if not os.path.isfile(data_filepath):
            raise FileNotFoundError(f"File '{data_filepath}' not found!")
        
        # Check file extension
        self.encrypted_data_filename, self.encrypted_data_fileext = os.path.splitext(data_filepath)
        self.original_dir, self.original_file = os.path.split(data_filepath)
        
        if self.encrypted_data_fileext != ".aesd":
            raise ValueError(f"Error: the file you want to decrypt has a bad suffix (filename: {self.encrypted_data_filename})")
        
        # Output filename is the same as input without the .aesd extension
        self.output_filename = self.encrypted_data_filename
        
        # Read file header
        with open(data_filepath, "rb") as f_in:
            self.file_header = f_in.read(HEADER_LENGTH)
        
        # Parse header
        self.data_file = aesdatafile.DataFile(self.file_header)
        self.file_stats = os.stat(data_filepath)
        
        # Initialize crypto elements
        self._init_crypto()
    
    def _init_crypto(self) -> None:
        """
        Initialize cryptographic elements needed for decryption.
        
        This method derives the necessary keys from the password and prepares
        for the decryption process.
        """
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=self.data_file.global_salt,
            iterations=KDF_ITERATIONS,
            backend=self.backend
        )
        
        self.pwd_derived_key = kdf.derive(self.password.encode(PWD_ENCODING))
        
        # Clear password from memory for security
        self.password = None
        
        # Create file seed (note: salt comes before derived key according to spec)
        self.file_seed = self.data_file.file_salt + self.pwd_derived_key
        
        # Generate file key hash
        sha512 = hashlib.sha512()
        sha512.update(self.file_seed)
        self.file_key_hash = sha512.digest()
        
        # Extract encryption key and initialization vector
        self.header_encryption_key = self.file_key_hash[0:32]
        self.init_vector = self.file_key_hash[32:44]
    
    def decrypt_header(self) -> bytes:
        """
        Decrypt the AES-GCM encrypted header.
        
        Returns:
            bytes: The decrypted header
            
        Raises:
            InvalidTag: If decryption fails (likely due to wrong password)
            Exception: For other decryption errors
        """
        aesgcm = AESGCM(self.header_encryption_key)
        
        # Combine header and auth tag for decryption
        encrypted_msg = self.data_file.aes_gcm_header + self.data_file.aes_gcm_auth_tag
        
        try:
            return aesgcm.decrypt(self.init_vector, encrypted_msg, None)
        except InvalidTag:
            logging.error("Failed to decrypt header. Invalid authentication tag - likely wrong password.")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during header decryption: {e}")
            raise
    
    def decrypt_file(self) -> None:
        """
        Decrypt the entire file using the XTS-AES mode.
        
        This method decrypts the file content sector by sector and writes
        the decrypted data to the output file.
        """
        logging.info(f"Decrypting '{self.data_filepath}' file...")
        
        # Decrypt the header first to get XTS keys
        decrypted_header = self.decrypt_header()
        
        # Parse the decrypted header
        header_padding_length = int.from_bytes(decrypted_header[0:2], 'big')
        header_xts_key1 = decrypted_header[16:48]
        header_xts_key2 = decrypted_header[48:80]
        
        # Combine XTS keys
        xts_key = header_xts_key1 + header_xts_key2
        
        # Calculate expected file length
        file_length = self.file_stats.st_size - HEADER_LENGTH - header_padding_length
        
        # Start decryption
        t0 = time.time()
        
        with open(self.data_filepath, "rb") as f_in, open(self.output_filename, "wb") as f_out:
            # Skip header
            f_in.seek(HEADER_LENGTH)
            
            current_sector_offset = 0
            byte_offset = 0
            
            while True:
                chunk = f_in.read(SECTOR_LENGTH)
                if not chunk:
                    break
                
                # Create tweak value for XTS mode
                tweak = current_sector_offset.to_bytes(16, 'little')
                
                # Decrypt the chunk
                decryptor_xts = Cipher(algorithms.AES(xts_key), modes.XTS(tweak), backend=self.backend).decryptor()
                decrypted_chunk = decryptor_xts.update(chunk)
                
                byte_offset += SECTOR_LENGTH
                
                # Handle the last block which might be partial
                if byte_offset > file_length:
                    last_block_length = file_length % SECTOR_LENGTH
                    f_out.write(decrypted_chunk[0:last_block_length])
                    break
                else:
                    f_out.write(decrypted_chunk)
                
                # Move to next sector
                current_sector_offset += 1
        
        execution_time = time.time() - t0
        logging.info(f"File decrypted in {execution_time:.2f} seconds")
    
    def print_file_info(self) -> None:
        """
        Print information about the file being decrypted.
        """
        helper.print_parameter("Data directory", os.path.abspath(self.original_dir))
        helper.print_parameter("File name (input)", self.original_file)
        helper.print_parameter("File name (output)", self.output_filename)
        helper.print_data_file_info(self.data_file)


def parse_arguments(argv: list) -> Dict[str, str]:
    """
    Parse command line arguments.
    
    Args:
        argv: List of command line arguments
        
    Returns:
        Dictionary containing the parsed arguments
    """
    return helper.check_arguments(argv)


def main() -> None:
    """
    Main function to run the decryptor.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    arguments = parse_arguments(sys.argv)
    if arguments is None:
        return
    
    try:
        # Get file path
        data_filepath = arguments.get("file") if arguments.get("file") else input("Data file: ") or DEFAULT_FILE
        
        # Get password
        pwd = arguments.get("pwd") if arguments.get("pwd") else getpass.getpass(prompt="AES Drive password: ") or DEFAULT_PWD
        
        # Create decryptor
        decryptor = AESDecryptor(data_filepath, pwd)
        
        # Print file info
        print('-'*72)
        decryptor.print_file_info()
        print('-'*72)
        
        # Decrypt file
        print("Start decrypting...")
        print("-"*72)
        decryptor.decrypt_file()
        
        print()
        print("-"*72)
        print("End of decrypting...")
        print("="*72)
        
    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
    except ValueError as e:
        logging.error(f"Value error: {e}")
    except InvalidTag:
        logging.error("Decryption failed: Invalid password or corrupted file")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
