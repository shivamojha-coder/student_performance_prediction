import sqlite3
import config
import os

def add_section_column():
    """Add section column to users and predictions tables."""
    db_path = os.path.join(os.getcwd(), 'student_perf.db')
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add section to users
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN section TEXT DEFAULT 'A'")
        print("Added 'section' column to 'users' table.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'section' in 'users': {e}")
        
    # Add section to predictions
    try:
        cursor.execute("ALTER TABLE predictions ADD COLUMN section TEXT DEFAULT 'A'")
        print("Added 'section' column to 'predictions' table.")
    except sqlite3.OperationalError as e:
        print(f"Skipping 'section' in 'predictions': {e}")
        
    conn.commit()
    conn.close()
    print("Database migration completed.")

if __name__ == "__main__":
    add_section_column()
