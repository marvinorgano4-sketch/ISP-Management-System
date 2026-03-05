"""Billing service for managing monthly bills"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_
from models.billing import Billing
from models.client import Client
from extensions import db


class BillingService:
    """Service class for handling billing operations"""
    
    @staticmethod
    def generate_monthly_bills(month, year):
        """
        Generate monthly bills for all active clients.
        
        Args:
            month (int): Billing month (1-12)
            year (int): Billing year
            
        Returns:
            list[Billing]: List of created billing records
            
        Raises:
            ValueError: If month or year is invalid
        """
        # Validate month and year
        if not (1 <= month <= 12):
            raise ValueError('Ang buwan ay dapat 1-12 lamang.')
        if year < 2000 or year > 2100:
            raise ValueError('Invalid na taon.')
        
        # Check if bills already exist for this period
        existing_bills = Billing.query.filter_by(
            billing_month=month,
            billing_year=year
        ).first()
        
        if existing_bills:
            raise ValueError(f'May existing bills na para sa {month}/{year}.')
        
        # Get all active clients
        active_clients = Client.query.filter_by(status='active').all()
        
        if not active_clients:
            raise ValueError('Walang active na clients.')
        
        # Calculate due date (end of the month)
        billing_date = date(year, month, 1)
        due_date = billing_date + relativedelta(day=31)
        
        created_bills = []
        
        for client in active_clients:
            billing = Billing(
                client_id=client.id,
                amount=client.plan_amount,
                billing_month=month,
                billing_year=year,
                due_date=due_date,
                status='unpaid'
            )
            db.session.add(billing)
            created_bills.append(billing)
        
        db.session.commit()
        
        return created_bills
    
    @staticmethod
    def get_billing(billing_id):
        """
        Get a billing record by ID.
        
        Args:
            billing_id (int): The billing ID
            
        Returns:
            Billing | None: The billing object if found, None otherwise
        """
        return Billing.query.get(billing_id)
    
    @staticmethod
    def get_client_bills(client_id, filters=None):
        """
        Get all billing records for a specific client.
        
        Args:
            client_id (int): The client ID
            filters (dict): Optional filters (status, month, year)
            
        Returns:
            list[Billing]: List of billing records
        """
        query = Billing.query.filter_by(client_id=client_id)
        
        if filters:
            if filters.get('status'):
                query = query.filter_by(status=filters['status'])
            if filters.get('month'):
                query = query.filter_by(billing_month=filters['month'])
            if filters.get('year'):
                query = query.filter_by(billing_year=filters['year'])
        
        return query.order_by(Billing.billing_year.desc(), Billing.billing_month.desc()).all()
    
    @staticmethod
    def get_all_bills(filters=None):
        """
        Get all billing records with optional filters.
        
        Args:
            filters (dict): Optional filters (status, month, year, client_name)
            
        Returns:
            list[Billing]: List of billing records
        """
        query = Billing.query.join(Client)
        
        if filters:
            # Filter by status
            if filters.get('status'):
                query = query.filter(Billing.status == filters['status'])
            
            # Filter by month
            if filters.get('month'):
                query = query.filter(Billing.billing_month == filters['month'])
            
            # Filter by year
            if filters.get('year'):
                query = query.filter(Billing.billing_year == filters['year'])
            
            # Search by client name
            if filters.get('client_name'):
                search = f"%{filters['client_name']}%"
                query = query.filter(Client.full_name.ilike(search))
        
        # Check for overdue bills and update status
        today = date.today()
        overdue_bills = query.filter(
            and_(
                Billing.status == 'unpaid',
                Billing.due_date < today
            )
        ).all()
        
        for bill in overdue_bills:
            bill.status = 'overdue'
        
        if overdue_bills:
            db.session.commit()
        
        return query.order_by(Billing.billing_year.desc(), Billing.billing_month.desc()).all()
    
    @staticmethod
    def calculate_total_due(client_id):
        """
        Calculate the total amount due for a client (unpaid + overdue).
        
        Args:
            client_id (int): The client ID
            
        Returns:
            float: Total amount due
        """
        total = db.session.query(db.func.sum(Billing.amount)).filter(
            and_(
                Billing.client_id == client_id,
                or_(Billing.status == 'unpaid', Billing.status == 'overdue')
            )
        ).scalar()
        
        return float(total) if total else 0.0
    
    @staticmethod
    def mark_as_paid(billing_id, payment_id):
        """
        Mark a billing record as paid.
        
        Args:
            billing_id (int): The billing ID
            payment_id (int): The payment ID
            
        Returns:
            Billing: The updated billing object
            
        Raises:
            ValueError: If billing not found or already paid
        """
        billing = Billing.query.get(billing_id)
        
        if not billing:
            raise ValueError('Hindi nahanap ang billing record.')
        
        if billing.status == 'paid':
            raise ValueError('Ang billing record ay paid na.')
        
        billing.status = 'paid'
        billing.paid_at = datetime.utcnow()
        billing.payment_id = payment_id
        
        db.session.commit()
        
        return billing
