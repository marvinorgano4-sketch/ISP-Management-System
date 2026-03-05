"""Tests for authentication routes"""
import pytest
from flask import url_for
from models.user import User
from extensions import db


class TestAuthRoutes:
    """Test authentication routes functionality"""
    
    def test_login_page_loads(self, client):
        """Test that login page loads successfully"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_login_with_valid_credentials(self, client, app):
        """Test login with valid username and password"""
        # Create a test user
        with app.app_context():
            user = User(username='testuser', full_name='Test User')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Attempt login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to index page after successful login
    
    def test_login_with_invalid_credentials(self, client, app, db):
        """Test login with invalid credentials shows error"""
        # Create a test user
        with app.app_context():
            user = User(username='testuser2', full_name='Test User 2')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Attempt login with wrong password
        response = client.post('/login', data={
            'username': 'testuser2',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Mali' in response.data or b'error' in response.data
    
    def test_login_with_empty_credentials(self, client):
        """Test login with empty username and password"""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Mali' in response.data or b'error' in response.data
    
    def test_logout_clears_session(self, client, app, db):
        """Test that logout clears the session"""
        # Create and login a test user
        with app.app_context():
            user = User(username='testuser3', full_name='Test User 3')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Login
        client.post('/login', data={
            'username': 'testuser3',
            'password': 'testpass123'
        })
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to login page
        assert b'login' in response.data.lower()
