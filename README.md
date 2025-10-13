# MCP Tutorial - Multi-Server IT Support System

A hands-on demonstration of the **Model Context Protocol (MCP)** with 5 specialized servers orchestrated by OpenAI GPT-4.

## What You'll Learn

- How to build multi-server AI systems using MCP
- OpenAI function calling integration
- Server orchestration and tool discovery
- Natural language queries across multiple data sources

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 3. Try It Out

**Interactive Chat (Recommended):**
```bash
python interactive_client.py
```

Ask questions like:
- "What are all the critical priority tickets?"
- "Show me customer CUST-001's information and SLA terms"
- "Which assets have expired warranties?"

**Jupyter Notebook:**
```bash
jupyter notebook MCP_Demo.ipynb
```

**Test Server Startup:**
```bash
python mcp_client.py
```

## Complete Learning Guide

📚 **See [TUTORIAL.md](TUTORIAL.md) for the complete learning guide** including:

- MCP concepts and architecture
- Detailed system overview
- Example queries to try
- Technical deep dive
- Exercises and extensions

## Repository Structure

```
MCP-tutorial/
├── TUTORIAL.md              # Complete learning guide (start here!)
├── README.md                # This file - quick start
├── requirements.txt         # Python dependencies
│
├── servers/                 # MCP server implementations
│   ├── ticket_server.py     # Ticket management (4 tools)
│   ├── customer_server.py   # Customer database (4 tools)
│   ├── billing_server.py    # Billing system (4 tools)
│   ├── kb_server.py         # Knowledge base (4 tools)
│   └── asset_server.py      # Asset tracking (4 tools)
│
├── mcp_client.py            # Orchestrator (coordinates all servers)
├── interactive_client.py    # CLI chat interface
└── MCP_Demo.ipynb           # Jupyter notebook demo
```

## The Five Servers

1. **Ticket Server** - Manage support tickets (search, metrics, similar tickets)
2. **Customer Server** - Customer info and SLA terms
3. **Billing Server** - Invoices and payment tracking
4. **Knowledge Base Server** - Technical articles and solutions
5. **Asset Server** - Hardware/software asset and warranty tracking

**Total: 20 tools** across 5 servers, all discoverable and callable via natural language.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User / Interactive Client                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Orchestrator (mcp_client.py)               │
│  - Manages server processes                                 │
│  - Coordinates tool calls                                   │
│  - Integrates with OpenAI GPT-4                            │
└─────────────────────────────────────────────────────────────┘
          │          │          │          │          │
          ▼          ▼          ▼          ▼          ▼
    ┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
    │ Ticket  ││Customer ││ Billing ││   KB    ││  Asset  │
    │ Server  ││ Server  ││ Server  ││ Server  ││ Server  │
    └─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
```

## Troubleshooting

**Servers won't start:**
- Check Python version: `python --version` (need 3.10+)
- Verify all files are present in `servers/` folder

**OpenAI API errors:**
- Verify API key: `echo $OPENAI_API_KEY`
- Check API credits at https://platform.openai.com/

**Need help?**
See [TUTORIAL.md](TUTORIAL.md) for detailed troubleshooting and learning resources.

## License

MIT

## Credits

Built with:
- [Model Context Protocol (MCP)](https://github.com/anthropics/mcp)
- [OpenAI API](https://platform.openai.com/)
