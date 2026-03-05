"""Unit tests for Client model"""
import pytest
from models.client import Client
from extensions import db


def test_client_creation(app):
    """Test creating a client instance"""
    with app.app_context():
        client = Client(
            full_name='Juan Dela Cruz',
            address='123 Main St, Manila',
            contact_number='09171234567',
            email='juan@example.com',
            pppoe_username='juan_pppoe',
            plan_name='Plan A - 10Mbps',
            plan_amount=999.00,
            status='active'
        )
        
        assert client.full_name == 'Juan Dela Cruz'
        assert client.address == '123 Main St, Manila'
        assert client.contact_number == '09171234567'
        assert client.email == 'juan@example.com'
        assert client.pppoe_username == 'juan_pppoe'
        assert client.plan_name == 'Plan A - 10Mbps'
        assert client.plan_amount == 999.00
        assert client.status == 'active'


def test_client_default_status(app, db):
    """Test that client status defaults to 'active'"""
    with app.app_context():
        client = Client(
            full_name='Test User',
            pppoe_username='test_pppoe',
            plan_name='Plan B',
            plan_amount=1500.00
        )
        client.set_password('test_password')
        db.session.add(client)
        db.session.commit()
        
        assert client.status == 'active'


def test_client_pppoe_username_unique(app, db):
    """Test that PPPoE username must be unique"""
    with app.app_context():
        # Create first client
        client1 = Client(
            full_name='Client One',
            pppoe_username='unique_user',
            plan_name='Plan A',
            plan_amount=999.00
        )
        client1.set_password('password1')
        db.session.add(client1)
        db.session.commit()
        
        # Attempt to create second client with same PPPoE username
        client2 = Client(
            full_name='Client Two',
            pppoe_username='unique_user',
            plan_name='Plan B',
            plan_amount=1500.00
        )
        client2.set_password('password2')
        db.session.add(client2)
        
        # Should raise IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy raises IntegrityError
            db.session.commit()


def test_client_required_fields(app, db):
    """Test that required fields cannot be null"""
    with app.app_context():
        # Missing full_name
        client = Client(
            pppoe_username='test_user',
            plan_name='Plan A',
            plan_amount=999.00
        )
        client.full_name = None
        db.session.add(client)
        
        with pytest.raises(Exception):
            db.session.commit()


def test_client_repr(app):
    """Test client string representation"""
    with app.app_context():
        client = Client(
            full_name='Juan Dela Cruz',
            pppoe_username='juan_pppoe',
            plan_name='Plan A',
            plan_amount=999.00
        )
        
        assert repr(client) == '<Client Juan Dela Cruz (juan_pppoe)>'


def test_client_timestamps(app, db):
    """Test that timestamps are set correctly"""
    with app.app_context():
        client = Client(
            full_name='Test User',
            pppoe_username='test_pppoe',
            plan_name='Plan A',
            plan_amount=999.00
        )
        client.set_password('test_password')
        db.session.add(client)
        db.session.commit()
        
        assert client.created_at is not None
        assert client.updated_at is not None
        # Timestamps should be very close (within 1 second)
        assert abs((client.created_at - client.updated_at).total_seconds()) < 1
