"""GCash payment service for generating payment links"""
from datetime import datetime
from urllib.parse import urlencode
from models.billing import Billing


class GCashPaymentService:
    """Service class for handling GCash payment link generation"""
    
    GCASH_NUMBER = "09495502589"
    GCASH_NAME = "Jean Kimberlyn L"
    
    @staticmethod
    def generate_payment_link(billing_id: int) -> str:
        """
        Generate a GCash payment deep link with pre-filled payment details.
        
        Args:
            billing_id (int): The billing record ID
            
        Returns:
            str: GCash payment URL with pre-filled details
            
        Raises:
            ValueError: If billing record not found, already paid, or has invalid amount
        """
        # Fetch the billing record
        billing = Billing.query.get(billing_id)
        
        if not billing:
            raise ValueError('Hindi nahanap ang billing record.')
        
        if billing.status == 'paid':
            raise ValueError('Ang billing record ay paid na.')
        
        # Validate amount
        if billing.amount <= 0:
            raise ValueError('Invalid na payment amount.')
        
        # Generate reference number
        reference = GCashPaymentService.generate_reference_number(
            billing.client_id, 
            billing_id
        )
        
        # Build GCash deep link URL
        params = {
            'number': GCashPaymentService.GCASH_NUMBER,
            'name': GCashPaymentService.GCASH_NAME,
            'amount': f"{billing.amount:.2f}",
            'reference': reference
        }
        
        gcash_url = f"gcash://pay?{urlencode(params)}"
        
        return gcash_url
    
    @staticmethod
    def generate_reference_number(client_id: int, billing_id: int) -> str:
        """
        Generate a unique payment reference number.
        
        Format: CLIENT{client_id}-BILL{billing_id}-{timestamp}
        
        Args:
            client_id (int): The client ID
            billing_id (int): The billing record ID
            
        Returns:
            str: Unique reference number
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        reference = f"CLIENT{client_id}-BILL{billing_id}-{timestamp}"
        
        return reference
