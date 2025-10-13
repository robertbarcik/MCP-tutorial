#!/bin/bash

# Quick start script for MCP Tutorial
# This script helps set up and test the MCP orchestrator

echo "================================"
echo "MCP Tutorial - Quick Start"
echo "================================"
echo ""

# Check Python version
echo "1. Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "   ✓ Python found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "   ✓ Python found: $(python --version)"
else
    echo "   ✗ Python not found. Please install Python 3.10+"
    exit 1
fi
echo ""

# Check if in correct directory
if [ ! -f "mcp_client.py" ]; then
    echo "   ✗ Please run this script from the mcp_tutorial directory"
    exit 1
fi

# Install dependencies
echo "2. Installing dependencies..."
echo "   (This may take a minute...)"
$PYTHON_CMD -m pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✓ Dependencies installed"
else
    echo "   ✗ Failed to install dependencies"
    exit 1
fi
echo ""

# Test server imports
echo "3. Testing server files..."
for server in ticket_server customer_server billing_server kb_server asset_server; do
    $PYTHON_CMD -c "import ${server}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✓ ${server}.py"
    else
        echo "   ✗ ${server}.py has import errors"
    fi
done
echo ""

# Test orchestrator import
echo "4. Testing orchestrator..."
$PYTHON_CMD -c "from mcp_client import MCPOrchestrator" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ mcp_client.py"
else
    echo "   ✗ mcp_client.py has import errors"
fi
echo ""

# Check for OpenAI API key
echo "5. Checking OpenAI API key..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "   ⚠️  OPENAI_API_KEY not set in environment"
    echo "   To use interactive mode, set your API key:"
    echo "   export OPENAI_API_KEY='sk-...'"
else
    echo "   ✓ OPENAI_API_KEY is set"
fi
echo ""

# Show next steps
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Test server startup:"
echo "   $PYTHON_CMD mcp_client.py"
echo ""
echo "2. Try interactive mode (requires OpenAI API key):"
echo "   export OPENAI_API_KEY='sk-...'"
echo "   $PYTHON_CMD interactive_client.py"
echo ""
echo "3. Run intent tests:"
echo "   $PYTHON_CMD test_intents.py"
echo ""
echo "4. Explore Jupyter notebook:"
echo "   jupyter notebook MCP_Demo.ipynb"
echo ""
