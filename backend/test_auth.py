#!/usr/bin/env python3
"""
Test script to verify authentication system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.auth.security import get_password_hash, verify_password

def test_auth():
    """Test authentication system"""
    print("Testing authentication system...")
    
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test 1: Check if test user exists and can be authenticated
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if test_user:
            print(f"✓ Test user found: {test_user.email}")
            
            # Test password verification
            if verify_password("password123", test_user.hashed_password):
                print("✓ Password verification works")
            else:
                print("✗ Password verification failed")
        else:
            print("✗ Test user not found")
        
        # Test 2: Check admin user
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if admin_user:
            print(f"✓ Admin user found: {admin_user.email}")
            
            # Test password verification
            if verify_password("admin123", admin_user.hashed_password):
                print("✓ Admin password verification works")
            else:
                print("✗ Admin password verification failed")
        else:
            print("✗ Admin user not found")
        
        # Test 3: List all users
        all_users = db.query(User).all()
        print(f"\nAll users in database ({len(all_users)}):")
        for user in all_users:
            print(f"  - {user.email} ({user.full_name}) - Active: {user.is_active}, Verified: {user.is_verified}")
        
        # Test 4: Test password hashing
        test_password = "testpassword123"
        hashed = get_password_hash(test_password)
        print(f"\n✓ Password hashing works: {hashed[:20]}...")
        
        if verify_password(test_password, hashed):
            print("✓ Password verification with new hash works")
        else:
            print("✗ Password verification with new hash failed")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_auth()
