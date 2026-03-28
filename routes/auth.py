import os
import random
import string
import time
from urllib.parse import urlencode

import requests as http_requests
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

import config
from core.extensions import db
from forms.auth_forms import (
    ForgotPasswordForm,
    LoginForm,
    RegisterForm,
    ResendOtpForm,
    ResetPasswordForm,
    VerifyOtpForm,
)
from models.entities import User
from services.email_service import queue_otp_email, queue_reset_email
from services.id_service import generate_otp, generate_student_id
from services.oauth_service import get_google_provider_cfg, get_oauth_redirect_uri, social_login_user
from services.otp_service import store_otp, verify_otp


auth_bp = Blueprint("auth", __name__)


def _flash_form_errors(form):
    for errors in form.errors.values():
        for err in errors:
            flash(err, "danger")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    register_form = RegisterForm()

    if login_form.validate_on_submit():
        email = login_form.email.data.strip()
        password = login_form.password.data
        role = login_form.role.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if user.role != role:
                flash(f"This account is registered as {user.role}, not {role}.", "danger")
                return render_template("login.html")

            session.permanent = True
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role
            session["email"] = user.email
            session["class_name"] = user.class_name
            session["section"] = user.section
            session["student_id"] = user.student_id

            flash(f"Welcome back, {user.name}!", "success")
            if user.role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            return redirect(url_for("student.student_dashboard"))

        flash("Invalid email or password.", "danger")
    elif request.method == "POST":
        _flash_form_errors(login_form)

    return render_template("login.html", login_form=login_form, register_form=register_form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip()
        mobile = form.mobile.data.strip()
        password = form.password.data
        class_name = form.class_name.data.strip()
        section = (form.section.data or "A").strip() or "A"

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.login", tab="register"))

        otp_code = generate_otp()
        try:
            queue_otp_email(email, otp_code)
        except Exception as e:
            print(f"[OTP] Email queue error: {e}")
            flash("Failed to send verification email. Please try again.", "danger")
            return redirect(url_for("auth.login", tab="register"))

        store_otp(email, otp_code)
        session["pending_reg"] = {
            "name": name,
            "email": email,
            "mobile": mobile,
            "password": password,
            "class_name": class_name,
            "section": section,
        }
        flash("A 6-digit verification code has been sent to your email.", "info")
        return redirect(url_for("auth.verify_otp_page"))
    elif request.method == "POST":
        _flash_form_errors(form)

    return redirect(url_for("auth.login", tab="register"))


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp_page():
    form = VerifyOtpForm()
    resend_form = ResendOtpForm()
    pending = session.get("pending_reg")
    if not pending:
        flash("Please register first.", "warning")
        return redirect(url_for("auth.register"))

    if form.validate_on_submit():
        user_otp = form.otp.data.strip()
        email = pending["email"]

        if verify_otp(email, user_otp):
            student_id = generate_student_id()
            password_hash = generate_password_hash(pending["password"])
            user = User(
                name=pending["name"],
                email=email,
                mobile=pending.get("mobile", ""),
                password_hash=password_hash,
                role="student",
                class_name=pending["class_name"],
                section=pending.get("section", "A"),
                student_id=student_id,
                is_verified=1,
            )
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Email already registered.", "danger")
                return redirect(url_for("auth.login"))

            new_user_id = user.id
            session.pop("pending_reg", None)

            session.permanent = True
            session["user_id"] = new_user_id
            session["user_name"] = pending["name"]
            session["role"] = "student"
            session["email"] = email
            session["class_name"] = pending["class_name"]
            session["section"] = pending.get("section", "A")
            session["student_id"] = student_id

            flash(f"Welcome, {pending['name']}! Your account has been created successfully.", "success")
            return redirect(url_for("student.student_dashboard"))

        flash("Invalid or expired OTP. Please try again.", "danger")
    elif request.method == "POST":
        _flash_form_errors(form)

    masked_email = pending["email"]
    at_idx = masked_email.index("@")
    masked_email = masked_email[0] + "***" + masked_email[at_idx:]
    return render_template("verify_otp.html", masked_email=masked_email, otp_form=form, resend_form=resend_form)


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    form = ResendOtpForm()
    if not form.validate_on_submit():
        _flash_form_errors(form)
        return redirect(url_for("auth.verify_otp_page"))

    pending = session.get("pending_reg")
    if not pending:
        flash("Please register first.", "warning")
        return redirect(url_for("auth.register"))

    email = pending["email"]
    otp_code = generate_otp()
    try:
        queue_otp_email(email, otp_code)
        store_otp(email, otp_code)
        flash("A new code has been sent to your email.", "info")
    except Exception as e:
        print(f"[OTP] Resend queue error: {e}")
        flash("Failed to resend code. Please try again.", "danger")

    return redirect(url_for("auth.verify_otp_page"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        user = User.query.filter_by(email=email).first()

        if user:
            token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
            expiry = time.time() + 900  # 15 minutes

            user.reset_token = token
            user.reset_token_expiry = expiry
            db.session.commit()

            try:
                reset_link = url_for("auth.reset_password", token=token, _external=True)
                queue_reset_email(email, reset_link)
                flash("Password reset link sent to your email.", "info")
            except Exception as e:
                print(f"Error queueing email: {e}")
                flash("Error sending email. Please try again later.", "danger")
        else:
            flash("Email address not found.", "danger")

        return redirect(url_for("auth.login"))
    elif request.method == "POST":
        _flash_form_errors(form)

    return render_template("forgot_password.html", forgot_form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.login"))

    if user.reset_token_expiry < time.time():
        flash("Reset link has expired. Please request a new one.", "warning")
        return redirect(url_for("auth.forgot_password"))

    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        user.password_hash = password_hash
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash("Your password has been updated. Please log in.", "success")
        return redirect(url_for("auth.login"))
    elif request.method == "POST":
        _flash_form_errors(form)

    return render_template("reset_password.html", token=token, reset_form=form)


@auth_bp.route("/auth/google")
def google_login():
    if not config.GOOGLE_CLIENT_ID or not config.GOOGLE_CLIENT_SECRET:
        flash("Google sign-in is not configured. Add Google OAuth credentials first.", "danger")
        return redirect(url_for("auth.login"))

    try:
        google_cfg = get_google_provider_cfg()
        authorization_endpoint = google_cfg["authorization_endpoint"]
    except Exception:
        flash("Unable to reach Google. Please try again later.", "danger")
        return redirect(url_for("auth.login"))

    state = os.urandom(16).hex()
    # Keep a small rolling list so parallel/tabbed OAuth attempts don't invalidate each other.
    states = session.get("google_oauth_states", [])
    states = [s for s in states if isinstance(s, str)]
    states.append(state)
    session["google_oauth_states"] = states[-5:]
    session["google_oauth_state"] = state  # backward compatibility

    callback_url = get_oauth_redirect_uri("auth.google_callback")
    redirect_map = session.get("google_oauth_redirect_uris", {})
    if not isinstance(redirect_map, dict):
        redirect_map = {}
    redirect_map[state] = callback_url
    # Keep map bounded
    if len(redirect_map) > 10:
        keys = list(redirect_map.keys())[-10:]
        redirect_map = {k: redirect_map[k] for k in keys}
    session["google_oauth_redirect_uris"] = redirect_map
    session["google_oauth_redirect_uri"] = callback_url  # backward compatibility
    params = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": callback_url,
        "scope": "openid email profile",
        "response_type": "code",
        "state": state,
        "prompt": "select_account",
    }
    auth_url = f"{authorization_endpoint}?{urlencode(params)}"
    return redirect(auth_url)


@auth_bp.route("/auth/google/callback")
def google_callback():
    req_state = request.args.get("state")
    states = session.get("google_oauth_states", [])
    legacy_state = session.get("google_oauth_state")
    valid_states = set(states if isinstance(states, list) else [])
    if legacy_state:
        valid_states.add(legacy_state)

    if not req_state or req_state not in valid_states:
        flash(
            "Authentication failed - invalid state. Ensure same URL host is used (localhost vs 127.0.0.1) and try again.",
            "danger",
        )
        return redirect(url_for("auth.login"))

    # Consume matched state (single-use)
    if isinstance(states, list):
        session["google_oauth_states"] = [s for s in states if s != req_state]
    if legacy_state == req_state:
        session.pop("google_oauth_state", None)

    if request.args.get("error"):
        reason = request.args.get("error_description") or request.args.get("error") or "Access denied"
        flash(f"Google sign-in failed: {reason}", "danger")
        return redirect(url_for("auth.login"))

    code = request.args.get("code")
    if not code:
        flash("Google sign-in was cancelled.", "warning")
        return redirect(url_for("auth.login"))

    try:
        google_cfg = get_google_provider_cfg()
        token_endpoint = google_cfg["token_endpoint"]
        redirect_map = session.get("google_oauth_redirect_uris", {})
        redirect_uri = None
        if isinstance(redirect_map, dict):
            redirect_uri = redirect_map.pop(req_state, None)
            session["google_oauth_redirect_uris"] = redirect_map
        redirect_uri = redirect_uri or session.pop("google_oauth_redirect_uri", None) or get_oauth_redirect_uri("auth.google_callback")

        token_response = http_requests.post(
            token_endpoint,
            data={
                "code": code,
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        try:
            token_data = token_response.json()
        except ValueError:
            token_data = {}

        if token_response.status_code >= 400 or "error" in token_data:
            err = str(token_data.get("error", "")).strip() or f"http_{token_response.status_code}"
            err_desc = str(token_data.get("error_description", "")).strip()
            print(
                f"[GOOGLE AUTH ERROR] status={token_response.status_code}, "
                f"error={err}, desc={err_desc}, redirect_uri={redirect_uri}"
            )

            if err == "redirect_uri_mismatch" or "redirect_uri_mismatch" in err_desc:
                flash(
                    f"Google redirect URI mismatch. Add this exact callback URI in Google Console: {redirect_uri}",
                    "danger",
                )
            elif err == "invalid_client":
                flash("Google client ID or secret is invalid. Recheck OAuth credentials.", "danger")
            else:
                friendly = err_desc or err or "Unknown error from Google"
                flash(f"Google authentication failed: {friendly}", "danger")
            return redirect(url_for("auth.login"))

        access_token = token_data.get("access_token")
        if not access_token:
            print(f"[GOOGLE AUTH ERROR] Missing access token in response: {token_data}")
            flash("Google authentication failed: access token missing.", "danger")
            return redirect(url_for("auth.login"))

        userinfo_endpoint = google_cfg["userinfo_endpoint"]
        userinfo_response = http_requests.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        try:
            userinfo = userinfo_response.json()
        except ValueError:
            userinfo = {}

        if userinfo_response.status_code >= 400:
            print(f"[GOOGLE USERINFO ERROR] status={userinfo_response.status_code}, body={userinfo}")
            flash("Google sign-in failed while reading profile. Please try again.", "danger")
            return redirect(url_for("auth.login"))

        if not userinfo.get("email_verified", False):
            flash("Google account email is not verified.", "danger")
            return redirect(url_for("auth.login"))

        google_id = userinfo["sub"]
        email = userinfo["email"]
        name = userinfo.get("name", email.split("@")[0])
        picture = userinfo.get("picture", "")
        return social_login_user("Google", google_id, name, email, picture)

    except Exception as e:
        print(f"[Google OAuth] Error: {e}")
        flash("Google sign-in failed. Please try again.", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/auth/microsoft")
def microsoft_login():
    if not config.MICROSOFT_CLIENT_ID or not config.MICROSOFT_CLIENT_SECRET:
        flash("Microsoft sign-in is not configured. Add Microsoft OAuth credentials first.", "danger")
        return redirect(url_for("auth.login"))

    state = os.urandom(16).hex()
    ms_states = session.get("ms_oauth_states", [])
    ms_states = [s for s in ms_states if isinstance(s, str)]
    ms_states.append(state)
    session["ms_oauth_states"] = ms_states[-5:]
    session["ms_oauth_state"] = state

    callback_url = get_oauth_redirect_uri("auth.microsoft_callback")
    ms_redirect_map = session.get("ms_oauth_redirect_uris", {})
    if not isinstance(ms_redirect_map, dict):
        ms_redirect_map = {}
    ms_redirect_map[state] = callback_url
    if len(ms_redirect_map) > 10:
        keys = list(ms_redirect_map.keys())[-10:]
        ms_redirect_map = {k: ms_redirect_map[k] for k in keys}
    session["ms_oauth_redirect_uris"] = ms_redirect_map
    session["ms_oauth_redirect_uri"] = callback_url
    params = {
        "client_id": config.MICROSOFT_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": callback_url,
        "response_mode": "query",
        "scope": config.MICROSOFT_SCOPE,
        "state": state,
        "prompt": "select_account",
    }
    auth_url = f"{config.MICROSOFT_AUTHORIZE_URL}?{urlencode(params)}"
    return redirect(auth_url)


@auth_bp.route("/auth/microsoft/callback")
def microsoft_callback():
    req_state = request.args.get("state")
    ms_states = session.get("ms_oauth_states", [])
    legacy_state = session.get("ms_oauth_state")
    valid_states = set(ms_states if isinstance(ms_states, list) else [])
    if legacy_state:
        valid_states.add(legacy_state)

    if not req_state or req_state not in valid_states:
        flash("Authentication failed - invalid state. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    if isinstance(ms_states, list):
        session["ms_oauth_states"] = [s for s in ms_states if s != req_state]
    if legacy_state == req_state:
        session.pop("ms_oauth_state", None)

    if request.args.get("error"):
        flash("Microsoft sign-in was cancelled or denied.", "warning")
        return redirect(url_for("auth.login"))

    code = request.args.get("code")
    if not code:
        flash("Microsoft sign-in was cancelled.", "warning")
        return redirect(url_for("auth.login"))

    try:
        ms_redirect_map = session.get("ms_oauth_redirect_uris", {})
        redirect_uri = None
        if isinstance(ms_redirect_map, dict):
            redirect_uri = ms_redirect_map.pop(req_state, None)
            session["ms_oauth_redirect_uris"] = ms_redirect_map
        redirect_uri = redirect_uri or session.pop("ms_oauth_redirect_uri", None) or get_oauth_redirect_uri("auth.microsoft_callback")
        token_response = http_requests.post(
            config.MICROSOFT_TOKEN_URL,
            data={
                "client_id": config.MICROSOFT_CLIENT_ID,
                "client_secret": config.MICROSOFT_CLIENT_SECRET,
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
                "scope": config.MICROSOFT_SCOPE,
            },
            timeout=10,
        )
        token_data = token_response.json()

        if "error" in token_data:
            flash("Microsoft authentication failed. Please try again.", "danger")
            return redirect(url_for("auth.login"))

        access_token = token_data.get("access_token")
        if not access_token:
            flash("Microsoft authentication failed. Access token missing.", "danger")
            return redirect(url_for("auth.login"))

        profile_response = http_requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        profile = profile_response.json()

        microsoft_id = profile.get("id")
        email = profile.get("mail") or profile.get("userPrincipalName")
        if not microsoft_id or not email:
            flash("Microsoft profile is missing required email information.", "danger")
            return redirect(url_for("auth.login"))

        name = profile.get("displayName", email.split("@")[0])
        return social_login_user("Microsoft", microsoft_id, name, email, "")

    except Exception as e:
        print(f"[Microsoft OAuth] Error: {e}")
        flash("Microsoft sign-in failed. Please try again.", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
