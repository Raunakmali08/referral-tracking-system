from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.helpers import hash_password, check_password, make_jwt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'username, email, password required'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username taken'}), 409

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password']),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registered', 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email', '')).first()
    if not user or not check_password(data.get('password', ''), user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    return jsonify({'access_token': make_jwt(user.id), 'user': user.to_dict()}), 200
