"""Dashboard service for aggregating system statistics"""
from datetime import datetime, date
from sqlalchemy import and_, or_, func
from models.client import Client
from models.billing import Billing
from models.payment import Payment
from services.mikrotik_service import MikrotikService
from config import Config
from extensions import db


class DashboardService:
    """Service class for handling dashboard operations"""
    
    @staticmethod
    def get_statistics():
        """
        Get dashboard statistics.
        
        Returns:
            dict: Statistics containing total_clients, active_connections,
                  pending_payments, total_revenue_month, total_revenue_all, overdue_bills
        """
        # Total clients
        total_clients = Client.query.filter_by(status='active').count()
        
        # Active connections (from Mikrotik)
        active_connections = 0
        try:
            mikrotik = MikrotikService(
                Config.MIKROTIK_HOST,
                Config.MIKROTIK_USER,
                Config.MIKROTIK_PASSWORD
            )
            active_users = mikrotik.get_active_pppoe_users()
            active_connections = len(active_users) if active_users else 0
            mikrotik.disconnect()
        except Exception as e:
            # If Mikrotik connection fails, just set to 0
            active_connections = 0
        
        # Pending payments (unpaid + overdue)
        pending_payments = Billing.query.filter(
            or_(Billing.status == 'unpaid', Billing.status == 'overdue')
        ).count()
        
        # Total revenue for current month
        today = date.today()
        month_start = date(today.year, today.month, 1)
        total_revenue_month = db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= month_start
        ).scalar() or 0.0
        
        # Total revenue all time
        total_revenue_all = db.session.query(func.sum(Payment.amount)).scalar() or 0.0
        
        # Overdue bills
        overdue_bills = Billing.query.filter(
            and_(
                Billing.status == 'unpaid',
                Billing.due_date < today
            )
        ).count()
        
        # Update overdue bills status
        overdue_records = Billing.query.filter(
            and_(
                Billing.status == 'unpaid',
                Billing.due_date < today
            )
        ).all()
        
        for bill in overdue_records:
            bill.status = 'overdue'
        
        if overdue_records:
            db.session.commit()
        
        return {
            'total_clients': total_clients,
            'active_connections': active_connections,
            'pending_payments': pending_payments,
            'total_revenue_month': float(total_revenue_month),
            'total_revenue_all': float(total_revenue_all),
            'overdue_bills': overdue_bills
        }
    
    @staticmethod
    def get_active_connections():
        """
        Get active PPPoE connections from Mikrotik.
        
        Returns:
            list[dict]: List of active connections with client information
        """
        try:
            mikrotik = MikrotikService(
                Config.MIKROTIK_HOST,
                Config.MIKROTIK_USER,
                Config.MIKROTIK_PASSWORD
            )
            active_users = mikrotik.get_active_pppoe_users()
            mikrotik.disconnect()
            
            if not active_users:
                return []
            
            # Enrich with client information
            connections = []
            for user in active_users:
                # Find client by PPPoE username
                client = Client.query.filter_by(pppoe_username=user['name']).first()
                
                connection = {
                    'pppoe_username': user['name'],
                    'ip_address': user.get('address', 'N/A'),
                    'service': user.get('service', 'N/A'),
                    'uptime': user.get('uptime', 'N/A'),
                    'caller_id': user.get('caller_id', 'N/A'),
                    'client_name': client.full_name if client else 'Unknown',
                    'client_id': client.id if client else None
                }
                connections.append(connection)
            
            return connections
            
        except Exception as e:
            # Return empty list if Mikrotik connection fails
            return []
    
    @staticmethod
    def get_recent_payments(limit=10):
        """
        Get recent payments.
        
        Args:
            limit (int): Maximum number of payments to return
            
        Returns:
            list[Payment]: List of recent payment records
        """
        return Payment.query.order_by(Payment.payment_date.desc()).limit(limit).all()
    
    @staticmethod
    def get_pending_bills(limit=10):
        """
        Get pending bills (unpaid + overdue).
        
        Args:
            limit (int): Maximum number of bills to return
            
        Returns:
            list[Billing]: List of pending billing records
        """
        return Billing.query.filter(
            or_(Billing.status == 'unpaid', Billing.status == 'overdue')
        ).order_by(Billing.due_date.asc()).limit(limit).all()

