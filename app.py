"""
Flask Application — Student Performance Prediction Platform
"""
import os
import sqlite3
import csv
import io
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from functools import wraps
import time

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, jsonify, Response, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import numpy as np
import requests as http_requests

import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['DATABASE'] = config.DATABASE
app.config['SESSION_COOKIE_HTTPONLY'] = getattr(config, 'SESSION_COOKIE_HTTPONLY', True)
app.config['SESSION_COOKIE_SAMESITE'] = getattr(config, 'SESSION_COOKIE_SAMESITE', 'Lax')
from datetime import timedelta
app.permanent_session_lifetime = timedelta(seconds=getattr(config, 'PERMANENT_SESSION_LIFETIME', 1800))

# ─── Database helpers ────────────────────────────────────────────────

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database from schema.sql and create admin user."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        script = f.read()
    # Remove the INSERT line — we'll handle admin creation below
    lines = [l for l in script.split('\n') if not l.strip().startswith('INSERT')]
    db.executescript('\n'.join(lines))

    # Create default admin
    admin_hash = generate_password_hash('admin123')
    try:
        db.execute(
            'INSERT INTO users (name, email, mobile, password_hash, role, class_name, student_id, is_verified) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            ('Dr. Julian Vance', 'admin@edupredict.com', '0000000000', admin_hash, 'admin', 'All', 'ADM-0001', 1)
        )
        db.commit()
        print("Admin user created: admin@edupredict.com / admin123")
    except sqlite3.IntegrityError:
        pass  # Already exists

@app.cli.command('init-db')
def init_db_command():
    init_db()
    print('Database initialized.')

# ─── Auth decorators ─────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('student_dashboard'))
        return f(*args, **kwargs)
    return decorated

# ─── ML helper ───────────────────────────────────────────────────────

def predict_score(attendance, study_hours, previous_marks, assignments, internal_marks):
    """Load model and predict score."""
    model_artifact = joblib.load(config.MODEL_PATH)
    pipeline = model_artifact['pipeline']
    feature_cols = model_artifact['feature_cols']

    # Build feature vector matching training features
    features = [attendance, study_hours, previous_marks]
    if 'Assignments_Completed' in feature_cols or 'Internal_Marks' in feature_cols:
        features.append(assignments)
        features.append(internal_marks)
    if 'Assignment_Ratio' in feature_cols:
        ratio = (assignments / 15) * 100  # Assume ~15 total assignments
        features.append(ratio)

    X = np.array(features).reshape(1, -1)
    score = float(pipeline.predict(X)[0])
    score = max(0, min(100, round(score, 1)))

    if score >= 75:
        label = 'Good'
    elif score >= 50:
        label = 'Average'
    else:
        label = 'Poor'

    return score, label

def generate_student_id():
    """Generate a unique student ID."""
    nums = ''.join(random.choices(string.digits, k=4))
    return f'STU-{nums}-{random.randint(10, 99)}'

# ─── OTP / Email helpers ────────────────────────────────────────────

# In-memory store: { email: { 'otp': '123456', 'expires': timestamp } }
_otp_store: dict = {}

def generate_otp(length=6):
    """Generate a numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(recipient_email, otp_code):
    """Send an OTP verification email via Gmail SMTP."""
    subject = 'SuccessPredict — Email Verification Code'
    html_body = f"""
    <div style="font-family:'Inter',Arial,sans-serif;max-width:480px;margin:auto;
                padding:32px;background:#f8fafc;border-radius:12px;">
        <h2 style="color:#1a365d;margin:0 0 8px;">SuccessPredict</h2>
        <p style="color:#4a5568;font-size:14px;">Use the code below to verify your email
           and complete your registration.</p>
        <div style="text-align:center;margin:24px 0;">
            <span style="display:inline-block;font-size:32px;letter-spacing:8px;
                         font-weight:700;color:#2563eb;background:#e0e7ff;
                         padding:12px 28px;border-radius:8px;">{otp_code}</span>
        </div>
        <p style="color:#718096;font-size:13px;">This code expires in 5 minutes.
           If you didn't request this, just ignore this email.</p>
    </div>
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config.SMTP_EMAIL
    msg['To'] = recipient_email
    msg.attach(MIMEText(f'Your SuccessPredict verification code is: {otp_code}', 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(config.SMTP_EMAIL, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_EMAIL, recipient_email, msg.as_string())

def store_otp(email, otp_code):
    """Store OTP with expiry."""
    _otp_store[email] = {
        'otp': otp_code,
        'expires': time.time() + config.OTP_EXPIRY_SECONDS,
    }

def verify_otp(email, user_otp):
    """Return True if `user_otp` matches and hasn't expired."""
    entry = _otp_store.get(email)
    if not entry:
        return False
    if time.time() > entry['expires']:
        _otp_store.pop(email, None)
        return False
    if entry['otp'] != user_otp:
        return False
    _otp_store.pop(email, None)
    return True

# ─── Google OAuth helpers ────────────────────────────────────────────

def get_google_provider_cfg():
    """Fetch Google's OpenID Connect discovery document."""
    return http_requests.get(config.GOOGLE_DISCOVERY_URL, timeout=10).json()


def _google_login_user(google_id, name, email, picture):
    """Find or create a user from Google data and set session. Returns redirect."""
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if user:
        # Existing user — log them in
        session.permanent = True
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['role'] = user['role']
        session['email'] = user['email']
        session['class_name'] = user['class_name']
        session['student_id'] = user['student_id']
        session['profile_picture'] = picture
        flash(f'Welcome back, {user["name"]}!', 'success')
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    else:
        # New user — auto-create student account
        student_id = generate_student_id()
        random_pw = generate_password_hash(os.urandom(24).hex())
        cursor = db.execute(
            'INSERT INTO users (name, email, mobile, password_hash, role, '
            'class_name, student_id, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (name, email, '', random_pw, 'student',
             'Computer Science 101', student_id, 1)
        )
        db.commit()
        new_id = cursor.lastrowid

        session.permanent = True
        session['user_id'] = new_id
        session['user_name'] = name
        session['role'] = 'student'
        session['email'] = email
        session['class_name'] = 'Computer Science 101'
        session['student_id'] = student_id
        session['profile_picture'] = picture
        flash(f'Welcome, {name}! Your account has been created via Google.', 'success')
        return redirect(url_for('student_dashboard'))

# ─── Routes ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

# ── Auth ──

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            if user['role'] != role:
                flash(f'This account is registered as {user["role"]}, not {role}.', 'danger')
                return render_template('login.html')

            session.permanent = True
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']
            session['class_name'] = user['class_name']
            session['student_id'] = user['student_id']

            flash(f'Welcome back, {user["name"]}!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        class_name = request.form.get('class_name', 'Computer Science 101')

        if not name or not email or not mobile or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        # Validate mobile number (digits only, 10 digits)
        import re
        if not re.match(r'^\d{10}$', mobile):
            flash('Please enter a valid 10-digit mobile number.', 'danger')
            return render_template('register.html')

        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        # Generate & send OTP
        otp_code = generate_otp()
        try:
            send_otp_email(email, otp_code)
        except Exception as e:
            print(f'[OTP] Email send error: {e}')
            flash('Failed to send verification email. Please try again.', 'danger')
            return render_template('register.html')

        store_otp(email, otp_code)

        # Stash registration data in session until verified
        session['pending_reg'] = {
            'name': name,
            'email': email,
            'mobile': mobile,
            'password': password,
            'class_name': class_name,
        }
        flash('A 6-digit verification code has been sent to your email.', 'info')
        return redirect(url_for('verify_otp_page'))

    return render_template('register.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    pending = session.get('pending_reg')
    if not pending:
        flash('Please register first.', 'warning')
        return redirect(url_for('register'))

    if request.method == 'POST':
        user_otp = request.form.get('otp', '').strip()
        email = pending['email']

        if verify_otp(email, user_otp):
            # OTP correct — create the user account
            db = get_db()
            student_id = generate_student_id()
            password_hash = generate_password_hash(pending['password'])
            cursor = db.execute(
                'INSERT INTO users (name, email, mobile, password_hash, role, class_name, student_id, is_verified) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (pending['name'], email, pending.get('mobile', ''), password_hash,
                 'student', pending['class_name'], student_id, 1)
            )
            db.commit()
            new_user_id = cursor.lastrowid
            session.pop('pending_reg', None)

            # Auto-login: set session variables and redirect to dashboard
            session.permanent = True
            session['user_id'] = new_user_id
            session['user_name'] = pending['name']
            session['role'] = 'student'
            session['email'] = email
            session['class_name'] = pending['class_name']
            session['student_id'] = student_id

            flash(f'Welcome, {pending["name"]}! Your account has been created successfully.', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')

    masked_email = pending['email']
    at_idx = masked_email.index('@')
    masked_email = masked_email[0] + '***' + masked_email[at_idx:]
    return render_template('verify_otp.html', masked_email=masked_email)

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    pending = session.get('pending_reg')
    if not pending:
        flash('Please register first.', 'warning')
        return redirect(url_for('register'))

    email = pending['email']
    otp_code = generate_otp()
    try:
        send_otp_email(email, otp_code)
        store_otp(email, otp_code)
        flash('A new code has been sent to your email.', 'info')
    except Exception as e:
        print(f'[OTP] Resend error: {e}')
        flash('Failed to resend code. Please try again.', 'danger')

    return redirect(url_for('verify_otp_page'))

# ── Google OAuth Routes ──

@app.route('/auth/google')
def google_login():
    """Redirect user to Google's OAuth 2.0 consent screen."""
    try:
        google_cfg = get_google_provider_cfg()
        authorization_endpoint = google_cfg['authorization_endpoint']
    except Exception:
        flash('Unable to reach Google. Please try again later.', 'danger')
        return redirect(url_for('login'))

    # Generate a random state token for CSRF protection
    state = os.urandom(16).hex()
    session['oauth_state'] = state

    callback_url = url_for('google_callback', _external=True)
    params = {
        'client_id': config.GOOGLE_CLIENT_ID,
        'redirect_uri': callback_url,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
        'prompt': 'select_account',
    }
    auth_url = f"{authorization_endpoint}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return redirect(auth_url)


@app.route('/auth/google/callback')
def google_callback():
    """Handle the callback from Google after user grants consent."""
    # Verify state to prevent CSRF
    if request.args.get('state') != session.pop('oauth_state', None):
        flash('Authentication failed — invalid state. Please try again.', 'danger')
        return redirect(url_for('login'))

    code = request.args.get('code')
    if not code:
        flash('Google sign-in was cancelled.', 'warning')
        return redirect(url_for('login'))

    try:
        google_cfg = get_google_provider_cfg()
        token_endpoint = google_cfg['token_endpoint']

        # Exchange the authorization code for tokens
        token_response = http_requests.post(
            token_endpoint,
            data={
                'code': code,
                'client_id': config.GOOGLE_CLIENT_ID,
                'client_secret': config.GOOGLE_CLIENT_SECRET,
                'redirect_uri': url_for('google_callback', _external=True),
                'grant_type': 'authorization_code',
            },
            timeout=10,
        )
        token_data = token_response.json()

        if 'error' in token_data:
            flash('Google authentication failed. Please try again.', 'danger')
            return redirect(url_for('login'))

        # Use the access token to get user info
        userinfo_endpoint = google_cfg['userinfo_endpoint']
        userinfo_response = http_requests.get(
            userinfo_endpoint,
            headers={'Authorization': f'Bearer {token_data["access_token"]}'},
            timeout=10,
        )
        userinfo = userinfo_response.json()

        if not userinfo.get('email_verified', False):
            flash('Google account email is not verified.', 'danger')
            return redirect(url_for('login'))

        google_id = userinfo['sub']
        email = userinfo['email']
        name = userinfo.get('name', email.split('@')[0])
        picture = userinfo.get('picture', '')

        return _google_login_user(google_id, name, email, picture)

    except Exception as e:
        print(f'[Google OAuth] Error: {e}')
        flash('Google sign-in failed. Please try again.', 'danger')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ── Student Routes ──

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    db = get_db()
    recent = db.execute(
        'SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
        (session['user_id'],)
    ).fetchall()
    return render_template('student/dashboard.html', recent_predictions=recent)

@app.route('/student/predict', methods=['POST'])
@login_required
def student_predict():
    try:
        attendance = float(request.form.get('attendance', 0))
        study_hours = float(request.form.get('study_hours', 0))
        previous_marks = float(request.form.get('previous_marks', 0))
        assignments = float(request.form.get('assignments', 0))
        internal_marks = float(request.form.get('internal_marks', 0))
        class_name = request.form.get('class_name', session.get('class_name', 'Computer Science 101'))

        # Validate ranges
        if not (0 <= attendance <= 100):
            flash('Attendance must be between 0 and 100.', 'danger')
            return redirect(url_for('student_dashboard'))
        if not (0 <= study_hours <= 80):
            flash('Study hours must be between 0 and 80.', 'danger')
            return redirect(url_for('student_dashboard'))

        score, label = predict_score(attendance, study_hours, previous_marks, assignments, internal_marks)

        db = get_db()
        cursor = db.execute(
            'INSERT INTO predictions '
            '(user_id, attendance, study_hours, previous_marks, assignments, internal_marks, '
            'class_name, predicted_score, performance_label) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (session['user_id'], attendance, study_hours, previous_marks,
             assignments, internal_marks, class_name, score, label)
        )
        db.commit()
        prediction_id = cursor.lastrowid
        return redirect(url_for('student_result', pred_id=prediction_id))

    except Exception as e:
        flash(f'Prediction failed: {str(e)}', 'danger')
        return redirect(url_for('student_dashboard'))

@app.route('/student/result/<int:pred_id>')
@login_required
def student_result(pred_id):
    db = get_db()
    prediction = db.execute(
        'SELECT * FROM predictions WHERE id = ? AND user_id = ?',
        (pred_id, session['user_id'])
    ).fetchone()
    if not prediction:
        flash('Prediction not found.', 'danger')
        return redirect(url_for('student_dashboard'))

    # Get class averages for comparison
    class_avg = db.execute(
        'SELECT AVG(attendance) as avg_attendance, AVG(study_hours) as avg_study, '
        'AVG(previous_marks) as avg_marks, AVG(predicted_score) as avg_score '
        'FROM predictions WHERE class_name = ?',
        (prediction['class_name'],)
    ).fetchone()

    return render_template('student/result.html', prediction=prediction, class_avg=class_avg)

@app.route('/student/history')
@login_required
def student_history():
    db = get_db()
    predictions = db.execute(
        'SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    return render_template('student/history.html', predictions=predictions)

# ── Admin Routes ──

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()

    # Get all distinct classes
    classes = db.execute(
        'SELECT DISTINCT class_name FROM predictions ORDER BY class_name'
    ).fetchall()

    selected_class = request.args.get('class', 'All')

    # Base query
    if selected_class == 'All':
        where_clause = ''
        params = ()
    else:
        where_clause = 'WHERE p.class_name = ?'
        params = (selected_class,)

    # Summary stats
    total_students = db.execute('SELECT COUNT(*) FROM users WHERE role = "student"').fetchone()[0]
    total_predictions = db.execute(f'SELECT COUNT(*) FROM predictions p {where_clause}', params).fetchone()[0]

    avg_score_row = db.execute(
        f'SELECT AVG(predicted_score) FROM predictions p {where_clause}', params
    ).fetchone()
    avg_score = round(avg_score_row[0], 1) if avg_score_row[0] else 0

    at_risk = db.execute(
        f'SELECT COUNT(*) FROM predictions p {where_clause} {"AND" if where_clause else "WHERE"} '
        f'p.performance_label = "Poor"', params
    ).fetchone()[0]

    # Performance distribution
    good_count = db.execute(
        f'SELECT COUNT(*) FROM predictions p {where_clause} {"AND" if where_clause else "WHERE"} '
        f'p.performance_label = "Good"', params
    ).fetchone()[0]
    avg_count = db.execute(
        f'SELECT COUNT(*) FROM predictions p {where_clause} {"AND" if where_clause else "WHERE"} '
        f'p.performance_label = "Average"', params
    ).fetchone()[0]
    poor_count = at_risk

    # Recent predictions with flags
    recent_flags = db.execute(
        f'SELECT p.*, u.name, u.student_id FROM predictions p '
        f'JOIN users u ON p.user_id = u.id '
        f'{where_clause} ORDER BY p.created_at DESC LIMIT 10', params
    ).fetchall()

    stats = {
        'total_students': total_students,
        'avg_score': avg_score,
        'total_predictions': total_predictions,
        'at_risk': at_risk,
        'good': good_count,
        'average': avg_count,
        'poor': poor_count,
    }

    return render_template('admin/dashboard.html',
                         stats=stats, classes=classes,
                         selected_class=selected_class,
                         recent_flags=recent_flags)

@app.route('/admin/students')
@admin_required
def admin_students():
    db = get_db()
    search = request.args.get('search', '')
    class_filter = request.args.get('class', '')

    query = '''
        SELECT u.*, 
               (SELECT predicted_score FROM predictions WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) as latest_score,
               (SELECT performance_label FROM predictions WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) as latest_label,
               (SELECT COUNT(*) FROM predictions WHERE user_id = u.id) as prediction_count
        FROM users u WHERE u.role = 'student'
    '''
    params = []
    if search:
        query += ' AND (u.name LIKE ? OR u.email LIKE ? OR u.student_id LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    if class_filter:
        query += ' AND u.class_name = ?'
        params.append(class_filter)

    query += ' ORDER BY u.name'
    students = db.execute(query, params).fetchall()

    classes = db.execute(
        'SELECT DISTINCT class_name FROM users WHERE role = "student" ORDER BY class_name'
    ).fetchall()

    return render_template('admin/students.html', students=students, classes=classes,
                         search=search, class_filter=class_filter)

@app.route('/admin/reports')
@admin_required
def admin_reports():
    db = get_db()
    classes = db.execute(
        'SELECT DISTINCT class_name FROM predictions ORDER BY class_name'
    ).fetchall()
    return render_template('admin/reports.html', classes=classes)

@app.route('/admin/export/csv')
@admin_required
def export_csv():
    db = get_db()
    class_filter = request.args.get('class', '')

    query = '''
        SELECT u.name, u.email, u.student_id, u.class_name,
               p.attendance, p.study_hours, p.previous_marks, p.assignments,
               p.internal_marks, p.predicted_score, p.performance_label, p.created_at
        FROM predictions p JOIN users u ON p.user_id = u.id
    '''
    params = []
    if class_filter:
        query += ' WHERE p.class_name = ?'
        params.append(class_filter)
    query += ' ORDER BY p.created_at DESC'

    rows = db.execute(query, params).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Student ID', 'Class', 'Attendance', 'Study Hours',
                     'Previous Marks', 'Assignments', 'Internal Marks',
                     'Predicted Score', 'Performance', 'Date'])
    for row in rows:
        writer.writerow([row['name'], row['email'], row['student_id'], row['class_name'],
                        row['attendance'], row['study_hours'], row['previous_marks'],
                        row['assignments'], row['internal_marks'],
                        row['predicted_score'], row['performance_label'], row['created_at']])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=student_report_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

@app.route('/admin/export/pdf')
@admin_required
def export_pdf():
    from fpdf import FPDF

    db = get_db()
    class_filter = request.args.get('class', '')

    query = '''
        SELECT u.name, u.student_id, u.class_name,
               p.predicted_score, p.performance_label, p.created_at
        FROM predictions p JOIN users u ON p.user_id = u.id
    '''
    params = []
    if class_filter:
        query += ' WHERE p.class_name = ?'
        params.append(class_filter)
    query += ' ORDER BY p.created_at DESC LIMIT 50'

    rows = db.execute(query, params).fetchall()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Student Performance Report', ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 8, f'Generated: {datetime.now().strftime("%B %d, %Y")}', ln=True, align='C')
    if class_filter:
        pdf.cell(0, 8, f'Class: {class_filter}', ln=True, align='C')
    pdf.ln(10)

    # Table header
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(26, 115, 232)
    pdf.set_text_color(255, 255, 255)
    col_widths = [45, 25, 45, 25, 25, 25]
    headers = ['Name', 'ID', 'Class', 'Score', 'Level', 'Date']
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, fill=True, align='C')
    pdf.ln()

    # Table rows
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(0, 0, 0)
    for row in rows:
        pdf.cell(col_widths[0], 7, str(row['name'])[:25], border=1)
        pdf.cell(col_widths[1], 7, str(row['student_id'] or ''), border=1, align='C')
        pdf.cell(col_widths[2], 7, str(row['class_name'])[:25], border=1)
        pdf.cell(col_widths[3], 7, str(row['predicted_score']), border=1, align='C')
        pdf.cell(col_widths[4], 7, str(row['performance_label']), border=1, align='C')
        date_str = str(row['created_at'])[:10] if row['created_at'] else ''
        pdf.cell(col_widths[5], 7, date_str, border=1, align='C')
        pdf.ln()

    pdf_bytes = pdf.output()
    return Response(
        bytes(pdf_bytes),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=report_{datetime.now().strftime("%Y%m%d")}.pdf'}
    )

# ── API Endpoints ──

@app.route('/api/class-stats')
@admin_required
def api_class_stats():
    db = get_db()
    class_name = request.args.get('class', 'All')

    if class_name == 'All':
        where = ''
        params = ()
    else:
        where = 'WHERE class_name = ?'
        params = (class_name,)

    # Performance distribution
    good = db.execute(f'SELECT COUNT(*) FROM predictions {where} {"AND" if where else "WHERE"} performance_label = "Good"', params).fetchone()[0]
    average = db.execute(f'SELECT COUNT(*) FROM predictions {where} {"AND" if where else "WHERE"} performance_label = "Average"', params).fetchone()[0]
    poor = db.execute(f'SELECT COUNT(*) FROM predictions {where} {"AND" if where else "WHERE"} performance_label = "Poor"', params).fetchone()[0]

    # Monthly trend (last 7 months)
    monthly_scores = db.execute(
        f'SELECT strftime("%Y-%m", created_at) as month, AVG(predicted_score) as avg_score '
        f'FROM predictions {where} GROUP BY month ORDER BY month DESC LIMIT 7', params
    ).fetchall()

    # Comparative by class
    class_comparison = db.execute(
        'SELECT class_name, AVG(predicted_score) as avg_score, COUNT(*) as count '
        'FROM predictions GROUP BY class_name ORDER BY avg_score DESC'
    ).fetchall()

    return jsonify({
        'distribution': {'good': good, 'average': average, 'poor': poor},
        'monthly_trend': {
            'labels': [r['month'] for r in reversed(monthly_scores)],
            'scores': [round(r['avg_score'], 1) for r in reversed(monthly_scores)]
        },
        'class_comparison': {
            'labels': [r['class_name'] for r in class_comparison],
            'scores': [round(r['avg_score'], 1) for r in class_comparison],
            'counts': [r['count'] for r in class_comparison]
        },
        'summary': {
            'total_predictions': good + average + poor,
            'avg_score': round((good * 85 + average * 62 + poor * 35) / max(good + average + poor, 1), 1),
            'pass_rate': round((good + average) / max(good + average + poor, 1) * 100, 1)
        }
    })

# ─── App startup ─────────────────────────────────────────────────────

with app.app_context():
    if not os.path.exists(app.config['DATABASE']):
        init_db()
        print("Database created and initialized.")
    else:
        # Check if tables exist
        db = get_db()
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t['name'] for t in tables]
        if 'users' not in table_names:
            init_db()
            print("Database tables created.")

if __name__ == '__main__':
    print("\n\n-------------------------------------------------------------")
    print("   Project Running! Open this link: http://localhost:5000")
    print("-------------------------------------------------------------\n\n")
    app.run(debug=config.DEBUG, host='127.0.0.1', port=5000)
