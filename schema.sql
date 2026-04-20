DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS otp_logs;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mobile TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    class_name TEXT DEFAULT 'Computer Science 101',
    section TEXT DEFAULT 'A',
    student_id TEXT UNIQUE,
    is_verified INTEGER DEFAULT 0,
    profile_image_path TEXT,
    two_factor_enabled INTEGER NOT NULL DEFAULT 0,
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
    section TEXT NOT NULL DEFAULT 'A',
    predicted_score REAL NOT NULL,
    performance_label TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE otp_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    otp_hash TEXT NOT NULL,
    purpose TEXT NOT NULL DEFAULT 'registration',
    is_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- Insert default admin user (password: admin123)
INSERT INTO users (name, email, mobile, password_hash, role, class_name, student_id, is_verified)
VALUES ('Dr. Julian Vance', 'admin@edupredict.com', '0000000000',
        'scrypt:32768:8:1$salt$adminhashedpassword', 'admin', 'All', 'ADM-0001', 1);
