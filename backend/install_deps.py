#!/usr/bin/env python3
"""
Quick dependency installer for Worqly backend
"""

import subprocess
import sys

def install_package(package):
    """Install a Python package"""
    print(f"📦 Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install missing dependencies"""
    print("🔧 Installing missing dependencies...")
    
    # Install pydantic-settings
    if not install_package("pydantic-settings"):
        print("❌ Failed to install pydantic-settings")
        return False
    
    # Install other potentially missing packages
    packages = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "requests"
    ]
    
    for package in packages:
        install_package(package)
    
    print("\n🎉 Dependencies installed!")
    print("You can now start the backend with:")
    print("python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
