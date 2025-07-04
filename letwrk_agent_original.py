#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Letwrk AI Agent - A conversational productivity assistant powered by OpenAI GPT
"""

import warnings
# Suppress all urllib3 warnings first thing - these are harmless SSL warnings
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

import os
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from rapidfuzz import fuzz, process

# Also disable urllib3 warnings directly
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
except (ImportError, AttributeError):
    pass

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# Mock data structures for tasks and users
MOCK_TASKS = [
    {
        "id": 1,
        "title": "Review API documentation",
        "assignee": "Ravi",
        "status": "in_progress",
        "priority": "high",
        "created_at": "2024-01-15",
        "due_date": "2024-01-20"
    },
    {
        "id": 2,
        "title": "Update login flow design",
        "assignee": "Ankita",
        "status": "pending",
        "priority": "medium",
        "created_at": "2024-01-16",
        "due_date": "2024-01-25"
    },
    {
        "id": 3,
        "title": "Fix database connection issues",
        "assignee": "Sam",
        "status": "done",
        "priority": "high",
        "created_at": "2024-01-10",
        "due_date": "2024-01-18"
    }
]

TEAM_MEMBERS = ["Ravi", "Ankita", "Sam", "Alex", "Maya", "Jordan", "Taylor"]

task_counter = len(MOCK_TASKS)


def fuzzy_match_name(input_name: str, threshold: float = 70.0) -> Tuple[Optional[str], float]:
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


def read_tasks_tool(query: str = "", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """
    Read and filter tasks based on the query.
    Can filter by assignee, status, priority, or return all tasks.
    """
    try:
        filtered_tasks = MOCK_TASKS.copy()
        
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
                            filtered_tasks = [t for t in filtered_tasks if t["assignee"] == matched_name]
                        break
            
            # Filter by status
            if "pending" in query_lower:
                filtered_tasks = [t for t in filtered_tasks if t["status"] == "pending"]
            elif "in progress" in query_lower or "in_progress" in query_lower:
                filtered_tasks = [t for t in filtered_tasks if t["status"] == "in_progress"]
            elif "done" in query_lower or "completed" in query_lower:
                filtered_tasks = [t for t in filtered_tasks if t["status"] == "done"]
            
            # Filter by priority
            if "high priority" in query_lower or "urgent" in query_lower:
                filtered_tasks = [t for t in filtered_tasks if t["priority"] == "high"]
        
        if not filtered_tasks:
            return "No tasks found matching your criteria."
        
        # Format tasks for display
        result = "Here are the tasks:\n\n"
        for task in filtered_tasks:
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "done": "✅"}
            priority_emoji = {"high": "🔥", "medium": "📋", "low": "📝"}
            
            result += f"{status_emoji.get(task['status'], '📋')} **Task {task['id']}**: {task['title']}\n"
            result += f"   👤 Assignee: {task['assignee']}\n"
            result += f"   {priority_emoji.get(task['priority'], '📝')} Priority: {task['priority']}\n"
            result += f"   📅 Due: {task['due_date']}\n"
            result += f"   Status: {task['status']}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error reading tasks: {str(e)}"


def create_task_tool(task_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """
    Create a new task. Can handle single tasks or meeting summaries that need to be broken down.
    Expected formats:
    - Simple task: "title for [assignee] with priority [priority] due [date]"
    - Meeting summary: "from this meeting create tasks: [meeting content]"
    """
    global task_counter
    
    try:
        # Check if this is a meeting summary that needs to be broken down
        meeting_indicators = [
            r'from.*?(?:this\s+)?meeting.*?create.*?tasks?',
            r'meeting\s+summary.*?create.*?tasks?',
            r'create.*?tasks?.*?from.*?meeting',
            r'break.*?down.*?into.*?tasks?',
            r'actionable.*?items?.*?from',
            r'MEETING\s+SUMMARY',
            r'DEMO\s+MEETING',
            r'meeting.*?notes'
        ]
        
        is_meeting_content = any(re.search(pattern, task_description, re.IGNORECASE) for pattern in meeting_indicators)
        
        if is_meeting_content:
            return handle_meeting_breakdown(task_description)
        
        # Parse the task description for regular tasks
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
                instruction_patterns = [
                    r'^.*?create\s+(?:a\s+)?(?:new\s+)?task\s*(?:called\s+|named\s+|titled\s+|:\s*)',
                    r'^.*?add\s+(?:a\s+)?(?:new\s+)?task\s*(?:called\s+|named\s+|titled\s+|:\s*)',
                    r'^.*?new\s+task\s*(?:called\s+|named\s+|titled\s+|for\s+|:\s*)',
                    r'^.*?task\s*(?:called\s+|named\s+|titled\s+|:\s*)',
                ]
                
                for pattern in instruction_patterns:
                    new_title = re.sub(pattern, '', title, flags=re.IGNORECASE).strip()
                    if new_title and new_title != title:  # If something was removed and we have content
                        title = new_title
                        break
        
        # Extract assignee
        assignee_match = re.search(r'\bfor\s+(\w+)', task_description, re.IGNORECASE)
        if assignee_match:
            potential_assignee = assignee_match.group(1)
            matched_name, confidence = fuzzy_match_name(potential_assignee)
            
            if matched_name and confidence >= 70:
                assignee = matched_name
                # Clean the assignee from title
                title = re.sub(r'\s+for\s+\w+', '', title, flags=re.IGNORECASE)
                
                if confidence < 100:
                    # Return confirmation message for fuzzy match
                    return f"Did you mean to assign this task to '{matched_name}'? (I interpreted '{potential_assignee}' as '{matched_name}' with {confidence:.0f}% confidence). Please confirm or specify the correct name."
            else:
                return f"I couldn't find a team member named '{potential_assignee}'. Available team members: {', '.join(TEAM_MEMBERS)}. Please specify the correct name."
        
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
        
        # Remove any remaining artifacts
        title = re.sub(r'^(to\s+)?', '', title, flags=re.IGNORECASE)  # Remove leading "to"
        title = re.sub(r'[\'"]*$', '', title)  # Remove trailing quotes
        title = re.sub(r'^[\'"]*', '', title)  # Remove leading quotes
        title = title.strip()
        
        # Ensure we have a valid task title
        if not title or len(title.strip()) == 0:
            return "❌ Please provide a valid task title. Example: 'Create a new task: Update documentation' or 'Add task called \"Fix bugs\"'"
        
        # Create new task
        task_counter += 1
        new_task = {
            "id": task_counter,
            "title": title,
            "assignee": assignee,
            "status": "pending",
            "priority": priority,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "due_date": due_date
        }
        
        MOCK_TASKS.append(new_task)
        
        return f"✅ Created new task:\n**Task {new_task['id']}**: {new_task['title']}\n👤 Assignee: {new_task['assignee']}\n🔥 Priority: {new_task['priority']}\n📅 Due: {new_task['due_date']}"
        
    except Exception as e:
        return f"Error creating task: {str(e)}"


def update_task_tool(update_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """
    Update a task's status or assignee.
    Expected format: "task [id] status [new_status]", "assign task [id] to [assignee]", or "assign all tasks to [assignee]"
    """
    try:
        # Check for "all tasks" operations first
        if re.search(r'\ball\s+tasks?\b', update_description, re.IGNORECASE):
            return handle_bulk_task_update(update_description)
        
        # Extract task ID for single task operations
        task_id_match = re.search(r'\btask\s+(\d+)', update_description, re.IGNORECASE)
        if not task_id_match:
            return "Please specify the task ID (e.g., 'task 2') or use 'all tasks' for bulk operations."
        
        task_id = int(task_id_match.group(1))
        
        # Find the task
        task = None
        for t in MOCK_TASKS:
            if t["id"] == task_id:
                task = t
                break
        
        if not task:
            return f"Task {task_id} not found."
        
        # Check for status update
        status_patterns = [
            (r'\b(done|completed|finished)\b', 'done'),
            (r'\b(pending|todo|waiting)\b', 'pending'),
            (r'\b(in[_\s]progress|working|started)\b', 'in_progress')
        ]
        
        for pattern, status in status_patterns:
            if re.search(pattern, update_description, re.IGNORECASE):
                old_status = task["status"]
                task["status"] = status
                return f"✅ Updated Task {task_id}: '{task['title']}'\nStatus changed from '{old_status}' to '{status}'"
        
        # Check for unassigning operations on single tasks
        unassign_patterns = [
            r'\bunassign.*?task\s+' + str(task_id) + r'\b',
            r'\btask\s+' + str(task_id) + r'.*?unassign',
            r'\bremove.*?assignee.*?from.*?task\s+' + str(task_id) + r'\b'
        ]
        
        for pattern in unassign_patterns:
            if re.search(pattern, update_description, re.IGNORECASE):
                old_assignee = task["assignee"]
                task["assignee"] = "unassigned"
                return f"✅ Updated Task {task_id}: '{task['title']}'\nUnassigned (was: {old_assignee})"
        
        # Check for assignee update
        assign_match = re.search(r'\bassign.*?to\s+(\w+)', update_description, re.IGNORECASE)
        if assign_match:
            potential_assignee = assign_match.group(1)
            
            # Handle "unassigned" directly for single tasks too
            if potential_assignee.lower() == "unassigned":
                old_assignee = task["assignee"]
                task["assignee"] = "unassigned"
                return f"✅ Updated Task {task_id}: '{task['title']}'\nUnassigned (was: {old_assignee})"
            
            matched_name, confidence = fuzzy_match_name(potential_assignee)
            
            if matched_name and confidence >= 70:
                old_assignee = task["assignee"]
                task["assignee"] = matched_name
                
                if confidence < 100:
                    return f"✅ Updated Task {task_id}: '{task['title']}'\nAssigned to '{matched_name}' (interpreted '{potential_assignee}' as '{matched_name}' with {confidence:.0f}% confidence)"
                else:
                    return f"✅ Updated Task {task_id}: '{task['title']}'\nAssigned from '{old_assignee}' to '{matched_name}'"
            else:
                return f"I couldn't find a team member named '{potential_assignee}'. Available team members: {', '.join(TEAM_MEMBERS)}"
        
        return f"I couldn't understand what you want to update for Task {task_id}. You can:\n- Change status: 'mark task {task_id} as done/pending/in progress'\n- Change assignee: 'assign task {task_id} to [name]'\n- Unassign: 'unassign task {task_id}' or 'assign task {task_id} to unassigned'"
        
    except ValueError:
        return "Please provide a valid task ID number."
    except Exception as e:
        return f"Error updating task: {str(e)}"


def handle_bulk_task_update(update_description: str) -> str:
    """
    Handle bulk operations on all tasks like 'assign all tasks to [name]', 'unassign all tasks', or 'mark all tasks as done'
    """
    try:
        updated_tasks = []
        
        # Check for unassigning operations first
        unassign_patterns = [
            r'\bunassign.*?all.*?tasks?\b',
            r'\bmake.*?all.*?tasks?.*?unassigned\b',
            r'\bremove.*?assignees?.*?from.*?all.*?tasks?\b',
            r'\ball.*?tasks?.*?unassigned\b'
        ]
        
        for pattern in unassign_patterns:
            if re.search(pattern, update_description, re.IGNORECASE):
                for task in MOCK_TASKS:
                    old_assignee = task["assignee"]
                    task["assignee"] = "unassigned"
                    updated_tasks.append(f"Task {task['id']}: '{task['title']}' (was: {old_assignee})")
                
                result = f"✅ Unassigned all {len(updated_tasks)} tasks:\n\n"
                for task_update in updated_tasks:
                    result += f"  • {task_update}\n"
                
                return result
        
        # Check for bulk assignee update
        assign_match = re.search(r'\bassign.*?all.*?tasks?.*?to\s+(\w+)', update_description, re.IGNORECASE)
        if assign_match:
            potential_assignee = assign_match.group(1)
            
            # Don't try to fuzzy match "unassigned" - handle it directly
            if potential_assignee.lower() == "unassigned":
                for task in MOCK_TASKS:
                    old_assignee = task["assignee"]
                    task["assignee"] = "unassigned"
                    updated_tasks.append(f"Task {task['id']}: '{task['title']}' (was: {old_assignee})")
                
                result = f"✅ Unassigned all {len(updated_tasks)} tasks:\n\n"
                for task_update in updated_tasks:
                    result += f"  • {task_update}\n"
                
                return result
            
            matched_name, confidence = fuzzy_match_name(potential_assignee)
            
            if matched_name and confidence >= 70:
                for task in MOCK_TASKS:
                    old_assignee = task["assignee"]
                    task["assignee"] = matched_name
                    updated_tasks.append(f"Task {task['id']}: '{task['title']}' (was: {old_assignee})")
                
                result = f"✅ Assigned all {len(updated_tasks)} tasks to '{matched_name}':\n\n"
                for task_update in updated_tasks:
                    result += f"  • {task_update}\n"
                
                if confidence < 100:
                    result += f"\n(Interpreted '{potential_assignee}' as '{matched_name}' with {confidence:.0f}% confidence)"
                
                return result
            else:
                return f"I couldn't find a team member named '{potential_assignee}'. Available team members: {', '.join(TEAM_MEMBERS)}"
        
        # Check for bulk status update
        status_patterns = [
            (r'\b(done|completed|finished)\b', 'done'),
            (r'\b(pending|todo|waiting)\b', 'pending'),
            (r'\b(in[_\s]progress|working|started)\b', 'in_progress')
        ]
        
        for pattern, status in status_patterns:
            if re.search(pattern, update_description, re.IGNORECASE):
                for task in MOCK_TASKS:
                    old_status = task["status"]
                    task["status"] = status
                    updated_tasks.append(f"Task {task['id']}: '{task['title']}' ({old_status} → {status})")
                
                result = f"✅ Updated all {len(updated_tasks)} tasks to '{status}' status:\n\n"
                for task_update in updated_tasks:
                    result += f"  • {task_update}\n"
                
                return result
        
        return "I couldn't understand the bulk operation. You can:\n- 'assign all tasks to [name]'\n- 'unassign all tasks' or 'remove assignees from all tasks'\n- 'mark all tasks as done/pending/in progress'"
        
    except Exception as e:
        return f"Error updating all tasks: {str(e)}"


def handle_meeting_breakdown(meeting_description: str) -> str:
    """
    Analyze meeting content and suggest actionable tasks that can be created.
    """
    try:
        # Extract the actual meeting content
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
            keyword_tasks = {
                r'demo|demonstration': 'Prepare demo presentation',
                r'integration|connect': 'Set up integrations',
                r'dashboard|overview': 'Design dashboard overview',
                r'problem|solution': 'Document problem and solution',
                r'walkthrough|tutorial': 'Create walkthrough guide',
                r'documentation|docs': 'Update documentation',
                r'testing|test': 'Conduct testing',
                r'meeting|presentation': 'Schedule follow-up meeting'
            }
            
            for pattern, task_title in keyword_tasks.items():
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
    global task_counter, suggested_tasks
    
    if not suggested_tasks:
        return "❌ No task suggestions available. Please provide meeting content first."
    
    try:
        selection = selection.lower().strip()
        
        if selection in ['none', 'cancel', 'no']:
            suggested_tasks = []
            return "✅ Task creation cancelled. Suggestions cleared."
        
        # Parse selection
        selected_indices = []
        
        if selection in ['all', 'yes', 'create all']:
            selected_indices = list(range(len(suggested_tasks)))
        else:
            # Parse specific numbers/ranges
            parts = selection.replace(' ', '').split(',')
            for part in parts:
                if '-' in part and part.count('-') == 1:
                    # Range like "1-3"
                    start, end = part.split('-')
                    try:
                        start_idx = int(start) - 1
                        end_idx = int(end) - 1
                        selected_indices.extend(range(start_idx, end_idx + 1))
                    except ValueError:
                        continue
                else:
                    # Single number
                    try:
                        selected_indices.append(int(part) - 1)
                    except ValueError:
                        continue
        
        # Remove duplicates and invalid indices
        selected_indices = list(set(i for i in selected_indices if 0 <= i < len(suggested_tasks)))
        
        if not selected_indices:
            return "❌ No valid task numbers found. Please specify which tasks to create (e.g., '1,3,5' or 'all')."
        
        # Create the selected tasks
        created_tasks = []
        for idx in sorted(selected_indices):
            task_data = suggested_tasks[idx]
            task_counter += 1
            
            new_task = {
                'id': task_counter,
                'title': task_data['title'],
                'description': task_data['details'],
                'assignee': task_data['suggested_assignee'],
                'status': 'todo',
                'priority': task_data['priority'],
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'due_date': task_data.get('due_date')
            }
            
            MOCK_TASKS.append(new_task)
            created_tasks.append(f"Task {task_counter}: {task_data['title']}")
        
        # Clear suggestions after creation
        suggested_tasks = []
        
        result = f"✅ Created {len(created_tasks)} tasks:\n\n"
        for task_name in created_tasks:
            result += f"• {task_name}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error creating tasks: {str(e)}"


def create_langchain_tools():
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


def create_agent():
    """Create and configure the LangChain agent."""
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found! Please set OPENAI_API_KEY environment variable.\n"
            "Get your API key from: https://platform.openai.com/api-keys\n"
            "Set it with: export OPENAI_API_KEY='your-api-key-here'"
        )
    
    # Initialize OpenAI LLM
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    llm = ChatOpenAI(
        model=model,
        temperature=0.1,
        openai_api_key=api_key
    )
    
    # Create tools
    tools = create_langchain_tools()
    
    # Create prompt template for the new agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are Letwrk, a helpful and friendly productivity assistant. Your role is to help users manage their tasks efficiently.

CORE PRINCIPLES:
- Be concise, helpful, and friendly in your responses
- Never hallucinate or make up information about tasks or team members
- Always confirm uncertain actions, especially with fuzzy name matches
- Ask clarifying questions when user requests are vague or ambiguous
- Use the available tools to read, create, and update tasks

AVAILABLE TEAM MEMBERS: Ravi, Ankita, Sam, Alex, Maya, Jordan, Taylor

BEHAVIOR GUIDELINES:
1. When users ask about tasks ("what do I have to do"), use read_tasks tool
2. When users want to create single tasks, use create_task tool and include all provided details
3. When users provide meeting content/summaries for task creation, use create_task tool to analyze and suggest actionable tasks
4. When users respond to task suggestions (like "create all" or "1,3,5"), use create_suggested_tasks tool
5. When users want to update task status or assignments, use update_task tool (supports both single tasks and bulk operations with "all tasks")
6. If a name seems misspelled (like "Rave" for "Ravi"), confirm the correction before proceeding
7. If a request is vague, ask specific clarifying questions
8. Always acknowledge successful actions with clear confirmation

RESPONSE STYLE:
- Use emojis appropriately (✅ for success, ⏳ for pending, 🔄 for in progress, etc.)
- Be conversational but professional
- Provide clear status updates after actions
- Offer helpful suggestions when appropriate

Remember: You are a productivity assistant, not a general chatbot. Focus on task management and stay within your domain expertise."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create memory for conversation context
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create the agent using the new constructor
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,  # Set to False to avoid callback issues
        handle_parsing_errors=True
    )
    
    return agent_executor


def main():
    """Main function to run the Letwrk agent."""
    print("🚀 Welcome to Letwrk - Your AI Productivity Assistant!")
    print("Powered by OpenAI GPT")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    try:
        agent = create_agent()
        
        # Example queries to show capabilities
        print("💡 Try these example queries:")
        print("  - 'What do I have to do today?'")
        print("  - 'Create a task for Rave to update the login flow'")
        print("  - 'Mark task 2 as done'")
        print("  - 'Assign all tasks to Sam'")
        print("  - 'Unassign all tasks'")
        print("  - 'Show me high priority tasks'\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Have a productive day!")
                break
            
            if not user_input:
                continue
            
            try:
                response = agent.invoke({"input": user_input})
                # Handle both string responses and dict responses
                if isinstance(response, dict) and 'output' in response:
                    print(f"\nLetwrk: {response['output']}\n")
                elif isinstance(response, str):
                    print(f"\nLetwrk: {response}\n")
                else:
                    print(f"\nLetwrk: {str(response)}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Have a productive day!")
                break
            except Exception as e:
                print(f"\n❌ Sorry, I encountered an error: {str(e)}")
                print("Please try rephrasing your request.\n")
    
    except Exception as e:
        print(f"❌ Failed to initialize Letwrk agent: {str(e)}")
        print("Make sure you have set your OpenAI API key.")
        print("Get your API key from: https://platform.openai.com/api-keys")


if __name__ == "__main__":
    main() 