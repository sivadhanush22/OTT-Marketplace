from flask import Blueprint, request, jsonify, current_app
from src.models.user import db
from src.models.product import Product
from src.routes.user import token_required

product_bp = Blueprint('product', __name__)

@product_bp.route('/', methods=['GET'])
def get_all_products():
    products = Product.query.filter_by(active=True).all()
    return jsonify([product.to_dict() for product in products]), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@product_bp.route('/category/<category>', methods=['GET'])
def get_products_by_category(category):
    products = Product.query.filter_by(category=category, active=True).all()
    return jsonify([product.to_dict() for product in products]), 200

# Admin routes for product management
@product_bp.route('/', methods=['POST'])
@token_required
def create_product(current_user):
    # In a real app, check if user is admin
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'price', 'duration_months', 'category']):
        return jsonify({'message': 'Missing required fields'}), 400
    
    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        duration_months=data['duration_months'],
        category=data['category']
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify(new_product.to_dict()), 201

@product_bp.route('/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    # In a real app, check if user is admin
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'duration_months' in data:
        product.duration_months = data['duration_months']
    if 'category' in data:
        product.category = data['category']
    if 'active' in data:
        product.active = data['active']
    
    db.session.commit()
    
    return jsonify(product.to_dict()), 200

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    # In a real app, check if user is admin
    product = Product.query.get_or_404(product_id)
    
    # Soft delete by setting active to False
    product.active = False
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'}), 200

# Bulk import products from spreadsheet (simplified version)
@product_bp.route('/import', methods=['POST'])
@token_required
def import_products(current_user):
    # In a real app, check if user is admin
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    # This is a placeholder - in a real implementation, we would parse the spreadsheet
    # and import the products
    
    return jsonify({'message': 'Products imported successfully'}), 200
