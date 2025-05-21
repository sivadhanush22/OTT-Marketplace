from flask import Blueprint, request, jsonify, current_app
from src.models.user import db, User
from src.models.product import Product
from src.models.order import Order, OrderItem, Credential
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jwt

admin_bp = Blueprint('admin', __name__)

# Helper function to verify admin token
def admin_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user or not current_user.is_admin:
                return jsonify({'message': 'Not authorized'}), 403
                
        except Exception as e:
            return jsonify({'message': 'Invalid token', 'error': str(e)}), 401
            
        return f(current_user, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

# Admin login
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']) or not user.is_admin:
        return jsonify({'message': 'Invalid credentials'}), 401
        
    token = jwt.encode(
        {
            'user_id': user.id,
            'is_admin': user.is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        },
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

# Get all orders
@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_orders(current_user):
    status = request.args.get('status')
    
    query = Order.query
    
    if status:
        query = query.filter_by(payment_status=status)
        
    orders = query.order_by(Order.created_at.desc()).all()
    
    return jsonify({
        'orders': [order.to_dict() for order in orders]
    }), 200

# Get order details
@admin_bp.route('/orders/<int:order_id>', methods=['GET'])
@admin_required
def get_order(current_user, order_id):
    order = Order.query.get_or_404(order_id)
    
    return jsonify({
        'order': order.to_dict()
    }), 200

# Update order status
@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(current_user, order_id):
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'message': 'Status is required'}), 400
        
    order = Order.query.get_or_404(order_id)
    order.payment_status = data['status']
    
    # If order is verified, send email notification
    if data['status'] == 'verified':
        user = User.query.get(order.user_id)
        
        # Send email notification
        try:
            send_order_verification_email(user.email, order.order_number)
        except Exception as e:
            # Log the error but continue
            print(f"Error sending email: {str(e)}")
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order status updated',
        'order': order.to_dict()
    }), 200

# Add credentials for an order item
@admin_bp.route('/orders/<int:order_id>/credentials', methods=['POST'])
@admin_required
def add_credentials(current_user, order_id):
    data = request.get_json()
    
    if not data or not data.get('order_item_id') or not data.get('username') or not data.get('password') or not data.get('expiry_date'):
        return jsonify({'message': 'Missing required fields'}), 400
        
    order = Order.query.get_or_404(order_id)
    
    # Verify order item belongs to this order
    order_item = OrderItem.query.filter_by(id=data['order_item_id'], order_id=order_id).first()
    
    if not order_item:
        return jsonify({'message': 'Order item not found for this order'}), 404
        
    # Create credential
    credential = Credential(
        order_item_id=data['order_item_id'],
        username=data['username'],
        password=data['password'],
        expiry_date=datetime.datetime.fromisoformat(data['expiry_date']),
        notes=data.get('notes')
    )
    
    db.session.add(credential)
    db.session.commit()
    
    # Send email notification
    user = User.query.get(order.user_id)
    try:
        send_credential_email(user.email, credential)
    except Exception as e:
        # Log the error but continue
        print(f"Error sending email: {str(e)}")
    
    return jsonify({
        'message': 'Credentials added successfully',
        'credential': credential.to_dict()
    }), 201

# Update credentials
@admin_bp.route('/credentials/<int:credential_id>', methods=['PUT'])
@admin_required
def update_credential(current_user, credential_id):
    data = request.get_json()
    
    credential = Credential.query.get_or_404(credential_id)
    
    if 'username' in data:
        credential.username = data['username']
    
    if 'password' in data:
        credential.password = data['password']
    
    if 'expiry_date' in data:
        credential.expiry_date = datetime.datetime.fromisoformat(data['expiry_date'])
    
    if 'notes' in data:
        credential.notes = data['notes']
    
    credential.updated_at = datetime.datetime.utcnow()
    
    db.session.commit()
    
    # Send email notification
    order_item = OrderItem.query.get(credential.order_item_id)
    order = Order.query.get(order_item.order_id)
    user = User.query.get(order.user_id)
    
    try:
        send_credential_update_email(user.email, credential)
    except Exception as e:
        # Log the error but continue
        print(f"Error sending email: {str(e)}")
    
    return jsonify({
        'message': 'Credential updated successfully',
        'credential': credential.to_dict()
    }), 200

# Get all products
@admin_bp.route('/products', methods=['GET'])
@admin_required
def get_products(current_user):
    products = Product.query.all()
    
    return jsonify({
        'products': [product.to_dict() for product in products]
    }), 200

# Add new product
@admin_bp.route('/products', methods=['POST'])
@admin_required
def add_product(current_user):
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('price') or not data.get('duration_months') or not data.get('platform'):
        return jsonify({'message': 'Missing required fields'}), 400
        
    product = Product(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        duration_months=data['duration_months'],
        platform=data['platform'],
        image_url=data.get('image_url'),
        is_available=data.get('is_available', True),
        is_featured=data.get('is_featured', False)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product added successfully',
        'product': product.to_dict()
    }), 201

# Update product
@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(current_user, product_id):
    data = request.get_json()
    
    product = Product.query.get_or_404(product_id)
    
    if 'name' in data:
        product.name = data['name']
    
    if 'description' in data:
        product.description = data['description']
    
    if 'price' in data:
        product.price = data['price']
    
    if 'duration_months' in data:
        product.duration_months = data['duration_months']
    
    if 'platform' in data:
        product.platform = data['platform']
    
    if 'image_url' in data:
        product.image_url = data['image_url']
    
    if 'is_available' in data:
        product.is_available = data['is_available']
    
    if 'is_featured' in data:
        product.is_featured = data['is_featured']
    
    product.updated_at = datetime.datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200

# Delete product
@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product deleted successfully'
    }), 200

# Get all users
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    users = User.query.filter_by(is_admin=False).all()
    
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

# Get user details
@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(current_user, user_id):
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'user': user.to_dict()
    }), 200

# Get expiring subscriptions
@admin_bp.route('/expiring-subscriptions', methods=['GET'])
@admin_required
def get_expiring_subscriptions(current_user):
    days = request.args.get('days', 7, type=int)
    
    # Calculate the date threshold
    threshold_date = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    
    # Get credentials expiring within the threshold
    expiring_credentials = Credential.query.filter(
        Credential.expiry_date <= threshold_date,
        Credential.expiry_date >= datetime.datetime.utcnow()
    ).all()
    
    result = []
    
    for credential in expiring_credentials:
        order_item = OrderItem.query.get(credential.order_item_id)
        order = Order.query.get(order_item.order_id)
        user = User.query.get(order.user_id)
        product = Product.query.get(order_item.product_id)
        
        result.append({
            'credential': credential.to_dict(),
            'user': user.to_dict(),
            'product': product.to_dict(),
            'days_remaining': (credential.expiry_date - datetime.datetime.utcnow()).days
        })
    
    return jsonify({
        'expiring_subscriptions': result
    }), 200

# Send reminder emails for expiring subscriptions
@admin_bp.route('/send-expiry-reminders', methods=['POST'])
@admin_required
def send_expiry_reminders(current_user):
    days = request.args.get('days', 7, type=int)
    
    # Calculate the date threshold
    threshold_date = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    
    # Get credentials expiring within the threshold
    expiring_credentials = Credential.query.filter(
        Credential.expiry_date <= threshold_date,
        Credential.expiry_date >= datetime.datetime.utcnow()
    ).all()
    
    sent_count = 0
    
    for credential in expiring_credentials:
        order_item = OrderItem.query.get(credential.order_item_id)
        order = Order.query.get(order_item.order_id)
        user = User.query.get(order.user_id)
        product = Product.query.get(order_item.product_id)
        
        try:
            send_expiry_reminder_email(
                user.email,
                user.username,
                product.name,
                credential.expiry_date,
                (credential.expiry_date - datetime.datetime.utcnow()).days
            )
            sent_count += 1
        except Exception as e:
            # Log the error but continue
            print(f"Error sending email to {user.email}: {str(e)}")
    
    return jsonify({
        'message': f'Sent {sent_count} expiry reminder emails'
    }), 200

# Helper functions for sending emails
def send_order_verification_email(email, order_number):
    subject = f"Your OTT Marketplace Order #{order_number} has been verified"
    body = f"""
    <html>
    <body>
        <h2>Order Verified</h2>
        <p>Your order #{order_number} has been verified and is being processed.</p>
        <p>You will receive your subscription credentials shortly.</p>
        <p>Thank you for choosing OTT Marketplace!</p>
    </body>
    </html>
    """
    
    send_email(email, subject, body)

def send_credential_email(email, credential):
    order_item = OrderItem.query.get(credential.order_item_id)
    product = Product.query.get(order_item.product_id)
    
    subject = f"Your {product.name} Subscription Credentials"
    body = f"""
    <html>
    <body>
        <h2>Your Subscription Credentials</h2>
        <p>Here are your login credentials for {product.name}:</p>
        <p><strong>Username:</strong> {credential.username}</p>
        <p><strong>Password:</strong> {credential.password}</p>
        <p><strong>Valid until:</strong> {credential.expiry_date.strftime('%B %d, %Y')}</p>
        
        {f"<p><strong>Notes:</strong> {credential.notes}</p>" if credential.notes else ""}
        
        <p>You can also view these credentials in your dashboard at any time.</p>
        <p>Thank you for choosing OTT Marketplace!</p>
    </body>
    </html>
    """
    
    send_email(email, subject, body)

def send_credential_update_email(email, credential):
    order_item = OrderItem.query.get(credential.order_item_id)
    product = Product.query.get(order_item.product_id)
    
    subject = f"Your {product.name} Subscription Credentials Have Been Updated"
    body = f"""
    <html>
    <body>
        <h2>Updated Subscription Credentials</h2>
        <p>Your login credentials for {product.name} have been updated:</p>
        <p><strong>Username:</strong> {credential.username}</p>
        <p><strong>Password:</strong> {credential.password}</p>
        <p><strong>Valid until:</strong> {credential.expiry_date.strftime('%B %d, %Y')}</p>
        
        {f"<p><strong>Notes:</strong> {credential.notes}</p>" if credential.notes else ""}
        
        <p>You can also view these credentials in your dashboard at any time.</p>
        <p>Thank you for choosing OTT Marketplace!</p>
    </body>
    </html>
    """
    
    send_email(email, subject, body)

def send_expiry_reminder_email(email, username, product_name, expiry_date, days_remaining):
    subject = f"Your {product_name} Subscription is Expiring Soon"
    body = f"""
    <html>
    <body>
        <h2>Subscription Expiring Soon</h2>
        <p>Hello {username},</p>
        <p>Your {product_name} subscription will expire in {days_remaining} days (on {expiry_date.strftime('%B %d, %Y')}).</p>
        <p>To continue enjoying your subscription without interruption, please renew it before the expiry date.</p>
        <p>Thank you for choosing OTT Marketplace!</p>
    </body>
    </html>
    """
    
    send_email(email, subject, body)

def send_email(to_email, subject, body):
    # In a production environment, this would use a proper email service
    # For now, we'll just print the email details
    print(f"Sending email to: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    
    # Uncomment and configure this for actual email sending
    """
    from_email = current_app.config['ADMIN_EMAIL']
    password = os.environ.get('EMAIL_PASSWORD')
    
    if not password:
        raise Exception("Email password not configured")
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.send_message(msg)
    server.quit()
    """
