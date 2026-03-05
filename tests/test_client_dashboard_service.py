"""Tests for ClientDashboardService"""
import pytest
from datetime import date, timedelta
from models.client import Client
from models.billing import Billing
from models.payment import Payment
from services.client_dashboard_service import ClientDashboardService
from extensions import db


@pytest.fixture
def test_client(app, db):
    """Create a test client"""
    with app.app_context():
        client = Client(
            full_name='Test Client',
            pppoe_username='testuser',
            plan_name='Basic Plan',
            plan_amount=1500.0,
            status='active'
        )
        client.set_password('testpass123')
        db.session.add(client)
        db.session.commit()
        db.session.refresh(client)
        yield client


@pytest.fixture
def test_billing_records(app, db, test_client):
    """Create test billing records"""
    with app.app_context():
        # Create unpaid bill due in 10 days
        bill1 = Billing(
            client_id=test_client.id,
            billing_month=date.today().month,
            billing_year=date.today().year,
            amount=1500.0,
            due_date=date.today() + timedelta(days=10),
            status='unpaid'
        )
        
        # Create overdue bill
        bill2 = Billing(
            client_id=test_client.id,
            billing_month=(date.today().month - 1) if date.today().month > 1 else 12,
            billing_year=date.today().year if date.today().month > 1 else date.today().year - 1,
            amount=1500.0,
            due_date=date.today() - timedelta(days=5),
            status='overdue'
        )
        
        # Create paid bill
        bill3 = Billing(
            client_id=test_client.id,
            billing_month=(date.today().month - 2) if date.today().month > 2 else 12,
            billing_year=date.today().year if date.today().month > 2 else date.today().year - 1,
            amount=1500.0,
            due_date=date.today() - timedelta(days=35),
            status='paid'
        )
        
        db.session.add_all([bill1, bill2, bill3])
        db.session.commit()
        
        yield [bill1, bill2, bill3]


@pytest.fixture
def test_payments(app, db, test_client, test_billing_records):
    """Create test payment records"""
    with app.app_context():
        payment = Payment(
            client_id=test_client.id,
            billing_id=test_billing_records[2].id,
            amount=1500.0,
            payment_date=date.today() - timedelta(days=30),
            payment_method='gcash',
            reference_number='TEST123'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        yield [payment]


class TestClientDashboardService:
    """Test cases for ClientDashboardService"""
    
    def test_get_dashboard_data_with_valid_client(self, app, test_client, test_billing_records, test_payments):
        """Test getting dashboard data for a valid client"""
        with app.app_context():
            result = ClientDashboardService.get_dashboard_data(test_client.id)
            
            assert result is not None
            assert 'client' in result
            assert 'remaining_days' in result
            assert 'unpaid_balance' in result
            assert 'connection_status' in result
            assert 'recent_bills' in result
            assert 'recent_payments' in result
            
            # Check client data
            assert result['client']['full_name'] == 'Test Client'
            assert result['client']['pppoe_username'] == 'testuser'
            assert result['client']['plan_name'] == 'Basic Plan'
            assert result['client']['plan_amount'] == 1500.0
            assert result['client']['status'] == 'active'
    
    def test_get_dashboard_data_with_invalid_client(self, app):
        """Test getting dashboard data for invalid client raises error"""
        with app.app_context():
            with pytest.raises(ValueError, match='Hindi nahanap ang client'):
                ClientDashboardService.get_dashboard_data(99999)
    
    def test_calculate_remaining_days_with_unpaid_bills(self, app, test_client, test_billing_records):
        """Test calculating remaining days with unpaid bills"""
        with app.app_context():
            remaining_days = ClientDashboardService.calculate_remaining_days(test_client.id)
            
            # Should return the days until the earliest unpaid bill (which is the overdue one, -5 days)
            assert remaining_days is not None
            assert remaining_days == -5
    
    def test_calculate_remaining_days_with_no_unpaid_bills(self, app, test_client):
        """Test calculating remaining days with no unpaid bills"""
        with app.app_context():
            remaining_days = ClientDashboardService.calculate_remaining_days(test_client.id)
            
            assert remaining_days is None
    
    def test_get_total_unpaid_balance(self, app, test_client, test_billing_records):
        """Test calculating total unpaid balance"""
        with app.app_context():
            unpaid_balance = ClientDashboardService.get_total_unpaid_balance(test_client.id)
            
            # Should be sum of unpaid (1500) and overdue (1500) = 3000
            assert unpaid_balance == 3000.0
    
    def test_get_total_unpaid_balance_with_no_unpaid_bills(self, app, test_client):
        """Test calculating unpaid balance with no unpaid bills"""
        with app.app_context():
            unpaid_balance = ClientDashboardService.get_total_unpaid_balance(test_client.id)
            
            assert unpaid_balance == 0.0
    
    def test_get_connection_status_returns_dict(self, app, test_client):
        """Test that connection status returns a dict with expected keys"""
        with app.app_context():
            status = ClientDashboardService.get_connection_status('testuser')
            
            assert isinstance(status, dict)
            assert 'online' in status
            assert 'address' in status
            assert 'uptime' in status
            
            # Since Mikrotik is likely not configured in test, should return offline
            assert status['online'] is False
            assert status['address'] is None
            assert status['uptime'] is None
    
    def test_dashboard_data_includes_recent_bills(self, app, test_client, test_billing_records):
        """Test that dashboard includes recent billing records"""
        with app.app_context():
            result = ClientDashboardService.get_dashboard_data(test_client.id)
            
            assert len(result['recent_bills']) <= 3
            assert len(result['recent_bills']) > 0
    
    def test_dashboard_data_includes_recent_payments(self, app, test_client, test_billing_records, test_payments):
        """Test that dashboard includes recent payment records"""
        with app.app_context():
            result = ClientDashboardService.get_dashboard_data(test_client.id)
            
            assert len(result['recent_payments']) <= 3
            assert len(result['recent_payments']) > 0
