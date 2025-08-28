#!/usr/bin/env python3
"""
Script to check users in the database
"""
import sqlite3
from datetime import datetime

def check_users():
    """Display all users in the database"""
    conn = sqlite3.connect('worqly.db')
    cursor = conn.cursor()
    
    print("=== USERS IN DATABASE ===")
    cursor.execute("""
        SELECT id, email, full_name, is_active, is_verified, created_at 
        FROM users 
        ORDER BY created_at DESC
    """)
    
    users = cursor.fetchall()
    
    if not users:
        print("No users found in database.")
        return
    
    print(f"{'ID':<3} {'Email':<25} {'Name':<15} {'Active':<6} {'Verified':<8} {'Created'}")
    print("-" * 80)
    
    for user in users:
        id, email, full_name, is_active, is_verified, created_at = user
        active = "Yes" if is_active else "No"
        verified = "Yes" if is_verified else "No"
        created = created_at.split()[0] if created_at else "N/A"
        
        print(f"{id:<3} {email:<25} {full_name:<15} {active:<6} {verified:<8} {created}")
    
    conn.close()

def check_user_by_email(email):
    """Check specific user by email"""
    conn = sqlite3.connect('worqly.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, email, full_name, is_active, is_verified, created_at 
        FROM users 
        WHERE email = ?
    """, (email,))
    
    user = cursor.fetchone()
    
    if user:
        id, email, full_name, is_active, is_verified, created_at = user
        print(f"\n=== USER DETAILS ===")
        print(f"ID: {id}")
        print(f"Email: {email}")
        print(f"Full Name: {full_name}")
        print(f"Active: {'Yes' if is_active else 'No'}")
        print(f"Verified: {'Yes' if is_verified else 'No'}")
        print(f"Created: {created_at}")
    else:
        print(f"No user found with email: {email}")
    
    conn.close()

if __name__ == "__main__":
    check_users()
    
    # You can also check specific users
    print("\n" + "="*50)
    check_user_by_email("jamesgr@uci.edu")
