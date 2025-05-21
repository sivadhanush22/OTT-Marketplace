from src.models.user import db
import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # netflix, prime, hotstar, etc.
    image_url = db.Column(db.String(255), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __init__(self, name, price, duration_months, platform, description=None, image_url=None, is_available=True, is_featured=False):
        self.name = name
        self.description = description
        self.price = price
        self.duration_months = duration_months
        self.platform = platform
        self.image_url = image_url
        self.is_available = is_available
        self.is_featured = is_featured
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration_months': self.duration_months,
            'platform': self.platform,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Product {self.name}>'
