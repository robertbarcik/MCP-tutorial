# MCP Tutorial - Multi-Server IT Support System

A hands-on tutorial for the **Model Context Protocol (MCP)** built around a complete IT support system with 5 specialized servers. The tutorial covers both cloud-based AI models (OpenAI gpt-5-nano) and local open source models (Gemma 2 2B).

## What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol for connecting AI models with external tools and data sources. Instead of writing custom integration code for every service, MCP provides a common interface that any AI model can use to discover and call tools across multiple services.

This tutorial demonstrates MCP through a complete IT support system with 5 servers (tickets, customers, billing, knowledge base, assets), all orchestrated to answer natural language questions through a single AI model.

## Notebooks

The tutorial is organized into three notebooks that build on each other:

### Notebook 1: `1_MCP_Demo.ipynb` - Exploring MCP Server Functions

The starting point. You'll learn what MCP is, how the 5 servers work together, and explore each server by calling its functions directly as Python. The notebook also shows how to run the full MCP system with `interactive_client.py` from a terminal.

**What you'll learn:**
- What MCP is and why it's useful
- How 5 specialized servers work together
- How each server function behaves with successful queries and error responses
- How structured error responses guide AI models toward recovery

### Notebook 2: `2_MCP_resources_prompts_sampling.ipynb` - Advanced MCP Features

Goes beyond basic tool calling to explore three additional MCP features: **Resources** (exposing readable documents), **Prompts** (reusable AI workflow templates), and **Sampling** (bidirectional communication where the server asks the host's AI model for help).

**What you'll learn:**
- How to expose documents and data through MCP resources
- How to create reusable workflow templates with prompts
- How sampling enables privacy-preserving AI by keeping sensitive data on the server

### Notebook 3: `3_MCP_with_Local_Model.ipynb` - MCP with Local Open Source Models

Shows how to use the same MCP servers with a **local open source model** instead of OpenAI's API. You'll load Gemma 2 2B with 4-bit quantization and implement the entire tool calling loop manually.

**What you'll learn:**
- How to load and run a local model on a free Colab GPU
- How to describe tools in a format the model understands
- How to implement the tool calling loop from scratch
- The trade-offs between cloud APIs and local models for tool calling

## Quick Start

### Option 1: Google Colab (Recommended)

1. Open one of the notebooks in Google Colab
2. Upload the required Python files (listed in the notebook's Setup section) to the Colab Files panel
3. Follow the instructions in the notebook

For notebooks that need an OpenAI API key, the script will prompt you when needed. For notebook 3, you'll need a free Hugging Face account to download the Gemma model (instructions in the notebook).

### Option 2: Local Setup

```bash
# Clone the repository
git clone <repo-url>
cd MCP-tutorial

# Install dependencies
pip install -r requirements.txt

# Run a notebook
jupyter notebook 1_MCP_Demo.ipynb
```

To run the full MCP system from the command line:

```bash
export OPENAI_API_KEY="sk-your-key-here"
python interactive_client.py
```

Then ask questions like:
- "What are all the critical priority tickets?"
- "Show me customer CUST-001's information and SLA terms"
- "Which customers have both open tickets and overdue invoices?"

## The Five Servers

This tutorial implements an IT support system with 5 specialized MCP servers:

| Server | Purpose | Tools |
|--------|---------|-------|
| **Ticket Server** | Track and manage support tickets | `search_tickets`, `get_ticket_details`, `get_ticket_metrics`, `find_similar_tickets` |
| **Customer Server** | Customer info and SLA terms | `lookup_customer`, `check_customer_status`, `get_sla_terms`, `list_customer_contacts` |
| **Billing Server** | Invoices and payment tracking | `get_invoice`, `check_payment_status`, `get_billing_history`, `calculate_outstanding_balance` |
| **Knowledge Base Server** | Technical articles and solutions | `search_solutions`, `get_article`, `find_related_articles`, `get_common_fixes` |
| **Asset Server** | Hardware/software asset tracking | `lookup_asset`, `check_warranty`, `get_software_licenses`, `get_asset_history` |

**Total: 20 tools** across 5 servers, all discoverable and callable via natural language.

## Repository Structure

```
MCP-tutorial/
├── README.md                                # This file
├── requirements.txt                         # Python dependencies
│
├── 1_MCP_Demo.ipynb                         # Notebook 1 - Exploring MCP servers
├── 2_MCP_resources_prompts_sampling.ipynb   # Notebook 2 - Advanced features
├── 3_MCP_with_Local_Model.ipynb             # Notebook 3 - Local open source model
│
├── ticket_server.py                         # Ticket management MCP server
├── customer_server.py                       # Customer database MCP server
├── billing_server.py                        # Billing system MCP server
├── kb_server.py                             # Knowledge base MCP server
├── asset_server.py                          # Asset tracking MCP server
│
├── mcp_client.py                            # Orchestrator (coordinates all servers)
├── interactive_client.py                    # CLI chat interface
├── sampling_demo.py                         # Sampling pattern demo (notebook 2)
└── quickstart.sh                            # Local setup helper script
```

## Prerequisites

- **Python 3.10+** (for local setup)
- **OpenAI API Key** (for notebook 1 with `interactive_client.py`)
- **Hugging Face account** (free, for notebook 3 to download Gemma)
- **Google Colab with T4 GPU** (recommended, free tier works)

## Additional Resources

- [MCP Official Documentation](https://github.com/anthropics/mcp)
- [MCP Python SDK](https://github.com/anthropics/python-sdk)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

## License

MIT
