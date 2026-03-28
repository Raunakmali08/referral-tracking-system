import hashlib
import datetime
import bcrypt
import jwt
import os
from functools import wraps
from flask import request, jsonify, g


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def make_jwt(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp':     datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, os.environ.get('SECRET_KEY', 'dev-secret'), algorithm='HS256')


def get_visitor_hash(req) -> str:
    raw = f"{get_client_ip(req)}|{req.headers.get('User-Agent', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_client_ip(req) -> str:
    return req.headers.get('X-Forwarded-For', req.remote_addr or '').split(',')[0].strip()


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        token = header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'dev-secret'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        from app.models import User
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        g.user = user
        return f(*args, **kwargs)
    return decorated
