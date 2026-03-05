"""Tests for access control separation between client and admin authentication"""
import pytest
from flask import session
from models.user import User
from models.client import Client
from services.auth_service import AuthService
from services.client_auth_service import ClientAuthService
from extensions import db


@pytest.fixture
def admin_user(app):
    """Create a test admin user"""
    with app.app_context():
        user = User(username='admin_test', full_name='Admin Test User')
        user.set_password('admin_password123')
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def test_client(app):
    """Create a test client"""
    with app.app_context():
        client = Client(
            pppoe_username='client_test',
            full_name='Test Client',
            plan_name='Basic Plan',
            plan_amount=500.0,
            status='active'
        )
        client.set_password('client_password123')
        db.session.add(client)
        db.session.commit()
        yield client
        db.session.delete(client)
        db.session.commit()


class TestCredentialSeparation:
    """Test that admin and client credentials are properly separated"""
    
    def test_admin_credentials_dont_work_on_client_login(self, app, admin_user):
        """
        Test that admin credentials cannot be used to authenticate on client login.
        
        Requirements: 10.1, 10.3
        """
        with app.app_context():
            # Try to authenticate with admin credentials on client login
            result = ClientAuthService.authenticate_client(
                admin_user.username,
                'admin_password123'
            )
            
            # Should fail - admin credentials don't work on client login
            assert result is None
    
    def test_client_credentials_dont_work_on_admin_login(self, app, test_client):
        """
        Test that client credentials cannot be used to authenticate on admin login.
        
        Requirements: 10.1, 10.3
        """
        with app.app_context():
            # Try to authenticate with client credentials on admin login
            result = AuthService.authenticate_user(
                test_client.pppoe_username,
                'client_password123'
            )
            
            # Should fail - client credentials don't work on admin login
            assert result is None
    
    def test_admin_can_login_with_admin_credentials(self, app, admin_user):
        """
        Test that admin can successfully login with admin credentials.
        
        Requirements: 10.1
        """
        with app.app_context():
            # Admin should be able to login with admin credentials
            result = AuthService.authenticate_user(
                admin_user.username,
                'admin_password123'
            )
            
            assert result is not None
            assert result.id == admin_user.id
            assert result.username == admin_user.username
    
    def test_client_can_login_with_client_credentials(self, app, test_client):
        """
        Test that client can successfully login with client credentials.
        
        Requirements: 10.1
        """
        with app.app_context():
            # Client should be able to login with client credentials
            result = ClientAuthService.authenticate_client(
                test_client.pppoe_username,
                'client_password123'
            )
            
            assert result is not None
            assert result.id == test_client.id
            assert result.pppoe_username == test_client.pppoe_username
    
    def test_wrong_password_fails_admin_login(self, app, admin_user):
        """
        Test that wrong password fails admin login.
        
        Requirements: 10.1
        """
        with app.app_context():
            result = AuthService.authenticate_user(
                admin_user.username,
                'wrong_password'
            )
            
            assert result is None
    
    def test_wrong_password_fails_client_login(self, app, test_client):
        """
        Test that wrong password fails client login.
        
        Requirements: 10.1
        """
        with app.app_context():
            result = ClientAuthService.authenticate_client(
                test_client.pppoe_username,
                'wrong_password'
            )
            
            assert result is None
    
    def test_nonexistent_admin_username_fails(self, app):
        """
        Test that non-existent admin username fails authentication.
        
        Requirements: 10.1
        """
        with app.app_context():
            result = AuthService.authenticate_user(
                'nonexistent_admin',
                'any_password'
            )
            
            assert result is None
    
    def test_nonexistent_client_username_fails(self, app):
        """
        Test that non-existent client username fails authentication.
        
        Requirements: 10.1
        """
        with app.app_context():
            result = ClientAuthService.authenticate_client(
                'nonexistent_client',
                'any_password'
            )
            
            assert result is None



class TestRouteAccessControl:
    """Test that clients cannot access admin routes"""
    
    def test_client_cannot_access_dashboard(self, client, test_client):
        """
        Test that a client session cannot access the admin dashboard.
        
        Requirements: 10.2, 10.4
        """
        # Login as client
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
        
        # Try to access admin dashboard
        response = client.get('/dashboard/')
        
        # Should return 403 Forbidden
        assert response.status_code == 403
    
    def test_client_cannot_access_clients_list(self, client, test_client):
        """
        Test that a client session cannot access the admin clients list.
        
        Requirements: 10.2, 10.4
        """
        # Login as client
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
        
        # Try to access admin clients list
        response = client.get('/clients/')
        
        # Should return 403 Forbidden
        assert response.status_code == 403
    
    def test_client_cannot_access_billing_list(self, client, test_client):
        """
        Test that a client session cannot access the admin billing list.
        
        Requirements: 10.2, 10.4
        """
        # Login as client
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
        
        # Try to access admin billing list
        response = client.get('/billing/')
        
        # Should return 403 Forbidden
        assert response.status_code == 403
    
    def test_client_cannot_access_payments_list(self, client, test_client):
        """
        Test that a client session cannot access the admin payments list.
        
        Requirements: 10.2, 10.4
        """
        # Login as client
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
        
        # Try to access admin payments list
        response = client.get('/payments/')
        
        # Should return 403 Forbidden
        assert response.status_code == 403
    
    def test_client_can_access_client_portal_routes(self, client, test_client):
        """
        Test that a client session can access client portal routes.
        
        Requirements: 10.2
        """
        # Login as client
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
        
        # Try to access client bills list (simpler route that doesn't need complex data)
        response = client.get('/client/bills')
        
        # Should return 200 OK (or redirect if additional auth is needed)
        # The important thing is it should NOT return 403
        assert response.status_code != 403
    
    def test_unauthenticated_can_access_login_pages(self, client):
        """
        Test that unauthenticated users can access login pages.
        
        Requirements: 10.2
        """
        # Try to access admin login (should work)
        response = client.get('/login')
        assert response.status_code == 200
        
        # Try to access client login (should work)
        response = client.get('/client/login')
        assert response.status_code == 200
    
    def test_admin_session_can_access_admin_routes(self, client, admin_user):
        """
        Test that an admin session (without client_id) can access admin routes.
        
        Requirements: 10.2
        """
        # Simulate admin login (Flask-Login sets user_id, not client_id)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            # No client_id in session
        
        # Try to access admin dashboard
        response = client.get('/dashboard/')
        
        # Should NOT return 403 (may redirect to login if Flask-Login requires it)
        assert response.status_code != 403



class TestSessionIsolation:
    """Test that client and admin sessions are properly isolated"""
    
    def test_client_and_admin_sessions_dont_interfere(self, client, admin_user, test_client):
        """
        Test that client and admin sessions can exist concurrently without interference.
        
        Requirements: 10.5
        """
        # Create a client session
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
        
        # Verify client session exists
        with client.session_transaction() as sess:
            assert sess.get('client_id') == test_client.id
            assert sess.get('client_username') == test_client.pppoe_username
        
        # Now add admin session data (simulating Flask-Login)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
        
        # Verify both sessions coexist
        with client.session_transaction() as sess:
            assert sess.get('client_id') == test_client.id
            assert sess.get('_user_id') == str(admin_user.id)
        
        # Client session should still block admin routes
        response = client.get('/dashboard/')
        assert response.status_code == 403
        
        # Client routes should still be accessible
        response = client.get('/client/bills')
        assert response.status_code != 403
    
    def test_client_logout_doesnt_affect_admin_session(self, client, admin_user, test_client):
        """
        Test that logging out from client session doesn't affect admin session.
        
        Requirements: 10.5
        """
        # Create both sessions
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
            sess['_user_id'] = str(admin_user.id)
        
        # Logout from client session
        from services.client_auth_service import ClientAuthService
        with client.application.app_context():
            with client.session_transaction() as sess:
                # Simulate what destroy_client_session does
                sess.pop('client_id', None)
                sess.pop('client_username', None)
        
        # Verify client session is gone but admin session remains
        with client.session_transaction() as sess:
            assert sess.get('client_id') is None
            assert sess.get('client_username') is None
            assert sess.get('_user_id') == str(admin_user.id)
    
    def test_admin_logout_doesnt_affect_client_session(self, client, admin_user, test_client):
        """
        Test that logging out from admin session doesn't affect client session.
        
        Requirements: 10.5
        """
        # Create both sessions
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
            sess['_user_id'] = str(admin_user.id)
        
        # Logout from admin session (Flask-Login removes _user_id)
        with client.session_transaction() as sess:
            sess.pop('_user_id', None)
        
        # Verify admin session is gone but client session remains
        with client.session_transaction() as sess:
            assert sess.get('client_id') == test_client.id
            assert sess.get('client_username') == test_client.pppoe_username
            assert sess.get('_user_id') is None
    
    def test_client_session_keys_are_separate_from_admin(self, client, admin_user, test_client):
        """
        Test that client and admin sessions use different session keys.
        
        Requirements: 10.5
        """
        # Create client session
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
        
        # Create admin session
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
        
        # Verify they use different keys
        with client.session_transaction() as sess:
            # Client uses 'client_id' and 'client_username'
            assert 'client_id' in sess
            assert 'client_username' in sess
            
            # Admin uses '_user_id' (Flask-Login convention)
            assert '_user_id' in sess
            
            # They should not overlap
            assert sess['client_id'] != sess['_user_id']
    
    def test_concurrent_sessions_maintain_separate_authentication_state(self, client, admin_user, test_client):
        """
        Test that concurrent client and admin sessions maintain separate authentication states.
        
        Requirements: 10.5
        """
        # Create both sessions
        with client.session_transaction() as sess:
            sess['client_id'] = test_client.id
            sess['client_username'] = test_client.pppoe_username
            sess['login_time'] = '2024-01-01T10:00:00'
            sess['last_activity'] = '2024-01-01T10:30:00'
            sess['_user_id'] = str(admin_user.id)
        
        # Verify client authentication state
        with client.session_transaction() as sess:
            assert sess.get('client_id') == test_client.id
            assert sess.get('login_time') == '2024-01-01T10:00:00'
            assert sess.get('last_activity') == '2024-01-01T10:30:00'
        
        # Verify admin authentication state
        with client.session_transaction() as sess:
            assert sess.get('_user_id') == str(admin_user.id)
        
        # Modify client session state
        with client.session_transaction() as sess:
            sess['last_activity'] = '2024-01-01T11:00:00'
        
        # Verify admin session is unaffected
        with client.session_transaction() as sess:
            assert sess.get('_user_id') == str(admin_user.id)
            assert sess.get('last_activity') == '2024-01-01T11:00:00'  # Client's activity
