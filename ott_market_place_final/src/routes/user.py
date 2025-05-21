from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from functools import wraps
from src.models.user import db, User

user_bp = Blueprint('user', __name__)

# Simple JWT implementation without cryptography dependency
class SimpleJWT:
    @staticmethod
    def encode(payload, secret, algorithm='HS256'):
        # Create header
        header = {'alg': algorithm, 'typ': 'JWT'}
        
        # Encode header and payload
        header_json = json.dumps(header, separators=(',', ':')).encode()
        header_b64 = base64.urlsafe_b64encode(header_json).decode().rstrip('=')
        
        payload_json = json.dumps(payload, separators=(',', ':')).encode()
        payload_b64 = base64.urlsafe_b64encode(payload_json).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Return complete JWT
        return f"{header_b64}.{payload_b64}.{signature_b64}"
    
    @staticmethod
    def decode(token, secret, algorithms=None):
        try:
            # Split token into parts
            header_b64, payload_b64, signature_b64 = token.split('.')
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode().rstrip('=')
            
            if signature_b64 != expected_signature_b64:
                raise Exception("Invalid signature")
            
            # Decode payload
            payload_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_json = base64.urlsafe_b64decode(payload_padded)
            payload = json.loads(payload_json)
            
            # Check expiration
            if 'exp' in payload and payload['exp'] < time.time():
                raise Exception("Token expired")
            
            return payload
        except Exception as e:
            raise Exception(f"Invalid token: {str(e)}")

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = SimpleJWT.decode(token, current_app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except Exception as e:
            return jsonify({'message': f'Token is invalid! {str(e)}'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User with this email already exists'}), 409
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already taken'}), 409
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Generate token
    token = SimpleJWT.encode({
        'user_id': user.id,
        'exp': int((datetime.utcnow() + timedelta(days=7)).timestamp())
    }, current_app.config['SECRET_KEY'])
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify(current_user.to_dict()), 200

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    
    if 'username' in data and data['username'] != current_user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already taken'}), 409
        current_user.username = data['username']
    
    if 'email' in data and data['email'] != current_user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already in use'}), 409
        current_user.email = data['email']
    
    if 'password' in data:
        current_user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    }), 200
