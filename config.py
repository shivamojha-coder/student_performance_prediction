import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _fallback_load_dotenv(dotenv_path):
    """Minimal .env reader used only when python-dotenv is unavailable."""
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            raw = line.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            key = key.strip()
            if not key:
                continue
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)

dotenv_file = os.path.join(BASE_DIR, ".env")
if load_dotenv:
    load_dotenv(dotenv_file, override=True)
else:
    _fallback_load_dotenv(dotenv_file)

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DATABASE = os.path.join(BASE_DIR, 'student_perf.db')
MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'models', 'student_model.pkl')
DATASET_PATH = os.path.join(BASE_DIR, 'ml', 'data', 'student_performance_dataset.csv')
DEBUG = True
PROFILE_IMAGE_UPLOAD_SUBDIR = os.environ.get('PROFILE_IMAGE_UPLOAD_SUBDIR', 'uploads/profile_pictures')
PROFILE_IMAGE_MAX_BYTES = int(os.environ.get('PROFILE_IMAGE_MAX_BYTES', 5 * 1024 * 1024))

# â”€â”€â”€ Email / OTP Configuration (Gmail SMTP with App Password) â”€â”€â”€â”€â”€â”€â”€
# To use Gmail:
#   1. Enable 2-Step Verification on your Google Account
#   2. Go to https://myaccount.google.com/apppasswords
#   3. Generate an App Password for "Mail"
#   4. Paste that 16-char App Password below (or set via environment variable)
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com').strip() or 'smtp.gmail.com'
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '').strip()
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '').strip()
OTP_EXPIRY_SECONDS = 300  # 5 minutes

# â”€â”€â”€ Google OAuth 2.0 Configuration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
# Optional overrides for OAuth callback URLs:
# - GOOGLE_REDIRECT_URI: full callback URL for Google only
# - OAUTH_REDIRECT_BASE_URL: common base URL, e.g. https://yourdomain.com
GOOGLE_REDIRECT_URI = os.environ.get(
    'GOOGLE_REDIRECT_URI',
    ''
).strip()
OAUTH_REDIRECT_BASE_URL = os.environ.get('OAUTH_REDIRECT_BASE_URL', '').strip()
# Microsoft OAuth 2.0 Configuration
# Redirect URI to add in Azure:
#   http://localhost:5000/auth/microsoft/callback
MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID', '')
MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET', '')
MICROSOFT_TENANT_ID = os.environ.get('MICROSOFT_TENANT_ID', 'common')
MICROSOFT_AUTHORITY = f'https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}'
MICROSOFT_AUTHORIZE_URL = f'{MICROSOFT_AUTHORITY}/oauth2/v2.0/authorize'
MICROSOFT_TOKEN_URL = f'{MICROSOFT_AUTHORITY}/oauth2/v2.0/token'
MICROSOFT_SCOPE = 'openid profile email User.Read'

# â”€â”€â”€ Session Configuration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SESSION_COOKIE_HTTPONLY = True        # Prevent JS access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'      # CSRF protection
PERMANENT_SESSION_LIFETIME = 1800    # 30 minutes

