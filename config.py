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
#   4. Paste that 16-char App Password below (or set via environment variable)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', 'mrsnewzebral82@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'ubrc zsjc feho ejzp')
OTP_EXPIRY_SECONDS = 300  # 5 minutes

# ─── Google OAuth 2.0 Configuration ─────────────────────────────────
# To set up Google OAuth:
#   1. Go to https://console.cloud.google.com/apis/credentials
#   2. Create a new OAuth 2.0 Client ID (Web application)
#   3. Add http://localhost:5000 to Authorized JavaScript Origins
#   4. Add http://localhost:5000/auth/google/callback to Authorized Redirect URIs
#   5. Copy the Client ID and Client Secret below
GOOGLE_CLIENT_ID = os.environ.get(
    'GOOGLE_CLIENT_ID',
    'your_id_here'
)
GOOGLE_CLIENT_SECRET = os.environ.get(
    'GOOGLE_CLIENT_SECRET',
    'your_secret_here'
)
GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'

# ─── Session Configuration ──────────────────────────────────────────
SESSION_COOKIE_HTTPONLY = True        # Prevent JS access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'      # CSRF protection
PERMANENT_SESSION_LIFETIME = 1800    # 30 minutes
