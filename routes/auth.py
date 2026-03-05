"""Authentication routes for login and logout"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.auth_service import AuthService

# Create blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    GET: Display login form
    POST: Process login credentials and authenticate user
    
    Requirements: 1.1, 1.2
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Authenticate user
        user = AuthService.authenticate_user(username, password)
        
        if user:
            # Create session and redirect to dashboard
            AuthService.create_session(user)
            flash(f'Maligayang pagdating, {user.full_name}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            # Authentication failed
            flash('Mali ang username o password. Subukan ulit.', 'error')
    
    # Display login form (GET request or failed POST)
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """
    Handle user logout.
    
    Clear session and redirect to login page.
    
    Requirements: 1.4
    """
    AuthService.destroy_session()
    flash('Matagumpay na nag-logout. Hanggang sa muli!', 'info')
    return redirect(url_for('auth.login'))
