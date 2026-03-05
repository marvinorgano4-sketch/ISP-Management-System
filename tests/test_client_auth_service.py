"""Tests for ClientAuthService"""
import pytest
from datetime import datetime, timedelta
from flask import session
from models.client import Client
from services.client_auth_service import ClientAuthService
from extensions import db


@pytest.fixture
def test_client(app, db):
    """Create a test client with password"""
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


class TestClientAuthService:
    """Test cases for ClientAuthService"""
    
    def test_authenticate_client_with_valid_credentials(self, app, test_client):
        """Test authentication with valid credentials"""
        with app.app_context():
            result = ClientAuthService.authenticate_client('testuser', 'testpass123')
            
            assert result is not None
            assert result.id == test_client.id
            assert result.pppoe_username == 'testuser'
            assert result.last_login is not None
    
    def test_authenticate_client_with_invalid_username(self, app, test_client):
        """Test authentication with invalid username"""
        with app.app_context():
            result = ClientAuthService.authenticate_client('wronguser', 'testpass123')
            
            assert result is None
    
    def test_authenticate_client_with_invalid_password(self, app, test_client):
        """Test authentication with invalid password"""
        with app.app_context():
            result = ClientAuthService.authenticate_client('testuser', 'wrongpass')
            
            assert result is None
    
    def test_authenticate_client_with_empty_username(self, app, test_client):
        """Test authentication with empty username"""
        with app.app_context():
            with pytest.raises(ValueError, match='Username at password ay kinakailangan'):
                ClientAuthService.authenticate_client('', 'testpass123')
    
    def test_authenticate_client_with_empty_password(self, app, test_client):
        """Test authentication with empty password"""
        with app.app_context():
            with pytest.raises(ValueError, match='Username at password ay kinakailangan'):
                ClientAuthService.authenticate_client('testuser', '')
    
    def test_authenticate_client_with_none_credentials(self, app, test_client):
        """Test authentication with None credentials"""
        with app.app_context():
            with pytest.raises(ValueError, match='Username at password ay kinakailangan'):
                ClientAuthService.authenticate_client(None, None)
    
    def test_authenticate_client_with_inactive_account(self, app, db):
        """Test authentication with inactive account"""
        with app.app_context():
            # Create an inactive client
            inactive_client = Client(
                full_name='Inactive User',
                pppoe_username='inactiveuser',
                plan_name='Basic Plan',
                plan_amount=500.0,
                status='inactive'
            )
            inactive_client.set_password('testpass123')
            db.session.add(inactive_client)
            db.session.commit()
            
            with pytest.raises(ValueError, match='Ang iyong account ay kasalukuyang inactive'):
                ClientAuthService.authenticate_client('inactiveuser', 'testpass123')
    
    def test_create_client_session(self, app, test_client):
        """Test session creation for authenticated client"""
        with app.test_request_context():
            ClientAuthService.create_client_session(test_client)
            
            assert session.get('client_id') == test_client.id
            assert session.get('client_username') == 'testuser'
            assert session.get('login_time') is not None
            assert session.get('last_activity') is not None
            assert session.permanent is True
    
    def test_create_client_session_clears_previous_session(self, app, test_client):
        """Test that creating a new session clears previous session data"""
        with app.test_request_context():
            # Set some previous session data
            session['old_data'] = 'should be cleared'
            session['client_id'] = 999
            
            ClientAuthService.create_client_session(test_client)
            
            assert session.get('old_data') is None
            assert session.get('client_id') == test_client.id
    
    def test_destroy_client_session(self, app, test_client):
        """Test session destruction (logout)"""
        with app.test_request_context():
            # Create a session first
            ClientAuthService.create_client_session(test_client)
            
            # Verify session exists
            assert session.get('client_id') is not None
            
            # Destroy session
            ClientAuthService.destroy_client_session()
            
            # Verify session is cleared
            assert session.get('client_id') is None
            assert session.get('client_username') is None
            assert session.get('login_time') is None
            assert session.get('last_activity') is None
    
    def test_get_current_client_with_valid_session(self, app, test_client):
        """Test getting current client with valid session"""
        with app.test_request_context():
            ClientAuthService.create_client_session(test_client)
            
            current_client = ClientAuthService.get_current_client()
            
            assert current_client is not None
            assert current_client.id == test_client.id
            assert current_client.pppoe_username == 'testuser'
    
    def test_get_current_client_with_no_session(self, app):
        """Test getting current client with no session"""
        with app.test_request_context():
            current_client = ClientAuthService.get_current_client()
            
            assert current_client is None
    
    def test_get_current_client_updates_last_activity(self, app, test_client):
        """Test that getting current client updates last_activity timestamp"""
        with app.test_request_context():
            ClientAuthService.create_client_session(test_client)
            
            # Get initial last_activity
            initial_activity = session.get('last_activity')
            
            # Wait a tiny bit (not necessary but conceptually clear)
            import time
            time.sleep(0.01)
            
            # Get current client (should update last_activity)
            ClientAuthService.get_current_client()
            
            # Check that last_activity was updated
            updated_activity = session.get('last_activity')
            assert updated_activity != initial_activity
    
    def test_get_current_client_with_expired_session(self, app, test_client):
        """Test that expired session (>30 minutes) returns None"""
        with app.test_request_context():
            ClientAuthService.create_client_session(test_client)
            
            # Manually set last_activity to 31 minutes ago
            expired_time = datetime.utcnow() - timedelta(minutes=31)
            session['last_activity'] = expired_time.isoformat()
            
            current_client = ClientAuthService.get_current_client()
            
            assert current_client is None
            # Session should be destroyed
            assert session.get('client_id') is None
    
    def test_require_client_login_decorator_with_authenticated_client(self, app, test_client):
        """Test require_client_login decorator allows authenticated clients"""
        with app.test_request_context():
            ClientAuthService.create_client_session(test_client)
            
            @ClientAuthService.require_client_login
            def protected_route():
                return 'success'
            
            result = protected_route()
            assert result == 'success'
    
    def test_require_client_login_decorator_without_authentication(self, app):
        """Test require_client_login decorator redirects unauthenticated users"""
        with app.test_request_context():
            # Mock the url_for to avoid BuildError since client_portal blueprint doesn't exist yet
            from unittest.mock import patch
            
            @ClientAuthService.require_client_login
            def protected_route():
                return 'success'
            
            with patch('services.client_auth_service.url_for', return_value='/client/login'):
                result = protected_route()
            
            # Should return a redirect response
            assert result.status_code == 302
            assert '/client/login' in result.location
    
    def test_authenticate_updates_last_login_timestamp(self, app, test_client):
        """Test that successful authentication updates last_login timestamp"""
        with app.app_context():
            # Get initial last_login
            initial_last_login = test_client.last_login
            
            # Authenticate
            result = ClientAuthService.authenticate_client('testuser', 'testpass123')
            
            # Check that last_login was updated
            assert result.last_login is not None
            assert result.last_login != initial_last_login
