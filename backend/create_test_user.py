#!/usr/bin/env python3
"""
Script to create a test user in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.models.user import User
from app.auth.security import get_password_hash

def create_test_user():
    """Create a test user in the database"""
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("Test user already exists!")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_verified=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"Test user created successfully!")
        print(f"Email: test@example.com")
        print(f"Password: password123")
        print(f"User ID: {test_user.id}")
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
