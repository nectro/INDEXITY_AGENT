# Letwrk AI Agent 🚀

A conversational AI productivity assistant powered by **OpenAI GPT** via **LangChain**. Letwrk helps you manage tasks efficiently with natural language processing, fuzzy name matching, and intelligent conversation handling.

## Features ✨

### Core Functionality
- **📋 Task Management**: Read, create, and update tasks with natural language
- **🔍 Fuzzy Name Matching**: Automatically corrects misspelled names (e.g., "Rave" → "Ravi")
- **❓ Smart Clarification**: Asks clarifying questions for ambiguous requests
- **💬 Conversational Interface**: Friendly, helpful responses with emojis
- **🧠 Powered by OpenAI**: Uses GPT-3.5-turbo or GPT-4 via OpenAI API

### Technical Features
- **🤖 LangChain Agent**: Uses `OPENAI_FUNCTIONS` agent type with tool calling
- **🛠️ Custom Tools**: Three specialized tools for task management
- **💾 Conversation Memory**: Maintains context across interactions
- **🔧 Error Handling**: Graceful error handling with helpful messages

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
```bash
./run_agent
```

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

## Team Members 👥

Built-in team members (easily customizable):
- Ravi, Ankita, Sam, Alex, Maya, Jordan, Taylor

**Note**: The fuzzy matching system handles common misspellings and asks for confirmation when uncertain.

## Architecture 🏗️

### Project Structure
```
letwrk_agent/
├── letwrk_env/          # Virtual environment
├── letwrk_agent.py      # Main AI agent (400 lines)
├── test_agent.py        # Comprehensive tests
├── requirements.txt     # Dependencies
├── run_agent            # Auto-runner script
├── setup_env.sh         # Environment setup helper
├── SETUP.md            # Detailed setup guide
└── README.md           # This file
```

### Core Components

1. **Main Agent** (`create_agent()`):
   - LangChain agent with OPENAI_FUNCTIONS
   - OpenAI GPT LLM via ChatOpenAI
   - Conversation memory
   - System prompt for behavior definition

2. **Tools** (`create_langchain_tools()`):
   - `read_tasks`: List and filter tasks
   - `create_task`: Create new tasks
   - `update_task`: Update task status/assignee

3. **Fuzzy Matching** (`fuzzy_match_name()`):
   - Uses RapidFuzz for name similarity
   - 70% confidence threshold
   - Returns best match with confidence score

### Data Structure
```python
{
    "id": 1,
    "title": "Review API documentation",
    "assignee": "Ravi",
    "status": "in_progress",  # pending, in_progress, done
    "priority": "high",       # high, medium, low
    "created_at": "2024-01-15",
    "due_date": "2024-01-20"
}
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
- **Team Members**: Edit `TEAM_MEMBERS` list in `letwrk_agent.py`
- **Mock Data**: Replace `MOCK_TASKS` with database connection
- **Tools**: Add new tools following the existing pattern

## Troubleshooting 🔧

### Common Issues

1. **"Failed to initialize Letwrk agent"**:
   - Check if OPENAI_API_KEY is set: `echo $OPENAI_API_KEY`
   - Get API key from: https://platform.openai.com/api-keys
   - Set it with: `export OPENAI_API_KEY="your-key-here"`

2. **Import Errors**:
   - Activate virtual environment: `source letwrk_env/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

3. **Virtual Environment Issues**:
   - Check Python version: `python3 --version` (requires 3.8+)
   - Recreate if needed: `rm -rf letwrk_env && python3 -m venv letwrk_env`

## Development 👨‍💻

### Adding New Tools

1. **Create tool function**:
   ```python
   def my_new_tool(query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
       # Tool logic here
       return "Tool response"
   ```

2. **Add to tools list** in `create_langchain_tools()`

3. **Update system prompt** to include new capabilities

### Testing
```bash
# Activate virtual environment
source letwrk_env/bin/activate

# Run comprehensive tests
python test_agent.py
```

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