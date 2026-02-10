DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS predictions;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    class_name TEXT DEFAULT 'Computer Science 101',
    student_id TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    attendance REAL NOT NULL,
    study_hours REAL NOT NULL,
    previous_marks REAL NOT NULL,
    assignments REAL NOT NULL,
    internal_marks REAL NOT NULL,
    class_name TEXT NOT NULL,
    predicted_score REAL NOT NULL,
    performance_label TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert default admin user (password: admin123)
INSERT INTO users (name, email, password_hash, role, class_name, student_id)
VALUES ('Dr. Julian Vance', 'admin@edupredict.com',
        'scrypt:32768:8:1$salt$adminhashedpassword', 'admin', 'All', 'ADM-0001');
