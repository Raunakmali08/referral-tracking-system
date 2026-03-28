from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # ── Config ──────────────────────────────────────────────
    app.config['SECRET_KEY']                  = os.environ.get('SECRET_KEY', 'dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI']     = os.environ.get('DATABASE_URL', 'sqlite:///referral.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BASE_URL']                    = os.environ.get('BASE_URL', 'http://localhost:5000')

    db.init_app(app)
    migrate.init_app(app, db)

    # ── Register blueprints ──────────────────────────────────
    from app.routes.auth      import auth_bp
    from app.routes.referral  import referral_bp
    from app.routes.analytics import analytics_bp
    from app.routes.webhook   import webhook_bp

    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(referral_bp,  url_prefix='/api/referrals')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(webhook_bp,   url_prefix='/api/webhooks')

    # ── Frontend Routes ──────────────────────────────────────
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    # ── Health check ─────────────────────────────────────────
    @app.route('/health')
    def health():
        from flask import jsonify
        return jsonify({'status': 'ok', 'service': 'referral-tracking-system'}), 200

    with app.app_context():
        db.create_all()

    return app

