#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run all tests for the AES Drive tools.
"""

import unittest
import sys
from pathlib import Path

# Add the tests directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Discover and run all tests
if __name__ == '__main__':
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())