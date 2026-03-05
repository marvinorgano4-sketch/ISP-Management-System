"""Receipt generation routes"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from services.receipt_service import ReceiptService

# Create blueprint for receipt routes
receipts_bp = Blueprint('receipts', __name__, url_prefix='/receipts')


@receipts_bp.route('/<int:receipt_id>')
@login_required
def view_receipt(receipt_id):
    """
    View receipt in printable format.
    
    Requirements: 6.3, 8.4
    """
    # Get receipt
    receipt = ReceiptService.get_receipt(receipt_id)
    if not receipt:
        flash('Hindi nahanap ang receipt.', 'error')
        return redirect(url_for('payments.list_payments'))
    
    return render_template('receipts/receipt.html', receipt=receipt)
