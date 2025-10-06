"""
Customer Database MCP Server
Provides tools for accessing customer information and account details
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Sample customer data
CUSTOMERS = [
    {
        "customer_id": "CUST-001",
        "company_name": "TechCorp Industries",
        "email": "support@techcorp.com",
        "phone": "+1-555-0101",
        "tier": "premium",
        "status": "active",
        "account_manager": "Alice Johnson",
        "created_date": "2023-05-15",
        "last_activity": "2025-10-05",
        "sla_terms": {
            "level": "platinum",
            "response_time_hours": 1,
            "resolution_time_hours": 8,
            "support_hours": "24/7",
            "dedicated_support": True,
            "escalation_contacts": ["manager@techcorp.com", "cto@techcorp.com"]
        },
        "contacts": [
            {"name": "David Chen", "email": "david.chen@techcorp.com", "role": "IT Director", "phone": "+1-555-0102"},
            {"name": "Maria Garcia", "email": "maria.g@techcorp.com", "role": "Systems Administrator", "phone": "+1-555-0103"}
        ]
    },
    {
        "customer_id": "CUST-002",
        "company_name": "DataFlow Solutions",
        "email": "it@dataflow.io",
        "phone": "+1-555-0201",
        "tier": "premium",
        "status": "active",
        "account_manager": "Bob Martinez",
        "created_date": "2022-11-20",
        "last_activity": "2025-10-05",
        "sla_terms": {
            "level": "gold",
            "response_time_hours": 2,
            "resolution_time_hours": 16,
            "support_hours": "24/7",
            "dedicated_support": True,
            "escalation_contacts": ["ops@dataflow.io"]
        },
        "contacts": [
            {"name": "Sarah Williams", "email": "sarah.w@dataflow.io", "role": "DevOps Lead", "phone": "+1-555-0202"},
            {"name": "James Liu", "email": "james.l@dataflow.io", "role": "Infrastructure Manager", "phone": "+1-555-0203"}
        ]
    },
    {
        "customer_id": "CUST-003",
        "company_name": "Global Enterprises Ltd",
        "email": "helpdesk@globalent.com",
        "phone": "+1-555-0301",
        "tier": "standard",
        "status": "active",
        "account_manager": "Carol White",
        "created_date": "2024-01-10",
        "last_activity": "2025-10-03",
        "sla_terms": {
            "level": "silver",
            "response_time_hours": 4,
            "resolution_time_hours": 24,
            "support_hours": "Business hours (9-5 EST)",
            "dedicated_support": False,
            "escalation_contacts": ["it.manager@globalent.com"]
        },
        "contacts": [
            {"name": "Robert Taylor", "email": "robert.t@globalent.com", "role": "IT Manager", "phone": "+1-555-0302"}
        ]
    },
    {
        "customer_id": "CUST-004",
        "company_name": "Innovate Systems",
        "email": "support@innovatesys.net",
        "phone": "+1-555-0401",
        "tier": "standard",
        "status": "active",
        "account_manager": "Alice Johnson",
        "created_date": "2023-08-22",
        "last_activity": "2025-10-05",
        "sla_terms": {
            "level": "silver",
            "response_time_hours": 4,
            "resolution_time_hours": 24,
            "support_hours": "Extended hours (7-9 EST)",
            "dedicated_support": False,
            "escalation_contacts": ["admin@innovatesys.net"]
        },
        "contacts": [
            {"name": "Emily Brown", "email": "emily.b@innovatesys.net", "role": "Systems Engineer", "phone": "+1-555-0402"},
            {"name": "Michael Davis", "email": "michael.d@innovatesys.net", "role": "Network Admin", "phone": "+1-555-0403"}
        ]
    },
    {
        "customer_id": "CUST-005",
        "company_name": "CloudFirst Inc",
        "email": "tech@cloudfirst.cloud",
        "phone": "+1-555-0501",
        "tier": "premium",
        "status": "active",
        "account_manager": "Bob Martinez",
        "created_date": "2022-03-15",
        "last_activity": "2025-10-05",
        "sla_terms": {
            "level": "platinum",
            "response_time_hours": 1,
            "resolution_time_hours": 8,
            "support_hours": "24/7",
            "dedicated_support": True,
            "escalation_contacts": ["ceo@cloudfirst.cloud", "cto@cloudfirst.cloud"]
        },
        "contacts": [
            {"name": "Lisa Anderson", "email": "lisa.a@cloudfirst.cloud", "role": "CTO", "phone": "+1-555-0502"},
            {"name": "Tom Wilson", "email": "tom.w@cloudfirst.cloud", "role": "Senior DevOps", "phone": "+1-555-0503"}
        ]
    },
    {
        "customer_id": "CUST-006",
        "company_name": "SecureNet Partners",
        "email": "info@securenet.biz",
        "phone": "+1-555-0601",
        "tier": "basic",
        "status": "active",
        "account_manager": "Carol White",
        "created_date": "2024-06-01",
        "last_activity": "2025-10-02",
        "sla_terms": {
            "level": "bronze",
            "response_time_hours": 8,
            "resolution_time_hours": 48,
            "support_hours": "Business hours (9-5 EST)",
            "dedicated_support": False,
            "escalation_contacts": []
        },
        "contacts": [
            {"name": "Kevin Martinez", "email": "kevin.m@securenet.biz", "role": "IT Coordinator", "phone": "+1-555-0602"}
        ]
    },
    {
        "customer_id": "CUST-007",
        "company_name": "MegaCorp International",
        "email": "itsupport@megacorp.com",
        "phone": "+1-555-0701",
        "tier": "premium",
        "status": "active",
        "account_manager": "Alice Johnson",
        "created_date": "2021-09-10",
        "last_activity": "2025-10-05",
        "sla_terms": {
            "level": "gold",
            "response_time_hours": 2,
            "resolution_time_hours": 12,
            "support_hours": "24/7",
            "dedicated_support": True,
            "escalation_contacts": ["director@megacorp.com"]
        },
        "contacts": [
            {"name": "Patricia Lee", "email": "patricia.l@megacorp.com", "role": "Director of IT", "phone": "+1-555-0702"},
            {"name": "Daniel Kim", "email": "daniel.k@megacorp.com", "role": "Senior SysAdmin", "phone": "+1-555-0703"},
            {"name": "Jennifer Park", "email": "jennifer.p@megacorp.com", "role": "Network Specialist", "phone": "+1-555-0704"}
        ]
    },
    {
        "customer_id": "CUST-008",
        "company_name": "StartupHub Ventures",
        "email": "tech@startuphub.io",
        "phone": "+1-555-0801",
        "tier": "standard",
        "status": "active",
        "account_manager": "Bob Martinez",
        "created_date": "2024-02-28",
        "last_activity": "2025-09-30",
        "sla_terms": {
            "level": "silver",
            "response_time_hours": 4,
            "resolution_time_hours": 24,
            "support_hours": "Extended hours (7-9 EST)",
            "dedicated_support": False,
            "escalation_contacts": ["founder@startuphub.io"]
        },
        "contacts": [
            {"name": "Alex Thompson", "email": "alex.t@startuphub.io", "role": "Tech Lead", "phone": "+1-555-0802"}
        ]
    }
]




# ============================================================================
# REGULAR PYTHON FUNCTIONS - Can be called directly without MCP
# ============================================================================

def lookup_customer(customer_id=None, email=None, company_name=None):
    """
    Look up customer information by ID, email, or company name.
    
    Can be called directly:
        from customer_server import lookup_customer
        customer = lookup_customer(customer_id="CUST-001")
    
    Args:
        customer_id: Unique customer identifier
        email: Customer email address
        company_name: Company name (partial match supported)
    
    Returns:
        dict: Customer information or error dict
    """
    customer = search_customer(customer_id=customer_id, email=email, company_name=company_name)
    
    if not customer:
        return {
            "error": "Customer not found",
            "search_criteria": {k: v for k, v in {"customer_id": customer_id, "email": email, "company_name": company_name}.items() if v}
        }
    else:
        return customer.copy()


def check_customer_status(customer_id):
    """
    Check the current status of a customer account.
    
    Can be called directly:
        from customer_server import check_customer_status
        status = check_customer_status("CUST-001")
    
    Args:
        customer_id: Unique customer identifier
    
    Returns:
        dict: Customer status information or error dict
    """
    customer = search_customer(customer_id=customer_id)
    
    if not customer:
        return {
            "error": f"Customer {customer_id} not found",
            "customer_id": customer_id
        }
    else:
        return {
            "customer_id": customer["customer_id"],
            "company_name": customer["company_name"],
            "status": customer["status"],
            "tier": customer["tier"],
            "account_manager": customer["account_manager"],
            "last_activity": customer["last_activity"],
            "created_date": customer["created_date"]
        }


def get_sla_terms(customer_id):
    """
    Retrieve SLA terms and conditions for a customer.
    
    Can be called directly:
        from customer_server import get_sla_terms
        sla = get_sla_terms("CUST-001")
    
    Args:
        customer_id: Unique customer identifier
    
    Returns:
        dict: SLA terms or error dict
    """
    customer = search_customer(customer_id=customer_id)
    
    if not customer:
        return {
            "error": f"Customer {customer_id} not found",
            "customer_id": customer_id
        }
    else:
        return {
            "customer_id": customer["customer_id"],
            "company_name": customer["company_name"],
            "tier": customer["tier"],
            "sla_terms": customer["sla_terms"]
        }


def list_customer_contacts(customer_id):
    """
    Get all contacts associated with a customer account.
    
    Can be called directly:
        from customer_server import list_customer_contacts
        contacts = list_customer_contacts("CUST-001")
    
    Args:
        customer_id: Unique customer identifier
    
    Returns:
        dict: List of contacts or error dict
    """
    customer = search_customer(customer_id=customer_id)
    
    if not customer:
        return {
            "error": f"Customer {customer_id} not found",
            "customer_id": customer_id
        }
    else:
        return {
            "customer_id": customer["customer_id"],
            "company_name": customer["company_name"],
            "contacts": customer["contacts"],
            "total_contacts": len(customer["contacts"])
        }


# ============================================================================
# MCP SERVER SETUP - Wraps the above functions for MCP protocol
# ============================================================================

# Initialize the MCP server
app = Server("customer-database-server")


# Helper functions
def search_customer(customer_id=None, email=None, company_name=None):
    """Search for a customer by various criteria"""
    for customer in CUSTOMERS:
        if customer_id and customer["customer_id"] == customer_id:
            return customer
        if email and customer["email"].lower() == email.lower():
            return customer
        if company_name and company_name.lower() in customer["company_name"].lower():
            return customer
    return None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available customer database tools"""
    return [
        Tool(
            name="lookup_customer",
            description="Look up customer information by customer ID, email, or company name",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Unique customer identifier"},
                    "email": {"type": "string", "description": "Customer email address"},
                    "company_name": {"type": "string", "description": "Company name (partial match supported)"}
                }
            }
        ),
        Tool(
            name="check_customer_status",
            description="Check the current status of a customer account (active, suspended, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Unique customer identifier"}
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="get_sla_terms",
            description="Retrieve Service Level Agreement terms and conditions for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Unique customer identifier"}
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="list_customer_contacts",
            description="Get a list of all contacts associated with a customer account",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Unique customer identifier"}
                },
                "required": ["customer_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls - delegates to regular Python functions"""

    if name == "lookup_customer":
        result = lookup_customer(**arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "check_customer_status":
        result = check_customer_status(arguments.get("customer_id"))
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_sla_terms":
        result = get_sla_terms(arguments.get("customer_id"))
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "list_customer_contacts":
        result = list_customer_contacts(arguments.get("customer_id"))
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")



async def main():
    """Run the customer database server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
