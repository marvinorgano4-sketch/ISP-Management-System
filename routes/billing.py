"""Billing management routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from services.billing_service import BillingService

# Create blueprint for billing routes
billing_bp = Blueprint('billing', __name__, url_prefix='/billing')


@billing_bp.route('/')
@login_required
def list_bills():
    """
    Display list of all bills with filters.
    
    Requirements: 4.3
    """
    # Get filters from request
    status_filter = request.args.get('status', '')
    month_filter = request.args.get('month', '')
    year_filter = request.args.get('year', '')
    client_name = request.args.get('client_name', '').strip()
    
    # Build filters
    filters = {}
    if status_filter:
        filters['status'] = status_filter
    if month_filter:
        filters['month'] = int(month_filter)
    if year_filter:
        filters['year'] = int(year_filter)
    if client_name:
        filters['client_name'] = client_name
    
    # Get bills
    bills = BillingService.get_all_bills(filters if filters else None)
    
    return render_template('billing/list.html', 
                         bills=bills,
                         status_filter=status_filter,
                         month_filter=month_filter,
                         year_filter=year_filter,
                         client_name=client_name)


@billing_bp.route('/generate', methods=['GET'])
@login_required
def generate_form():
    """
    Display generate bills form.
    
    Requirements: 4.1
    """
    from datetime import datetime
    return render_template('billing/generate.html', now=datetime.now())


@billing_bp.route('/generate', methods=['POST'])
@login_required
def generate_bills():
    """
    Generate monthly bills for all active clients.
    
    Requirements: 4.1, 4.2
    """
    try:
        # Get form data
        month = int(request.form.get('month', 0))
        year = int(request.form.get('year', 0))
        
        # Generate bills
        bills = BillingService.generate_monthly_bills(month, year)
        
        flash(f'Matagumpay na nag-generate ng {len(bills)} bills para sa {month}/{year}', 'success')
        return redirect(url_for('billing.list_bills'))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('billing.generate_form'))
    except Exception as e:
        flash(f'Error sa pag-generate ng bills: {str(e)}', 'error')
        return redirect(url_for('billing.generate_form'))


@billing_bp.route('/<int:billing_id>')
@login_required
def view_bill(billing_id):
    """
    View billing details.
    
    Requirements: 4.3
    """
    # Get billing record
    billing = BillingService.get_billing(billing_id)
    if not billing:
        flash('Hindi nahanap ang billing record.', 'error')
        return redirect(url_for('billing.list_bills'))
    
    return render_template('billing/detail.html', billing=billing)
