#!/usr/bin/env python3
"""
Simple test script to verify user authentication
"""
import sqlite3
import os
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_simple_auth():
    """Test authentication system using direct database access"""
    print("Testing authentication system...")
    
    db_path = "worqly.db"
    
    if not os.path.exists(db_path):
        print(f"✗ Database file {db_path} not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test 1: Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("✗ Users table does not exist")
            return
        
        # Test 2: Get all users
        cursor.execute("SELECT id, email, full_name, hashed_password, is_active, is_verified FROM users")
        users = cursor.fetchall()
        
        print(f"✓ Found {len(users)} users in database:")
        
        for user in users:
            user_id, email, full_name, hashed_password, is_active, is_verified = user
            print(f"  - {email} ({full_name}) - Active: {is_active}, Verified: {is_verified}")
            
            # Test password verification for known users
            if email == "test@example.com":
                if hashed_password and pwd_context.verify("password123", hashed_password):
                    print(f"    ✓ Test user password verification works")
                else:
                    print(f"    ✗ Test user password verification failed")
            
            elif email == "admin@example.com":
                if hashed_password and pwd_context.verify("admin123", hashed_password):
                    print(f"    ✓ Admin user password verification works")
                else:
                    print(f"    ✗ Admin user password verification failed")
        
        # Test 3: Test password hashing
        test_password = "testpassword123"
        hashed = pwd_context.hash(test_password)
        print(f"\n✓ Password hashing works: {hashed[:20]}...")
        
        if pwd_context.verify(test_password, hashed):
            print("✓ Password verification with new hash works")
        else:
            print("✗ Password verification with new hash failed")
        
        # Test 4: Show login credentials
        print(f"\n📋 Login Credentials:")
        print(f"  Test User: test@example.com / password123")
        print(f"  Admin User: admin@example.com / admin123")
        print(f"  James Ruiz: jamesgr@uci.edu / (password not shown)")
        print(f"  James: imjamesruiz@gmail.com / (password not shown)")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_simple_auth()
