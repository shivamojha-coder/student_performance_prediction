import sqlite3
import config
import os

def create_new_tables():
    """Create student_goals and assignment_deadlines tables."""
    db_path = os.path.join(os.getcwd(), 'student_perf.db')
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create student_goals table
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_percentage REAL NOT NULL,
                required_attendance REAL,
                required_study_hours REAL,
                required_internal_marks REAL,
                required_assignments REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("Created 'student_goals' table.")
    except Exception as e:
        print(f"Error creating 'student_goals': {e}")
        
    # Create assignment_deadlines table
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignment_deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                deadline_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("Created 'assignment_deadlines' table.")
    except Exception as e:
        print(f"Error creating 'assignment_deadlines': {e}")
        
    conn.commit()
    conn.close()
    print("Database migration completed.")

if __name__ == "__main__":
    create_new_tables()
