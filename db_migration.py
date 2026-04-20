import sqlite3
import config

def add_reset_columns():
    """Add auth/profile related columns to users table."""
    conn = sqlite3.connect(config.DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
        print("Added 'reset_token' column.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'reset_token': {e}")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expiry REAL")
        print("Added 'reset_token_expiry' column.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'reset_token_expiry': {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_image_path TEXT")
        print("Added 'profile_image_path' column.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'profile_image_path': {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN two_factor_enabled INTEGER NOT NULL DEFAULT 0")
        print("Added 'two_factor_enabled' column.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'two_factor_enabled': {e}")
        
    conn.commit()
    conn.close()
    print("Database migration completed.")

if __name__ == "__main__":
    add_reset_columns()
