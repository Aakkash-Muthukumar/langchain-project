"""
Billing Tools

Tools for managing billing, payments, and subscriptions
"""

from typing import Dict, Any
import json


def query_billing_history(customer_id: str, months: int = 6) -> str:
    """
    Query customer's billing and payment history
    
    Args:
        customer_id: Customer identifier
        months: Number of months to retrieve
        
    Returns:
        JSON string with billing history
    """
    mock_history = {
        "customer_id": customer_id,
        "transactions": [
            {
                "date": "2025-10-01",
                "amount": 29.99,
                "description": "Monthly subscription - Premium",
                "status": "completed"
            },
            {
                "date": "2025-09-01",
                "amount": 29.99,
                "description": "Monthly subscription - Premium",
                "status": "completed"
            },
            {
                "date": "2025-08-01",
                "amount": 29.99,
                "description": "Monthly subscription - Premium",
                "status": "completed"
            }
        ],
        "total_spent": 179.94,
        "payment_method": "Visa ending in 1234"
    }
    
    return json.dumps(mock_history)


def process_refund(transaction_id: str, amount: float, reason: str) -> str:
    """
    Process a refund for a customer
    
    Args:
        transaction_id: Transaction to refund
        amount: Refund amount
        reason: Reason for refund
        
    Returns:
        Refund confirmation
    """
    return f"Refund processed: ${amount:.2f} for transaction {transaction_id}. Reason: {reason}. Funds will appear in 5-7 business days."


def update_subscription(customer_id: str, plan: str) -> str:
    """
    Update or modify customer subscription
    
    Args:
        customer_id: Customer identifier
        plan: New plan name (e.g., 'basic', 'premium', 'enterprise')
        
    Returns:
        Update confirmation
    """
    return f"Subscription updated for customer {customer_id} to '{plan}' plan. Changes will take effect immediately."


def cancel_subscription(customer_id: str, reason: str = None) -> str:
    """
    Cancel customer subscription
    
    Args:
        customer_id: Customer identifier
        reason: Optional cancellation reason
        
    Returns:
        Cancellation confirmation
    """
    message = f"Subscription cancelled for customer {customer_id}. Access will continue until end of billing period."
    if reason:
        message += f" Reason: {reason}"
    return message


def apply_discount(customer_id: str, discount_code: str) -> str:
    """
    Apply discount code to customer account
    
    Args:
        customer_id: Customer identifier
        discount_code: Discount code to apply
        
    Returns:
        Discount confirmation
    """
    return f"Discount code '{discount_code}' applied to customer {customer_id}. 20% off for 3 months."
