#!/usr/bin/env python3
"""
Script to run all tests for the AI Docs Generator project.
"""
import os
import sys
import unittest
import pytest

def run_tests():
    """Run all unit tests using unittest."""
    print("Running tests...")
    # Add the project root to the path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, root_dir)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(root_dir, 'tests')
    suite = loader.discover(start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def run_pytest():
    """Run all tests using pytest."""
    print("Running tests with pytest...")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, root_dir)
    
    return pytest.main(['-xvs', 'tests'])

if __name__ == '__main__':
    # Check if pytest is preferred
    if len(sys.argv) > 1 and sys.argv[1] == '--pytest':
        sys.exit(run_pytest())
    else:
        sys.exit(run_tests()) 