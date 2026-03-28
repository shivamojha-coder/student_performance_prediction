from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

import config
from core.extensions import db
from models.entities import OtpLog


def ensure_otp_logs_table():
    """Kept for backward compatibility with existing call sites."""
    db.create_all()


def store_otp(email, otp_code, purpose="registration"):
    """Store hashed OTP in database with expiry timestamp."""
    ensure_otp_logs_table()
    otp_hash = generate_password_hash(otp_code)
    expires_at = datetime.utcnow() + timedelta(seconds=config.OTP_EXPIRY_SECONDS)

    OtpLog.query.filter_by(email=email, purpose=purpose, is_used=0).update(
        {OtpLog.is_used: 1},
        synchronize_session=False,
    )
    db.session.add(
        OtpLog(
            email=email,
            otp_hash=otp_hash,
            purpose=purpose,
            is_used=0,
            expires_at=expires_at,
        )
    )
    db.session.commit()


def verify_otp(email, user_otp, purpose="registration"):
    """Return True if latest OTP matches, is unused, and has not expired."""
    ensure_otp_logs_table()
    latest_otp = (
        OtpLog.query.filter_by(email=email, purpose=purpose, is_used=0)
        .order_by(OtpLog.id.desc())
        .first()
    )
    if not latest_otp:
        return False

    expires_at = latest_otp.expires_at
    if isinstance(expires_at, str):
        try:
            expires_at = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            latest_otp.is_used = 1
            db.session.commit()
            return False

    if datetime.utcnow() > expires_at:
        latest_otp.is_used = 1
        db.session.commit()
        return False

    try:
        if not check_password_hash(latest_otp.otp_hash, user_otp):
            return False
    except (TypeError, ValueError):
        return False

    used_rows = (
        OtpLog.query.filter_by(id=latest_otp.id, is_used=0)
        .update({OtpLog.is_used: 1}, synchronize_session=False)
    )
    if used_rows != 1:
        db.session.rollback()
        return False

    OtpLog.query.filter(
        OtpLog.email == email,
        OtpLog.purpose == purpose,
        OtpLog.id != latest_otp.id,
        OtpLog.is_used == 0,
    ).update({OtpLog.is_used: 1}, synchronize_session=False)
    db.session.commit()
    return True

