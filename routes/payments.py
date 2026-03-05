"""Payment processing routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from services.payment_service import PaymentService
from services.billing_service import BillingService
from services.receipt_service import ReceiptService

# Create blueprint for payment routes
payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


@payments_bp.route('/')
@login_required
def list_payments():
    """
    Display list of all payments with filters.
    
    Requirements: 5.4
    """
    # Get filters from request
    client_name = request.args.get('client_name', '').strip()
    payment_method = request.args.get('payment_method', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build filters
    filters = {}
    if client_name:
        filters['client_name'] = client_name
    if payment_method:
        filters['payment_method'] = payment_method
    if date_from:
        filters['date_from'] = date_from
    if date_to:
        filters['date_to'] = date_to
    
    # Get payments
    payments = PaymentService.get_all_payments(filters if filters else None)
    
    return render_template('payments/list.html',
                         payments=payments,
                         client_name=client_name,
                         payment_method=payment_method,
                         date_from=date_from,
                         date_to=date_to)


@payments_bp.route('/new', methods=['GET'])
@login_required
def new_payment():
    """
    Display payment form.
    
    Requirements: 5.1, 5.2
    """
    from datetime import datetime
    
    # Get billing_id from query parameter
    billing_id = request.args.get('billing_id', type=int)
    
    billing = None
    if billing_id:
        billing = BillingService.get_billing(billing_id)
        if not billing:
            flash('Hindi nahanap ang billing record.', 'error')
            return redirect(url_for('billing.list_bills'))
    
    return render_template('payments/form.html', billing=billing, now=datetime.now())


@payments_bp.route('/', methods=['POST'])
@login_required
def record_payment():
    """
    Record new payment and generate receipt.
    
    Requirements: 5.1, 5.2, 5.3
    """
    try:
        # Get form data
        billing_id = int(request.form.get('billing_id', 0))
        data = {
            'amount': request.form.get('amount', '0'),
            'payment_date': request.form.get('payment_date', ''),
            'payment_method': request.form.get('payment_method', ''),
            'reference_number': request.form.get('reference_number', '').strip(),
            'notes': request.form.get('notes', '').strip()
        }
        
        # Record payment
        payment = PaymentService.record_payment(billing_id, data)
        
        # Generate receipt
        receipt = ReceiptService.generate_receipt(payment.id)
        
        flash(f'Matagumpay na nag-record ng payment. Receipt No: {receipt.receipt_number}', 'success')
        return redirect(url_for('receipts.view_receipt', receipt_id=receipt.id))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('payments.new_payment', billing_id=request.form.get('billing_id')))
    except Exception as e:
        flash(f'Error sa pag-record ng payment: {str(e)}', 'error')
        return redirect(url_for('payments.new_payment', billing_id=request.form.get('billing_id')))


@payments_bp.route('/<int:payment_id>')
@login_required
def view_payment(payment_id):
    """
    View payment details.
    
    Requirements: 5.4
    """
    # Get payment
    payment = PaymentService.get_payment(payment_id)
    if not payment:
        flash('Hindi nahanap ang payment record.', 'error')
        return redirect(url_for('payments.list_payments'))
    
    return render_template('payments/detail.html', payment=payment)
