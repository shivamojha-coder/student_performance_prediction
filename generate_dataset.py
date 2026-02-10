"""
Generate synthetic student performance dataset.
This supplements the existing dataset with additional features needed for the platform.
"""
import pandas as pd
import numpy as np
import os

np.random.seed(42)

N = 500

# Generate base features
attendance = np.random.uniform(40, 100, N)
study_hours = np.random.uniform(5, 40, N)
previous_marks = np.random.uniform(30, 100, N)
assignments = np.random.randint(5, 20, N)
total_assignments = np.random.randint(15, 20, N)
internal_marks = np.random.uniform(5, 30, N)

classes = np.random.choice([
    'Computer Science 101', 'Advanced Math', 'Database Systems',
    'ML Fundamentals', 'UI/UX Design', 'Statistical Analysis'
], N)

genders = np.random.choice(['Male', 'Female'], N)

# Generate correlated final score
final_score = (
    0.25 * attendance +
    0.20 * (study_hours / 40 * 100) +
    0.25 * previous_marks +
    0.15 * (assignments / total_assignments * 100) +
    0.15 * (internal_marks / 30 * 100) +
    np.random.normal(0, 5, N)
)

final_score = np.clip(final_score, 0, 100).round(1)

# Build DataFrame
df = pd.DataFrame({
    'Student_ID': [f'S{str(i).zfill(3)}' for i in range(1, N + 1)],
    'Gender': genders,
    'Attendance_Rate': attendance.round(2),
    'Study_Hours_per_Week': study_hours.round(1),
    'Past_Exam_Scores': previous_marks.round(1),
    'Assignments_Completed': assignments,
    'Total_Assignments': total_assignments,
    'Internal_Marks': internal_marks.round(1),
    'Class': classes,
    'Final_Exam_Score': final_score,
    'Pass_Fail': np.where(final_score >= 50, 'Pass', 'Fail')
})

out_path = os.path.join(os.path.dirname(__file__), 'student_data.csv')
df.to_csv(out_path, index=False)
print(f"Generated {N} records → {out_path}")
print(f"Score range: {final_score.min():.1f} – {final_score.max():.1f}")
print(f"Pass rate: {(final_score >= 50).mean() * 100:.1f}%")
