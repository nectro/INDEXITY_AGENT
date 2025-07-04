"""
Core agent module for Letwrk AI Agent
"""

import os
import warnings
from typing import Optional

# Suppress warnings
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
except (ImportError, AttributeError):
    pass

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.tools.task_tools import create_langchain_tools
from src.config.settings import DEFAULT_MODEL, DEFAULT_TEMPERATURE


def create_agent() -> AgentExecutor:
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
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    llm = ChatOpenAI(
        model=model,
        temperature=DEFAULT_TEMPERATURE,
        openai_api_key=api_key
    )
    
    # Create tools
    tools = create_langchain_tools()
    
    # Create prompt template for the agent
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


def create_agent_without_api() -> Optional[AgentExecutor]:
    """Create a basic agent for testing without API key."""
    try:
        return create_agent()
    except ValueError as e:
        print(f"⚠️  Warning: {str(e)}")
        print("Running in test mode without AI functionality...")
        return None 