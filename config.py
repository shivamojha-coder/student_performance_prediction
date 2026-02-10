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
#   4. Store the 16-char password in a secret store or env var (do NOT hardcode)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = os.environ.get('mrsnewzebral82@gmail.com')       
# Never default to a real password; require it from environment/secret manager
SMTP_PASSWORD = os.environ.get( 'tywa qefo xbev tglp')
OTP_EXPIRY_SECONDS = 300  # 5 minutes
