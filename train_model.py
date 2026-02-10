"""
Train student performance prediction model.
Uses existing dataset if available, otherwise uses generated data.
Trains a RandomForestRegressor pipeline and saves to model/student_model.pkl.
"""
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use generated dataset with all features (5 input columns)
dataset_path = os.path.join(BASE_DIR, 'student_data.csv')
if not os.path.exists(dataset_path):
    dataset_path = os.path.join(BASE_DIR, 'ml', 'data', 'student_performance_dataset.csv')

print(f"Loading dataset: {dataset_path}")
df = pd.read_csv(dataset_path)

print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Determine feature/target columns based on available data
if 'Internal_Marks' in df.columns:
    # Generated dataset
    feature_cols = ['Attendance_Rate', 'Study_Hours_per_Week', 'Past_Exam_Scores',
                    'Assignments_Completed', 'Internal_Marks']
    # Compute assignment ratio if total available
    if 'Total_Assignments' in df.columns:
        df['Assignment_Ratio'] = df['Assignments_Completed'] / df['Total_Assignments'] * 100
        feature_cols.append('Assignment_Ratio')
else:
    # Original dataset columns
    feature_cols = ['Attendance_Rate', 'Study_Hours_per_Week', 'Past_Exam_Scores']

target_col = 'Final_Exam_Score'

# Clean data
df = df.dropna(subset=feature_cols + [target_col])

X = df[feature_cols].values
y = df[target_col].values

print(f"\nFeatures: {feature_cols}")
print(f"Target: {target_col}")
print(f"Samples: {len(X)}")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestRegressor(random_state=42))
])

# Hyperparameter tuning
param_grid = {
    'model__n_estimators': [100, 200],
    'model__max_depth': [10, 20, None],
    'model__min_samples_split': [2, 5],
}

print("\nTraining with GridSearchCV...")
grid = GridSearchCV(pipeline, param_grid, cv=5, scoring='r2', n_jobs=-1, verbose=0)
grid.fit(X_train, y_train)

best_model = grid.best_estimator_
print(f"Best params: {grid.best_params_}")

# Evaluate
y_pred = best_model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"\n{'='*40}")
print(f"Model Evaluation Results:")
print(f"  R² Score: {r2:.4f}")
print(f"  MAE:      {mae:.4f}")
print(f"{'='*40}")

# Save model and metadata
model_dir = os.path.join(BASE_DIR, 'model')
os.makedirs(model_dir, exist_ok=True)

model_artifact = {
    'pipeline': best_model,
    'feature_cols': feature_cols,
    'r2_score': r2,
    'mae': mae,
    'best_params': grid.best_params_
}

model_path = os.path.join(model_dir, 'student_model.pkl')
joblib.dump(model_artifact, model_path)
print(f"\nModel saved to: {model_path}")

# Performance label logic
def get_performance_label(score):
    if score >= 75:
        return 'Good'
    elif score >= 50:
        return 'Average'
    else:
        return 'Poor'

# Test label distribution
labels = [get_performance_label(s) for s in y_pred]
from collections import Counter
label_counts = Counter(labels)
print(f"\nPredicted label distribution:")
for label, count in sorted(label_counts.items()):
    print(f"  {label}: {count}")
