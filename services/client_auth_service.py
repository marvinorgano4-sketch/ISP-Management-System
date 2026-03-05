"""Client authentication service for client portal login and session management"""
from functools import wraps
from datetime import datetime
from flask import session, redirect, url_for, flash
from models.client import Client
from extensions import db


class ClientAuthService:
    """Service class for handling client authentication operations"""
    
    @staticmethod
    def authenticate_client_by_username(pppoe_username: str) -> Client | None:
        """
        Authenticate a client using only PPPoE username (no password required).
        
        This method authenticates clients using ONLY the username.
        Admin credentials (User model) will NOT work here.
        
        Args:
            pppoe_username (str): The PPPoE username to authenticate
            
        Returns:
            Client | None: The authenticated Client object if successful, None otherwise
            
        Raises:
            ValueError: If username is empty or account is inactive
        """
        if not pppoe_username:
            raise ValueError('Please enter your account number.')
        
        # Only query Client model - admin User credentials will not work
        client = Client.query.filter_by(pppoe_username=pppoe_username).first()
        
        if not client:
            return None
        
        # Check if account is active
        if client.status != 'active':
            raise ValueError('Your account is currently inactive. Please contact support.')
        
        # Update last login timestamp
        client.last_login = datetime.utcnow()
        db.session.commit()
        return client
    
    @staticmethod
    def authenticate_client(pppoe_username: str, password: str) -> Client | None:
        """
        Authenticate a client with PPPoE username and password.
        
        This method ONLY authenticates clients using the Client model.
        Admin credentials (User model) will NOT work here.
        
        Args:
            pppoe_username (str): The PPPoE username to authenticate
            password (str): The password to verify
            
        Returns:
            Client | None: The authenticated Client object if successful, None otherwise
            
        Raises:
            ValueError: If credentials are empty or client account is inactive
        """
        if not pppoe_username or not password:
            raise ValueError('Username at password ay kinakailangan.')
        
        # Only query Client model - admin User credentials will not work
        client = Client.query.filter_by(pppoe_username=pppoe_username).first()
        
        if not client:
            # Don't reveal if username exists (security best practice)
            return None
        
        # Check if account is inactive
        if client.status == 'inactive':
            raise ValueError('Ang iyong account ay kasalukuyang inactive. Makipag-ugnayan sa support.')
        
        if client.check_password(password):
            # Update last login timestamp
            client.last_login = datetime.utcnow()
            db.session.commit()
            return client
        
        return None
    
    @staticmethod
    def create_client_session(client: Client) -> None:
        """
        Create a login session for the authenticated client.
        
        Regenerates session ID to prevent session fixation attacks.
        
        Args:
            client (Client): The client object to create a session for
        """
        # Regenerate session ID to prevent session fixation attacks
        # session.clear() removes all data and forces Flask to create a new session ID
        session.clear()
        
        # Mark session as modified to ensure new session ID is generated
        session.modified = True
        
        # Store client information in session
        session['client_id'] = client.id
        session['client_username'] = client.pppoe_username
        session['login_time'] = datetime.utcnow().isoformat()
        session['last_activity'] = datetime.utcnow().isoformat()
        session.permanent = True  # Enable session timeout
    
    @staticmethod
    def destroy_client_session() -> None:
        """
        Destroy the current client session (logout).
        """
        session.pop('client_id', None)
        session.pop('client_username', None)
        session.pop('login_time', None)
        session.pop('last_activity', None)
    
    @staticmethod
    def get_current_client() -> Client | None:
        """
        Get the currently authenticated client from the session.
        
        Returns:
            Client | None: The authenticated Client object if session is valid, None otherwise
        """
        client_id = session.get('client_id')
        
        if not client_id:
            return None
        
        # Check session timeout (30 minutes)
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            time_diff = (datetime.utcnow() - last_activity_time).total_seconds()
            
            # Session timeout: 30 minutes (1800 seconds)
            if time_diff > 1800:
                ClientAuthService.destroy_client_session()
                flash('Nag-expire na ang iyong session. Mag-login ulit.', 'warning')
                return None
        
        # Update last activity timestamp
        session['last_activity'] = datetime.utcnow().isoformat()
        
        # Fetch and return the client
        return Client.query.get(client_id)
    
    @staticmethod
    def require_client_login(func):
        """
        Decorator to require client authentication for a route.
        
        Usage:
            @app.route('/client/dashboard')
            @ClientAuthService.require_client_login
            def client_dashboard():
                return "Client dashboard content"
        
        Args:
            func: The function to wrap
            
        Returns:
            The wrapped function that checks client authentication
        """
        @wraps(func)
        def decorated_function(*args, **kwargs):
            client = ClientAuthService.get_current_client()
            
            if not client:
                flash('Kailangan mong mag-login para ma-access ang page na ito.', 'warning')
                return redirect(url_for('client_portal.login'))
            
            return func(*args, **kwargs)
        
        return decorated_function
