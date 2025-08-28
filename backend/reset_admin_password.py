#!/usr/bin/env python3
"""
Script to reset admin password
"""
import sqlite3
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_admin_password(new_password):
    """Reset admin password"""
    conn = sqlite3.connect('worqly.db')
    cursor = conn.cursor()
    
    # Hash the new password
    hashed_password = pwd_context.hash(new_password)
    
    # Update the admin password
    cursor.execute("""
        UPDATE users 
        SET hashed_password = ? 
        WHERE email = 'admin@example.com'
    """, (hashed_password,))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ Admin password updated successfully!")
        print(f"📧 Email: admin@example.com")
        print(f"🔑 New password: {new_password}")
        print(f"💡 Please remember this password!")
    else:
        print("❌ Admin account not found!")
    
    conn.close()

if __name__ == "__main__":
    print("=== ADMIN PASSWORD RESET ===")
    new_password = input("Enter new password for admin@example.com: ")
    
    if len(new_password) < 8:
        print("❌ Password must be at least 8 characters long!")
    else:
        reset_admin_password(new_password)
