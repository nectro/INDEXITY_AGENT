# Letwrk Agent - Setup Guide 🚀

This guide will walk you through setting up the Letwrk AI Agent from scratch, including virtual environment setup, dependencies, and running the application.

## Prerequisites 📋

- **Python 3.8+** (Check with: `python3 --version`)
- **Git** (if cloning from repository)
- **Internet connection** (for downloading packages and API calls)
- **OpenAI API Key** (for AI functionality)

## Step-by-Step Setup

### 1. Project Setup 📁

```bash
# Clone or navigate to the project directory
cd /path/to/letwrk-agent

# Verify you have the required files
ls -la
# Should show: letwrk_agent.py, requirements.txt, README.md, etc.
```

### 2. Create Virtual Environment 🐍

```bash
# Create a new virtual environment named 'letwrk_env'
python3 -m venv letwrk_env

# Verify creation
ls -la letwrk_env/
# Should show: bin/, lib/, pyvenv.cfg, etc.
```

### 3. Activate Virtual Environment ⚡

#### For macOS/Linux (Bash/Zsh):
```bash
source letwrk_env/bin/activate

# You should see (letwrk_env) in your prompt
# Example: (letwrk_env) user@machine:~/letwrk-agent$
```

#### For Windows:
```cmd
# Command Prompt
letwrk_env\Scripts\activate.bat

# PowerShell
letwrk_env\Scripts\Activate.ps1
```

#### For Fish Shell:
```fish
source letwrk_env/bin/activate.fish
```

### 4. Upgrade Pip (Recommended) 📦

```bash
# Ensure you're using the latest pip
pip install --upgrade pip

# Verify pip is from virtual environment
which pip
# Should show: /path/to/letwrk-agent/letwrk_env/bin/pip
```

### 5. Install Dependencies 📚

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
# Should show: langchain, langchain-openai, rapidfuzz, etc.
```

#### What Gets Installed:
- **langchain**: Core LangChain framework
- **langchain-openai**: OpenAI integration for LangChain
- **rapidfuzz**: Fast fuzzy string matching
- **openai**: OpenAI Python client
- **tiktoken**: Tokenization for OpenAI models
- **Other dependencies**: Various supporting packages

### 6. Setup OpenAI API Key 🔑

#### Get Your API Key:
1. Visit: https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### Set Environment Variable:

**Option A - Temporary (Current Session Only):**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

**Option B - Permanent (Recommended):**
```bash
# Add to your shell configuration file
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.zshrc

# For bash users:
# echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.bashrc

# Reload your shell configuration
source ~/.zshrc
```

**Option C - Using the Setup Script:**
```bash
# Make the setup script executable
chmod +x setup_env.sh

# Run the interactive setup
./setup_env.sh
```

#### Optional: Choose AI Model
```bash
# Default is gpt-3.5-turbo, but you can change it:
export OPENAI_MODEL="gpt-4"
# or
export OPENAI_MODEL="gpt-3.5-turbo"
```

### 7. Verify Setup ✅

```bash
# Test the installation without full AI
python test_agent.py

# Should show: "Testing completed!" with all tests passing
```

### 8. Run the Application 🎯

```bash
# Using the convenience script (recommended)
./run_agent

# Or run directly with Python
python letwrk_agent.py
```

You should see:
```
🚀 Welcome to Letwrk - Your AI Productivity Assistant!
Powered by OpenAI GPT
Type 'quit' or 'exit' to end the conversation.

💡 Try these example queries:
  - 'What do I have to do today?'
  - 'Create a task for Rave to update the login flow'
  - 'Mark task 2 as done'
  - 'Assign the design task to Ankti'
  - 'Show me high priority tasks'

You: 
```

## Troubleshooting 🔧

### Virtual Environment Issues

**Problem**: `source: command not found`
```bash
# Make sure you're using the right shell
echo $SHELL

# For zsh/bash:
source letwrk_env/bin/activate

# For fish:
source letwrk_env/bin/activate.fish
```

**Problem**: Virtual environment not activating
```bash
# Check if virtual environment was created properly
ls -la letwrk_env/bin/

# Recreate if necessary
rm -rf letwrk_env
python3 -m venv letwrk_env
```

### Dependency Issues

**Problem**: `pip install` fails
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output to see errors
pip install -r requirements.txt -v

# Try installing packages individually
pip install langchain langchain-openai rapidfuzz
```

**Problem**: Import errors when running
```bash
# Check if packages are installed in the right environment
pip list | grep langchain

# Make sure virtual environment is activated
which python
# Should point to: /path/to/letwrk_env/bin/python
```

### API Key Issues

**Problem**: "OpenAI API key not found"
```bash
# Check if the variable is set
echo $OPENAI_API_KEY

# If empty, set it:
export OPENAI_API_KEY="your-key-here"

# Check the format (should start with 'sk-')
echo $OPENAI_API_KEY | head -c 3
# Should output: sk-
```

**Problem**: "Invalid API key"
- Double-check your API key from OpenAI dashboard
- Make sure there are no extra spaces or quotes
- Verify your OpenAI account has credits/billing set up

### Application Issues

**Problem**: Agent doesn't respond to queries
```bash
# Test with basic functionality first
python test_agent.py

# Check your internet connection
curl -s https://api.openai.com/v1/models > /dev/null && echo "OpenAI API reachable"
```

**Problem**: Permission denied running `./run_agent`
```bash
# Make the script executable
chmod +x run_agent

# Or run directly
bash run_agent
```

## Development Workflow 💻

### Daily Development:
```bash
# 1. Navigate to project
cd /path/to/letwrk-agent

# 2. Activate virtual environment
source letwrk_env/bin/activate

# 3. Run the agent
./run_agent

# 4. When done, deactivate (optional)
deactivate
```

### Adding New Dependencies:
```bash
# 1. Activate virtual environment
source letwrk_env/bin/activate

# 2. Install new package
pip install new-package

# 3. Update requirements file
pip freeze > requirements.txt

# 4. Commit the updated requirements.txt
```

### Testing Changes:
```bash
# Run tests
python test_agent.py

# Test specific functionality
python -c "from letwrk_agent import fuzzy_match_name; print(fuzzy_match_name('Rave'))"
```

## Quick Reference 📝

### Essential Commands:
```bash
# Activate environment
source letwrk_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key"

# Run application
./run_agent

# Run tests
python test_agent.py

# Deactivate environment
deactivate
```

### Project Structure:
```
letwrk-agent/
├── letwrk_agent.py      # Main application
├── requirements.txt     # Python dependencies
├── test_agent.py       # Test suite
├── run_agent           # Convenience script
├── setup_env.sh        # Environment setup helper
├── README.md           # Project documentation
├── SETUP.md           # This setup guide
└── letwrk_env/        # Virtual environment
    ├── bin/           # Executables
    ├── lib/           # Installed packages
    └── pyvenv.cfg     # Environment config
```

## Next Steps 🎯

1. **Explore the Agent**: Try different queries to understand capabilities
2. **Read the Code**: Check `letwrk_agent.py` to understand the implementation
3. **Customize**: Modify the team members, tasks, or behavior
4. **Extend**: Add new tools or features to the agent

For more detailed information about the agent's features and usage, see [README.md](README.md).

---

**Need Help?** 
- Check the troubleshooting section above
- Review the main [README.md](README.md) for feature details
- Test with `python test_agent.py` for basic functionality 