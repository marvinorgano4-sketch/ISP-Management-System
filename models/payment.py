"""Payment model for payment records"""
from datetime import datetime
from extensions import db


class Payment(db.Model):
    """Payment model for payment records"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    billing_id = db.Column(db.Integer, db.ForeignKey('billings.id'), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # cash, gcash, bank_transfer
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), index=True)
    
    # Relationships
    client = db.relationship('Client', backref=db.backref('payments', lazy='dynamic'))
    receipt = db.relationship('Receipt', foreign_keys=[receipt_id], backref='payment_record', uselist=False)
    
    def __repr__(self):
        return f'<Payment {self.id} - Client {self.client_id} - {self.amount}>'
