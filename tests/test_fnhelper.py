#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the AES Drive helper functions.
"""

import os
import sys
import unittest
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from res.fnhelper_improved import check_arguments


class TestFnHelper(unittest.TestCase):
    """Test cases for the helper functions."""
    
    def test_check_arguments_file(self):
        """Test parsing a file argument."""
        args = ["program.py", "file.aesd"]
        result = check_arguments(args)
        self.assertEqual(result, {"file": "file.aesd"})
    
    def test_check_arguments_file_and_password(self):
        """Test parsing a file and password argument."""
        args = ["program.py", "file.aesd", "-p", "password"]
        result = check_arguments(args)
        self.assertEqual(result, {"file": "file.aesd", "pwd": "password"})
    
    def test_check_arguments_help(self):
        """Test that help argument returns None."""
        with patch('sys.stdout', new=StringIO()):  # Suppress output
            args = ["program.py", "--help"]
            result = check_arguments(args)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()