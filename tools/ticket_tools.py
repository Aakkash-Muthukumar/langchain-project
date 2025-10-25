"""
Ticket Management Tools

Tools for creating and managing support tickets
"""

from typing import Dict, Any
import json
from datetime import datetime


def create_ticket(
    title: str,
    description: str,
    priority: str = "medium",
    category: str = "general"
) -> str:
    """
    Create a support ticket for human agents
    
    Args:
        title: Ticket title
        description: Detailed description
        priority: Priority level (low, medium, high, critical)
        category: Ticket category
        
    Returns:
        Ticket creation confirmation with ID
    """
    ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    ticket_data = {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "assigned_to": None
    }
    
    return json.dumps(ticket_data)


def assign_to_human(ticket_id: str, agent_name: str = "next_available") -> str:
    """
    Assign ticket to a human support agent
    
    Args:
        ticket_id: Ticket identifier
        agent_name: Name of agent to assign to
        
    Returns:
        Assignment confirmation
    """
    return f"Ticket {ticket_id} assigned to {agent_name}. They will respond within 2 hours."


def update_ticket(ticket_id: str, updates: Dict[str, Any]) -> str:
    """
    Update ticket information
    
    Args:
        ticket_id: Ticket identifier
        updates: Dictionary of fields to update
        
    Returns:
        Update confirmation
    """
    return f"Ticket {ticket_id} updated successfully with changes: {updates}"


def close_ticket(ticket_id: str, resolution: str) -> str:
    """
    Close a support ticket
    
    Args:
        ticket_id: Ticket identifier
        resolution: Resolution summary
        
    Returns:
        Closure confirmation
    """
    return f"Ticket {ticket_id} closed. Resolution: {resolution}"
