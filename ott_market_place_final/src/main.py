import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from src.models.user import db, User
from src.models.product import Product
from src.models.order import Order, OrderItem, Credential
from src.routes.user import user_bp
from src.routes.product import product_bp
from src.routes.order import order_bp
from src.routes.admin import admin_bp
from src.routes.notification import notification_bp
from src.routes.reset import reset_bp
import datetime
import secrets
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ott_marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', 'netflixbestott@gmail.com')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(product_bp, url_prefix='/api/products')
app.register_blueprint(order_bp, url_prefix='/api/orders')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(notification_bp, url_prefix='/api/notifications')
app.register_blueprint(reset_bp, url_prefix='/api/reset')

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# Serve HTML pages
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/login.html')
def login():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/signup.html')
def signup():
    return send_from_directory(app.static_folder, 'signup.html')

@app.route('/catalog.html')
def catalog():
    return send_from_directory(app.static_folder, 'catalog.html')

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/reset-password.html')
def reset_password():
    return send_from_directory(app.static_folder, 'reset-password.html')

# Admin routes
@app.route('/admin')
def admin_index():
    return send_from_directory(app.static_folder, 'admin_site/index.html')

@app.route('/admin/<path:filename>')
def admin_static(filename):
    return send_from_directory(os.path.join(app.static_folder, 'admin_site'), filename)

# Customer routes
@app.route('/customer')
def customer_index():
    return send_from_directory(app.static_folder, 'customer_site/index.html')

@app.route('/customer/<path:filename>')
def customer_static(filename):
    return send_from_directory(os.path.join(app.static_folder, 'customer_site'), filename)

# Initialize database tables
# Fix for Flask 2.0+ compatibility - replacing @app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists, if not create one
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                username="admin",
                email=app.config['ADMIN_EMAIL'],
                password="admin123",
                is_admin=True
            )
            db.session.add(admin)
            
            # Add some sample products
            products = [
                Product(
                    name="Netflix Standard",
                    description="Watch Netflix on two screens at once with Full HD quality",
                    price=1399,
                    duration_months=3,
                    platform="netflix",
                    image_url="images/netflix.jpg",
                    is_featured=True
                ),
                Product(
                    name="Amazon Prime",
                    description="Stream thousands of movies and TV shows, including Amazon Originals",
                    price=849,
                    duration_months=6,
                    platform="prime",
                    image_url="images/prime.jpg",
                    is_featured=True
                ),
                Product(
                    name="Disney+ Hotstar",
                    description="Stream Disney, Marvel, Pixar, Star Wars, National Geographic and more",
                    price=299,
                    duration_months=1,
                    platform="hotstar",
                    image_url="images/hotstar.jpg",
                    is_featured=True
                ),
                Product(
                    name="Sony LIV Premium",
                    description="Watch Sony LIV originals, live sports, TV shows and movies",
                    price=599,
                    duration_months=3,
                    platform="sonyliv",
                    image_url="images/sonyliv.jpg"
                ),
                Product(
                    name="ZEE5 Premium",
                    description="Stream ZEE5 originals, exclusive movies, TV shows and more",
                    price=699,
                    duration_months=3,
                    platform="zee5",
                    image_url="images/zee5.jpg"
                )
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()

# Call create_tables when the app starts
with app.app_context():
    create_tables()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
