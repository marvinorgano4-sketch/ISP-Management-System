"""Receipt model for payment receipts"""
from datetime import datetime
from extensions import db


class Receipt(db.Model):
    """Receipt model for payment receipts"""
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False, index=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    client_name = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='paid')  # paid, void
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    payment = db.relationship('Payment', foreign_keys=[payment_id], backref='receipt_obj')
    
    def __repr__(self):
        return f'<Receipt {self.receipt_number} - {self.client_name}>'
