#!/usr/bin/env python3
"""
Script to fix the test user's password
"""
import sqlite3
import os
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fix_test_user():
    """Fix the test user's password"""
    print("Fixing test user password...")
    
    db_path = "worqly.db"
    
    if not os.path.exists(db_path):
        print(f"✗ Database file {db_path} not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Update test user password
        new_password_hash = pwd_context.hash("password123")
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE email = ?",
            (new_password_hash, "test@example.com")
        )
        
        if cursor.rowcount > 0:
            print("✓ Test user password updated successfully")
            
            # Verify the update
            cursor.execute("SELECT hashed_password FROM users WHERE email = ?", ("test@example.com",))
            result = cursor.fetchone()
            if result and pwd_context.verify("password123", result[0]):
                print("✓ Password verification confirmed")
            else:
                print("✗ Password verification failed after update")
        else:
            print("✗ Test user not found or no changes made")
        
        conn.commit()
        
    except Exception as e:
        print(f"✗ Error fixing test user: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_test_user()
