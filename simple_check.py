import sqlite3

# Connect to database
conn = sqlite3.connect('ecogrid.db')
cursor = conn.cursor()

# Check all users
cursor.execute("SELECT id, name, email FROM users")
users = cursor.fetchall()
print(f"Total users: {len(users)}")

for user in users:
    print(f"User: {user[1]} ({user[2]})")
    
    # Check user's configurations
    cursor.execute("SELECT id, name, is_active, created_at FROM system_configurations WHERE user_id = ?", (user[0],))
    configs = cursor.fetchall()
    print(f"  Configurations: {len(configs)}")
    
    for config in configs:
        print(f"    - {config[1]} (Active: {config[2]})")
        if config[2] == 1:
            print(f"      Created: {config[3]}")
            # Check config data length
            cursor.execute("SELECT config_data FROM system_configurations WHERE id = ?", (config[0],))
            config_data = cursor.fetchone()
            if config_data and config_data[0]:
                print(f"      Config data length: {len(config_data[0])}")

conn.close()
