#!/bin/zsh

# Letwrk Agent - Environment Setup Script
echo "🔧 Setting up Letwrk Agent environment..."

# Check if API key is already set
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OPENAI_API_KEY is already set"
    echo "Current model: ${OPENAI_MODEL:-gpt-3.5-turbo}"
    exit 0
fi

echo ""
echo "🔑 You need an OpenAI API key to use the full AI functionality."
echo "📝 Follow these steps:"
echo ""
echo "1. Get your API key:"
echo "   👉 Visit: https://platform.openai.com/api-keys"
echo "   👉 Create account or sign in"
echo "   👉 Click 'Create new secret key'"
echo "   👉 Copy the key (starts with 'sk-')"
echo ""
echo "2. Set the API key:"
echo "   👉 Option A (temporary): export OPENAI_API_KEY='your-key-here'"
echo "   👉 Option B (permanent): add to ~/.zshrc"
echo ""

read -q "setup?Would you like to set it up now? (y/N): "
echo ""

if [[ $setup == "y" ]]; then
    echo ""
    echo "📝 Enter your OpenAI API key:"
    read -s "api_key?API Key: "
    echo ""
    
    if [[ $api_key == sk-* ]]; then
        echo "export OPENAI_API_KEY='$api_key'" >> ~/.zshrc
        echo "export OPENAI_MODEL='gpt-3.5-turbo'" >> ~/.zshrc
        echo ""
        echo "✅ Environment variables added to ~/.zshrc"
        echo "🔄 Reload your shell: source ~/.zshrc"
        echo "🚀 Then run: ./run_agent"
    else
        echo "❌ Invalid API key format. Keys should start with 'sk-'"
        echo "Please get a valid key from: https://platform.openai.com/api-keys"
    fi
else
    echo ""
    echo "💡 Manual setup:"
    echo "   export OPENAI_API_KEY='your-key-here'"
    echo "   export OPENAI_MODEL='gpt-3.5-turbo'  # optional"
    echo ""
fi

echo ""
echo "📚 For more help, see: README.md" 