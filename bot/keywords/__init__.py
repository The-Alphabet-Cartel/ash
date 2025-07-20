"""
Keywords package for Ash Bot Crisis Detection System

This package contains modular keyword files for different crisis levels:
- high_crisis.py: Suicidal ideation, self-harm, immediate danger
- medium_crisis.py: Severe distress, panic attacks, trauma responses  
- low_crisis.py: Depression, anxiety, identity struggles

Each module provides standardized functions for keyword management.
"""

from .high_crisis import get_high_crisis_keywords
from .medium_crisis import get_medium_crisis_keywords  
from .low_crisis import get_low_crisis_keywords

__all__ = [
    'get_high_crisis_keywords',
    'get_medium_crisis_keywords', 
    'get_low_crisis_keywords'
]

def get_all_crisis_keywords():
    """
    Get all keywords from all crisis levels in a single dictionary
    
    Returns:
        dict: Complete keyword structure with crisis levels as top-level keys
    """
    return {
        'high_crisis': get_high_crisis_keywords(),
        'medium_crisis': get_medium_crisis_keywords(),
        'low_crisis': get_low_crisis_keywords()
    }

def get_total_keyword_count():
    """
    Get total count of keywords across all crisis levels
    
    Returns:
        dict: Breakdown of keyword counts by crisis level and total
    """
    from .high_crisis import get_keyword_count as high_count
    from .medium_crisis import get_keyword_count as medium_count
    from .low_crisis import get_keyword_count as low_count
    
    high_stats = high_count()
    medium_stats = medium_count()
    low_stats = low_count()
    
    return {
        'high_crisis': high_stats['total'],
        'medium_crisis': medium_stats['total'],
        'low_crisis': low_stats['total'],
        'total': high_stats['total'] + medium_stats['total'] + low_stats['total']
    }