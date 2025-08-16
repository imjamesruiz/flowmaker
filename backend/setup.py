#!/usr/bin/env python3
"""
Setup script for Worqly backend
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Worqly Backend")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Please run this script from the backend directory")
        print("   cd flowmaker/backend && python setup.py")
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("\n💡 If you're having issues, try:")
        print("   1. Create a virtual environment: python -m venv venv")
        print("   2. Activate it: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
        print("   3. Upgrade pip: pip install --upgrade pip")
        print("   4. Run this script again")
        return False
    
    # Create test user
    if os.path.exists("create_test_user.py"):
        if not run_command("python create_test_user.py", "Creating test user"):
            print("⚠️  Test user creation failed, but you can continue")
    
    print("\n🎉 Backend setup completed!")
    print("\n📋 Next steps:")
    print("   1. Start the backend: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("   2. Open another terminal and run: python test_workflow_connections.py")
    print("   3. Check the API docs at: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
