#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the AES Drive DataFile module.
"""

import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from res.aesdatafile import DataFile


class TestDataFile(unittest.TestCase):
    """Test cases for the DataFile class."""
    
    def test_invalid_header_length(self):
        """Test that an invalid header length raises a ValueError."""
        with self.assertRaises(ValueError):
            DataFile(b'too short')
    
    def test_checksum_verification(self):
        """Test that a header with an invalid checksum raises a ValueError."""
        # Create a mock header with an invalid checksum
        mock_header = bytearray(144)
        mock_header[0:4] = b'AESD'  # File type
        mock_header[4] = 1  # Version
        # The checksum bytes are at positions 12-16
        mock_header[12:16] = b'\x00\x00\x00\x01'  # Invalid checksum
        
        with self.assertRaises(ValueError):
            DataFile(bytes(mock_header))


if __name__ == '__main__':
    unittest.main()