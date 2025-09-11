#!/usr/bin/env python3
"""
Example script to demonstrate running the workflow integration tests.

This script shows how to run the tests and what to expect.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def main():
    """Main example runner."""
    print("Workflow Automation Platform - Test Example")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("Error: tests directory not found. Please run from backend directory.")
        sys.exit(1)
    
    # Example 1: Run a simple unit test
    print("\n1. Running a simple unit test (user authentication)...")
    success = run_command(
        ["python", "-m", "pytest", "tests/test_workflows.py::TestUserAuthentication::test_user_registration", "-v"],
        "User Registration Test"
    )
    
    if not success:
        print("❌ Unit test failed. Check the output above.")
        return
    
    # Example 2: Run all authentication tests
    print("\n2. Running all authentication tests...")
    success = run_command(
        ["python", "-m", "pytest", "tests/test_workflows.py::TestUserAuthentication", "-v"],
        "All Authentication Tests"
    )
    
    if not success:
        print("❌ Authentication tests failed. Check the output above.")
        return
    
    # Example 3: Run quick tests (excluding integration)
    print("\n3. Running quick tests (excluding integration tests)...")
    success = run_command(
        ["python", "-m", "pytest", "-m", "not integration", "-v"],
        "Quick Tests (No Integration)"
    )
    
    if not success:
        print("❌ Quick tests failed. Check the output above.")
        return
    
    print("\n✅ All example tests completed successfully!")
    print("\nNext steps:")
    print("1. Run full test suite: python run_tests.py")
    print("2. Run with coverage: python run_tests.py --coverage")
    print("3. Run integration tests: python run_tests.py --integration")
    print("4. Check test documentation: tests/README.md")


if __name__ == "__main__":
    main()
