from datetime import timedelta

from flask import Flask, flash, redirect, request, url_for
from flask_wtf.csrf import CSRFError

import config
from core.db import ensure_database_ready, register_db
from core.extensions import csrf
from models import entities  # noqa: F401 - ensures models are registered before db.create_all
from routes.admin import admin_bp
from routes.api import api_bp
from routes.auth import auth_bp
from routes.public import public_bp
from routes.student import student_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config["DATABASE"] = config.DATABASE
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{config.DATABASE}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = getattr(config, "SESSION_COOKIE_HTTPONLY", True)
    app.config["SESSION_COOKIE_SAMESITE"] = getattr(config, "SESSION_COOKIE_SAMESITE", "Lax")
    app.permanent_session_lifetime = timedelta(seconds=getattr(config, "PERMANENT_SESSION_LIFETIME", 1800))
    app.config["WTF_CSRF_TIME_LIMIT"] = 3600

    register_db(app)
    csrf.init_app(app)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("Security token expired or missing. Please submit the form again.", "danger")
        return redirect(request.path or url_for("auth.login"))

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        ensure_database_ready()

    return app


app = create_app()


if __name__ == "__main__":
    print("\n\n-------------------------------------------------------------")
    print("   Project Running! Open this link: http://127.0.0.1:5000")
    print("-------------------------------------------------------------\n\n")
    app.run(debug=config.DEBUG, host="0.0.0.0", port=5000)
