"""
Pydantic models for FastAPI request and response schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat conversations"""
    message: str = Field(..., description="User message to process")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User ID for personalization")


class ChatResponse(BaseModel):
    """Response model for chat conversations"""
    response: str = Field(..., description="AI agent response")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    success: bool = Field(True, description="Whether the request was successful")
    error: Optional[str] = Field(None, description="Error message if any")


class TaskCreateRequest(BaseModel):
    """Request model for creating tasks"""
    title: str = Field(..., description="Task title")
    assignee: Optional[str] = Field("unassigned", description="Task assignee")
    priority: Optional[str] = Field("medium", description="Task priority (high/medium/low)")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    description: Optional[str] = Field(None, description="Task description")


class TaskUpdateRequest(BaseModel):
    """Request model for updating tasks"""
    status: Optional[str] = Field(None, description="New status (pending/in_progress/done)")
    assignee: Optional[str] = Field(None, description="New assignee")
    priority: Optional[str] = Field(None, description="New priority (high/medium/low)")
    title: Optional[str] = Field(None, description="New title")
    due_date: Optional[str] = Field(None, description="New due date")


class TaskResponse(BaseModel):
    """Response model for task operations"""
    id: int
    title: str
    assignee: str
    status: str
    priority: str
    created_at: str
    due_date: str
    description: Optional[str] = None


class TaskListResponse(BaseModel):
    """Response model for task lists"""
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total_count: int = Field(..., description="Total number of tasks")
    filtered_count: int = Field(..., description="Number of tasks after filtering")


class BulkTaskUpdateRequest(BaseModel):
    """Request model for bulk task operations"""
    operation: str = Field(..., description="Operation type (assign_all/unassign_all/status_all)")
    assignee: Optional[str] = Field(None, description="Assignee for assign_all operation")
    status: Optional[str] = Field(None, description="Status for status_all operation")


class MeetingAnalysisRequest(BaseModel):
    """Request model for meeting content analysis"""
    meeting_content: str = Field(..., description="Meeting content to analyze")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class SuggestedTask(BaseModel):
    """Model for suggested tasks from meeting analysis"""
    title: str
    details: str
    suggested_assignee: str
    priority: str


class MeetingAnalysisResponse(BaseModel):
    """Response model for meeting analysis"""
    suggested_tasks: List[SuggestedTask] = Field(..., description="List of suggested tasks")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    total_suggestions: int = Field(..., description="Total number of suggestions")


class TaskSelectionRequest(BaseModel):
    """Request model for selecting tasks from suggestions"""
    selection: str = Field(..., description="Selection (all, none, or specific numbers like 1,3,5)")
    session_id: str = Field(..., description="Session ID for conversation continuity")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    version: str = Field(..., description="API version")
    openai_configured: bool = Field(..., description="Whether OpenAI is configured")


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 