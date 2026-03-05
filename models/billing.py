"""Billing model for monthly billing records"""
from datetime import datetime
from extensions import db


class Billing(db.Model):
    """Billing model for monthly billing records"""
    __tablename__ = 'billings'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    billing_month = db.Column(db.Integer, nullable=False)  # 1-12
    billing_year = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='unpaid')  # unpaid, paid, overdue
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), index=True)
    
    # Relationships
    client = db.relationship('Client', backref=db.backref('billings', lazy='dynamic'))
    payment = db.relationship('Payment', foreign_keys=[payment_id], backref='billing_record')
    
    def __repr__(self):
        return f'<Billing {self.id} - Client {self.client_id} - {self.billing_month}/{self.billing_year}>'
