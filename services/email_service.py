import smtplib
from concurrent.futures import ThreadPoolExecutor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os

import config

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

_EMAIL_WORKERS = getattr(config, "EMAIL_ASYNC_WORKERS", 4)
_email_executor = ThreadPoolExecutor(max_workers=_EMAIL_WORKERS, thread_name_prefix="mail-worker")


def _refresh_dotenv_runtime():
    """Reload .env so SMTP changes are picked up without server restart."""
    if not load_dotenv:
        return
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)


def _build_otp_message(recipient_email, otp_code, flow="registration"):
    if flow == "login":
        subject = "SuccessPredict - Sign-In Verification Code"
        intro = "Use the code below to complete your sign-in request."
        plain_text = f"Your SuccessPredict sign-in verification code is: {otp_code}"
    else:
        subject = "SuccessPredict - Email Verification Code"
        intro = "Use the code below to verify your email and complete your registration."
        plain_text = f"Your SuccessPredict verification code is: {otp_code}"

    html_body = f"""
    <div style="font-family:'Inter',Arial,sans-serif;max-width:480px;margin:auto;
                padding:32px;background:#f8fafc;border-radius:12px;">
        <h2 style="color:#1a365d;margin:0 0 8px;">SuccessPredict</h2>
        <p style="color:#4a5568;font-size:14px;">{intro}</p>
        <div style="text-align:center;margin:24px 0;">
            <span style="display:inline-block;font-size:32px;letter-spacing:8px;
                         font-weight:700;color:#2563eb;background:#e0e7ff;
                         padding:12px 28px;border-radius:8px;">{otp_code}</span>
        </div>
        <p style="color:#718096;font-size:13px;">This code expires in 5 minutes.
           If you didn't request this, just ignore this email.</p>
    </div>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.SMTP_EMAIL
    msg["To"] = recipient_email
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def _build_reset_message(recipient_email, reset_link):
    subject = "SuccessPredict - Password Reset Request"
    html_body = f"""
    <div style="font-family:'Inter',Arial,sans-serif;max-width:480px;margin:auto;
                padding:32px;background:#f8fafc;border-radius:12px;">
        <h2 style="color:#1a365d;margin:0 0 8px;">SuccessPredict</h2>
        <p style="color:#4a5568;font-size:14px;">You requested a password reset. Click the button below to set a new password.</p>
        <div style="text-align:center;margin:24px 0;">
            <a href="{reset_link}" style="display:inline-block;font-size:16px;font-weight:600;
                                          color:#ffffff;background:#2563eb;text-decoration:none;
                                          padding:12px 28px;border-radius:8px;">Reset Password</a>
        </div>
        <p style="color:#718096;font-size:13px;">If you didn't request this, please ignore this email. The link expires in 15 minutes.</p>
    </div>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.SMTP_EMAIL
    msg["To"] = recipient_email
    msg.attach(MIMEText(f"Reset your password here: {reset_link}", "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def _send_message(recipient_email, msg):
    _refresh_dotenv_runtime()

    smtp_email = (os.environ.get("SMTP_EMAIL") or config.SMTP_EMAIL or "").strip()
    smtp_password = (os.environ.get("SMTP_PASSWORD") or config.SMTP_PASSWORD or "").replace(" ", "").strip()
    smtp_server = (os.environ.get("SMTP_SERVER") or config.SMTP_SERVER or "smtp.gmail.com").strip()
    smtp_port_raw = os.environ.get("SMTP_PORT") or str(config.SMTP_PORT or 587)
    try:
        smtp_port = int(smtp_port_raw)
    except (TypeError, ValueError):
        smtp_port = 587

    if not smtp_email or not smtp_password:
        raise RuntimeError("SMTP credentials are missing. Set SMTP_EMAIL and SMTP_PASSWORD.")

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, recipient_email, msg.as_string())


def _log_background_result(future, recipient_email, email_type):
    try:
        future.result()
    except Exception as e:
        logging.exception("[EMAIL] Background %s email failed for %s: %s", email_type, recipient_email, e)


def send_otp_email(recipient_email, otp_code):
    """Send an OTP verification email via Gmail SMTP."""
    msg = _build_otp_message(recipient_email, otp_code, flow="registration")
    _send_message(recipient_email, msg)


def queue_otp_email(recipient_email, otp_code):
    """Queue OTP email sending in a background thread."""
    msg = _build_otp_message(recipient_email, otp_code, flow="registration")
    future = _email_executor.submit(_send_message, recipient_email, msg)
    future.add_done_callback(lambda f: _log_background_result(f, recipient_email, "OTP"))
    return future


def send_login_otp_email(recipient_email, otp_code):
    """Send a sign-in OTP email via Gmail SMTP."""
    msg = _build_otp_message(recipient_email, otp_code, flow="login")
    _send_message(recipient_email, msg)


def queue_login_otp_email(recipient_email, otp_code):
    """Queue sign-in OTP email sending in a background thread."""
    msg = _build_otp_message(recipient_email, otp_code, flow="login")
    future = _email_executor.submit(_send_message, recipient_email, msg)
    future.add_done_callback(lambda f: _log_background_result(f, recipient_email, "login-otp"))
    return future


def send_reset_email(recipient_email, reset_link):
    """Send a password reset link via Gmail SMTP."""
    msg = _build_reset_message(recipient_email, reset_link)
    _send_message(recipient_email, msg)


def queue_reset_email(recipient_email, reset_link):
    """Queue reset email sending in a background thread."""
    msg = _build_reset_message(recipient_email, reset_link)
    future = _email_executor.submit(_send_message, recipient_email, msg)
    future.add_done_callback(lambda f: _log_background_result(f, recipient_email, "reset"))
    return future
