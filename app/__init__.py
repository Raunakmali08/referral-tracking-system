from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    app = Flask(__name__)

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

    # ── Health check ─────────────────────────────────────────
    @app.route('/health')
    def health():
        from flask import jsonify
        return jsonify({'status': 'ok', 'service': 'referral-tracking-system'}), 200

    with app.app_context():
        db.create_all()

    return app
