"""
Agent service for handling AI agent operations in the API
"""

import os
from typing import Optional, Dict, Any
from langchain.agents import AgentExecutor
from langchain.schema import BaseMessage

from src.core.agent import create_agent, create_agent_without_api
from src.api.session_manager import session_manager
from src.models.task import Task, task_manager
from src.utils.fuzzy_matcher import fuzzy_match_name
from src.utils.formatters import format_tasks_list, format_task_creation_result
from src.utils.parsers import parse_task_creation_input, parse_task_update_input, parse_bulk_update_input
from src.config.settings import TEAM_MEMBERS


class AgentService:
    """Service class for handling AI agent operations"""
    
    def __init__(self):
        self.agent: Optional[AgentExecutor] = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LangChain agent"""
        try:
            self.agent = create_agent()
        except Exception as e:
            print(f"Warning: Could not initialize agent with OpenAI: {e}")
            self.agent = None
    
    def is_agent_available(self) -> bool:
        """Check if the agent is available"""
        return self.agent is not None
    
    def process_message(self, message: str, session_id: str) -> str:
        """Process a user message and return AI response"""
        if not self.agent:
            return "❌ AI agent is not available. Please check your OpenAI API configuration."
        
        try:
            # Get session memory
            memory = session_manager.get_session_memory(session_id)
            if not memory:
                return "❌ Session not found or expired."
            
            # Process the message
            response = self.agent.invoke({"input": message})
            
            # Handle response format
            if isinstance(response, dict) and 'output' in response:
                return response['output']
            elif isinstance(response, str):
                return response
            else:
                return str(response)
                
        except Exception as e:
            return f"❌ Error processing message: {str(e)}"
    
    def create_task(self, title: str, assignee: str = "unassigned", 
                   priority: str = "medium", due_date: Optional[str] = None) -> Dict[str, Any]:
        """Create a new task"""
        try:
            # Handle assignee matching
            if assignee != "unassigned":
                matched_name, confidence = fuzzy_match_name(assignee)
                if matched_name and confidence >= 70:
                    assignee = matched_name
                    if confidence < 100:
                        return {
                            "success": False,
                            "message": f"Did you mean to assign this task to '{matched_name}'? (I interpreted '{assignee}' as '{matched_name}' with {confidence:.0f}% confidence). Please confirm or specify the correct name.",
                            "suggested_assignee": matched_name,
                            "confidence": confidence
                        }
                else:
                    return {
                        "success": False,
                        "message": f"I couldn't find a team member named '{assignee}'. Available team members: {', '.join(TEAM_MEMBERS)}. Please specify the correct name."
                    }
            
            # Create task
            new_task = Task.create_new(
                title=title,
                assignee=assignee,
                priority=priority,
                due_date=due_date
            )
            
            created_task = task_manager.add_task(new_task)
            
            return {
                "success": True,
                "message": format_task_creation_result(created_task),
                "task": created_task
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating task: {str(e)}"
            }
    
    def update_task(self, task_id: int, **kwargs) -> Dict[str, Any]:
        """Update a task"""
        try:
            task = task_manager.get_task(task_id)
            if not task:
                return {
                    "success": False,
                    "message": f"Task {task_id} not found."
                }
            
            # Handle assignee updates
            if 'assignee' in kwargs and kwargs['assignee'] != "unassigned":
                matched_name, confidence = fuzzy_match_name(kwargs['assignee'])
                if matched_name and confidence >= 70:
                    kwargs['assignee'] = matched_name
                    if confidence < 100:
                        return {
                            "success": False,
                            "message": f"Did you mean '{matched_name}'? (I interpreted '{kwargs['assignee']}' as '{matched_name}' with {confidence:.0f}% confidence). Please confirm or specify the correct name.",
                            "suggested_assignee": matched_name,
                            "confidence": confidence
                        }
                else:
                    return {
                        "success": False,
                        "message": f"I couldn't find a team member named '{kwargs['assignee']}'. Available team members: {', '.join(TEAM_MEMBERS)}"
                    }
            
            # Update task
            updated_task = task_manager.update_task(task_id, **kwargs)
            
            return {
                "success": True,
                "message": f"✅ Updated Task {task_id}: '{task.title}'",
                "task": updated_task
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating task: {str(e)}"
            }
    
    def get_tasks(self, assignee: Optional[str] = None, 
                 status: Optional[str] = None, 
                 priority: Optional[str] = None) -> Dict[str, Any]:
        """Get tasks with optional filtering"""
        try:
            filters = {}
            if assignee:
                filters['assignee'] = assignee
            if status:
                filters['status'] = status
            if priority:
                filters['priority'] = priority
            
            tasks = task_manager.filter_tasks(**filters)
            
            return {
                "success": True,
                "tasks": tasks,
                "total_count": len(task_manager.get_all_tasks()),
                "filtered_count": len(tasks)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving tasks: {str(e)}"
            }
    
    def bulk_update_tasks(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Perform bulk operations on tasks"""
        try:
            if operation == "assign_all":
                assignee = kwargs.get('assignee')
                if not assignee:
                    return {
                        "success": False,
                        "message": "Assignee is required for assign_all operation"
                    }
                
                # Handle assignee matching
                matched_name, confidence = fuzzy_match_name(assignee)
                if matched_name and confidence >= 70:
                    assignee = matched_name
                    if confidence < 100:
                        return {
                            "success": False,
                            "message": f"Did you mean '{matched_name}'? (I interpreted '{assignee}' as '{matched_name}' with {confidence:.0f}% confidence). Please confirm or specify the correct name.",
                            "suggested_assignee": matched_name,
                            "confidence": confidence
                        }
                else:
                    return {
                        "success": False,
                        "message": f"I couldn't find a team member named '{assignee}'. Available team members: {', '.join(TEAM_MEMBERS)}"
                    }
                
                updated_tasks = task_manager.bulk_update(assignee=assignee)
                
            elif operation == "unassign_all":
                updated_tasks = task_manager.bulk_update(assignee="unassigned")
                
            elif operation == "status_all":
                status = kwargs.get('status')
                if not status:
                    return {
                        "success": False,
                        "message": "Status is required for status_all operation"
                    }
                updated_tasks = task_manager.bulk_update(status=status)
                
            else:
                return {
                    "success": False,
                    "message": f"Unknown bulk operation: {operation}"
                }
            
            return {
                "success": True,
                "message": f"✅ Updated {len(updated_tasks)} tasks",
                "updated_count": len(updated_tasks)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error performing bulk update: {str(e)}"
            }
    
    def analyze_meeting(self, meeting_content: str, session_id: str) -> Dict[str, Any]:
        """Analyze meeting content and suggest tasks"""
        try:
            # Import here to avoid circular imports
            from src.tools.task_tools import handle_meeting_breakdown
            
            # Store meeting content in session for later task creation
            session_manager.set_suggested_tasks(session_id, [])
            
            # Analyze meeting content
            result = handle_meeting_breakdown(meeting_content)
            
            # Extract suggested tasks from the result (this is a simplified approach)
            # In a real implementation, you'd want to parse the result more carefully
            suggested_tasks = []
            lines = result.split('\n')
            current_task = None
            
            for line in lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    # This is a task line
                    if current_task:
                        suggested_tasks.append(current_task)
                    
                    title = line.split('**')[1].split('**')[0] if '**' in line else line.split('.', 1)[1].strip()
                    current_task = {
                        'title': title,
                        'details': '',
                        'suggested_assignee': 'unassigned',
                        'priority': 'medium'
                    }
                elif current_task and line.strip().startswith('   Details:'):
                    current_task['details'] = line.replace('   Details:', '').strip()
            
            if current_task:
                suggested_tasks.append(current_task)
            
            session_manager.set_suggested_tasks(session_id, suggested_tasks)
            
            return {
                "success": True,
                "message": result,
                "suggested_tasks": suggested_tasks,
                "total_suggestions": len(suggested_tasks)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error analyzing meeting: {str(e)}"
            }
    
    def create_suggested_tasks(self, selection: str, session_id: str) -> Dict[str, Any]:
        """Create tasks from suggested tasks"""
        try:
            suggested_tasks = session_manager.get_suggested_tasks(session_id)
            
            if not suggested_tasks:
                return {
                    "success": False,
                    "message": "No task suggestions available. Please provide meeting content first."
                }
            
            # Import here to avoid circular imports
            from src.utils.parsers import parse_task_selection
            
            selected_indices = parse_task_selection(selection, len(suggested_tasks))
            
            if selected_indices is None:
                return {
                    "success": False,
                    "message": "No valid task numbers found. Please specify which tasks to create (e.g., '1,3,5' or 'all')."
                }
            
            if not selected_indices:
                session_manager.clear_suggested_tasks(session_id)
                return {
                    "success": True,
                    "message": "✅ Task creation cancelled. Suggestions cleared."
                }
            
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
                created_tasks.append(created_task)
            
            # Clear suggestions after creation
            session_manager.clear_suggested_tasks(session_id)
            
            return {
                "success": True,
                "message": f"✅ Created {len(created_tasks)} tasks",
                "created_tasks": created_tasks
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating tasks: {str(e)}"
            }


# Global agent service instance
agent_service = AgentService() 