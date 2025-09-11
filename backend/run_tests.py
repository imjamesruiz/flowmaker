#!/usr/bin/env python3
"""
Test runner script for workflow automation platform.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --quick            # Run quick tests (exclude slow/integration)
    python run_tests.py --coverage         # Run with coverage report
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", coverage=False, verbose=True):
    """Run tests with specified options."""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    if test_type == "unit":
        cmd.extend(["-m", "not integration and not slow"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "quick":
        cmd.extend(["-m", "not integration and not slow"])
    else:  # all
        pass
    
    cmd.append("tests/")
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run workflow automation tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--quick", action="store_true", help="Run quick tests (exclude slow/integration)")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--quiet", action="store_true", help="Run in quiet mode")
    
    args = parser.parse_args()
    
    # Determine test type
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    elif args.quick:
        test_type = "quick"
    else:
        test_type = "all"
    
    # Run tests
    exit_code = run_tests(
        test_type=test_type,
        coverage=args.coverage,
        verbose=not args.quiet
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
