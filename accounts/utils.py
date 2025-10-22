import requests
import uuid
from django.conf import settings
from decimal import Decimal


def generate_payment_reference():
    """Generate a unique payment reference for Paystack transactions."""
    return f"TXN_{uuid.uuid4().hex[:12].upper()}"


def verify_paystack_transaction(reference, secret_key):
    """
    Verify a Paystack transaction using the API.
    
    Args:
        reference (str): The transaction reference from Paystack
        secret_key (str): Paystack secret key
        
    Returns:
        dict: API response or None if verification fails
    """
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Paystack verification error: {e}")
        return None


def calculate_outstanding_balance(lease):
    """
    Calculate the outstanding service charge balance for a lease.
    
    Args:
        lease: Lease object
        
    Returns:
        Decimal: Outstanding balance amount
    """
    if not lease:
        return Decimal('0.00')
    
    # Get total service charge amount (assuming monthly charges)
    # This is a simplified calculation - you might want to make it more sophisticated
    total_charges = lease.service_charge
    
    # Get total payments made
    total_payments = sum(payment.amount for payment in lease.payments.all())
    
    # Calculate outstanding balance
    outstanding = total_charges - total_payments
    
    return max(outstanding, Decimal('0.00'))


def get_paystack_public_key():
    """Get Paystack public key from settings."""
    return settings.PAYSTACK_PUBLIC_KEY


def get_paystack_secret_key():
    """Get Paystack secret key from settings."""
    return settings.PAYSTACK_SECRET_KEY
