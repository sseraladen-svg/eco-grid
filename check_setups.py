#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import db, SystemConfiguration, User
from main import app

def check_setups():
    with app.app_context():
        users = User.query.all()
        print(f"Checking setups for {len(users)} users:")
        
        for user in users:
            print(f"\nUser: {user.name} ({user.email})")
            configs = SystemConfiguration.query.filter_by(user_id=user.id).all()
            print(f"  Configurations: {len(configs)}")
            
            for config in configs:
                print(f"  - {config.name} (Active: {config.is_active})")
                if config.is_active:
                    import json
                    data = json.loads(config.config_data)
                    print(f"    Location: {data.get('location', {}).get('latitude', 'N/A')}, {data.get('location', {}).get('longitude', 'N/A')}")
                    print(f"    Solar panels: {data.get('solar', {}).get('panel_count', 'N/A')}")

if __name__ == "__main__":
    check_setups()
