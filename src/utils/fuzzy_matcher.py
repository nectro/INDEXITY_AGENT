"""
Fuzzy matching utilities for Letwrk AI Agent
"""

from typing import Optional, Tuple
from rapidfuzz import fuzz, process
from src.config.settings import TEAM_MEMBERS, FUZZY_MATCH_THRESHOLD


def fuzzy_match_name(input_name: str, threshold: float = FUZZY_MATCH_THRESHOLD) -> Tuple[Optional[str], float]:
    """
    Find the best matching team member name using fuzzy matching.
    
    Args:
        input_name: The potentially misspelled name
        threshold: Minimum similarity score to consider a match
        
    Returns:
        Tuple of (best_match, confidence_score)
    """
    if not input_name:
        return None, 0.0
    
    # Check for exact match first
    if input_name in TEAM_MEMBERS:
        return input_name, 100.0
    
    # Use fuzzy matching to find the best match
    result = process.extractOne(input_name, TEAM_MEMBERS, scorer=fuzz.ratio)
    
    if result and result[1] >= threshold:
        return result[0], result[1]
    
    return None, 0.0


def get_available_team_members() -> str:
    """Get formatted string of available team members"""
    return ', '.join(TEAM_MEMBERS)


def is_valid_team_member(name: str) -> bool:
    """Check if a name is a valid team member"""
    return name in TEAM_MEMBERS 