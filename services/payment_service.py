"""Payment service for processing payments"""
from datetime import datetime, date
from sqlalchemy import and_
from models.payment import Payment
from models.billing import Billing
from models.client import Client
from extensions import db


class PaymentService:
    """Service class for handling payment operations"""
    
    @staticmethod
    def record_payment(billing_id, data):
        """
        Record a payment for a billing record.
        
        Args:
            billing_id (int): The billing ID
            data (dict): Payment data containing amount, payment_date, payment_method,
                        reference_number, notes
        
        Returns:
            Payment: The created payment object
            
        Raises:
            ValueError: If validation fails
        """
        # Get billing record
        billing = Billing.query.get(billing_id)
        if not billing:
            raise ValueError('Hindi nahanap ang billing record.')
        
        if billing.status == 'paid':
            raise ValueError('Ang billing record ay paid na.')
        
        # Validate payment amount
        amount = float(data.get('amount', 0))
        if not PaymentService.validate_payment_amount(billing_id, amount):
            raise ValueError('Ang payment amount ay hindi pwedeng mas mababa sa billed amount.')
        
        # Validate required fields
        if not data.get('payment_method'):
            raise ValueError('Ang payment method ay required.')
        
        # Parse payment date
        payment_date = data.get('payment_date')
        if isinstance(payment_date, str):
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
        elif not isinstance(payment_date, date):
            payment_date = date.today()
        
        # Create payment
        payment = Payment(
            billing_id=billing_id,
            client_id=billing.client_id,
            amount=amount,
            payment_date=payment_date,
            payment_method=data['payment_method'],
            reference_number=data.get('reference_number', ''),
            notes=data.get('notes', '')
        )
        
        db.session.add(payment)
        db.session.flush()  # Get payment ID before updating billing
        
        # Update billing status
        billing.status = 'paid'
        billing.paid_at = datetime.utcnow()
        billing.payment_id = payment.id
        
        db.session.commit()
        
        return payment
    
    @staticmethod
    def get_payment(payment_id):
        """
        Get a payment by ID.
        
        Args:
            payment_id (int): The payment ID
            
        Returns:
            Payment | None: The payment object if found, None otherwise
        """
        return Payment.query.get(payment_id)
    
    @staticmethod
    def get_client_payments(client_id):
        """
        Get all payments for a specific client.
        
        Args:
            client_id (int): The client ID
            
        Returns:
            list[Payment]: List of payment records
        """
        return Payment.query.filter_by(client_id=client_id).order_by(
            Payment.payment_date.desc()
        ).all()
    
    @staticmethod
    def get_all_payments(filters=None):
        """
        Get all payments with optional filters.
        
        Args:
            filters (dict): Optional filters (client_name, payment_method, date_from, date_to)
            
        Returns:
            list[Payment]: List of payment records
        """
        query = Payment.query.join(Client)
        
        if filters:
            # Search by client name
            if filters.get('client_name'):
                search = f"%{filters['client_name']}%"
                query = query.filter(Client.full_name.ilike(search))
            
            # Filter by payment method
            if filters.get('payment_method'):
                query = query.filter(Payment.payment_method == filters['payment_method'])
            
            # Filter by date range
            if filters.get('date_from'):
                date_from = filters['date_from']
                if isinstance(date_from, str):
                    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Payment.payment_date >= date_from)
            
            if filters.get('date_to'):
                date_to = filters['date_to']
                if isinstance(date_to, str):
                    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Payment.payment_date <= date_to)
        
        return query.order_by(Payment.payment_date.desc()).all()
    
    @staticmethod
    def calculate_total_paid(client_id):
        """
        Calculate the total amount paid by a client.
        
        Args:
            client_id (int): The client ID
            
        Returns:
            float: Total amount paid
        """
        total = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.client_id == client_id
        ).scalar()
        
        return float(total) if total else 0.0
    
    @staticmethod
    def validate_payment_amount(billing_id, amount):
        """
        Validate that payment amount is not less than billed amount.
        
        Args:
            billing_id (int): The billing ID
            amount (float): The payment amount
            
        Returns:
            bool: True if amount is valid, False otherwise
        """
        billing = Billing.query.get(billing_id)
        if not billing:
            return False
        
        return amount >= billing.amount
