"""
Formatting utilities for Letwrk AI Agent
"""

from typing import List
from src.models.task import Task
from src.config.settings import STATUS_EMOJIS, PRIORITY_EMOJIS


def format_task_display(task: Task) -> str:
    """Format a single task for display"""
    status_emoji = STATUS_EMOJIS.get(task.status, '📋')
    priority_emoji = PRIORITY_EMOJIS.get(task.priority, '📝')
    
    result = f"{status_emoji} **Task {task.id}**: {task.title}\n"
    result += f"   👤 Assignee: {task.assignee}\n"
    result += f"   {priority_emoji} Priority: {task.priority}\n"
    result += f"   📅 Due: {task.due_date}\n"
    result += f"   Status: {task.status}\n"
    
    return result


def format_tasks_list(tasks: List[Task]) -> str:
    """Format a list of tasks for display"""
    if not tasks:
        return "No tasks found matching your criteria."
    
    result = "Here are the tasks:\n\n"
    for task in tasks:
        result += format_task_display(task) + "\n"
    
    return result


def format_task_creation_result(task: Task) -> str:
    """Format task creation result"""
    return (f"✅ Created new task:\n"
            f"**Task {task.id}**: {task.title}\n"
            f"👤 Assignee: {task.assignee}\n"
            f"🔥 Priority: {task.priority}\n"
            f"📅 Due: {task.due_date}")


def format_task_update_result(task: Task, field: str, old_value: str, new_value: str) -> str:
    """Format task update result"""
    return (f"✅ Updated Task {task.id}: '{task.title}'\n"
            f"{field.capitalize()} changed from '{old_value}' to '{new_value}'")


def format_bulk_update_result(updated_tasks: List[str], operation: str) -> str:
    """Format bulk update result"""
    result = f"✅ {operation} all {len(updated_tasks)} tasks:\n\n"
    for task_update in updated_tasks:
        result += f"  • {task_update}\n"
    return result


def format_fuzzy_match_confirmation(input_name: str, matched_name: str, confidence: float) -> str:
    """Format fuzzy match confirmation message"""
    return (f"Did you mean to assign this task to '{matched_name}'? "
            f"(I interpreted '{input_name}' as '{matched_name}' with {confidence:.0f}% confidence). "
            f"Please confirm or specify the correct name.")


def format_unknown_team_member(name: str, available_members: str) -> str:
    """Format unknown team member error"""
    return (f"I couldn't find a team member named '{name}'. "
            f"Available team members: {available_members}. "
            f"Please specify the correct name.") 