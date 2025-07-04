"""
Command-line interface for Letwrk AI Agent
"""

from src.core.agent import create_agent, create_agent_without_api


def print_welcome_message():
    """Print the welcome message and usage examples."""
    print("🚀 Welcome to Letwrk - Your AI Productivity Assistant!")
    print("Powered by OpenAI GPT")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    print("💡 Try these example queries:")
    print("  - 'What do I have to do today?'")
    print("  - 'Create a task for Rave to update the login flow'")
    print("  - 'Mark task 2 as done'")
    print("  - 'Assign all tasks to Sam'")
    print("  - 'Unassign all tasks'")
    print("  - 'Show me high priority tasks'\n")


def run_cli():
    """Run the command-line interface."""
    print_welcome_message()
    
    try:
        agent = create_agent()
        run_conversation_loop(agent)
        
    except Exception as e:
        print(f"❌ Failed to initialize Letwrk agent: {str(e)}")
        print("Make sure you have set your OpenAI API key.")
        print("Get your API key from: https://platform.openai.com/api-keys")


def run_conversation_loop(agent):
    """Run the main conversation loop."""
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Have a productive day!")
                break
            
            if not user_input:
                continue
            
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


def run_test_mode():
    """Run the agent in test mode without API key."""
    print("🧪 Running Letwrk in test mode...")
    print("This mode tests the basic functionality without AI capabilities.\n")
    
    agent = create_agent_without_api()
    if agent:
        run_conversation_loop(agent)
    else:
        print("❌ Test mode failed. Please check your setup.")


if __name__ == "__main__":
    run_cli() 