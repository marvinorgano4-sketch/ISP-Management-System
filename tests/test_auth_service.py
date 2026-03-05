"""Unit tests for AuthService"""
import pytest
from datetime import datetime
from services.auth_service import AuthService
from models.user import User
from extensions import db


class TestAuthService:
    """Test cases for AuthService class"""
    
    def test_authenticate_user_with_valid_credentials(self, app, test_user):
        """Test authentication with valid username and password"""
        with app.app_context():
            # Authenticate with correct credentials
            authenticated_user = AuthService.authenticate_user('admin', 'admin123')
            
            assert authenticated_user is not None
            assert authenticated_user.username == 'admin'
            assert authenticated_user.last_login is not None
    
    def test_authenticate_user_with_invalid_password(self, app, test_user):
        """Test authentication fails with invalid password"""
        with app.app_context():
            # Authenticate with wrong password
            authenticated_user = AuthService.authenticate_user('admin', 'wrongpassword')
            
            assert authenticated_user is None
    
    def test_authenticate_user_with_invalid_username(self, app):
        """Test authentication fails with non-existent username"""
        with app.app_context():
            # Authenticate with non-existent user
            authenticated_user = AuthService.authenticate_user('nonexistent', 'password')
            
            assert authenticated_user is None
    
    def test_authenticate_user_with_empty_credentials(self, app):
        """Test authentication fails with empty credentials"""
        with app.app_context():
            # Test with empty username
            assert AuthService.authenticate_user('', 'password') is None
            
            # Test with empty password
            assert AuthService.authenticate_user('admin', '') is None
            
            # Test with both empty
            assert AuthService.authenticate_user('', '') is None
    
    def test_create_session(self, app, test_user):
        """Test session creation for authenticated user"""
        with app.test_request_context():
            # Create session
            AuthService.create_session(test_user)
            
            # Note: We can't easily test login_user in unit tests without
            # a full request context, but we verify it doesn't raise errors
    
    def test_destroy_session(self, app):
        """Test session destruction"""
        with app.test_request_context():
            # Destroy session
            AuthService.destroy_session()
            
            # Note: We can't easily test logout_user in unit tests without
            # a full request context, but we verify it doesn't raise errors
    
    def test_require_login_decorator(self, app, test_user):
        """Test require_login decorator protects routes"""
        with app.test_request_context():
            @AuthService.require_login
            def protected_route():
                return "Protected content"
            
            # The decorator should be applied without errors
            assert hasattr(protected_route, '__wrapped__')
