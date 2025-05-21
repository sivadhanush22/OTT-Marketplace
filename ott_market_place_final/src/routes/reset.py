from flask import Blueprint, request, jsonify, url_for, render_template
from werkzeug.security import generate_password_hash
from src.models.user import db, User
import secrets
import datetime
from src.routes.user import SimpleJWT

reset_bp = Blueprint('reset', __name__)

# Password reset request
@reset_bp.route('/request-reset', methods=['POST'])
def request_reset():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'message': 'Email is required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        # For security reasons, don't reveal that the email doesn't exist
        return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200
    
    # Generate reset token
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    db.session.commit()
    
    # In a real application, send an email with the reset link
    # For this demo, we'll just return the token
    reset_link = f"/reset-password?token={token}"
    
    # This would be replaced with actual email sending in production
    print(f"Password reset link for {user.email}: {reset_link}")
    
    return jsonify({
        'message': 'If your email is registered, you will receive a password reset link',
        'debug_link': reset_link  # Remove this in production
    }), 200

# Verify reset token
@reset_bp.route('/verify-token', methods=['POST'])
def verify_token():
    data = request.get_json()
    
    if not data or not data.get('token'):
        return jsonify({'message': 'Token is required'}), 400
    
    user = User.query.filter_by(reset_token=data['token']).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.datetime.utcnow():
        return jsonify({'message': 'Invalid or expired token'}), 400
    
    return jsonify({'message': 'Valid token', 'email': user.email}), 200

# Reset password
@reset_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not data or not data.get('token') or not data.get('password'):
        return jsonify({'message': 'Token and new password are required'}), 400
    
    user = User.query.filter_by(reset_token=data['token']).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.datetime.utcnow():
        return jsonify({'message': 'Invalid or expired token'}), 400
    
    # Update password
    user.set_password(data['password'])
    
    # Clear reset token
    user.reset_token = None
    user.reset_token_expiry = None
    
    db.session.commit()
    
    return jsonify({'message': 'Password has been reset successfully'}), 200
