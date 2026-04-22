import os

from flask import current_app
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash

from core.extensions import db


def _ensure_sqlite_columns():
    """Best-effort column migration for existing SQLite databases."""
    if not current_app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:///"):
        return

    engine = db.engine
    inspector = inspect(engine)

    def has_column(table_name, column_name):
        return any(col["name"] == column_name for col in inspector.get_columns(table_name))

    with engine.begin() as conn:
        if "users" in inspector.get_table_names():
            if not has_column("users", "reset_token"):
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token TEXT"))
            if not has_column("users", "reset_token_expiry"):
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expiry REAL"))
            if not has_column("users", "section"):
                conn.execute(text("ALTER TABLE users ADD COLUMN section TEXT DEFAULT 'A'"))
            if not has_column("users", "profile_image_path"):
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_image_path TEXT"))

        if "predictions" in inspector.get_table_names():
            if not has_column("predictions", "section"):
                conn.execute(text("ALTER TABLE predictions ADD COLUMN section TEXT DEFAULT 'A'"))
            if not has_column("predictions", "gender"):
                conn.execute(text("ALTER TABLE predictions ADD COLUMN gender TEXT"))
            if not has_column("predictions", "extracurricular"):
                conn.execute(text("ALTER TABLE predictions ADD COLUMN extracurricular TEXT"))
            if not has_column("predictions", "internet_access"):
                conn.execute(text("ALTER TABLE predictions ADD COLUMN internet_access TEXT"))
            if not has_column("predictions", "parental_education"):
                conn.execute(text("ALTER TABLE predictions ADD COLUMN parental_education TEXT"))

        if "student_goals" in inspector.get_table_names():
            if not has_column("student_goals", "current_percentage"):
                conn.execute(text("ALTER TABLE student_goals ADD COLUMN current_percentage FLOAT"))


def ensure_default_admin():
    from models.entities import User

    admin = User.query.filter_by(email="admin@edupredict.com").first()
    if admin:
        return

    admin = User(
        name="Dr. Julian Vance",
        email="admin@edupredict.com",
        mobile="0000000000",
        password_hash=generate_password_hash("admin123"),
        role="admin",
        class_name="All",
        section="A",
        student_id="ADM-0001",
        is_verified=1,
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin user created: admin@edupredict.com / admin123")


def ensure_database_ready():
    db_path = current_app.config["DATABASE"]
    is_new_db = not os.path.exists(db_path)

    db.create_all()
    _ensure_sqlite_columns()
    ensure_default_admin()

    if is_new_db:
        print("Database created and initialized.")


def register_db(app):
    db.init_app(app)

    @app.cli.command("init-db")
    def init_db_command():
        with app.app_context():
            db.drop_all()
            db.create_all()
            _ensure_sqlite_columns()
            ensure_default_admin()
        print("Database initialized.")

