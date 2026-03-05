"""Client dashboard service for aggregating client account data"""
from datetime import date
from typing import Optional
from sqlalchemy import or_
from models.client import Client
from models.billing import Billing
from models.payment import Payment
from services.billing_service import BillingService
from services.mikrotik_service import MikrotikService
from extensions import db
from flask import current_app


class ClientDashboardService:
    """Service for aggregating and calculating client dashboard metrics"""
    
    @staticmethod
    def get_dashboard_data(client_id: int) -> dict:
        """
        Get all dashboard data for a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            dict: Dashboard data containing:
                - client: Client information (full_name, pppoe_username, plan_name, plan_amount, status)
                - remaining_days: Days until next payment due
                - unpaid_balance: Total unpaid balance
                - connection_status: Connection status from Mikrotik (online, address, uptime)
                - recent_bills: Last 3 billing records
                - recent_payments: Last 3 payment records
                
        Raises:
            ValueError: If client not found
        """
        # Get client
        client = Client.query.get(client_id)
        if not client:
            raise ValueError('Hindi nahanap ang client.')
        
        # Get remaining days
        remaining_days = ClientDashboardService.calculate_remaining_days(client_id)
        
        # Get unpaid balance
        unpaid_balance = ClientDashboardService.get_total_unpaid_balance(client_id)
        
        # Get connection status
        connection_status = ClientDashboardService.get_connection_status(client.pppoe_username)
        
        # Get recent bills (last 3)
        recent_bills = Billing.query.filter_by(client_id=client_id)\
            .order_by(Billing.billing_year.desc(), Billing.billing_month.desc())\
            .limit(3).all()
        
        # Get recent payments (last 3)
        recent_payments = Payment.query.filter_by(client_id=client_id)\
            .order_by(Payment.payment_date.desc())\
            .limit(3).all()
        
        return {
            'client': {
                'full_name': client.full_name,
                'pppoe_username': client.pppoe_username,
                'plan_name': client.plan_name,
                'plan_amount': client.plan_amount,
                'status': client.status
            },
            'remaining_days': remaining_days,
            'unpaid_balance': unpaid_balance,
            'connection_status': connection_status,
            'recent_bills': recent_bills,
            'recent_payments': recent_payments
        }
    
    @staticmethod
    def calculate_remaining_days(client_id: int) -> Optional[int]:
        """
        Calculate the number of days until the next payment due date.
        
        This is calculated as the difference between the earliest unpaid
        due_date and the current date.
        
        Args:
            client_id: The client ID
            
        Returns:
            int: Number of days remaining (can be negative if overdue),
                 None if no unpaid bills
        """
        # Get the earliest unpaid billing record
        earliest_unpaid = Billing.query.filter(
            Billing.client_id == client_id,
            or_(Billing.status == 'unpaid', Billing.status == 'overdue')
        ).order_by(Billing.due_date.asc()).first()
        
        if not earliest_unpaid:
            return None
        
        # Calculate difference between due date and current date
        today = date.today()
        delta = earliest_unpaid.due_date - today
        
        return delta.days
    
    @staticmethod
    def get_total_unpaid_balance(client_id: int) -> float:
        """
        Calculate the total unpaid balance for a client.
        
        This is the sum of all unpaid and overdue billing records.
        
        Args:
            client_id: The client ID
            
        Returns:
            float: Total unpaid balance (0.0 if no unpaid bills)
        """
        total = db.session.query(db.func.sum(Billing.amount)).filter(
            Billing.client_id == client_id,
            or_(Billing.status == 'unpaid', Billing.status == 'overdue')
        ).scalar()
        
        return float(total) if total else 0.0
    
    @staticmethod
    def get_connection_status(pppoe_username: str) -> dict:
        """
        Get the current connection status from Mikrotik.
        
        Args:
            pppoe_username: The PPPoE username to check
            
        Returns:
            dict: Connection status containing:
                - online: bool indicating if user is online
                - address: IP address if online, None otherwise
                - uptime: Connection uptime if online, None otherwise
                - error: Error message if connection failed, None otherwise
                
        Note:
            If Mikrotik connection fails, returns offline status with
            online=False, address=None, uptime=None, and error message
        """
        try:
            # Initialize Mikrotik service with config
            mikrotik = MikrotikService(
                host=current_app.config['MIKROTIK_HOST'],
                username=current_app.config['MIKROTIK_USER'],
                password=current_app.config['MIKROTIK_PASSWORD']
            )
            
            # Get user connection info
            with mikrotik:
                user_info = mikrotik.get_user_by_name(pppoe_username)
            
            if user_info:
                return {
                    'online': True,
                    'address': user_info.get('address'),
                    'uptime': user_info.get('uptime'),
                    'error': None
                }
            else:
                return {
                    'online': False,
                    'address': None,
                    'uptime': None,
                    'error': None
                }
                
        except Exception as e:
            # Log error and return offline status with error message
            current_app.logger.error(f"Error getting connection status for {pppoe_username}: {str(e)}")
            return {
                'online': False,
                'address': None,
                'uptime': None,
                'error': 'Connection status ay pansamantalang hindi available'
            }
