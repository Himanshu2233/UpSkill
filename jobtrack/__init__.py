import os
import secrets
from pathlib import Path

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from .extensions import csrf, db, login_manager


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///jobtrack.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        MAX_CONTENT_LENGTH=128 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config['SECRET_KEY']:
        key_path = Path(app.instance_path) / 'secret.key'
        try:
            with key_path.open('x') as file:
                file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config['SECRET_KEY'] = key_path.read_text().strip()
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from .models import User
    from .auth import bp as auth_bp
    from .tracker import bp as tracker_bp
    from .cli import register_commands

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except ValueError:
            return None

    app.register_blueprint(auth_bp)
    app.register_blueprint(tracker_bp)
    register_commands(app)

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template('error.html', code=400, message='Your form expired or could not be verified. Refresh the page and try again.'), 400

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', code=404, message='We could not find that page or application.'), 404

    @app.after_request
    def response_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Cache-Control'] = 'no-store'
        return response

    return app
