# Letwrk AI Agent 🚀

A conversational AI productivity assistant powered by **OpenAI GPT** via **LangChain**. Letwrk helps you manage tasks efficiently with natural language processing, fuzzy name matching, and intelligent conversation handling.

## Features ✨

### Core Functionality
- **📋 Task Management**: Read, create, and update tasks with natural language
- **🔍 Fuzzy Name Matching**: Automatically corrects misspelled names (e.g., "Rave" → "Ravi")
- **❓ Smart Clarification**: Asks clarifying questions for ambiguous requests
- **💬 Conversational Interface**: Friendly, helpful responses with emojis
- **🧠 Powered by OpenAI**: Uses GPT-3.5-turbo or GPT-4 via OpenAI API
- **🌐 REST API**: FastAPI-based RESTful API for integration with other applications
- **🔄 Session Management**: Conversation memory across API calls

### Technical Features
- **🤖 LangChain Agent**: Uses `OPENAI_FUNCTIONS` agent type with tool calling
- **🛠️ Custom Tools**: Three specialized tools for task management
- **💾 Conversation Memory**: Maintains context across interactions
- **🔧 Error Handling**: Graceful error handling with helpful messages
- **🏗️ Modular Architecture**: Clean, maintainable code structure
- **🚀 FastAPI Backend**: High-performance async API with automatic documentation

## Quick Start 🏁

📖 **For complete step-by-step setup instructions, see [SETUP.md](SETUP.md)**

### Option A: Quick Setup (Experienced Users)

#### 1. Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv letwrk_env

# Activate virtual environment
source letwrk_env/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Install Dependencies & Setup API Key
```bash
# Install packages
pip install -r requirements.txt

# Set OpenAI API key (get from: https://platform.openai.com/api-keys)
export OPENAI_API_KEY="your-api-key-here"
```

#### 3. Run the Agent

**CLI Mode:**
```bash
./run_agent
```

**API Mode:**
```bash
./run_api_server
```

The API server will start on `http://localhost:8000` with interactive documentation at `/docs`.

### Option B: Detailed Setup (New Users)

The **[SETUP.md](SETUP.md)** guide provides comprehensive instructions including:
- ✅ Virtual environment setup for all operating systems
- ✅ Step-by-step dependency installation
- ✅ Multiple methods to configure OpenAI API key
- ✅ Troubleshooting common issues
- ✅ Development workflow tips
- ✅ Testing and verification steps

## Usage Examples 💡

### Basic Task Management
```
You: What do I have to do today?

Letwrk: Here are the tasks:

🔄 **Task 1**: Review API documentation
   👤 Assignee: Ravi
   🔥 Priority: high
   📅 Due: 2024-01-20
   Status: in_progress

⏳ **Task 2**: Update login flow design
   👤 Assignee: Ankita
   📋 Priority: medium
   📅 Due: 2024-01-25
   Status: pending
```

### Creating Tasks with Fuzzy Name Matching
```
You: Create a task for Rave to update the login flow

Letwrk: Did you mean to assign this task to 'Ravi'? (I interpreted 'Rave' as 'Ravi' with 88% confidence). Please confirm or specify the correct name.

You: Yes, assign it to Ravi

Letwrk: ✅ Created new task:
**Task 4**: update the login flow
👤 Assignee: Ravi
🔥 Priority: medium
📅 Due: 2024-01-27
```

### Updating Tasks
```
You: Mark task 2 as done

Letwrk: ✅ Updated Task 2: 'Update login flow design'
Status changed from 'pending' to 'done'

You: Assign the design task to Ankti

Letwrk: ✅ Updated Task 2: 'Update login flow design'
Assigned to 'Ankita' (interpreted 'Ankti' as 'Ankita' with 92% confidence)
```

## Available Commands 📝

### Task Reading
- `"What do I have to do today?"`
- `"Show me all tasks"`
- `"What tasks are assigned to Ravi?"`
- `"Show me high priority tasks"`
- `"List pending tasks"`

### Task Creation
- `"Create a task for [name] to [description]"`
- `"Add a new task: [description]"`
- `"Create high priority task for [name] to [description]"`

### Task Updates
- `"Mark task [id] as done"`
- `"Set task [id] to in progress"`
- `"Assign task [id] to [name]"`

## API Usage 🌐

The Letwrk AI Agent also provides a RESTful API for integration with other applications.

### Quick API Start
```bash
./run_api_server
```

### API Endpoints
- **Chat**: `POST /api/v1/chat` - Process natural language messages
- **Tasks**: `GET/POST/PUT/DELETE /api/v1/tasks` - Task management
- **Meeting Analysis**: `POST /api/v1/meeting/analyze` - Extract tasks from meetings
- **Sessions**: `GET/DELETE /api/v1/sessions` - Session management

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Express.js Integration Example
```javascript
const axios = require('axios');

// Chat with AI
const response = await axios.post('http://localhost:8000/api/v1/chat', {
  message: "What tasks do I have today?"
});

// Create a task
const task = await axios.post('http://localhost:8000/api/v1/tasks', {
  title: "Update documentation",
  assignee: "Ravi",
  priority: "high"
});
```

📖 **For complete API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

## Team Members 👥

Built-in team members (easily customizable):
- Ravi, Ankita, Sam, Alex, Maya, Jordan, Taylor

**Note**: The fuzzy matching system handles common misspellings and asks for confirmation when uncertain.

## Architecture 🏗️

### Project Structure
```
letwrk_agent/
├── src/                    # Source code directory
│   ├── config/            # Configuration settings
│   │   └── settings.py    # All constants and settings
│   ├── core/              # Core application logic
│   │   ├── agent.py       # LangChain agent creation
│   │   └── cli.py         # Command-line interface
│   ├── models/            # Data models
│   │   └── task.py        # Task model and manager
│   ├── tools/             # LangChain tools
│   │   └── task_tools.py  # Task management tools
│   ├── utils/             # Utility functions
│       ├── fuzzy_matcher.py # Name matching utilities
│       ├── formatters.py    # Output formatting
│       └── parsers.py       # Input parsing
│   └── api/               # FastAPI components
│       ├── app.py         # FastAPI application
│       ├── routes.py      # API routes
│       ├── models.py      # Pydantic models
│       ├── agent_service.py # Agent service
│       └── session_manager.py # Session management
├── letwrk_env/            # Virtual environment
├── main.py                # CLI entry point
├── api_server.py          # API server entry point
├── test_refactored.py     # Test script
├── test_api.py            # API test script
├── requirements.txt       # Dependencies
├── run_agent             # CLI runner script
├── run_api_server        # API server runner script
├── setup_env.sh          # Environment setup helper
├── API_DOCUMENTATION.md  # Comprehensive API docs
├── SETUP.md             # Detailed setup guide
└── README.md            # This file
```

### Core Components

1. **Main Entry Point** (`main.py`):
   - Clean entry point for the application
   - Imports and runs the CLI interface

2. **Agent Core** (`src/core/agent.py`):
   - LangChain agent with OPENAI_FUNCTIONS
   - OpenAI GPT LLM via ChatOpenAI
   - Conversation memory
   - System prompt for behavior definition

3. **Task Tools** (`src/tools/task_tools.py`):
   - `read_tasks`: List and filter tasks
   - `create_task`: Create new tasks or analyze meetings
   - `update_task`: Update task status/assignee (single or bulk)
   - `create_suggested_tasks`: Handle task suggestions

4. **Task Model** (`src/models/task.py`):
   - Task data structure with dataclass
   - TaskManager for CRUD operations
   - Mock data initialization

5. **Utilities** (`src/utils/`):
   - `fuzzy_matcher.py`: Name matching with RapidFuzz
   - `formatters.py`: Response formatting
   - `parsers.py`: Input parsing and validation

6. **Configuration** (`src/config/settings.py`):
   - Centralized settings and constants
   - Team members, thresholds, patterns
   - Emoji mappings and regex patterns

7. **API Layer** (`src/api/`):
   - `app.py`: FastAPI application with middleware
   - `routes.py`: REST API endpoints
   - `models.py`: Pydantic request/response models
   - `agent_service.py`: Service layer for API operations
   - `session_manager.py`: Session management for conversations

### Data Structure
```python
@dataclass
class Task:
    id: int
    title: str
    assignee: str
    status: str  # pending, in_progress, done
    priority: str  # high, medium, low
    created_at: str
    due_date: str
    description: Optional[str] = None
```

## Dependencies 📦

```
langchain>=0.1.0
langchain-openai>=0.0.5
rapidfuzz>=3.5.0
```

## Configuration ⚙️

### LLM Settings
- **Model**: `gpt-3.5-turbo` (configurable via OPENAI_MODEL env var)
- **Temperature**: `0.1` (low for consistent responses)
- **Agent Type**: `OPENAI_FUNCTIONS`

### Customization
- **Team Members**: Edit `TEAM_MEMBERS` list in `src/config/settings.py`
- **Fuzzy Matching**: Adjust `FUZZY_MATCH_THRESHOLD` in settings
- **Default Values**: Modify task defaults in settings

## Development 🛠️

### Testing
```bash
# Run the test suite
python test_refactored.py

# Test without API key
python -c "from src.core.cli import run_test_mode; run_test_mode()"
```

### Code Structure Benefits
- **Modularity**: Each component has a single responsibility
- **Maintainability**: Easy to modify and extend
- **Testability**: Isolated components for better testing
- **Reusability**: Utilities can be used across the application
- **Configuration**: Centralized settings management

### Adding New Features
1. **New Tools**: Add to `src/tools/task_tools.py`
2. **New Models**: Create in `src/models/`
3. **New Utils**: Add to `src/utils/`
4. **New Settings**: Update `src/config/settings.py`

## Migration from Original 🚚

The original single-file structure has been preserved as `letwrk_agent_original.py` for reference. The new modular structure maintains all original functionality while providing:

- Better code organization
- Easier maintenance
- Improved testability
- Enhanced extensibility
- Cleaner separation of concerns

All existing functionality works exactly the same way - only the internal structure has been improved.

## Future Enhancements 🔮

- [ ] Persistent task storage (database)
- [ ] Task scheduling and reminders  
- [ ] Team performance analytics
- [ ] Integration with project management tools
- [ ] Multi-language support
- [ ] Voice interface support

---

**Built with ❤️ for productivity enthusiasts**

Ready to boost your team's productivity with AI-powered task management! 