import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DATABASE = os.path.join(BASE_DIR, 'student_perf.db')
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'student_model.pkl')
DATASET_PATH = os.path.join(BASE_DIR, 'ml', 'data', 'student_performance_dataset.csv')
DEBUG = True

# ─── Email / OTP Configuration (Gmail SMTP with App Password) ───────
# To use Gmail:
#   1. Enable 2-Step Verification on your Google Account
#   2. Go to https://myaccount.google.com/apppasswords
#   3. Generate an App Password for "Mail"
#   4. Paste the 16-char password below (no spaces)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', 'mrsnewzebral82@gmail.com')       
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'ozpqqfvtynptigfy')
OTP_EXPIRY_SECONDS = 300  # 5 minutesss
