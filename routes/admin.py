import csv
import io
from datetime import datetime

from flask import Blueprint, Response, render_template, request
from sqlalchemy import func

from core.decorators import admin_required
from core.extensions import db
from models.entities import Prediction, User


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    class_rows = db.session.query(Prediction.class_name).distinct().order_by(Prediction.class_name.asc()).all()
    classes = [{"class_name": c[0]} for c in class_rows if c[0]]
    selected_class = request.args.get("class", "All")

    base_query = Prediction.query
    if selected_class != "All":
        base_query = base_query.filter(Prediction.class_name == selected_class)

    total_students = User.query.filter_by(role="student").count()
    total_predictions = base_query.count()
    avg_score_val = base_query.with_entities(func.avg(Prediction.predicted_score)).scalar()
    avg_score = round(avg_score_val, 1) if avg_score_val else 0

    at_risk = base_query.filter(Prediction.performance_label == "Poor").count()
    good_count = base_query.filter(Prediction.performance_label == "Good").count()
    avg_count = base_query.filter(Prediction.performance_label == "Average").count()

    recent_q = (
        db.session.query(
            Prediction.id,
            Prediction.class_name,
            Prediction.predicted_score,
            Prediction.performance_label,
            Prediction.created_at,
            User.name.label("name"),
            User.student_id.label("student_id"),
        )
        .join(User, Prediction.user_id == User.id)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .limit(10)
    )
    if selected_class != "All":
        recent_q = recent_q.filter(Prediction.class_name == selected_class)

    recent_flags = [
        {
            "id": row.id,
            "class_name": row.class_name,
            "predicted_score": row.predicted_score,
            "performance_label": row.performance_label,
            "created_at": row.created_at,
            "name": row.name,
            "student_id": row.student_id,
        }
        for row in recent_q.all()
    ]

    stats = {
        "total_students": total_students,
        "avg_score": avg_score,
        "total_predictions": total_predictions,
        "at_risk": at_risk,
        "good": good_count,
        "average": avg_count,
        "poor": at_risk,
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        classes=classes,
        selected_class=selected_class,
        recent_flags=recent_flags,
    )


@admin_bp.route("/admin/students")
@admin_required
def admin_students():
    search = request.args.get("search", "")
    class_filter = request.args.get("class", "")

    users_q = User.query.filter(User.role == "student")
    if search:
        like = f"%{search}%"
        users_q = users_q.filter(
            (User.name.like(like)) | (User.email.like(like)) | (User.student_id.like(like))
        )
    if class_filter:
        users_q = users_q.filter(User.class_name == class_filter)

    users = users_q.order_by(User.name.asc()).all()

    students = []
    for user in users:
        latest = (
            Prediction.query.filter_by(user_id=user.id)
            .order_by(Prediction.created_at.desc(), Prediction.id.desc())
            .first()
        )
        prediction_count = Prediction.query.filter_by(user_id=user.id).count()
        students.append(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "student_id": user.student_id,
                "class_name": user.class_name,
                "created_at": user.created_at,
                "latest_score": latest.predicted_score if latest else None,
                "latest_label": latest.performance_label if latest else None,
                "prediction_count": prediction_count,
            }
        )

    class_rows = (
        db.session.query(User.class_name)
        .filter(User.role == "student")
        .distinct()
        .order_by(User.class_name.asc())
        .all()
    )
    classes = [{"class_name": c[0]} for c in class_rows if c[0]]

    return render_template(
        "admin/students.html",
        students=students,
        classes=classes,
        search=search,
        class_filter=class_filter,
    )


@admin_bp.route("/admin/reports")
@admin_required
def admin_reports():
    class_rows = db.session.query(Prediction.class_name).distinct().order_by(Prediction.class_name.asc()).all()
    classes = [{"class_name": c[0]} for c in class_rows if c[0]]
    return render_template("admin/reports.html", classes=classes)


@admin_bp.route("/admin/export/csv")
@admin_required
def export_csv():
    class_filter = request.args.get("class", "")

    query = db.session.query(
        User.name,
        User.email,
        User.student_id,
        User.class_name,
        Prediction.attendance,
        Prediction.study_hours,
        Prediction.previous_marks,
        Prediction.assignments,
        Prediction.internal_marks,
        Prediction.predicted_score,
        Prediction.performance_label,
        Prediction.created_at,
    ).join(User, Prediction.user_id == User.id)

    if class_filter:
        query = query.filter(Prediction.class_name == class_filter)
    rows = query.order_by(Prediction.created_at.desc(), Prediction.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Name",
            "Email",
            "Student ID",
            "Class",
            "Attendance",
            "Study Hours",
            "Previous Marks",
            "Assignments",
            "Internal Marks",
            "Predicted Score",
            "Performance",
            "Date",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.name,
                row.email,
                row.student_id,
                row.class_name,
                row.attendance,
                row.study_hours,
                row.previous_marks,
                row.assignments,
                row.internal_marks,
                row.predicted_score,
                row.performance_label,
                row.created_at,
            ]
        )

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=student_report_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@admin_bp.route("/admin/export/pdf")
@admin_required
def export_pdf():
    from fpdf import FPDF

    class_filter = request.args.get("class", "")

    query = db.session.query(
        User.name,
        User.student_id,
        User.class_name,
        Prediction.predicted_score,
        Prediction.performance_label,
        Prediction.created_at,
    ).join(User, Prediction.user_id == User.id)

    if class_filter:
        query = query.filter(Prediction.class_name == class_filter)
    rows = query.order_by(Prediction.created_at.desc(), Prediction.id.desc()).limit(50).all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Student Performance Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y')}", ln=True, align="C")
    if class_filter:
        pdf.cell(0, 8, f"Class: {class_filter}", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(26, 115, 232)
    pdf.set_text_color(255, 255, 255)
    col_widths = [45, 25, 45, 25, 25, 25]
    headers = ["Name", "ID", "Class", "Score", "Level", "Date"]
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    for row in rows:
        pdf.cell(col_widths[0], 7, str(row.name)[:25], border=1)
        pdf.cell(col_widths[1], 7, str(row.student_id or ""), border=1, align="C")
        pdf.cell(col_widths[2], 7, str(row.class_name)[:25], border=1)
        pdf.cell(col_widths[3], 7, str(row.predicted_score), border=1, align="C")
        pdf.cell(col_widths[4], 7, str(row.performance_label), border=1, align="C")
        date_str = row.created_at.strftime("%Y-%m-%d") if row.created_at else ""
        pdf.cell(col_widths[5], 7, date_str, border=1, align="C")
        pdf.ln()

    pdf_bytes = pdf.output()
    return Response(
        bytes(pdf_bytes),
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d')}.pdf"},
    )

