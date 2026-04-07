import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, SystemConfiguration, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecogrid.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    db.create_all()
    
    # Check all users
    users = User.query.all()
    print(f"Total users: {len(users)}")
    
    for user in users:
        print(f"User: {user.name} ({user.email})")
        
        # Check user's configurations
        configs = SystemConfiguration.query.filter_by(user_id=user.id).all()
        print(f"  Configurations: {len(configs)}")
        
        for config in configs:
            print(f"    - {config.name} (Active: {config.is_active})")
            if config.is_active:
                print(f"      Created: {config.created_at}")
                print(f"      Config data length: {len(config.config_data or '')}")
