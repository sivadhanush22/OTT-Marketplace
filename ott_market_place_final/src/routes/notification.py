from flask import Blueprint, request, jsonify, current_app
import os
from datetime import datetime, timedelta
from src.models.user import db
from src.models.order import Order, OrderItem, Credential
from src.routes.user import token_required

notification_bp = Blueprint('notification', __name__)

# Helper function to send email (simplified for demo)
def send_email(to_email, subject, body):
    # In a production environment, you would use a proper email service
    # This is just a placeholder function
    print(f"Sending email to {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return True

@notification_bp.route('/check-expiring', methods=['GET'])
def check_expiring_subscriptions():
    # Find subscriptions expiring in the next day
    tomorrow = datetime.utcnow() + timedelta(days=1)
    expiring_items = OrderItem.query.filter(
        OrderItem.end_date >= tomorrow,
        OrderItem.end_date <= tomorrow + timedelta(days=1),
        OrderItem.status == 'active'
    ).all()
    
    notifications_sent = 0
    
    # Send notifications for each expiring subscription
    for item in expiring_items:
        order = Order.query.get(item.order_id)
        if order and order.customer:
            send_email(
                order.customer.email,
                'Your subscription is expiring soon',
                f'Your subscription will expire on {item.end_date.strftime("%Y-%m-%d")}. '
                f'Please renew to continue enjoying the service.'
            )
            notifications_sent += 1
    
    return jsonify({
        'message': f'Processed {len(expiring_items)} expiring subscriptions',
        'notifications_sent': notifications_sent
    }), 200

@notification_bp.route('/check-expired', methods=['GET'])
def check_expired_subscriptions():
    # Find subscriptions that expired today
    today = datetime.utcnow().date()
    expired_items = OrderItem.query.filter(
        OrderItem.end_date.cast(db.Date) == today,
        OrderItem.status == 'active'
    ).all()
    
    notifications_sent = 0
    
    # Send notifications and update status
    for item in expired_items:
        order = Order.query.get(item.order_id)
        if order and order.customer:
            send_email(
                order.customer.email,
                'Your subscription has expired',
                f'Your subscription has expired. If you wish to continue using the service, '
                f'please renew your subscription.'
            )
            
            # Update status to expired
            item.status = 'expired'
            notifications_sent += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Processed {len(expired_items)} expired subscriptions',
        'notifications_sent': notifications_sent
    }), 200

@notification_bp.route('/order-status/<int:order_id>', methods=['POST'])
@token_required
def send_order_status_notification(current_user, order_id):
    # In a real app, check if user is admin
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if not data or 'status' not in data or 'message' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Send notification to customer
    send_email(
        order.customer.email,
        f'Order {order.order_number} Status Update: {data["status"]}',
        data['message']
    )
    
    return jsonify({'message': 'Notification sent successfully'}), 200

@notification_bp.route('/credential-update/<int:order_id>', methods=['POST'])
@token_required
def send_credential_update_notification(current_user, order_id):
    # In a real app, check if user is admin
    order = Order.query.get_or_404(order_id)
    
    # Send notification to customer
    send_email(
        order.customer.email,
        'Your subscription credentials have been updated',
        f'Your credentials for order {order.order_number} have been updated. '
        f'Please check your account for the latest access information.'
    )
    
    return jsonify({'message': 'Credential update notification sent successfully'}), 200
