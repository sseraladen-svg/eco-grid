#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import db, User
from main import app

def check_users():
    with app.app_context():
        users = User.query.all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}, Active: {user.is_active}")

if __name__ == "__main__":
    check_users()
