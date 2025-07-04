"""
Configuration settings for Letwrk AI Agent
"""

import os
from typing import List

# Team members configuration
TEAM_MEMBERS: List[str] = ["Ravi", "Ankita", "Sam", "Alex", "Maya", "Jordan", "Taylor"]

# Fuzzy matching configuration
FUZZY_MATCH_THRESHOLD: float = 70.0

# OpenAI configuration
DEFAULT_MODEL: str = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE: float = 0.1

# Task configuration
DEFAULT_PRIORITY: str = "medium"
DEFAULT_STATUS: str = "pending"
DEFAULT_DUE_DAYS: int = 7

# Status and priority mappings
STATUS_OPTIONS: List[str] = ["pending", "in_progress", "done"]
PRIORITY_OPTIONS: List[str] = ["high", "medium", "low"]

# Emoji mappings
STATUS_EMOJIS: dict = {
    "pending": "⏳",
    "in_progress": "🔄", 
    "done": "✅"
}

PRIORITY_EMOJIS: dict = {
    "high": "🔥",
    "medium": "📋",
    "low": "📝"
}

# Meeting analysis patterns
MEETING_INDICATORS: List[str] = [
    r'from.*?(?:this\s+)?meeting.*?create.*?tasks?',
    r'meeting\s+summary.*?create.*?tasks?',
    r'create.*?tasks?.*?from.*?meeting',
    r'break.*?down.*?into.*?tasks?',
    r'actionable.*?items?.*?from',
    r'MEETING\s+SUMMARY',
    r'DEMO\s+MEETING',
    r'meeting.*?notes'
]

# Task creation patterns
TASK_INSTRUCTION_PATTERNS: List[str] = [
    r'^.*?create\s+(?:a\s+)?(?:new\s+)?task\s*(?:called\s+|named\s+|titled\s+|:\s*)',
    r'^.*?add\s+(?:a\s+)?(?:new\s+)?task\s*(?:called\s+|named\s+|titled\s+|:\s*)',
    r'^.*?new\s+task\s*(?:called\s+|named\s+|titled\s+|for\s+|:\s*)',
    r'^.*?task\s*(?:called\s+|named\s+|titled\s+|:\s*)',
]

# Status update patterns
STATUS_PATTERNS: List[tuple] = [
    (r'\b(done|completed|finished)\b', 'done'),
    (r'\b(pending|todo|waiting)\b', 'pending'),
    (r'\b(in[_\s]progress|working|started)\b', 'in_progress')
]

# Bulk operation patterns
BULK_UNASSIGN_PATTERNS: List[str] = [
    r'\bunassign.*?all.*?tasks?\b',
    r'\bmake.*?all.*?tasks?.*?unassigned\b',
    r'\bremove.*?assignees?.*?from.*?all.*?tasks?\b',
    r'\ball.*?tasks?.*?unassigned\b'
]

# Keyword-based task suggestions
KEYWORD_TASKS: dict = {
    r'demo|demonstration': 'Prepare demo presentation',
    r'integration|connect': 'Set up integrations',
    r'dashboard|overview': 'Design dashboard overview',
    r'problem|solution': 'Document problem and solution',
    r'walkthrough|tutorial': 'Create walkthrough guide',
    r'documentation|docs': 'Update documentation',
    r'testing|test': 'Conduct testing',
    r'meeting|presentation': 'Schedule follow-up meeting'
} 