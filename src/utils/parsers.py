"""
Parsing utilities for Letwrk AI Agent
"""

import re
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from src.config.settings import (
    TASK_INSTRUCTION_PATTERNS, 
    STATUS_PATTERNS, 
    BULK_UNASSIGN_PATTERNS,
    MEETING_INDICATORS,
    KEYWORD_TASKS
)


def parse_task_creation_input(task_description: str) -> Dict[str, Any]:
    """
    Parse task creation input to extract title, assignee, priority, and due date.
    
    Returns:
        Dictionary with parsed task information
    """
    title = task_description
    assignee = "unassigned"
    priority = "medium"
    due_date = None
    
    # Extract task name from quotes first (highest priority)
    quoted_task_patterns = [
        r"'([^']+)'",  # Single quotes
        r'"([^"]+)"'   # Double quotes
    ]
    
    for pattern in quoted_task_patterns:
        quote_match = re.search(pattern, task_description)
        if quote_match:
            title = quote_match.group(1).strip()
            break
    
    # If no quotes found, clean up common instruction phrases
    if title == task_description:  # No quotes were found
        # Handle rename operations specifically
        rename_match = re.search(r'rename\s+.*?\s+to\s+(.+)', title, re.IGNORECASE)
        if rename_match:
            title = rename_match.group(1).strip()
        else:
            # Remove common task creation phrases
            for pattern in TASK_INSTRUCTION_PATTERNS:
                new_title = re.sub(pattern, '', title, flags=re.IGNORECASE).strip()
                if new_title and new_title != title:  # If something was removed and we have content
                    title = new_title
                    break
    
    # Extract assignee
    assignee_match = re.search(r'\bfor\s+(\w+)', task_description, re.IGNORECASE)
    if assignee_match:
        assignee = assignee_match.group(1)
        # Clean the assignee from title
        title = re.sub(r'\s+for\s+\w+', '', title, flags=re.IGNORECASE)
    
    # Extract priority
    priority_match = re.search(r'\b(high|medium|low)\s+priority\b', task_description, re.IGNORECASE)
    if priority_match:
        priority = priority_match.group(1).lower()
        title = re.sub(r'\s+with\s+(high|medium|low)\s+priority', '', title, flags=re.IGNORECASE)
    
    # Extract due date
    due_match = re.search(r'\bdue\s+([0-9-]+)', task_description, re.IGNORECASE)
    if due_match:
        due_date = due_match.group(1)
        title = re.sub(r'\s+due\s+[0-9-]+', '', title, flags=re.IGNORECASE)
    else:
        # Default due date (7 days from now)
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Final cleanup of title
    title = title.strip()
    title = re.sub(r'^(to\s+)?', '', title, flags=re.IGNORECASE)  # Remove leading "to"
    title = re.sub(r'[\'"]*$', '', title)  # Remove trailing quotes
    title = re.sub(r'^[\'"]*', '', title)  # Remove leading quotes
    title = title.strip()
    
    return {
        'title': title,
        'assignee': assignee,
        'priority': priority,
        'due_date': due_date
    }


def parse_task_update_input(update_description: str) -> Dict[str, Any]:
    """
    Parse task update input to extract task ID and update information.
    
    Returns:
        Dictionary with parsed update information
    """
    # Check for "all tasks" operations first
    if re.search(r'\ball\s+tasks?\b', update_description, re.IGNORECASE):
        return {'is_bulk': True, 'operation': update_description}
    
    # Extract task ID for single task operations
    task_id_match = re.search(r'\btask\s+(\d+)', update_description, re.IGNORECASE)
    if not task_id_match:
        return {'error': 'Please specify the task ID (e.g., "task 2") or use "all tasks" for bulk operations.'}
    
    task_id = int(task_id_match.group(1))
    
    # Check for status update
    for pattern, status in STATUS_PATTERNS:
        if re.search(pattern, update_description, re.IGNORECASE):
            return {'task_id': task_id, 'update_type': 'status', 'new_value': status}
    
    # Check for unassigning operations
    unassign_patterns = [
        r'\bunassign.*?task\s+' + str(task_id) + r'\b',
        r'\btask\s+' + str(task_id) + r'.*?unassign',
        r'\bremove.*?assignee.*?from.*?task\s+' + str(task_id) + r'\b'
    ]
    
    for pattern in unassign_patterns:
        if re.search(pattern, update_description, re.IGNORECASE):
            return {'task_id': task_id, 'update_type': 'assignee', 'new_value': 'unassigned'}
    
    # Check for assignee update
    assign_match = re.search(r'\bassign.*?to\s+(\w+)', update_description, re.IGNORECASE)
    if assign_match:
        potential_assignee = assign_match.group(1)
        return {'task_id': task_id, 'update_type': 'assignee', 'new_value': potential_assignee}
    
    return {'error': f'I couldn\'t understand what you want to update for Task {task_id}.'}


def parse_bulk_update_input(update_description: str) -> Dict[str, Any]:
    """
    Parse bulk update input to determine the operation type.
    
    Returns:
        Dictionary with parsed bulk operation information
    """
    # Check for unassigning operations first
    for pattern in BULK_UNASSIGN_PATTERNS:
        if re.search(pattern, update_description, re.IGNORECASE):
            return {'operation': 'unassign_all'}
    
    # Check for bulk assignee update
    assign_match = re.search(r'\bassign.*?all.*?tasks?.*?to\s+(\w+)', update_description, re.IGNORECASE)
    if assign_match:
        potential_assignee = assign_match.group(1)
        return {'operation': 'assign_all', 'assignee': potential_assignee}
    
    # Check for bulk status update
    for pattern, status in STATUS_PATTERNS:
        if re.search(pattern, update_description, re.IGNORECASE):
            return {'operation': 'status_all', 'status': status}
    
    return {'error': 'I couldn\'t understand the bulk operation.'}


def is_meeting_content(content: str) -> bool:
    """Check if the content appears to be meeting content that needs task breakdown"""
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in MEETING_INDICATORS)


def parse_meeting_content(meeting_description: str) -> str:
    """Extract the actual meeting content from the instruction"""
    content = meeting_description
    
    # Remove the instruction part to get just the meeting content
    instruction_patterns = [
        r'^.*?from.*?(?:this\s+)?meeting.*?create.*?tasks?[:\s]*',
        r'^.*?meeting\s+summary.*?create.*?tasks?[:\s]*',
        r'^.*?create.*?tasks?.*?from.*?meeting[:\s]*',
        r'^.*?break.*?down.*?into.*?tasks?[:\s]*'
    ]
    
    for pattern in instruction_patterns:
        new_content = re.sub(pattern, '', content, flags=re.IGNORECASE).strip()
        if new_content != content:
            content = new_content
            break
    
    return content


def parse_task_selection(selection: str, max_tasks: int) -> Optional[list[int]]:
    """
    Parse task selection input (e.g., '1,3,5' or '1-3' or 'all').
    
    Returns:
        List of selected task indices or None if invalid
    """
    selection = selection.lower().strip()
    
    if selection in ['none', 'cancel', 'no']:
        return []
    
    if selection in ['all', 'yes', 'create all']:
        return list(range(max_tasks))
    
    # Parse specific numbers/ranges
    selected_indices = []
    parts = selection.replace(' ', '').split(',')
    
    for part in parts:
        if '-' in part and part.count('-') == 1:
            # Range like "1-3"
            start, end = part.split('-')
            try:
                start_idx = int(start) - 1  # Convert to 0-based index
                end_idx = int(end)
                selected_indices.extend(range(start_idx, end_idx))
            except ValueError:
                continue
        else:
            # Single number
            try:
                idx = int(part) - 1  # Convert to 0-based index
                selected_indices.append(idx)
            except ValueError:
                continue
    
    # Remove duplicates and invalid indices
    selected_indices = list(set(i for i in selected_indices if 0 <= i < max_tasks))
    
    return selected_indices if selected_indices else None 