"""
Database Tools

Tools for querying customer data and history
"""

from typing import Dict, Any, List
import json


def query_customer_history(customer_id: str) -> Dict[str, Any]:
    """
    Query customer's interaction history and account information
    
    Args:
        customer_id: Unique customer identifier
        
    Returns:
        Dictionary containing customer history and account details
    """
    # Simulated database query
    mock_data = {
        "customer_id": customer_id,
        "account_status": "active",
        "subscription_tier": "premium",
        "previous_interactions": [
            {"date": "2025-10-20", "type": "technical", "resolved": True},
            {"date": "2025-10-15", "type": "billing", "resolved": True}
        ],
        "total_tickets": 5,
        "satisfaction_score": 4.5
    }
    
    return json.dumps(mock_data)


def get_customer_info(customer_id: str) -> str:
    """
    Get basic customer information
    
    Args:
        customer_id: Customer identifier
        
    Returns:
        JSON string with customer info
    """
    mock_info = {
        "id": customer_id,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0123",
        "account_created": "2024-01-15",
        "last_login": "2025-10-24"
    }
    
    return json.dumps(mock_info)


def update_customer_record(customer_id: str, updates: Dict[str, Any]) -> str:
    """
    Update customer record in database
    
    Args:
        customer_id: Customer identifier
        updates: Dictionary of fields to update
        
    Returns:
        Success message
    """
    return f"Successfully updated customer {customer_id} with changes: {updates}"
