"""ISP Billing System - Main Application"""
from flask import Flask, session, request, abort
from config import Config
from extensions import db, login_manager, migrate, csrf
import logging
import os

logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure Flask-Login user loader
    from models import User, Client, Billing, Payment, Receipt
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.clients import clients_bp
    from routes.billing import billing_bp
    from routes.payments import payments_bp
    from routes.receipts import receipts_bp
    from routes.client_portal import client_portal_bp
    from routes.bandwidth import bandwidth_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(clients_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(client_portal_bp)
    app.register_blueprint(bandwidth_bp)
    
    # Add root route redirect
    @app.route('/')
    def index():
        """Redirect root URL to login page"""
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # Add database initialization endpoint (for debugging)
    @app.route('/init-db')
    def init_database():
        """Initialize database - for debugging only"""
        try:
            db.create_all()
            
            # Check if admin exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    full_name='Administrator',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                return "Database initialized! Admin user created (username: admin, password: admin123)"
            else:
                return "Database already initialized. Admin user exists."
        except Exception as e:
            return f"Error initializing database: {str(e)}"
    
    # Add middleware to prevent clients from accessing admin routes
    @app.before_request
    def check_client_access_to_admin_routes():
        """
        Prevent clients from accessing admin routes.
        
        If a client session is active (client_id in session) and the user
        tries to access an admin route (not starting with /client/), 
        deny access and log the attempt.
        
        Requirements: 10.2, 10.4
        """
        # Check if this is a client session
        client_id = session.get('client_id')
        
        # If no client session, allow the request (admin or unauthenticated)
        if not client_id:
            return None
        
        # Define admin route prefixes (routes that clients should not access)
        admin_prefixes = [
            '/dashboard',
            '/clients',
            '/billing',
            '/payments',
            '/receipts',
            '/admin'
        ]
        
        # Check if the request path starts with any admin prefix
        for prefix in admin_prefixes:
            if request.path.startswith(prefix):
                # Log the unauthorized access attempt
                client_username = session.get('client_username', 'unknown')
                logger.warning(
                    f"Unauthorized access attempt: Client '{client_username}' "
                    f"(ID: {client_id}) tried to access admin route: {request.path}"
                )
                
                # Return 403 Forbidden
                abort(403, description="Wala kang permission na mag-access ng admin routes.")
        
        # Allow the request if it's not an admin route
        return None
    
    # Initialize database on first run
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check if admin user exists, create if not
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    full_name='Administrator',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                logger.info("Default admin user created (username: admin, password: admin123)")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    return app

# Create app instance for production servers (gunicorn, etc.)
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)