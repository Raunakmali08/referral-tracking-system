import uuid
import datetime
from app import db


def generate_code():
    return uuid.uuid4().hex[:10].upper()


class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    referral_codes = db.relationship('ReferralCode', backref='owner', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}


class ReferralCode(db.Model):
    """One user can have multiple referral codes (campaigns)."""
    __tablename__ = 'referral_codes'
    id          = db.Column(db.Integer, primary_key=True)
    code        = db.Column(db.String(20), unique=True, nullable=False, default=generate_code)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    campaign    = db.Column(db.String(120), default='default')   # e.g. "twitter-promo"
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    clicks      = db.relationship('ReferralClick', backref='referral_code', lazy=True)
    conversions = db.relationship('Conversion', backref='referral_code', lazy=True)

    @property
    def referral_url(self):
        from flask import current_app
        return f"{current_app.config['BASE_URL']}/api/referrals/r/{self.code}"

    def to_dict(self):
        return {
            'id':           self.id,
            'code':         self.code,
            'campaign':     self.campaign,
            'is_active':    self.is_active,
            'referral_url': self.referral_url,
            'created_at':   self.created_at.isoformat(),
            'total_clicks':       len(self.clicks),
            'total_conversions':  len(self.conversions),
            'conversion_rate':    round(len(self.conversions) / len(self.clicks) * 100, 2)
                                  if self.clicks else 0.0,
        }


class ReferralClick(db.Model):
    """Every hit on /r/<code> is recorded here."""
    __tablename__ = 'referral_clicks'
    id              = db.Column(db.Integer, primary_key=True)
    referral_code_id = db.Column(db.Integer, db.ForeignKey('referral_codes.id'), nullable=False)
    visitor_ip      = db.Column(db.String(45))
    user_agent      = db.Column(db.String(256))
    referrer        = db.Column(db.String(256))
    # Fingerprint to detect unique vs repeat clicks
    visitor_hash    = db.Column(db.String(64))
    is_unique       = db.Column(db.Boolean, default=True)
    timestamp       = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'is_unique':  self.is_unique,
            'timestamp':  self.timestamp.isoformat(),
        }


class Conversion(db.Model):
    """
    A conversion is a meaningful action traced back to a referral.
    type: signup | purchase | hire | custom
    """
    __tablename__ = 'conversions'
    id               = db.Column(db.Integer, primary_key=True)
    referral_code_id = db.Column(db.Integer, db.ForeignKey('referral_codes.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    conversion_type  = db.Column(db.String(50), default='signup')
    value            = db.Column(db.Float, default=0.0)    # e.g. purchase amount
    metadata_json    = db.Column(db.Text)                  # arbitrary payload
    idempotency_key  = db.Column(db.String(64), unique=True)  # prevents double-counting
    timestamp        = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id':              self.id,
            'referral_code_id': self.referral_code_id,
            'referred_user_id': self.referred_user_id,
            'conversion_type': self.conversion_type,
            'value':           self.value,
            'timestamp':       self.timestamp.isoformat(),
        }
