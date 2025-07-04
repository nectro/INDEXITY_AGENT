"""
Task model and data structures for Letwrk AI Agent
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from src.config.settings import DEFAULT_PRIORITY, DEFAULT_STATUS, DEFAULT_DUE_DAYS


@dataclass
class Task:
    """Task data model"""
    id: int
    title: str
    assignee: str
    status: str
    priority: str
    created_at: str
    due_date: str
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        return cls(**data)
    
    @classmethod
    def create_new(cls, title: str, assignee: str = "unassigned", 
                   priority: str = DEFAULT_PRIORITY, due_date: Optional[str] = None) -> 'Task':
        """Create a new task with default values"""
        if due_date is None:
            due_date = (datetime.now() + timedelta(days=DEFAULT_DUE_DAYS)).strftime("%Y-%m-%d")
        
        return cls(
            id=0,  # Will be set by task manager
            title=title,
            assignee=assignee,
            status=DEFAULT_STATUS,
            priority=priority,
            created_at=datetime.now().strftime("%Y-%m-%d"),
            due_date=due_date
        )


class TaskManager:
    """Manages task storage and operations"""
    
    def __init__(self):
        self.tasks: list[Task] = []
        self.task_counter: int = 0
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize with mock data"""
        mock_tasks_data = [
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
        
        for task_data in mock_tasks_data:
            task = Task.from_dict(task_data)
            self.tasks.append(task)
            self.task_counter = max(self.task_counter, task.id)
    
    def add_task(self, task: Task) -> Task:
        """Add a new task"""
        self.task_counter += 1
        task.id = self.task_counter
        self.tasks.append(task)
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> list[Task]:
        """Get all tasks"""
        return self.tasks.copy()
    
    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """Update task fields"""
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task by ID"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def filter_tasks(self, **filters) -> list[Task]:
        """Filter tasks by various criteria"""
        filtered_tasks = self.tasks.copy()
        
        for key, value in filters.items():
            if key == "assignee":
                filtered_tasks = [t for t in filtered_tasks if t.assignee == value]
            elif key == "status":
                filtered_tasks = [t for t in filtered_tasks if t.status == value]
            elif key == "priority":
                filtered_tasks = [t for t in filtered_tasks if t.priority == value]
        
        return filtered_tasks
    
    def bulk_update(self, **kwargs) -> list[Task]:
        """Update all tasks with given fields"""
        updated_tasks = []
        for task in self.tasks:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            updated_tasks.append(task)
        return updated_tasks


# Global task manager instance
task_manager = TaskManager() 