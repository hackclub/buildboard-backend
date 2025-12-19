#!/usr/bin/env python3
"""
Script to add admin role to a user.

Usage:
    python scripts/add_admin.py <user_id_or_email>
    
Examples:
    python scripts/add_admin.py 75b6dde8-3f31-445b-a032-ebe896192120
    python scripts/add_admin.py dhamari@example.com
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.db import SessionLocal
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role


def add_admin(identifier: str):
    db = SessionLocal()
    
    try:
        # Find user by ID or email
        if "@" in identifier:
            user = db.query(User).filter(User.email == identifier.lower()).first()
        else:
            user = db.query(User).filter(User.user_id == identifier).first()
        
        if not user:
            print(f"❌ User not found: {identifier}")
            return False
        
        print(f"Found user: {user.email} (ID: {user.user_id})")
        
        # Check if admin role exists
        admin_role = db.query(Role).filter(Role.role_id == "admin").first()
        if not admin_role:
            print("Creating admin role...")
            admin_role = Role(role_id="admin", name="Admin", description="Administrator role")
            db.add(admin_role)
            db.commit()
        
        # Check if user already has admin role
        existing = db.query(UserRole).filter(
            UserRole.user_id == user.user_id,
            UserRole.role_id == "admin"
        ).first()
        
        if existing:
            print(f"✅ User {user.email} already has admin role")
            return True
        
        # Add admin role
        user_role = UserRole(user_id=user.user_id, role_id="admin")
        db.add(user_role)
        db.commit()
        
        print(f"✅ Added admin role to {user.email}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def list_admins():
    db = SessionLocal()
    
    try:
        admins = db.query(User).join(UserRole).filter(UserRole.role_id == "admin").all()
        
        if not admins:
            print("No admin users found")
            return
        
        print(f"\nCurrent admins ({len(admins)}):")
        for user in admins:
            print(f"  - {user.email} ({user.user_id})")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nListing current admins...")
        list_admins()
        sys.exit(0)
    
    identifier = sys.argv[1]
    
    if identifier == "--list":
        list_admins()
    else:
        success = add_admin(identifier)
        if success:
            list_admins()
        sys.exit(0 if success else 1)
