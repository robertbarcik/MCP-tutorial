"""
Customer server for the IT help desk: customer records, SLA terms, contacts.

Same four parts as every server in this course:
  1. DATA  2. PRIVATE HELPERS  3. TOOLS (plain functions)  4. MCP LAYER

Run:    python servers/customer_server.py [--http]
Import: from servers.customer_server import lookup_customer
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import READ_ONLY, days_ago, make_error
from mcp.server import MCPServer

# =============================================================================
# 1. DATA
# =============================================================================

CUSTOMERS = [
    {
        "customer_id": "CUST-001",
        "company_name": "TechCorp Industries",
        "email": "support@techcorp.com",
        "phone": "+1-555-0101",
        "tier": "premium",
        "status": "active",
        "account_manager": "Alice Johnson",
        "created_date": days_ago(870),
        "last_activity": days_ago(0),
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
        "created_date": days_ago(1050),
        "last_activity": days_ago(0),
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
        "created_date": days_ago(630),
        "last_activity": days_ago(2),
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
        "created_date": days_ago(780),
        "last_activity": days_ago(0),
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
        "created_date": days_ago(1300),
        "last_activity": days_ago(0),
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
        "created_date": days_ago(470),
        "last_activity": days_ago(3),
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
        "created_date": days_ago(1480),
        "last_activity": days_ago(0),
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
        "created_date": days_ago(590),
        "last_activity": days_ago(5),
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

# =============================================================================
# 2. PRIVATE HELPERS
# =============================================================================

def _find_customer(customer_id=None, email=None, company_name=None):
    """First customer matching any of the given identifiers, or None."""
    for customer in CUSTOMERS:
        if customer_id and customer["customer_id"] == customer_id:
            return customer
        if email and customer["email"].lower() == email.lower():
            return customer
        if company_name and company_name.lower() in customer["company_name"].lower():
            return customer
    return None


def _not_found(customer_id, reason, hints):
    return make_error(
        f"Customer {customer_id} not found",
        reason=reason,
        hints=hints,
        retryable=True,
        follow_up_tools=["lookup_customer"],
        customer_id=customer_id
    )

# =============================================================================
# 3. TOOLS - plain Python functions, importable without MCP
# =============================================================================

def lookup_customer(customer_id: str | None = None, email: str | None = None, company_name: str | None = None) -> dict:
    """Look up one customer by ID, email or company name (partial match on the name).

    Args:
        customer_id: unique customer identifier (e.g. CUST-001)
        email: the customer's support email address
        company_name: company name or part of it (e.g. "TechCorp")

    Returns:
        the customer record (with SLA terms and contacts), or an error dict
    """
    customer = _find_customer(customer_id=customer_id, email=email, company_name=company_name)
    if not customer:
        return make_error(
            "Customer not found",
            reason="No customer record matched the provided identifiers.",
            hints=[
                "Double-check the customer_id, email, or company_name values.",
                "Try company_name with a partial match (e.g., 'TechCorp')."
            ],
            retryable=True,
            follow_up_tools=["lookup_customer"],
            search_criteria={k: v for k, v in {"customer_id": customer_id, "email": email, "company_name": company_name}.items() if v}
        )
    return dict(customer)


def check_customer_status(customer_id: str) -> dict:
    """Short status summary of a customer account: status, tier, account manager, last activity.

    Args:
        customer_id: unique customer identifier (e.g. CUST-001)
    """
    customer = _find_customer(customer_id=customer_id)
    if not customer:
        return _not_found(customer_id, "The requested customer_id is not present in the dataset.", [
            "Call lookup_customer with company_name or email to rediscover the customer_id."
        ])
    return {
        "customer_id": customer["customer_id"],
        "company_name": customer["company_name"],
        "status": customer["status"],
        "tier": customer["tier"],
        "account_manager": customer["account_manager"],
        "last_activity": customer["last_activity"],
        "created_date": customer["created_date"]
    }


def get_sla_terms(customer_id: str) -> dict:
    """The service level agreement of a customer: response and resolution times, support hours, escalation contacts.

    Args:
        customer_id: unique customer identifier (e.g. CUST-001)
    """
    customer = _find_customer(customer_id=customer_id)
    if not customer:
        return _not_found(customer_id, "SLA information is only available for known customers.", [
            "Call lookup_customer first to confirm the customer_id."
        ])
    return {
        "customer_id": customer["customer_id"],
        "company_name": customer["company_name"],
        "tier": customer["tier"],
        "sla_terms": customer["sla_terms"]
    }


def list_customer_contacts(customer_id: str) -> dict:
    """All named contacts of a customer with their roles, emails and phone numbers.

    Args:
        customer_id: unique customer identifier (e.g. CUST-001)
    """
    customer = _find_customer(customer_id=customer_id)
    if not customer:
        return _not_found(customer_id, "Contacts can only be listed for customers that exist in the dataset.", [
            "Run lookup_customer to confirm the customer_id or discover alternatives."
        ])
    return {
        "customer_id": customer["customer_id"],
        "company_name": customer["company_name"],
        "contacts": customer["contacts"],
        "total_contacts": len(customer["contacts"])
    }

# =============================================================================
# 4. MCP LAYER - the only part of this file that knows MCP exists
# =============================================================================
# Never print() in a server: on stdio, stdout IS the wire to the client.

mcp = MCPServer("customers")

mcp.tool(annotations=READ_ONLY)(lookup_customer)
mcp.tool(annotations=READ_ONLY)(check_customer_status)
mcp.tool(annotations=READ_ONLY)(get_sla_terms)
mcp.tool(annotations=READ_ONLY)(list_customer_contacts)

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run()
