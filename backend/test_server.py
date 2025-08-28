#!/usr/bin/env python3
"""
Simple test to verify server functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db
from app.models.user import User
from app.auth.security import get_password_hash, verify_password
from sqlalchemy.orm import sessionmaker
from app.database import engine

def test_server_setup():
    """Test server setup and database connection"""
    print("Testing server setup...")
    
    try:
        # Initialize database
        init_db()
        print("✓ Database initialized successfully")
        
        # Test database connection
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test user query
        users = session.query(User).all()
        print(f"✓ Database connection works - found {len(users)} users")
        
        # Test password hashing
        test_password = "test123"
        hashed = get_password_hash(test_password)
        if verify_password(test_password, hashed):
            print("✓ Password hashing/verification works")
        else:
            print("✗ Password hashing/verification failed")
        
        session.close()
        
        print("\n✓ Server setup test passed!")
        print("\n📋 Available login credentials:")
        print("  - test@example.com / password123")
        print("  - admin@example.com / admin123")
        print("  - jamesgr@uci.edu / (check your password)")
        print("  - imjamesruiz@gmail.com / (check your password)")
        
    except Exception as e:
        print(f"✗ Server setup test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_server_setup()
