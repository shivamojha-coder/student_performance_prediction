import joblib
import numpy as np

import config


def predict_score(attendance, study_hours, previous_marks, gender, extracurricular, internet_access, parental_education):
    """Load model and predict score using 7 features."""
    model_artifact = joblib.load(config.MODEL_PATH)
    encoders = joblib.load("ml/models/feature_encoders.pkl")

    if isinstance(model_artifact, dict):
        pipeline = model_artifact.get("pipeline", model_artifact.get("model"))
    elif isinstance(model_artifact, list):
        pipeline = model_artifact[0]
    else:
        pipeline = model_artifact

    try:
        e_gender = encoders["Gender"].transform([gender])[0]
        e_ed = encoders["Parental_Education_Level"].transform([parental_education])[0]
        e_internet = encoders["Internet_Access_at_Home"].transform([internet_access])[0]
        e_extra = encoders["Extracurricular_Activities"].transform([extracurricular])[0]
    except Exception as e:
        print(f"Encoding error: {e}")
        e_gender, e_ed, e_internet, e_extra = 0, 0, 1, 0

    features = [
        e_gender,
        study_hours,
        attendance,
        previous_marks,
        e_ed,
        e_internet,
        e_extra,
    ]

    X = np.array(features).reshape(1, -1)
    score = float(pipeline.predict(X)[0])
    score = max(0, min(100, round(score, 1)))

    if score >= 75:
        label = "Good"
    elif score >= 50:
        label = "Average"
    else:
        label = "Poor"

    return score, label

