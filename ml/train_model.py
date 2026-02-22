import pandas as pd
import joblib
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('ml/data/student_performance_dataset.csv')
print("\n" + "="*80)
print("DATA INFO")
print("="*80 + "\n")
df.info()

print("\n" + "="*80)
print("DATA DESCRIBE")
print("="*80 + "\n")
print(df.describe())

print("\n" + "="*80)
print("MISSING VALUES")
print("="*80 + "\n")
print(df.isnull().sum())

#  REMOVE UNWANTED COLUMNS
print("\n" + "="*80)
print("REMOVING UNWANTED COLUMNS")
print("="*80 + "\n")

# Drop columns if they exist
cols_to_drop = ['Student_ID', 'Pass_Fail']
df = df.drop(columns=cols_to_drop, errors='ignore')
print(f"Dropped columns: {cols_to_drop}")

print("Dataset after Removing Unwanted Columns: ")
print(df.head())

#  SPLIT FEATURES AND TARGET
print("\n" + "="*80)
print("SPLITTING FEATURES AND TARGET")
print("="*80 + "\n")

X = df.drop(columns=['Final_Exam_Score'])
y = df['Final_Exam_Score']
print("Features:", X.columns.to_list())
print("Target:", y.name)

# ===============================
# 7. ENCODE CATEGORICAL FEATURES
print("\n" + "="*80)
print("ENCODING CATEGORICAL FEATURES")
print("="*80 + "\n")

# Store encoders in a dictionary for later use in predictions
feature_encoders = {}
for col in X.select_dtypes(include=["object"]).columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    feature_encoders[col] = le  # Store encoder for each column
    print(f"Encoded: {col}")


# ===============================
# 8. SPLIT DATA INTO TRAINING AND TESTING SETS
print("\n" + "="*80)
print("SPLITTING DATA INTO TRAINING AND TESTING SETS")
print("="*80 + "\n")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training set size: {X_train.shape[0]} samples")
print(f"Testing set size: {X_test.shape[0]} samples")

# ===============================
# 9. TRAIN RANDOM FOREST CLASSIFIER
print("\n" + "="*80)
print("\n" + "="*80)
print("TRAINING RANDOM FOREST REGRESSOR")
print("="*80 + "\n")

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("Random Forest model training complete.")

# Check Feature Importance
importances = model.feature_importances_
feature_names = X.columns
feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

print("\n" + "="*80)
print("FEATURE IMPORTANCE")
print("="*80 + "\n")
print(feature_importance_df)



# Combine X and y for correlation
df_corr = X.copy()
df_corr['target'] = y
correlation = df_corr.corr()['target'].sort_values(ascending=False)

print("Feature Correlation with Target:")
print(correlation)
print("-" * 40)

# 10.2 Training vs Testing Accuracy (R^2 Score)
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print(f"Training R^2 Score: {train_score:.4f}")
print(f"Testing R^2 Score:  {test_score:.4f}")

# 10.3 Output Regression Metrics
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)

print(f"RMSE: {rmse:.4f}")
print(f"MAE:  {mae:.4f}")
print("-" * 40)




# ===============================
# 11. SAVE MODEL AND ENCODERS
# ===============================
if not os.path.exists('ml/models'):
    os.makedirs('ml/models')

# Save Model
joblib.dump(model, 'ml/models/student_model.pkl')
print("\nModel saved to ml/models/student_model.pkl")

# Save the feature encoders that were used during training
joblib.dump(feature_encoders, 'ml/models/feature_encoders.pkl')
print("Feature Encoders saved to ml/models/feature_encoders.pkl")


