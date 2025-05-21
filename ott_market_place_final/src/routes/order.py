from flask import Blueprint, request, jsonify, current_app, send_from_directory
import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from src.models.user import db
from src.models.order import Order, OrderItem, Credential
from src.models.product import Product
from src.routes.user import token_required
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

order_bp = Blueprint('order', __name__)

# Helper function to generate order number
def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"

# Helper function to send email (simplified for demo)
def send_email(to_email, subject, body):
    # In a production environment, you would use a proper email service
    # This is just a placeholder function
    print(f"Sending email to {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return True

@order_bp.route('/', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json()
    
    if not data or not data.get('items') or len(data['items']) == 0:
        return jsonify({'message': 'No items in order'}), 400
    
    # Calculate total amount and validate products
    total_amount = 0
    order_items = []
    
    for item_data in data['items']:
        product = Product.query.get(item_data['product_id'])
        if not product or not product.active:
            return jsonify({'message': f'Product {item_data["product_id"]} not found or inactive'}), 400
        
        order_items.append({
            'product_id': product.id,
            'price': product.price,
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + timedelta(days=30 * product.duration_months),
            'status': 'pending'
        })
        
        total_amount += product.price
    
    # Create order
    new_order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        total_amount=total_amount,
        payment_status='pending'
    )
    
    db.session.add(new_order)
    db.session.flush()  # Get the order ID without committing
    
    # Create order items
    for item_data in order_items:
        new_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data['product_id'],
            price=item_data['price'],
            start_date=item_data['start_date'],
            end_date=item_data['end_date'],
            status=item_data['status']
        )
        db.session.add(new_item)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order': new_order.to_dict()
    }), 201

@order_bp.route('/', methods=['GET'])
@token_required
def get_user_orders(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return jsonify([order.to_dict() for order in orders]), 200

@order_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return jsonify(order.to_dict()), 200

@order_bp.route('/<int:order_id>/upload-payment', methods=['POST'])
@token_required
def upload_payment(current_user, order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file:
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Secure filename and save file
        filename = secure_filename(f"{order.order_number}_{uuid.uuid4().hex}.png")
        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)
        
        # Update order with payment screenshot
        order.payment_screenshot = f"/static/uploads/{filename}"
        order.payment_status = 'pending_verification'
        db.session.commit()
        
        # Notify admin about new payment (in a real app, this would be an email)
        # send_email('admin@example.com', f'New payment for order {order.order_number}', 
        #           f'A new payment has been uploaded for order {order.order_number}. Please verify.')
        
        return jsonify({
            'message': 'Payment screenshot uploaded successfully',
            'order': order.to_dict()
        }), 200

@order_bp.route('/<int:order_id>/verify-payment', methods=['POST'])
@token_required
def verify_payment(current_user, order_id):
    # In a real app, check if user is admin
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'message': 'Missing status field'}), 400
    
    if data['status'] not in ['completed', 'failed']:
        return jsonify({'message': 'Invalid status'}), 400
    
    order.payment_status = data['status']
    
    # If payment is completed, update order items status
    if data['status'] == 'completed':
        for item in order.items:
            item.status = 'active'
        
        # Create credentials if provided
        if 'credentials' in data:
            for cred_data in data['credentials']:
                new_cred = Credential(
                    order_id=order.id,
                    username=cred_data.get('username', ''),
                    password=cred_data.get('password', ''),
                    other_info=cred_data.get('other_info', '')
                )
                db.session.add(new_cred)
        
        # Send email to customer
        send_email(
            order.customer.email,
            f'Your order {order.order_number} has been confirmed',
            f'Your payment for order {order.order_number} has been verified. You can now access your subscriptions.'
        )
    
    db.session.commit()
    
    return jsonify({
        'message': f'Payment {data["status"]}',
        'order': order.to_dict()
    }), 200

@order_bp.route('/<int:order_id>/credentials', methods=['GET'])
@token_required
def get_credentials(current_user, order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    if order.payment_status != 'completed':
        return jsonify({'message': 'Payment not completed'}), 403
    
    credentials = Credential.query.filter_by(order_id=order.id).all()
    
    return jsonify([{
        'id': cred.id,
        'username': cred.username,
        'password': cred.password,
        'other_info': cred.other_info,
        'created_at': cred.created_at.isoformat(),
        'updated_at': cred.updated_at.isoformat()
    } for cred in credentials]), 200

@order_bp.route('/<int:order_id>/credentials', methods=['POST'])
@token_required
def update_credentials(current_user, order_id):
    # In a real app, check if user is admin
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if not data or not data.get('credentials'):
        return jsonify({'message': 'Missing credentials data'}), 400
    
    # Delete existing credentials
    Credential.query.filter_by(order_id=order.id).delete()
    
    # Create new credentials
    for cred_data in data['credentials']:
        new_cred = Credential(
            order_id=order.id,
            username=cred_data.get('username', ''),
            password=cred_data.get('password', ''),
            other_info=cred_data.get('other_info', '')
        )
        db.session.add(new_cred)
    
    db.session.commit()
    
    # Send email to customer about updated credentials
    send_email(
        order.customer.email,
        'Your subscription credentials have been updated',
        f'Your credentials for order {order.order_number} have been updated. Please check your account.'
    )
    
    return jsonify({'message': 'Credentials updated successfully'}), 200

# Endpoint to check for expiring subscriptions (would be called by a scheduler in production)
@order_bp.route('/check-expiring', methods=['GET'])
def check_expiring_subscriptions():
    # Find subscriptions expiring in the next day
    tomorrow = datetime.utcnow() + timedelta(days=1)
    expiring_items = OrderItem.query.filter(
        OrderItem.end_date >= tomorrow,
        OrderItem.end_date <= tomorrow + timedelta(days=1),
        OrderItem.status == 'active'
    ).all()
    
    # Send notifications for each expiring subscription
    for item in expiring_items:
        order = Order.query.get(item.order_id)
        product = Product.query.get(item.product_id)
        
        send_email(
            order.customer.email,
            f'Your {product.name} subscription is expiring soon',
            f'Your {product.name} subscription will expire on {item.end_date.strftime("%Y-%m-%d")}. '
            f'Please renew to continue enjoying the service.'
        )
    
    return jsonify({'message': f'Processed {len(expiring_items)} expiring subscriptions'}), 200
