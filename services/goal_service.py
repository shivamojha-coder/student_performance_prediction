import math


def _build_feasibility(gap, days_left, study_hours, attendance):
    if gap > days_left:
        return "Unrealistic Goal"

    if gap <= 5:
        level_index = 0
    elif gap <= 15:
        level_index = 1
    else:
        level_index = 2

    if study_hours < 10:
        level_index = min(level_index + 1, 2)
    if attendance < 75:
        level_index = min(level_index + 1, 2)

    levels = [
        "Easily Achievable",
        "Moderately Challenging",
        "Difficult but Possible",
    ]
    return levels[level_index]


def _study_hours_band(gap):
    if gap > 15:
        return 4, 6
    if gap >= 8:
        return 3, 4
    return 2, 3


def _weekly_breakdown(predicted_score, gap, days_left):
    weeks = max(1, math.ceil(days_left / 7))
    rows = []

    if gap <= 0:
        for week_no in range(1, weeks + 1):
            rows.append(
                {
                    "week": week_no,
                    "improvement": 0.0,
                    "expected_score": round(min(100, predicted_score), 1),
                }
            )
        return rows

    remaining = round(gap, 2)
    cumulative = 0.0
    for week_no in range(1, weeks + 1):
        weeks_left = weeks - week_no + 1
        step = round(remaining / weeks_left, 2)
        remaining = round(max(0.0, remaining - step), 2)
        cumulative = round(cumulative + step, 2)
        rows.append(
            {
                "week": week_no,
                "improvement": step,
                "expected_score": round(min(100, predicted_score + cumulative), 1),
            }
        )
    return rows


def build_goal_analysis(study_hours, attendance, past_score, predicted_score, goal_score, days_left):
    gap_raw = round(goal_score - predicted_score, 1)
    gap = round(max(0.0, gap_raw), 1)
    goal_already_met = gap_raw <= 0

    feasibility = _build_feasibility(gap, days_left, study_hours, attendance)
    if goal_already_met:
        feasibility = "Easily Achievable"

    daily_improvement = round(gap / days_left, 2) if days_left > 0 else 0.0
    day_min, day_max = _study_hours_band(gap)

    weak_min, weak_max = round(day_min * 0.5, 1), round(day_max * 0.5, 1)
    practice_min, practice_max = round(day_min * 0.3, 1), round(day_max * 0.3, 1)
    revision_min, revision_max = round(day_min * 0.2, 1), round(day_max * 0.2, 1)

    weekly_targets = _weekly_breakdown(predicted_score, gap, days_left)
    recommended_weekly_min = day_min * 7

    recommendations = []
    if study_hours < recommended_weekly_min:
        recommendations.append(
            f"Current study time is {study_hours:.1f} hrs/week. Increase it to at least {recommended_weekly_min:.1f} hrs/week."
        )
    if attendance < 75:
        recommendations.append(
            f"Attendance is {attendance:.1f}%. Push it above 75% quickly to improve consistency and internal marks."
        )
    if past_score < 60:
        recommendations.append(
            "Past score is low, so spend extra time on core concepts before moving to advanced practice."
        )
    if predicted_score >= 85:
        recommendations.append(
            "Predicted score is already strong. Focus on timed mock tests and error analysis to stay above target."
        )
    if days_left <= 14 and gap > 5:
        recommendations.append(
            "Exam is close. Prioritize high-weight topics and one full-length mock test every 2-3 days."
        )
    if not recommendations:
        recommendations.append(
            "Your profile is balanced. Follow the daily plan consistently and track progress every evening."
        )

    behavioral_insights = [
        "Stay consistent with fixed daily slots instead of long random sessions.",
        "Avoid last-minute cramming. Use short revision loops every day.",
        "Start each session with your weakest subject first.",
        "Track daily progress in a notebook and adjust next day targets.",
    ]

    if feasibility == "Unrealistic Goal":
        final_advice = "Target ko phased milestones me split karo, fir har week measurable progress maintain karo."
    elif feasibility == "Difficult but Possible":
        final_advice = "Discipline aur daily tracking se ye target possible hai, lekin break days minimum rakho."
    elif feasibility == "Moderately Challenging":
        final_advice = "Plan consistent rakho, weekly review karo, aur weak topics par regular practice maintain karo."
    else:
        final_advice = "Aapka goal reachable hai. Bas daily routine ko stable rakho aur mock tests continue karo."

    return {
        "study_hours": round(study_hours, 1),
        "attendance": round(attendance, 1),
        "past_score": round(past_score, 1),
        "predicted_score": round(predicted_score, 1),
        "goal_score": round(goal_score, 1),
        "days_left": int(days_left),
        "goal_already_met": goal_already_met,
        "feasibility": feasibility,
        "gap": gap,
        "daily_improvement": daily_improvement,
        "daily_hours_min": day_min,
        "daily_hours_max": day_max,
        "time_distribution": {
            "weak_areas": f"{weak_min}-{weak_max} hrs/day (50%)",
            "practice": f"{practice_min}-{practice_max} hrs/day (30%)",
            "revision": f"{revision_min}-{revision_max} hrs/day (20%)",
        },
        "weekly_targets": weekly_targets,
        "recommendations": recommendations,
        "behavioral_insights": behavioral_insights,
        "final_advice": final_advice,
    }
