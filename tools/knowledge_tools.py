"""
Knowledge Base Tools

Tools for searching documentation and knowledge articles
"""

from typing import List, Dict
import json


def search_knowledge_base(query: str) -> str:
    """
    Search the knowledge base for relevant articles and documentation
    
    Args:
        query: Search query string
        
    Returns:
        JSON string containing relevant articles
    """
    # Simulated knowledge base search
    mock_articles = [
        {
            "id": "KB001",
            "title": "Common Login Issues",
            "summary": "Troubleshooting guide for login problems",
            "url": "https://kb.example.com/login-issues",
            "relevance": 0.95
        },
        {
            "id": "KB002",
            "title": "Password Reset Guide",
            "summary": "Step-by-step password reset instructions",
            "url": "https://kb.example.com/password-reset",
            "relevance": 0.87
        },
        {
            "id": "KB003",
            "title": "Account Security Best Practices",
            "summary": "Security recommendations for your account",
            "url": "https://kb.example.com/security",
            "relevance": 0.73
        }
    ]
    
    return json.dumps(mock_articles)


def get_article_content(article_id: str) -> str:
    """
    Get full content of a knowledge base article
    
    Args:
        article_id: Unique article identifier
        
    Returns:
        Full article content
    """
    mock_content = f"""
    Article ID: {article_id}
    
    Title: Troubleshooting Guide
    
    Content: This article provides detailed steps to resolve common issues...
    
    Step 1: Check your internet connection
    Step 2: Clear browser cache
    Step 3: Try a different browser
    """
    
    return mock_content
