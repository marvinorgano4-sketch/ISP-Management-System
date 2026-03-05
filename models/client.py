"""Client model for ISP customer management"""
from datetime import datetime
import bcrypt
from extensions import db


class Client(db.Model):
    """Client model for ISP customers"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255))
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    pppoe_username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    plan_name = db.Column(db.String(100), nullable=False)
    plan_amount = db.Column(db.Float, nullable=False)
    mikrotik_profile = db.Column(db.String(100), nullable=True, default='default')
    status = db.Column(db.String(20), nullable=False, default='active')
    password_hash = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (will be added when Billing and Payment models are created)
    # billings = db.relationship('Billing', back_populates='client', lazy='dynamic')
    # payments = db.relationship('Payment', back_populates='client', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """Hash and set the client password using bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against stored hash using bcrypt"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def __repr__(self):
        return f'<Client {self.full_name} ({self.pppoe_username})>'
