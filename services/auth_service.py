"""Authentication service for user login and session management"""
from functools import wraps
from datetime import datetime
from flask import redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from models.user import User
from extensions import db


class AuthService:
    """Service class for handling authentication operations"""
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate an admin user with username and password.
        
        This method ONLY authenticates admin users using the User model.
        Client credentials (Client model) will NOT work here.
        
        Args:
            username (str): The username to authenticate
            password (str): The password to verify
            
        Returns:
            User | None: The authenticated User object if successful, None otherwise
        """
        if not username or not password:
            return None
        
        # Check if any users exist in the database
        user_count = User.query.count()
        if user_count == 0:
            # No users exist - create default admin user
            try:
                admin = User(
                    username='admin',
                    full_name='Administrator'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # If creation fails, continue with authentication attempt
                pass
        
        # Only query User model - client credentials will not work
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Update last login timestamp
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        
        return None
    
    @staticmethod
    def create_session(user):
        """
        Create a login session for the authenticated user.
        
        Args:
            user (User): The user object to create a session for
        """
        login_user(user)
    
    @staticmethod
    def destroy_session():
        """
        Destroy the current user session (logout).
        """
        logout_user()
    
    @staticmethod
    def require_login(func):
        """
        Decorator to require authentication for a route.
        
        Usage:
            @app.route('/protected')
            @AuthService.require_login
            def protected_route():
                return "Protected content"
        
        Args:
            func: The function to wrap
            
        Returns:
            The wrapped function that checks authentication
        """
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Kailangan mong mag-login para ma-access ang page na ito.', 'warning')
                return redirect(url_for('auth.login'))
            return func(*args, **kwargs)
        return decorated_function
