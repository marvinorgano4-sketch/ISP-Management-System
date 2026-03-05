"""Receipt service for generating payment receipts"""
from datetime import datetime
from models.receipt import Receipt
from models.payment import Payment
from extensions import db


class ReceiptService:
    """Service class for handling receipt operations"""
    
    @staticmethod
    def generate_receipt(payment_id):
        """
        Generate a receipt for a payment.
        
        Args:
            payment_id (int): The payment ID
            
        Returns:
            Receipt: The created receipt object
            
        Raises:
            ValueError: If payment not found or receipt already exists
        """
        # Get payment
        payment = Payment.query.get(payment_id)
        if not payment:
            raise ValueError('Hindi nahanap ang payment record.')
        
        # Check if receipt already exists
        existing_receipt = Receipt.query.filter_by(payment_id=payment_id).first()
        if existing_receipt:
            return existing_receipt
        
        # Generate unique receipt number
        receipt_number = ReceiptService.generate_receipt_number()
        
        # Get client name from payment
        client_name = payment.client.full_name
        
        # Create receipt
        receipt = Receipt(
            payment_id=payment_id,
            receipt_number=receipt_number,
            client_name=client_name,
            amount=payment.amount,
            payment_date=payment.payment_date,
            status='paid'
        )
        
        db.session.add(receipt)
        db.session.flush()  # Get receipt ID
        
        # Update payment with receipt ID
        payment.receipt_id = receipt.id
        
        db.session.commit()
        
        return receipt
    
    @staticmethod
    def get_receipt(receipt_id):
        """
        Get a receipt by ID.
        
        Args:
            receipt_id (int): The receipt ID
            
        Returns:
            Receipt | None: The receipt object if found, None otherwise
        """
        return Receipt.query.get(receipt_id)
    
    @staticmethod
    def get_receipt_by_number(receipt_number):
        """
        Get a receipt by receipt number.
        
        Args:
            receipt_number (str): The receipt number
            
        Returns:
            Receipt | None: The receipt object if found, None otherwise
        """
        return Receipt.query.filter_by(receipt_number=receipt_number).first()
    
    @staticmethod
    def format_for_print(receipt):
        """
        Format receipt data for printing.
        
        Args:
            receipt (Receipt): The receipt object
            
        Returns:
            str: Formatted receipt text
        """
        if not receipt:
            return ""
        
        # Format receipt for thermal printer (300px width)
        formatted = f"""
========================================
      L SECURITY ISP BILLING
========================================

Receipt No: {receipt.receipt_number}
Date: {receipt.payment_date.strftime('%B %d, %Y')}

----------------------------------------
Client: {receipt.client_name}
Amount Paid: ₱{receipt.amount:,.2f}
Status: {receipt.status.upper()}
----------------------------------------

        Thank you for your payment!
        
========================================
        """
        
        return formatted.strip()
    
    @staticmethod
    def generate_receipt_number():
        """
        Generate a unique receipt number in format: LSEC-YYYYMMDD-XXXX
        
        Returns:
            str: Unique receipt number
        """
        # Get current date
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        # Get count of receipts created today
        today_start = datetime(today.year, today.month, today.day)
        today_end = datetime(today.year, today.month, today.day, 23, 59, 59)
        
        count = Receipt.query.filter(
            Receipt.created_at >= today_start,
            Receipt.created_at <= today_end
        ).count()
        
        # Generate sequential number (padded to 4 digits)
        sequence = str(count + 1).zfill(4)
        
        # Format: LSEC-YYYYMMDD-XXXX
        receipt_number = f"LSEC-{date_str}-{sequence}"
        
        # Ensure uniqueness (in case of race condition)
        while Receipt.query.filter_by(receipt_number=receipt_number).first():
            count += 1
            sequence = str(count + 1).zfill(4)
            receipt_number = f"LSEC-{date_str}-{sequence}"
        
        return receipt_number
