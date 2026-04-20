import os
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import config
from core.decorators import login_required
from core.extensions import db
from models.entities import Prediction, StudentGoal, User
from services.goal_service import build_goal_analysis
from services.ml_service import predict_score


student_bp = Blueprint("student", __name__)

_ALLOWED_PROFILE_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def _resolve_profile_image_url(profile_image_path):
    if not profile_image_path:
        return ""
    if profile_image_path.startswith(("http://", "https://", "data:")):
        return profile_image_path
    return url_for("static", filename=profile_image_path)


def _delete_local_profile_image(profile_image_path):
    if not profile_image_path:
        return
    if profile_image_path.startswith(("http://", "https://", "data:")):
        return

    safe_relative = profile_image_path.lstrip("/\\")
    file_path = os.path.join(current_app.static_folder, safe_relative)
    file_path = os.path.normpath(file_path)
    static_root = os.path.normpath(current_app.static_folder)
    if not file_path.startswith(static_root):
        return

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass


@student_bp.route("/student/dashboard")
@login_required
def student_dashboard():
    user_info = User.query.filter_by(id=session["user_id"]).first()
    recent = (
        Prediction.query.filter_by(user_id=session["user_id"])
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .limit(5)
        .all()
    )
    all_preds = (
        Prediction.query.filter_by(user_id=session["user_id"])
        .order_by(Prediction.created_at.asc(), Prediction.id.asc())
        .all()
    )
    dashboard_payload = {
        "userName": session.get("user_name", "Student"),
        "firstName": session.get("user_name", "Student").split(" ")[0],
        "className": user_info.class_name if user_info else "Class Not Set",
        "section": user_info.section if user_info else "A",
        "stats": {
            "totalPredictions": len(all_preds),
            "latestScore": recent[0].predicted_score if recent else "--",
            "attendance": int(round(recent[0].attendance)) if recent else "--",
            "studyHours": int(round(recent[0].study_hours)) if recent else "--",
        },
        "defaults": {
            "gender": "Male",
            "extracurricular": "No",
            "internet_access": "Yes",
            "parental_education": "High School",
        },
        "formAction": url_for("student.student_predict"),
        "historyUrl": url_for("student.student_history"),
        "allPredictions": [
            {
                "date": pred.created_at.strftime("%Y-%m-%d") if pred.created_at else "",
                "score": pred.predicted_score,
            }
            for pred in all_preds
        ],
        "recentPredictions": [
            {
                "id": pred.id,
                "date": pred.created_at.strftime("%Y-%m-%d") if pred.created_at else "",
                "score": pred.predicted_score,
                "label": pred.performance_label,
                "attendance": pred.attendance,
                "study_hours": pred.study_hours,
            }
            for pred in recent
        ],
    }
    return render_template(
        "student/dashboard.html",
        recent_predictions=recent,
        all_predictions=all_preds,
        user_info=user_info,
        dashboard_payload=dashboard_payload,
    )


@student_bp.route("/student/predict", methods=["POST"])
@login_required
def student_predict():
    try:
        attendance = float(request.form.get("attendance", 0))
        study_hours = float(request.form.get("study_hours", 0))
        previous_marks = float(request.form.get("previous_marks", 0))

        gender = request.form.get("gender", "Male")
        extracurricular = request.form.get("extracurricular", "No")
        internet_access = request.form.get("internet_access", "Yes")
        parental_education = request.form.get("parental_education", "High School")

        user_info = User.query.filter_by(id=session["user_id"]).first()
        if not user_info:
            flash("User profile not found.", "danger")
            return redirect(url_for("student.student_dashboard"))

        class_name = user_info.class_name
        section = user_info.section

        if not (0 <= attendance <= 100):
            flash("Attendance must be between 0 and 100.", "danger")
            return redirect(url_for("student.student_dashboard"))
        if not (0 <= study_hours <= 168):
            flash("Weekly study hours must be between 0 and 168.", "danger")
            return redirect(url_for("student.student_dashboard"))

        score, label = predict_score(
            attendance,
            study_hours,
            previous_marks,
            gender,
            extracurricular,
            internet_access,
            parental_education,
        )

        pred = Prediction(
            user_id=session["user_id"],
            attendance=attendance,
            study_hours=study_hours,
            previous_marks=previous_marks,
            assignments=0,
            internal_marks=0,
            class_name=class_name,
            section=section,
            predicted_score=score,
            performance_label=label,
            gender=gender,
            extracurricular=extracurricular,
            internet_access=internet_access,
            parental_education=parental_education,
        )
        db.session.add(pred)
        db.session.commit()
        return redirect(url_for("student.student_result", pred_id=pred.id))

    except Exception as e:
        flash(f"Prediction failed: {str(e)}", "danger")
        return redirect(url_for("student.student_dashboard"))


@student_bp.route("/student/result/<int:pred_id>")
@login_required
def student_result(pred_id):
    prediction = Prediction.query.filter_by(id=pred_id, user_id=session["user_id"]).first()
    if not prediction:
        flash("Prediction not found.", "danger")
        return redirect(url_for("student.student_dashboard"))

    class_avg = (
        db.session.query(
            func.avg(Prediction.attendance).label("avg_attendance"),
            func.avg(Prediction.study_hours).label("avg_study"),
            func.avg(Prediction.previous_marks).label("avg_marks"),
            func.avg(Prediction.predicted_score).label("avg_score"),
        )
        .filter(Prediction.class_name == prediction.class_name)
        .first()
    )

    return render_template("student/result.html", prediction=prediction, class_avg=class_avg)


@student_bp.route("/student/history")
@login_required
def student_history():
    predictions = (
        Prediction.query.filter_by(user_id=session["user_id"])
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .all()
    )
    return render_template("student/history.html", predictions=predictions)


@student_bp.route("/student/goal-setting", methods=["GET", "POST"])
@login_required
def student_goal_setting():
    user_id = session["user_id"]

    current = (
        Prediction.query.filter_by(user_id=user_id)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .first()
    )
    goal = (
        StudentGoal.query.filter_by(user_id=user_id)
        .order_by(StudentGoal.created_at.desc(), StudentGoal.id.desc())
        .first()
    )
    goal_analysis = None
    try:
        days_left_default = int(request.args.get("days_left", 30))
    except (TypeError, ValueError):
        days_left_default = 30
    days_left_default = max(1, min(days_left_default, 365))

    if request.method == "POST":
        try:
            target = float(request.form.get("target_percentage", 0))
            days_left = int(request.form.get("days_left", 0))
            if not current:
                flash("Please complete at least one prediction first to set a goal baseline.", "info")
                return redirect(url_for("student.student_dashboard"))
            if not (0 <= target <= 100):
                flash("Target must be between 0 and 100.", "danger")
                return redirect(url_for("student.student_goal_setting"))
            if not (1 <= days_left <= 365):
                flash("Days left must be between 1 and 365.", "danger")
                return redirect(url_for("student.student_goal_setting"))

            req_attendance = current.attendance
            req_study = current.study_hours

            gender = current.gender or "Male"
            extra = current.extracurricular or "No"
            internet = current.internet_access or "Yes"
            par_ed = current.parental_education or "High School"

            best_score, _ = predict_score(req_attendance, req_study, current.previous_marks, gender, extra, internet, par_ed)

            steps = 0
            while best_score < target and steps < 100:
                if req_attendance < 98:
                    req_attendance += 1
                elif req_study < 60:
                    req_study += 2
                else:
                    break

                best_score, _ = predict_score(
                    req_attendance,
                    req_study,
                    current.previous_marks,
                    gender,
                    extra,
                    internet,
                    par_ed,
                )
                steps += 1

            new_goal = StudentGoal(
                user_id=user_id,
                target_percentage=target,
                current_percentage=current.predicted_score,
                required_attendance=round(req_attendance, 1),
                required_study_hours=round(req_study, 1),
                required_assignments=0,
            )

            db.session.add(new_goal)
            db.session.commit()

            flash(f"Goal updated for {target}%!", "success")
            return redirect(url_for("student.student_goal_setting", days_left=days_left))

        except ValueError:
            flash("Please enter valid numeric values for target and days left.", "danger")
            return redirect(url_for("student.student_goal_setting"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error calculating goals: {str(e)}", "danger")
            return redirect(url_for("student.student_goal_setting"))

    if current:
        active_target = round(goal.target_percentage, 1) if goal else round(min(100.0, current.predicted_score + 10), 1)
        goal_analysis = build_goal_analysis(
            study_hours=current.study_hours,
            attendance=current.attendance,
            past_score=current.previous_marks,
            predicted_score=current.predicted_score,
            goal_score=active_target,
            days_left=days_left_default,
        )
        if goal:
            goal_analysis["required_attendance"] = round(goal.required_attendance, 1)
            goal_analysis["required_study_hours"] = round(goal.required_study_hours, 1)
        else:
            goal_analysis["required_attendance"] = round(current.attendance, 1)
            goal_analysis["required_study_hours"] = round(current.study_hours, 1)

    return render_template(
        "student/goal_setting.html",
        current=current,
        goal=goal,
        goal_analysis=goal_analysis,
        days_left_default=days_left_default,
    )


@student_bp.route("/student/profile", methods=["GET", "POST"])
@login_required
def student_profile():
    user_id = session["user_id"]
    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash("User profile not found.", "danger")
        return redirect(url_for("student.student_dashboard"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        mobile = (request.form.get("mobile") or "").strip()
        current_password = request.form.get("current_password") or ""
        new_password = request.form.get("new_password") or ""
        confirm_password = request.form.get("confirm_password") or ""
        two_factor_enabled = 1 if request.form.get("two_factor_enabled") == "1" else 0
        uploaded_image = request.files.get("profile_image")
        old_profile_image_path = user.profile_image_path
        saved_image_path = None

        try:
            if not name or not email or not mobile:
                flash("Name, email, and mobile number are required.", "danger")
                return redirect(url_for("student.student_profile"))

            if not mobile.isdigit() or len(mobile) != 10:
                flash("Please enter a valid 10-digit mobile number.", "danger")
                return redirect(url_for("student.student_profile"))

            if (new_password or confirm_password) and not current_password:
                flash("Current password is required to change your password.", "danger")
                return redirect(url_for("student.student_profile"))

            if confirm_password and not new_password:
                flash("Please enter a new password before confirming it.", "danger")
                return redirect(url_for("student.student_profile"))

            if (new_password or confirm_password) and not check_password_hash(user.password_hash, current_password):
                flash("Current password is incorrect.", "danger")
                return redirect(url_for("student.student_profile"))

            if new_password and len(new_password) < 6:
                flash("New password must be at least 6 characters long.", "danger")
                return redirect(url_for("student.student_profile"))

            if new_password and new_password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for("student.student_profile"))

            existing = User.query.filter(User.email == email, User.id != user_id).first()
            if existing:
                flash("Email is already in use.", "danger")
                return redirect(url_for("student.student_profile"))

            if uploaded_image and uploaded_image.filename:
                original_filename = secure_filename(uploaded_image.filename)
                _, extension = os.path.splitext(original_filename)
                extension = extension.lower()
                if extension not in _ALLOWED_PROFILE_IMAGE_EXTENSIONS:
                    flash("Only PNG, JPG, JPEG, and WEBP images are allowed.", "danger")
                    return redirect(url_for("student.student_profile"))

                uploaded_image.stream.seek(0, os.SEEK_END)
                file_size = uploaded_image.stream.tell()
                uploaded_image.stream.seek(0)
                if file_size > config.PROFILE_IMAGE_MAX_BYTES:
                    flash("Profile image must be 5MB or smaller.", "danger")
                    return redirect(url_for("student.student_profile"))

                upload_subdir = config.PROFILE_IMAGE_UPLOAD_SUBDIR.strip("/\\")
                upload_root = os.path.join(current_app.static_folder, upload_subdir)
                os.makedirs(upload_root, exist_ok=True)

                new_filename = f"user_{user_id}_{uuid4().hex}{extension}"
                saved_image_path = os.path.join(upload_root, new_filename)
                uploaded_image.save(saved_image_path)
                user.profile_image_path = f"{upload_subdir}/{new_filename}".replace("\\", "/")

            user.name = name
            user.email = email
            user.mobile = mobile
            user.two_factor_enabled = two_factor_enabled
            if new_password:
                user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            if old_profile_image_path and old_profile_image_path != user.profile_image_path:
                _delete_local_profile_image(old_profile_image_path)

            session["user_name"] = name
            session["email"] = email
            session["profile_picture"] = user.profile_image_path or ""

            flash("Profile updated successfully!", "success")
            return redirect(url_for("student.student_profile"))
        except Exception as e:
            db.session.rollback()
            if saved_image_path and os.path.exists(saved_image_path):
                try:
                    os.remove(saved_image_path)
                except OSError:
                    pass
            flash(f"Update failed: {str(e)}", "danger")
            return redirect(url_for("student.student_profile"))

    profile_image_url = _resolve_profile_image_url(user.profile_image_path)
    return render_template("student/profile.html", user=user, profile_image_url=profile_image_url)
