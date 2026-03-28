from core.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False, index=True)
    mobile = db.Column(db.Text, nullable=False, default="")
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False, default="student", index=True)
    class_name = db.Column(db.Text, default="Computer Science 101", index=True)
    section = db.Column(db.Text, default="A")
    student_id = db.Column(db.Text, unique=True)
    is_verified = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    reset_token = db.Column(db.Text, nullable=True, index=True)
    reset_token_expiry = db.Column(db.Float, nullable=True)

    predictions = db.relationship("Prediction", back_populates="user", lazy="dynamic")


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    attendance = db.Column(db.Float, nullable=False)
    study_hours = db.Column(db.Float, nullable=False)
    previous_marks = db.Column(db.Float, nullable=False)
    assignments = db.Column(db.Float, nullable=False, default=0)
    internal_marks = db.Column(db.Float, nullable=False, default=0)
    class_name = db.Column(db.Text, nullable=False, index=True)
    section = db.Column(db.Text, default="A")
    predicted_score = db.Column(db.Float, nullable=False, index=True)
    performance_label = db.Column(db.Text, nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), index=True)
    gender = db.Column(db.Text, nullable=True)
    extracurricular = db.Column(db.Text, nullable=True)
    internet_access = db.Column(db.Text, nullable=True)
    parental_education = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="predictions")


class StudentGoal(db.Model):
    __tablename__ = "student_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    target_percentage = db.Column(db.Float, nullable=False)
    current_percentage = db.Column(db.Float, nullable=True)
    required_attendance = db.Column(db.Float, nullable=True)
    required_study_hours = db.Column(db.Float, nullable=True)
    required_internal_marks = db.Column(db.Float, nullable=True)
    required_assignments = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), index=True)


class AssignmentDeadline(db.Model):
    __tablename__ = "assignment_deadlines"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.Text, nullable=False)
    deadline_date = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, default="pending", nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), index=True)


class OtpLog(db.Model):
    __tablename__ = "otp_logs"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, index=True)
    otp_hash = db.Column(db.Text, nullable=False)
    purpose = db.Column(db.Text, nullable=False, default="registration", index=True)
    is_used = db.Column(db.Integer, default=0, nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)

