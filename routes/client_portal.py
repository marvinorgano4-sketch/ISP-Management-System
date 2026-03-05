"""Client portal routes for client self-service"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.client_auth_service import ClientAuthService
from services.client_dashboard_service import ClientDashboardService
from services.gcash_payment_service import GCashPaymentService
from services.billing_service import BillingService
from services.payment_service import PaymentService
from services.receipt_service import ReceiptService
from models.billing import Billing
from models.payment import Payment
from models.receipt import Receipt

# Create blueprint for client portal routes
client_portal_bp = Blueprint('client_portal', __name__, url_prefix='/client')


@client_portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle client login.
    
    GET: Display client login form
    POST: Process login credentials and authenticate client
    
    Requirements: 1.1, 1.2, 1.3
    """
    if request.method == 'POST':
        pppoe_username = request.form.get('pppoe_username', '').strip()
        
        try:
            # Authenticate client using username only (no password required)
            client = ClientAuthService.authenticate_client_by_username(pppoe_username)
            
            if client:
                # Create session and redirect to dashboard
                ClientAuthService.create_client_session(client)
                flash(f'Welcome, {client.full_name}!', 'success')
                return redirect(url_for('client_portal.dashboard'))
            else:
                # Authentication failed
                flash('Invalid account number. Please try again.', 'error')
                
        except ValueError as e:
            # Handle specific errors (empty username, inactive account)
            flash(str(e), 'error')
        except Exception as e:
            # Handle unexpected errors
            flash('An error occurred during login. Please try again later.', 'error')
    
    # Display login form (GET request or failed POST)
    return render_template('client_login.html')


@client_portal_bp.route('/logout')
def logout():
    """
    Handle client logout.
    
    Clear client session and redirect to login page.
    
    Requirements: 1.6
    """
    ClientAuthService.destroy_client_session()
    flash('Matagumpay na nag-logout. Hanggang sa muli!', 'info')
    return redirect(url_for('client_portal.login'))


@client_portal_bp.route('/dashboard')
@ClientAuthService.require_client_login
def dashboard():
    """
    Display client dashboard with account summary.
    
    Shows:
    - Remaining days until next payment
    - Total unpaid balance
    - Connection status
    - Plan details
    - Recent bills and payments
    
    Requirements: 1.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
    """
    # Get current client
    client = ClientAuthService.get_current_client()
    
    try:
        # Get dashboard data
        dashboard_data = ClientDashboardService.get_dashboard_data(client.id)
        
        # Show warning if connection status has error
        if dashboard_data['connection_status'].get('error'):
            flash(dashboard_data['connection_status']['error'], 'warning')
        
        return render_template('client_dashboard.html', dashboard_data=dashboard_data)
    except Exception as e:
        # Log the error and show user-friendly message
        flash('An error occurred while loading the dashboard. Please try again later.', 'error')
        return redirect(url_for('client_portal.login'))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('client_portal.login'))
    except Exception as e:
        flash('May nangyaring error sa pag-load ng dashboard. Subukan ulit mamaya.', 'error')
        return redirect(url_for('client_portal.login'))


@client_portal_bp.route('/bills')
@ClientAuthService.require_client_login
def bills():
    """
    Display list of client's billing records.
    
    Supports filtering by status (all, unpaid, paid, overdue).
    
    Requirements: 1.5, 4.1, 4.2, 4.3, 4.4
    """
    # Get current client
    client = ClientAuthService.get_current_client()
    
    # Get status filter
    status_filter = request.args.get('status', '')
    
    # Build filters
    filters = {'client_id': client.id}
    if status_filter:
        filters['status'] = status_filter
    
    # Get bills for this client only
    bills = BillingService.get_all_bills(filters)
    
    return render_template('client_bills.html', 
                         bills=bills,
                         status_filter=status_filter)


@client_portal_bp.route('/bills/<int:billing_id>')
@ClientAuthService.require_client_login
def bill_detail(billing_id):
    """
    Display detailed view of a specific billing record.
    
    Access control: Client can only view their own bills.
    
    Requirements: 1.5, 4.4, 4.5
    """
    # Get current client
    client = ClientAuthService.get_current_client()
    
    # Get billing record
    billing = Billing.query.get(billing_id)
    
    if not billing:
        flash('Hindi nahanap ang billing record.', 'error')
        return redirect(url_for('client_portal.bills')), 404
    
    # Access control: Verify this bill belongs to the current client
    if billing.client_id != client.id:
        flash('Wala kang permission na mag-access ng billing record na ito.', 'error')
        return redirect(url_for('client_portal.bills')), 403
    
    return render_template('client_bill_detail.html', billing=billing)


@client_portal_bp.route('/bills/<int:billing_id>/pay')
@ClientAuthService.require_client_login
def pay_bill(billing_id):
    """
    Generate GCash payment link and redirect to GCash.
    
    Access control: Client can only pay their own bills.
    
    Requirements: 1.5, 4.4, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
    """
    # Get current client
    client = ClientAuthService.get_current_client()
    
    # Get billing record
    billing = Billing.query.get(billing_id)
    
    if not billing:
        flash('Hindi nahanap ang billing record.', 'error')
        return redirect(url_for('client_portal.bills')), 404
    
    # Access control: Verify this bill belongs to the current client
    if billing.client_id != client.id:
        flash('Wala kang permission na mag-access ng billing record na ito.', 'error')
        return redirect(url_for('client_portal.bills')), 403
    
    try:
        # Generate GCash payment link
        payment_link = GCashPaymentService.generate_payment_link(billing_id)
        
        # Redirect to GCash
        return redirect(payment_link)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('client_portal.bill_detail', billing_id=billing_id))
    except Exception as e:
        flash(f'Error sa pag-generate ng payment link: {str(e)}', 'error')
        return redirect(url_for('client_portal.bill_detail', billing_id=billing_id))


@client_portal_bp.route('/payments')
@ClientAuthService.require_client_login
def payments():
    """
    Display list of client's payment records.
    
    Sorted by payment date in descending order.
    
    Requirements: 1.5, 6.1, 6.2, 6.3, 6.4
    """
    # Get current client
    client = ClientAuthService.get_current_client()
    
    # Get payments for this client only, sorted by date descending
    payments = Payment.query.filter_by(client_id=client.id)\
        .order_by(Payment.payment_date.desc())\
        .all()
    
    return render_template('client_payments.html', payments=payments)


@client_portal_bp.route('/payments/<int:payment_id>')
@ClientAuthService.require_client_login
def payment_detail(payment_id):
    """
    Display detailed view of a specific payment record.
    
    Shows payment details and associated billing information.
    Access control: Client can only view their own payments.
    
    Requirements: 1.5, 6.4, 6.5, 7.1
    """
    # Get current client
    client = ClientAuthService.get_current_client()
    
    # Get payment record
    payment = Payment.query.get(payment_id)
    
    if not payment:
        flash('Hindi nahanap ang payment record.', 'error')
        return redirect(url_for('client_portal.payments')), 404
    
    # Access control: Verify this payment belongs to the current client
    if payment.client_id != client.id:
        flash('Wala kang permission na mag-access ng payment record na ito.', 'error')
        return redirect(url_for('client_portal.payments')), 403
    
    # Get associated billing record
    billing = Billing.query.get(payment.billing_id) if payment.billing_id else None
    
    return render_template('client_payment_detail.html', 
                         payment=payment,
                         billing=billing)


@client_portal_bp.route('/receipts/<int:receipt_id>')
@ClientAuthService.require_client_login
def receipt(receipt_id):
    """
    Display receipt for a payment.
    
    Access control: Client can only view their own receipts.
    
    Requirements: 1.5, 7.1, 7.2, 7.3, 7.4, 7.5
    """
    # Get current client
    client = ClientAuthService.get_current_client()
    
    # Get receipt record
    receipt = Receipt.query.get(receipt_id)
    
    if not receipt:
        flash('Hindi nahanap ang receipt.', 'error')
        return redirect(url_for('client_portal.payments')), 404
    
    # Get associated payment to verify ownership
    payment = Payment.query.get(receipt.payment_id)
    
    if not payment:
        flash('Hindi nahanap ang payment record para sa receipt na ito.', 'error')
        return redirect(url_for('client_portal.payments')), 404
    
    if payment.client_id != client.id:
        flash('Wala kang permission na mag-access ng receipt na ito.', 'error')
        return redirect(url_for('client_portal.payments')), 403
    
    # Get associated billing record
    billing = Billing.query.get(payment.billing_id) if payment.billing_id else None
    
    return render_template('receipts/receipt.html', 
                         receipt=receipt,
                         payment=payment,
                         billing=billing,
                         client=client)
