"""
FastAPI routes for Letwrk AI Agent API
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from src.api.models import (
    ChatRequest, ChatResponse, TaskCreateRequest, TaskUpdateRequest, 
    TaskResponse, TaskListResponse, BulkTaskUpdateRequest,
    MeetingAnalysisRequest, MeetingAnalysisResponse, TaskSelectionRequest,
    HealthResponse, ErrorResponse
)
from src.api.agent_service import agent_service
from src.api.session_manager import session_manager
from src.models.task import task_manager
from src.config.settings import TEAM_MEMBERS

# Create router
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    import os
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        openai_configured=agent_service.is_agent_available()
    )


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """Process a chat message and return AI response"""
    try:
        # Get or create session
        session_id = session_manager.get_or_create_session(request.session_id)
        
        # Process message
        response_text = agent_service.process_message(request.message, session_id)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", response_model=TaskListResponse, tags=["Tasks"])
async def get_tasks(
    assignee: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    """Get tasks with optional filtering"""
    try:
        result = agent_service.get_tasks(assignee=assignee, status=status, priority=priority)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        tasks = result["tasks"]
        task_responses = [
            TaskResponse(
                id=task.id,
                title=task.title,
                assignee=task.assignee,
                status=task.status,
                priority=task.priority,
                created_at=task.created_at,
                due_date=task.due_date,
                description=task.description
            ) for task in tasks
        ]
        
        return TaskListResponse(
            tasks=task_responses,
            total_count=result["total_count"],
            filtered_count=result["filtered_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(request: TaskCreateRequest):
    """Create a new task"""
    try:
        result = agent_service.create_task(
            title=request.title,
            assignee=request.assignee,
            priority=request.priority,
            due_date=request.due_date
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        task = result["task"]
        return TaskResponse(
            id=task.id,
            title=task.title,
            assignee=task.assignee,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at,
            due_date=task.due_date,
            description=task.description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(task_id: int, request: TaskUpdateRequest):
    """Update an existing task"""
    try:
        # Build update kwargs
        update_kwargs = {}
        if request.status is not None:
            update_kwargs['status'] = request.status
        if request.assignee is not None:
            update_kwargs['assignee'] = request.assignee
        if request.priority is not None:
            update_kwargs['priority'] = request.priority
        if request.title is not None:
            update_kwargs['title'] = request.title
        if request.due_date is not None:
            update_kwargs['due_date'] = request.due_date
        
        result = agent_service.update_task(task_id, **update_kwargs)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        task = result["task"]
        return TaskResponse(
            id=task.id,
            title=task.title,
            assignee=task.assignee,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at,
            due_date=task.due_date,
            description=task.description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(task_id: int):
    """Delete a task"""
    try:
        success = task_manager.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return {"message": f"Task {task_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/bulk", tags=["Tasks"])
async def bulk_update_tasks(request: BulkTaskUpdateRequest):
    """Perform bulk operations on tasks"""
    try:
        kwargs = {}
        if request.assignee is not None:
            kwargs['assignee'] = request.assignee
        if request.status is not None:
            kwargs['status'] = request.status
        
        result = agent_service.bulk_update_tasks(request.operation, **kwargs)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "message": result["message"],
            "updated_count": result.get("updated_count", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meeting/analyze", response_model=MeetingAnalysisResponse, tags=["Meeting Analysis"])
async def analyze_meeting(request: MeetingAnalysisRequest):
    """Analyze meeting content and suggest tasks"""
    try:
        # Get or create session
        session_id = session_manager.get_or_create_session(request.session_id)
        
        result = agent_service.analyze_meeting(request.meeting_content, session_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        suggested_tasks = []
        for task_data in result.get("suggested_tasks", []):
            suggested_tasks.append({
                "title": task_data["title"],
                "details": task_data["details"],
                "suggested_assignee": task_data["suggested_assignee"],
                "priority": task_data["priority"]
            })
        
        return MeetingAnalysisResponse(
            suggested_tasks=suggested_tasks,
            session_id=session_id,
            total_suggestions=result["total_suggestions"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meeting/create-tasks", tags=["Meeting Analysis"])
async def create_suggested_tasks(request: TaskSelectionRequest):
    """Create tasks from meeting analysis suggestions"""
    try:
        result = agent_service.create_suggested_tasks(request.selection, request.session_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        created_tasks = []
        for task in result.get("created_tasks", []):
            created_tasks.append({
                "id": task.id,
                "title": task.title,
                "assignee": task.assignee,
                "priority": task.priority
            })
        
        return {
            "message": result["message"],
            "created_tasks": created_tasks,
            "created_count": len(created_tasks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team-members", tags=["System"])
async def get_team_members():
    """Get list of available team members"""
    return {"team_members": TEAM_MEMBERS}


@router.get("/sessions", tags=["System"])
async def get_sessions():
    """Get information about all active sessions"""
    return {"sessions": session_manager.get_all_sessions_info()}


@router.delete("/sessions/{session_id}", tags=["System"])
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        session_manager.remove_session(session_id)
        return {"message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/cleanup", tags=["System"])
async def cleanup_sessions():
    """Clean up expired sessions"""
    try:
        cleaned_count = session_manager.cleanup_expired_sessions()
        return {"message": f"Cleaned up {cleaned_count} expired sessions"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Note: Exception handlers are defined in the main app.py file
# since APIRouter doesn't support exception handlers 