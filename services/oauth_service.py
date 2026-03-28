import os

import requests as http_requests
from flask import flash, redirect, session, url_for
from werkzeug.security import generate_password_hash

import config
from core.extensions import db
from models.entities import User
from services.id_service import generate_student_id


def get_google_provider_cfg():
    """Fetch Google's OpenID Connect discovery document."""
    return http_requests.get(config.GOOGLE_DISCOVERY_URL, timeout=10).json()


def get_oauth_redirect_uri(endpoint_name):
    """Build callback URL with optional explicit overrides from config."""
    if endpoint_name == "auth.google_callback":
        explicit_google_uri = getattr(config, "GOOGLE_REDIRECT_URI", "").strip()
        if explicit_google_uri:
            return explicit_google_uri

    explicit_base = getattr(config, "OAUTH_REDIRECT_BASE_URL", "").strip().rstrip("/")
    if explicit_base:
        return f"{explicit_base}{url_for(endpoint_name)}"

    return url_for(endpoint_name, _external=True)


def social_login_user(provider, provider_id, name, email, picture):
    """Find or create a user from social OAuth data and set session. Returns redirect."""
    user = User.query.filter_by(email=email).first()

    if user:
        session.permanent = True
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["role"] = user.role
        session["email"] = user.email
        session["class_name"] = user.class_name
        session["section"] = user.section
        session["student_id"] = user.student_id
        session["profile_picture"] = picture
        flash(f"Welcome back, {user.name}!", "success")
        if user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("student.student_dashboard"))

    student_id = generate_student_id()
    random_pw = generate_password_hash(os.urandom(24).hex())
    new_user = User(
        name=name,
        email=email,
        mobile="",
        password_hash=random_pw,
        role="student",
        class_name="Computer Science 101",
        section="A",
        student_id=student_id,
        is_verified=1,
    )
    db.session.add(new_user)
    db.session.commit()
    new_id = new_user.id

    session.permanent = True
    session["user_id"] = new_id
    session["user_name"] = name
    session["role"] = "student"
    session["email"] = email
    session["class_name"] = "Computer Science 101"
    session["section"] = "A"
    session["student_id"] = student_id
    session["profile_picture"] = picture
    flash(f"Welcome, {name}! Your account has been created via {provider}.", "success")
    return redirect(url_for("student.student_dashboard"))
