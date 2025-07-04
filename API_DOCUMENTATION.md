# Letwrk AI Agent - API Documentation

## Overview

The Letwrk AI Agent API provides a RESTful interface for interacting with the AI productivity assistant. The API supports task management, conversational AI, meeting analysis, and session management.

## Base URL

```
http://localhost:8000
```

## API Version

All endpoints are prefixed with `/api/v1/`

## Authentication

Currently, the API does not require authentication. In production, you should implement proper authentication mechanisms.

## Endpoints

### System Endpoints

#### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "openai_configured": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "Letwrk AI Agent API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

#### Team Members
```http
GET /api/v1/team-members
```

**Response:**
```json
{
  "team_members": ["Ravi", "Ankita", "Sam", "Alex", "Maya", "Jordan", "Taylor"]
}
```

### Chat Endpoints

#### Process Chat Message
```http
POST /api/v1/chat
```

**Request Body:**
```json
{
  "message": "What tasks do I have today?",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "response": "Here are your tasks:\n\n⏳ **Task 1**: Review API documentation...",
  "session_id": "generated-session-id",
  "timestamp": "2024-01-15T10:30:00",
  "success": true
}
```

### Task Management Endpoints

#### Get Tasks
```http
GET /api/v1/tasks?assignee=Ravi&status=pending&priority=high
```

**Query Parameters:**
- `assignee` (optional): Filter by assignee
- `status` (optional): Filter by status (pending/in_progress/done)
- `priority` (optional): Filter by priority (high/medium/low)

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Review API documentation",
      "assignee": "Ravi",
      "status": "pending",
      "priority": "high",
      "created_at": "2024-01-15",
      "due_date": "2024-01-20",
      "description": null
    }
  ],
  "total_count": 3,
  "filtered_count": 1
}
```

#### Create Task
```http
POST /api/v1/tasks
```

**Request Body:**
```json
{
  "title": "Update documentation",
  "assignee": "Ravi",
  "priority": "high",
  "due_date": "2024-01-25",
  "description": "Update the API documentation"
}
```

**Response:**
```json
{
  "id": 4,
  "title": "Update documentation",
  "assignee": "Ravi",
  "status": "pending",
  "priority": "high",
  "created_at": "2024-01-15",
  "due_date": "2024-01-25",
  "description": "Update the API documentation"
}
```

#### Update Task
```http
PUT /api/v1/tasks/{task_id}
```

**Request Body:**
```json
{
  "status": "in_progress",
  "assignee": "Ankita",
  "priority": "medium",
  "title": "Updated title",
  "due_date": "2024-01-30"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Updated title",
  "assignee": "Ankita",
  "status": "in_progress",
  "priority": "medium",
  "created_at": "2024-01-15",
  "due_date": "2024-01-30",
  "description": null
}
```

#### Delete Task
```http
DELETE /api/v1/tasks/{task_id}
```

**Response:**
```json
{
  "message": "Task 1 deleted successfully"
}
```

#### Bulk Update Tasks
```http
POST /api/v1/tasks/bulk
```

**Request Body:**
```json
{
  "operation": "assign_all",
  "assignee": "Sam"
}
```

**Available Operations:**
- `assign_all`: Assign all tasks to a specific person
- `unassign_all`: Unassign all tasks
- `status_all`: Update status of all tasks

**Response:**
```json
{
  "message": "✅ Updated 3 tasks",
  "updated_count": 3
}
```

### Meeting Analysis Endpoints

#### Analyze Meeting Content
```http
POST /api/v1/meeting/analyze
```

**Request Body:**
```json
{
  "meeting_content": "Meeting Summary:\n1. Review API documentation\n2. Update login flow\n3. Fix database issues",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "suggested_tasks": [
    {
      "title": "Review API documentation",
      "details": "Meeting Summary:\n1. Review API documentation",
      "suggested_assignee": "unassigned",
      "priority": "medium"
    },
    {
      "title": "Update login flow",
      "details": "2. Update login flow",
      "suggested_assignee": "unassigned",
      "priority": "medium"
    }
  ],
  "session_id": "generated-session-id",
  "total_suggestions": 2
}
```

#### Create Suggested Tasks
```http
POST /api/v1/meeting/create-tasks
```

**Request Body:**
```json
{
  "selection": "1,3",
  "session_id": "session-id-from-analysis"
}
```

**Selection Options:**
- `"all"`: Create all suggested tasks
- `"none"`: Cancel task creation
- `"1,3,5"`: Create specific tasks by number
- `"1-3"`: Create tasks in range

**Response:**
```json
{
  "message": "✅ Created 2 tasks",
  "created_tasks": [
    {
      "id": 5,
      "title": "Review API documentation",
      "assignee": "unassigned",
      "priority": "medium"
    },
    {
      "id": 6,
      "title": "Fix database issues",
      "assignee": "unassigned",
      "priority": "medium"
    }
  ],
  "created_count": 2
}
```

### Session Management Endpoints

#### Get Sessions
```http
GET /api/v1/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid-session-id",
      "created_at": "2024-01-15T10:30:00",
      "last_accessed": "2024-01-15T10:35:00",
      "message_count": 5,
      "suggested_tasks_count": 2
    }
  ]
}
```

#### Delete Session
```http
DELETE /api/v1/sessions/{session_id}
```

**Response:**
```json
{
  "message": "Session uuid-session-id deleted successfully"
}
```

#### Cleanup Expired Sessions
```http
POST /api/v1/sessions/cleanup
```

**Response:**
```json
{
  "message": "Cleaned up 2 expired sessions"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00",
  "details": {
    "additional": "error details"
  }
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (task/session not found)
- `500`: Internal Server Error

## Usage Examples

### Express.js Integration

```javascript
const axios = require('axios');

class LetwrkAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.sessionId = null;
  }

  async chat(message) {
    const response = await axios.post(`${this.baseURL}/api/v1/chat`, {
      message,
      session_id: this.sessionId
    });
    
    this.sessionId = response.data.session_id;
    return response.data;
  }

  async createTask(taskData) {
    const response = await axios.post(`${this.baseURL}/api/v1/tasks`, taskData);
    return response.data;
  }

  async getTasks(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await axios.get(`${this.baseURL}/api/v1/tasks?${params}`);
    return response.data;
  }

  async updateTask(taskId, updates) {
    const response = await axios.put(`${this.baseURL}/api/v1/tasks/${taskId}`, updates);
    return response.data;
  }

  async analyzeMeeting(content) {
    const response = await axios.post(`${this.baseURL}/api/v1/meeting/analyze`, {
      meeting_content: content,
      session_id: this.sessionId
    });
    
    this.sessionId = response.data.session_id;
    return response.data;
  }
}

// Usage
const letwrk = new LetwrkAPI();

// Chat with AI
const chatResponse = await letwrk.chat("What tasks do I have today?");

// Create a task
const task = await letwrk.createTask({
  title: "Update documentation",
  assignee: "Ravi",
  priority: "high"
});

// Get tasks for Ravi
const tasks = await letwrk.getTasks({ assignee: "Ravi" });
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Chat with AI
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What tasks do I have?"}'

# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New task", "assignee": "Ravi", "priority": "high"}'

# Get tasks
curl http://localhost:8000/api/v1/tasks?assignee=Ravi

# Update task
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# Analyze meeting
curl -X POST http://localhost:8000/api/v1/meeting/analyze \
  -H "Content-Type: application/json" \
  -d '{"meeting_content": "Meeting: 1. Review docs 2. Update API"}'
```

## Configuration

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload (default: false)
- `OPENAI_API_KEY`: OpenAI API key for AI functionality
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-3.5-turbo)

### CORS Configuration

The API includes CORS middleware configured to allow all origins. For production, you should configure this properly:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run the API test suite:

```bash
# Start the server
./run_api_server

# In another terminal, run tests
python test_api.py
```

## Production Deployment

For production deployment:

1. Set proper environment variables
2. Configure CORS for your domain
3. Enable trusted host middleware
4. Use a production ASGI server like Gunicorn
5. Set up proper logging
6. Implement authentication and rate limiting

Example production command:
```bash
gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
``` 