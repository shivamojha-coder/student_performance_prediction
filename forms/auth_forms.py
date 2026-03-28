from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp


class LoginForm(FlaskForm):
    student_id = StringField(validators=[Optional(), Length(max=64)])
    email = StringField(validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(validators=[DataRequired(), Length(min=1, max=255)])
    role = StringField(validators=[DataRequired(), Regexp(r"^(student|admin)$", message="Invalid login role.")])


class RegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField(validators=[DataRequired(), Email(), Length(max=255)])
    mobile = StringField(validators=[DataRequired(), Regexp(r"^\d{10}$", message="Please enter a valid 10-digit mobile number.")])
    password = PasswordField(validators=[DataRequired(), Length(min=6, max=128)])
    class_name = StringField(validators=[DataRequired(), Length(max=120)])
    section = StringField(validators=[Optional(), Length(max=32)])


class VerifyOtpForm(FlaskForm):
    otp = StringField(validators=[DataRequired(), Regexp(r"^\d{6}$", message="OTP must be a valid 6-digit code.")])


class ResendOtpForm(FlaskForm):
    pass


class ForgotPasswordForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email(), Length(max=255)])


class ResetPasswordForm(FlaskForm):
    password = PasswordField(validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords do not match."),
        ]
    )

