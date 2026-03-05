"""Unit tests for User model"""
import pytest
from models.user import User


def test_user_creation(app):
    """Test creating a user instance"""
    with app.app_context():
        user = User(username='admin', full_name='Admin User')
        assert user.username == 'admin'
        assert user.full_name == 'Admin User'


def test_password_hashing(app):
    """Test password hashing functionality"""
    with app.app_context():
        user = User(username='testuser')
        password = 'SecurePassword123'
        
        # Set password
        user.set_password(password)
        
        # Verify password hash is stored
        assert user.password_hash is not None
        assert user.password_hash != password  # Should be hashed, not plaintext
        assert len(user.password_hash) > 0


def test_password_verification(app):
    """Test password verification"""
    with app.app_context():
        user = User(username='testuser')
        password = 'SecurePassword123'
        
        # Set password
        user.set_password(password)
        
        # Verify correct password
        assert user.check_password(password) is True
        
        # Verify incorrect password
        assert user.check_password('WrongPassword') is False


def test_password_hash_uniqueness(app):
    """Test that same password generates different hashes (due to salt)"""
    with app.app_context():
        user1 = User(username='user1')
        user2 = User(username='user2')
        password = 'SamePassword123'
        
        user1.set_password(password)
        user2.set_password(password)
        
        # Hashes should be different due to different salts
        assert user1.password_hash != user2.password_hash
        
        # But both should verify correctly
        assert user1.check_password(password) is True
        assert user2.check_password(password) is True


def test_user_repr(app):
    """Test user string representation"""
    with app.app_context():
        user = User(username='admin')
        assert repr(user) == '<User admin>'
