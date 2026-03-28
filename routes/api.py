from flask import Blueprint, jsonify, request
from sqlalchemy import func

from core.decorators import admin_required
from core.extensions import db
from models.entities import Prediction


api_bp = Blueprint("api", __name__)


@api_bp.route("/api/class-stats")
@admin_required
def class_stats():
    class_name = request.args.get("class", "All")

    base_query = Prediction.query
    if class_name != "All":
        base_query = base_query.filter(Prediction.class_name == class_name)

    good = base_query.filter(Prediction.performance_label == "Good").count()
    average = base_query.filter(Prediction.performance_label == "Average").count()
    poor = base_query.filter(Prediction.performance_label == "Poor").count()

    monthly_scores = (
        base_query.with_entities(
            func.strftime("%Y-%m", Prediction.created_at).label("month"),
            func.avg(Prediction.predicted_score).label("avg_score"),
        )
        .group_by("month")
        .order_by(func.strftime("%Y-%m", Prediction.created_at).desc())
        .limit(7)
        .all()
    )

    class_comparison = (
        db.session.query(
            Prediction.class_name.label("class_name"),
            func.avg(Prediction.predicted_score).label("avg_score"),
            func.count(Prediction.id).label("count"),
        )
        .group_by(Prediction.class_name)
        .order_by(func.avg(Prediction.predicted_score).desc())
        .all()
    )

    return jsonify(
        {
            "distribution": {"good": good, "average": average, "poor": poor},
            "monthly_trend": {
                "labels": [r.month for r in reversed(monthly_scores)],
                "scores": [round(r.avg_score, 1) for r in reversed(monthly_scores)],
            },
            "class_comparison": {
                "labels": [r.class_name for r in class_comparison],
                "scores": [round(r.avg_score, 1) for r in class_comparison],
                "counts": [r.count for r in class_comparison],
            },
            "summary": {
                "total_predictions": good + average + poor,
                "avg_score": round((good * 85 + average * 62 + poor * 35) / max(good + average + poor, 1), 1),
                "pass_rate": round((good + average) / max(good + average + poor, 1) * 100, 1),
            },
        }
    )
