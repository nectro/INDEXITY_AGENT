"""
Task tools for Letwrk AI Agent - LangChain tool implementations
"""

import re
from typing import Optional, List, Dict, Any
from langchain.tools import Tool
from langchain.callbacks.manager import CallbackManagerForToolRun

from src.models.task import Task, task_manager
from src.utils.fuzzy_matcher import fuzzy_match_name, get_available_team_members
from src.utils.formatters import (
    format_tasks_list, 
    format_task_creation_result, 
    format_task_update_result,
    format_bulk_update_result,
    format_fuzzy_match_confirmation,
    format_unknown_team_member
)
from src.utils.parsers import (
    parse_task_creation_input,
    parse_task_update_input,
    parse_bulk_update_input,
    is_meeting_content,
    parse_meeting_content,
    parse_task_selection
)
from src.config.settings import KEYWORD_TASKS


def read_tasks_tool(query: str = "", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """
    Read and filter tasks based on the query.
    Can filter by assignee, status, priority, or return all tasks.
    """
    try:
        filtered_tasks = task_manager.get_all_tasks()
        
        # Parse query for filters
        if query:
            query_lower = query.lower()
            
            # Filter by assignee
            if "for" in query_lower or "assigned to" in query_lower:
                # Extract potential name from query
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() in ["for", "assigned"] and i + 1 < len(words):
                        potential_name = words[i + 1]
                        matched_name, confidence = fuzzy_match_name(potential_name)
                        if matched_name:
                            filtered_tasks = [t for t in filtered_tasks if t.assignee == matched_name]
                        break
            
            # Filter by status
            if "pending" in query_lower:
                filtered_tasks = [t for t in filtered_tasks if t.status == "pending"]
            elif "in progress" in query_lower or "in_progress" in query_lower:
                filtered_tasks = [t for t in filtered_tasks if t.status == "in_progress"]
            elif "done" in query_lower or "completed" in query_lower:
                filtered_tasks = [t for t in filtered_tasks if t.status == "done"]
            
            # Filter by priority
            if "high priority" in query_lower or "urgent" in query_lower:
                filtered_tasks = [t for t in filtered_tasks if t.priority == "high"]
        
        return format_tasks_list(filtered_tasks)
        
    except Exception as e:
        return f"Error reading tasks: {str(e)}"


def create_task_tool(task_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """
    Create a new task. Can handle single tasks or meeting summaries that need to be broken down.
    Expected formats:
    - Simple task: "title for [assignee] with priority [priority] due [date]"
    - Meeting summary: "from this meeting create tasks: [meeting content]"
    """
    try:
        # Check if this is a meeting summary that needs to be broken down
        if is_meeting_content(task_description):
            return handle_meeting_breakdown(task_description)
        
        # Parse the task description for regular tasks
        parsed_data = parse_task_creation_input(task_description)
        title = parsed_data['title']
        assignee = parsed_data['assignee']
        priority = parsed_data['priority']
        due_date = parsed_data['due_date']
        
        # Validate title
        if not title or len(title.strip()) == 0:
            return "❌ Please provide a valid task title. Example: 'Create a new task: Update documentation' or 'Add task called \"Fix bugs\"'"
        
        # Handle assignee matching
        if assignee != "unassigned":
            matched_name, confidence = fuzzy_match_name(assignee)
            
            if matched_name and confidence >= 70:
                assignee = matched_name
                if confidence < 100:
                    # Return confirmation message for fuzzy match
                    return format_fuzzy_match_confirmation(assignee, matched_name, confidence)
            else:
                return format_unknown_team_member(assignee, get_available_team_members())
        
        # Create new task
        new_task = Task.create_new(
            title=title,
            assignee=assignee,
            priority=priority,
            due_date=due_date
        )
        
        created_task = task_manager.add_task(new_task)
        return format_task_creation_result(created_task)
        
    except Exception as e:
        return f"Error creating task: {str(e)}"


def update_task_tool(update_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """
    Update a task's status or assignee.
    Expected format: "task [id] status [new_status]", "assign task [id] to [assignee]", or "assign all tasks to [assignee]"
    """
    try:
        # Parse the update input
        parsed_data = parse_task_update_input(update_description)
        
        if 'error' in parsed_data:
            return parsed_data['error']
        
        if parsed_data.get('is_bulk'):
            return handle_bulk_task_update(update_description)
        
        # Handle single task update
        task_id = parsed_data['task_id']
        update_type = parsed_data['update_type']
        new_value = parsed_data['new_value']
        
        task = task_manager.get_task(task_id)
        if not task:
            return f"Task {task_id} not found."
        
        if update_type == 'status':
            old_status = task.status
            task_manager.update_task(task_id, status=new_value)
            return format_task_update_result(task, 'status', old_status, new_value)
        
        elif update_type == 'assignee':
            if new_value == 'unassigned':
                old_assignee = task.assignee
                task_manager.update_task(task_id, assignee='unassigned')
                return format_task_update_result(task, 'assignee', old_assignee, 'unassigned')
            else:
                # Handle assignee matching
                matched_name, confidence = fuzzy_match_name(new_value)
                
                if matched_name and confidence >= 70:
                    old_assignee = task.assignee
                    task_manager.update_task(task_id, assignee=matched_name)
                    
                    if confidence < 100:
                        return (f"✅ Updated Task {task_id}: '{task.title}'\n"
                                f"Assigned to '{matched_name}' (interpreted '{new_value}' as '{matched_name}' with {confidence:.0f}% confidence)")
                    else:
                        return format_task_update_result(task, 'assignee', old_assignee, matched_name)
                else:
                    return format_unknown_team_member(new_value, get_available_team_members())
        
        return f"I couldn't understand what you want to update for Task {task_id}."
        
    except ValueError:
        return "Please provide a valid task ID number."
    except Exception as e:
        return f"Error updating task: {str(e)}"


def handle_bulk_task_update(update_description: str) -> str:
    """
    Handle bulk operations on all tasks like 'assign all tasks to [name]', 'unassign all tasks', or 'mark all tasks as done'
    """
    try:
        parsed_data = parse_bulk_update_input(update_description)
        
        if 'error' in parsed_data:
            return parsed_data['error']
        
        operation = parsed_data['operation']
        updated_tasks = []
        
        if operation == 'unassign_all':
            for task in task_manager.get_all_tasks():
                old_assignee = task.assignee
                task_manager.update_task(task.id, assignee='unassigned')
                updated_tasks.append(f"Task {task.id}: '{task.title}' (was: {old_assignee})")
            
            return format_bulk_update_result(updated_tasks, "Unassigned")
        
        elif operation == 'assign_all':
            potential_assignee = parsed_data['assignee']
            
            # Don't try to fuzzy match "unassigned" - handle it directly
            if potential_assignee.lower() == "unassigned":
                for task in task_manager.get_all_tasks():
                    old_assignee = task.assignee
                    task_manager.update_task(task.id, assignee='unassigned')
                    updated_tasks.append(f"Task {task.id}: '{task.title}' (was: {old_assignee})")
                
                return format_bulk_update_result(updated_tasks, "Unassigned")
            
            matched_name, confidence = fuzzy_match_name(potential_assignee)
            
            if matched_name and confidence >= 70:
                for task in task_manager.get_all_tasks():
                    old_assignee = task.assignee
                    task_manager.update_task(task.id, assignee=matched_name)
                    updated_tasks.append(f"Task {task.id}: '{task.title}' (was: {old_assignee})")
                
                result = format_bulk_update_result(updated_tasks, f"Assigned to '{matched_name}'")
                
                if confidence < 100:
                    result += f"\n(Interpreted '{potential_assignee}' as '{matched_name}' with {confidence:.0f}% confidence)"
                
                return result
            else:
                return format_unknown_team_member(potential_assignee, get_available_team_members())
        
        elif operation == 'status_all':
            status = parsed_data['status']
            for task in task_manager.get_all_tasks():
                old_status = task.status
                task_manager.update_task(task.id, status=status)
                updated_tasks.append(f"Task {task.id}: '{task.title}' ({old_status} → {status})")
            
            return format_bulk_update_result(updated_tasks, f"Updated to '{status}' status")
        
        return "I couldn't understand the bulk operation."
        
    except Exception as e:
        return f"Error updating all tasks: {str(e)}"


def handle_meeting_breakdown(meeting_description: str) -> str:
    """
    Analyze meeting content and suggest actionable tasks that can be created.
    """
    try:
        # Extract the actual meeting content
        content = parse_meeting_content(meeting_description)
        
        # Analyze content for actionable items
        actionable_items = []
        
        # Look for numbered lists or bullet points that suggest tasks
        sections = re.split(r'\n\s*(?:\d+\.|\-|\•|[a-zA-Z]\))', content)
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty split
            section = section.strip()
            if section and len(section) > 10:  # Only consider substantial sections
                # Extract the main action/topic from each section
                lines = section.split('\n')
                main_line = lines[0].strip()
                
                # Clean up and create actionable task names
                if main_line:
                    # Remove common non-actionable phrases
                    task_name = re.sub(r'^(brief|state|highlight|show|demonstrate|optional)', '', main_line, flags=re.IGNORECASE).strip()
                    task_name = re.sub(r'[:\-–—]+\s*', ' - ', task_name).strip()
                    
                    if task_name and len(task_name) > 5:
                        actionable_items.append({
                            'title': task_name[:80] + ('...' if len(task_name) > 80 else ''),
                            'details': section[:200] + ('...' if len(section) > 200 else ''),
                            'suggested_assignee': 'unassigned',
                            'priority': 'medium'
                        })
        
        # If no clear actionable items found, suggest based on keywords
        if not actionable_items:
            for pattern, task_title in KEYWORD_TASKS.items():
                if re.search(pattern, content, re.IGNORECASE):
                    actionable_items.append({
                        'title': task_title,
                        'details': 'Based on meeting content',
                        'suggested_assignee': 'unassigned',
                        'priority': 'medium'
                    })
        
        if not actionable_items:
            return ("📝 I found meeting content but couldn't identify specific actionable items. "
                   "Could you please specify what tasks you'd like me to create? For example:\n"
                   "- 'Create task: Prepare demo presentation'\n"
                   "- 'Add task: Update documentation'\n"
                   "- Or tell me which parts of the meeting need follow-up actions")
        
        # Store suggestions globally for later creation
        global suggested_tasks
        suggested_tasks = actionable_items
        
        # Present suggestions to user
        result = f"📋 I found {len(actionable_items)} potential tasks from the meeting content:\n\n"
        
        for i, item in enumerate(actionable_items[:5], 1):  # Limit to 5 suggestions
            result += f"{i}. **{item['title']}**\n"
            if item['details']:
                result += f"   Details: {item['details']}\n"
            result += f"   Priority: {item['priority']} | Assignee: {item['suggested_assignee']}\n\n"
        
        if len(actionable_items) > 5:
            result += f"... and {len(actionable_items) - 5} more potential tasks.\n\n"
        
        result += ("💡 Would you like me to:\n"
                  "- Create all these tasks as suggested?\n"
                  "- Create specific tasks (tell me which numbers)?\n"
                  "- Modify any of these before creating?\n"
                  "- Or would you prefer to specify different tasks?\n\n"
                  "Just let me know how you'd like to proceed!")
        
        return result
        
    except Exception as e:
        return f"❌ Error analyzing meeting content: {str(e)}. Please try specifying individual tasks instead."


# Global variable to store suggested tasks from meeting breakdown
suggested_tasks = []


def create_suggested_tasks_tool(selection: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """
    Create tasks from previously suggested meeting breakdown.
    Selection can be: 'all', 'none', or specific numbers like '1,3,5' or '1-3'.
    """
    global suggested_tasks
    
    if not suggested_tasks:
        return "❌ No task suggestions available. Please provide meeting content first."
    
    try:
        selected_indices = parse_task_selection(selection, len(suggested_tasks))
        
        if selected_indices is None:
            return "❌ No valid task numbers found. Please specify which tasks to create (e.g., '1,3,5' or 'all')."
        
        if not selected_indices:
            suggested_tasks = []
            return "✅ Task creation cancelled. Suggestions cleared."
        
        # Create the selected tasks
        created_tasks = []
        for idx in sorted(selected_indices):
            task_data = suggested_tasks[idx]
            new_task = Task.create_new(
                title=task_data['title'],
                assignee=task_data['suggested_assignee'],
                priority=task_data['priority']
            )
            
            created_task = task_manager.add_task(new_task)
            created_tasks.append(f"Task {created_task.id}: {task_data['title']}")
        
        # Clear suggestions after creation
        suggested_tasks = []
        
        result = f"✅ Created {len(created_tasks)} tasks:\n\n"
        for task_name in created_tasks:
            result += f"• {task_name}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error creating tasks: {str(e)}"


def create_langchain_tools() -> List[Tool]:
    """Create LangChain tools for the agent."""
    return [
        Tool(
            name="read_tasks",
            description="Read and list tasks. Can filter by assignee, status (pending/in_progress/done), or priority. Use this when users ask about tasks, what they need to do, or want to see specific tasks.",
            func=read_tasks_tool
        ),
        Tool(
            name="create_task",
            description="Create a new task or analyze meeting content for task suggestions. Use this for single tasks with title/assignee/priority details, or when users provide meeting content/summaries to break down into actionable tasks.",
            func=create_task_tool
        ),
        Tool(
            name="update_task", 
            description="Update a task's status or assignee. Use this when users want to mark tasks as done/completed, change status, reassign tasks, or unassign tasks. Can handle single tasks (include task ID) or bulk operations with 'all tasks' (e.g., 'assign all tasks to Sam', 'unassign all tasks', 'mark all tasks as done').",
            func=update_task_tool
        ),
        Tool(
            name="create_suggested_tasks",
            description="Create tasks from previously suggested meeting breakdown. Use this when user responds to task suggestions with selections like 'all', 'create all', specific numbers like '1,3,5', ranges like '1-3', or 'none'/'cancel' to skip.",
            func=create_suggested_tasks_tool
        )
    ] 