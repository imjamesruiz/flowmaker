#!/usr/bin/env python3
"""
Create an admin user for the Flowmaker application
"""

import os
import sys
from sqlalchemy.orm import Session
from app.database import get_db, init_db
from app.models.user import User
from app.auth.security import get_password_hash
from app.config import settings

def create_admin_user():
    """Create an admin user if one doesn't exist"""
    
    # Initialize database
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@flowmaker.com").first()
        
        if admin_user:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        admin_user = User(
            email="admin@flowmaker.com",
            username="admin",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print("📧 Email: admin@flowmaker.com")
        print("🔑 Password: admin123")
        print("⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
