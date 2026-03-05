"""Dashboard routes"""
from flask import Blueprint, render_template
from flask_login import login_required
from services.dashboard_service import DashboardService

# Create blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """
    Display dashboard with statistics and overview.
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    # Get statistics
    statistics = DashboardService.get_statistics()
    
    # Get active connections from Mikrotik
    active_connections = DashboardService.get_active_connections()
    
    # Get recent payments
    recent_payments = DashboardService.get_recent_payments(limit=10)
    
    # Get pending bills
    pending_bills = DashboardService.get_pending_bills(limit=10)
    
    return render_template('dashboard.html',
                         statistics=statistics,
                         active_connections=active_connections,
                         recent_payments=recent_payments,
                         pending_bills=pending_bills)
