#!/usr/bin/env python3
"""
Simple test runner to demonstrate the workflow integration tests.

This script shows how to run the tests step by step.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Main test runner."""
    print("🚀 Workflow Automation Platform - Test Runner")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Error: tests directory not found.")
        print("Please run this script from the backend directory.")
        sys.exit(1)
    
    print("\n📋 Available Test Options:")
    print("1. Run simple tests (no Redis required)")
    print("2. Run full integration tests (requires Redis)")
    print("3. Check Redis connection")
    print("4. Install Redis with Docker")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            run_simple_tests()
            break
        elif choice == "2":
            run_full_tests()
            break
        elif choice == "3":
            check_redis()
            break
        elif choice == "4":
            install_redis_docker()
            break
        elif choice == "5":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1-5.")


def run_simple_tests():
    """Run simple tests that don't require Redis."""
    print("\n🧪 Running Simple Tests (No Redis Required)")
    print("-" * 50)
    
    try:
        # Run the simple test file
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_workflows_simple.py", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Simple tests completed successfully!")
        else:
            print("❌ Some tests failed. Check the output above.")
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")


def run_full_tests():
    """Run full integration tests (requires Redis)."""
    print("\n🔧 Running Full Integration Tests (Requires Redis)")
    print("-" * 50)
    
    # First check if Redis is available
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=1)
        r.ping()
        print("✅ Redis is running and accessible")
    except Exception as e:
        print(f"❌ Redis is not available: {e}")
        print("\nTo run full integration tests, you need Redis running.")
        print("Options:")
        print("1. Start Redis with Docker: docker run -d -p 6379:6379 redis:alpine")
        print("2. Install Redis for Windows")
        print("3. Use Redis Cloud (free tier)")
        return
    
    try:
        # Run the full test suite
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_workflows.py", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Full integration tests completed successfully!")
        else:
            print("❌ Some tests failed. Check the output above.")
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")


def check_redis():
    """Check Redis connection."""
    print("\n🔍 Checking Redis Connection")
    print("-" * 30)
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=1)
        r.ping()
        print("✅ Redis is running and accessible on localhost:6379")
        
        # Test basic operations
        r.set("test_key", "test_value")
        value = r.get("test_key")
        r.delete("test_key")
        
        if value == b"test_value":
            print("✅ Redis read/write operations working correctly")
        else:
            print("❌ Redis read/write operations failed")
            
    except ImportError:
        print("❌ Redis Python package not installed")
        print("Install with: pip install redis")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nTo start Redis:")
        print("1. Docker: docker run -d -p 6379:6379 redis:alpine")
        print("2. Windows: Download from https://github.com/microsoftarchive/redis/releases")
        print("3. WSL: sudo apt install redis-server && sudo service redis-server start")


def install_redis_docker():
    """Show instructions for installing Redis with Docker."""
    print("\n🐳 Installing Redis with Docker")
    print("-" * 35)
    
    print("To install and start Redis with Docker:")
    print()
    print("1. Install Docker Desktop for Windows:")
    print("   https://www.docker.com/products/docker-desktop/")
    print()
    print("2. Start Redis container:")
    print("   docker run -d -p 6379:6379 --name redis-test redis:alpine")
    print()
    print("3. Verify Redis is running:")
    print("   docker ps")
    print()
    print("4. Stop Redis when done:")
    print("   docker stop redis-test")
    print("   docker rm redis-test")
    print()
    print("5. Run the tests:")
    print("   python run_simple_test.py")
    print("   (Choose option 2 for full integration tests)")


if __name__ == "__main__":
    main()
