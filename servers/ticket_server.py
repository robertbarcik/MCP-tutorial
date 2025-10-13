"""
Ticket Management MCP Server
Provides tools for searching and managing support tickets
"""

import asyncio
import json
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


def make_error(message, *, reason=None, hints=None, retryable=False, follow_up_tools=None, **extra):
    """Standardise ticket-server error payloads for downstream LLM consumers."""
    payload = {"error": message}
    if reason:
        payload["reason"] = reason
    if hints:
        payload["suggested_actions"] = hints
    payload["retryable"] = retryable
    if follow_up_tools:
        payload["follow_up_tools"] = follow_up_tools
    for key, value in extra.items():
        if value is not None:
            payload[key] = value
    return payload


# Sample ticket data
TICKETS = [
    {
        "ticket_id": "TKT-1001",
        "customer_id": "CUST-001",
        "subject": "Windows 11 BSOD - DRIVER_IRQL_NOT_LESS_OR_EQUAL",
        "description": "User experiencing frequent blue screens with error DRIVER_IRQL_NOT_LESS_OR_EQUAL. Occurs during video calls and heavy multitasking.",
        "status": "open",
        "priority": "high",
        "category": "OS Issues",
        "os": "Windows 11",
        "assignee": "John Doe",
        "created_date": "2025-10-01",
        "last_updated": "2025-10-04",
        "tags": ["bsod", "windows", "driver", "critical"]
    },
    {
        "ticket_id": "TKT-1002",
        "customer_id": "CUST-002",
        "subject": "Linux server disk full - /var/log consuming 95% space",
        "description": "Production Ubuntu 22.04 server has /var/log partition at 95% capacity. Log rotation not working properly.",
        "status": "in_progress",
        "priority": "critical",
        "category": "OS Issues",
        "os": "Linux",
        "assignee": "Jane Smith",
        "created_date": "2025-10-02",
        "last_updated": "2025-10-05",
        "tags": ["linux", "disk-space", "logs", "urgent"]
    },
    {
        "ticket_id": "TKT-1003",
        "customer_id": "CUST-003",
        "subject": "macOS Sonoma kernel panic on wake from sleep",
        "description": "MacBook Pro experiencing kernel panics when waking from sleep mode. Issue started after Sonoma 14.6 update.",
        "status": "resolved",
        "priority": "medium",
        "category": "OS Issues",
        "os": "macOS",
        "assignee": "Bob Wilson",
        "created_date": "2025-09-28",
        "last_updated": "2025-10-03",
        "resolution": "Reset SMC and NVRAM. Updated third-party kernel extensions.",
        "tags": ["macos", "kernel-panic", "sleep", "resolved"]
    },
    {
        "ticket_id": "TKT-1004",
        "customer_id": "CUST-001",
        "subject": "Windows Server 2022 slow network performance",
        "description": "File server experiencing degraded network throughput (10 Mbps instead of 1 Gbps). All hardware checks passed.",
        "status": "open",
        "priority": "high",
        "category": "Network",
        "os": "Windows Server 2022",
        "assignee": "Sarah Lee",
        "created_date": "2025-10-03",
        "last_updated": "2025-10-05",
        "tags": ["windows-server", "network", "performance"]
    },
    {
        "ticket_id": "TKT-1005",
        "customer_id": "CUST-004",
        "subject": "Ubuntu 24.04 apt update failing - repository errors",
        "description": "Cannot update packages. Getting 404 errors from archive.ubuntu.com repositories.",
        "status": "resolved",
        "priority": "medium",
        "category": "Software",
        "os": "Ubuntu 24.04",
        "assignee": "Mike Chen",
        "created_date": "2025-09-30",
        "last_updated": "2025-10-01",
        "resolution": "Updated sources.list to use correct mirror. Refreshed package cache.",
        "tags": ["linux", "apt", "package-management", "resolved"]
    },
    {
        "ticket_id": "TKT-1006",
        "customer_id": "CUST-005",
        "subject": "Windows 10 constant freezing during file operations",
        "description": "System freezes for 30-60 seconds when copying large files or opening File Explorer. Event viewer shows ntfs errors.",
        "status": "in_progress",
        "priority": "high",
        "category": "Storage",
        "os": "Windows 10",
        "assignee": "John Doe",
        "created_date": "2025-10-04",
        "last_updated": "2025-10-05",
        "tags": ["windows", "filesystem", "ntfs", "performance"]
    },
    {
        "ticket_id": "TKT-1007",
        "customer_id": "CUST-002",
        "subject": "Debian server SSH authentication very slow (20+ seconds)",
        "description": "SSH login takes 20-30 seconds to authenticate. After login, everything is fast. No DNS issues detected.",
        "status": "open",
        "priority": "medium",
        "category": "Network",
        "os": "Debian 12",
        "assignee": "Jane Smith",
        "created_date": "2025-10-05",
        "last_updated": "2025-10-05",
        "tags": ["linux", "ssh", "authentication", "performance"]
    },
    {
        "ticket_id": "TKT-1008",
        "customer_id": "CUST-006",
        "subject": "macOS Time Machine backup failing to network drive",
        "description": "Time Machine backups to Synology NAS failing with error 'The backup disk image could not be accessed'.",
        "status": "open",
        "priority": "low",
        "category": "Backup",
        "os": "macOS Ventura",
        "assignee": "Bob Wilson",
        "created_date": "2025-10-01",
        "last_updated": "2025-10-02",
        "tags": ["macos", "backup", "time-machine", "nas"]
    },
    {
        "ticket_id": "TKT-1009",
        "customer_id": "CUST-007",
        "subject": "Windows 11 BitLocker recovery key prompt on every boot",
        "description": "After BIOS update, system prompts for BitLocker recovery key on every startup. TPM shows as enabled in BIOS.",
        "status": "in_progress",
        "priority": "critical",
        "category": "Security",
        "os": "Windows 11",
        "assignee": "Sarah Lee",
        "created_date": "2025-10-02",
        "last_updated": "2025-10-05",
        "tags": ["windows", "bitlocker", "encryption", "tpm"]
    },
    {
        "ticket_id": "TKT-1010",
        "customer_id": "CUST-003",
        "subject": "CentOS 7 EOL - migration planning assistance",
        "description": "Customer needs help planning migration from CentOS 7 (EOL June 2024) to Rocky Linux or AlmaLinux. 12 production servers affected.",
        "status": "open",
        "priority": "high",
        "category": "Migration",
        "os": "CentOS 7",
        "assignee": "Mike Chen",
        "created_date": "2025-09-25",
        "last_updated": "2025-10-04",
        "tags": ["linux", "migration", "centos", "eol"]
    },
    {
        "ticket_id": "TKT-1011",
        "customer_id": "CUST-008",
        "subject": "Windows Server 2019 Active Directory replication failing",
        "description": "AD replication between DC1 and DC2 showing errors. Event ID 2042 - It has been too long since this machine replicated.",
        "status": "resolved",
        "priority": "critical",
        "category": "Active Directory",
        "os": "Windows Server 2019",
        "assignee": "Sarah Lee",
        "created_date": "2025-09-29",
        "last_updated": "2025-09-30",
        "resolution": "Forced replication sync. Fixed DNS entries for domain controllers. Replication now healthy.",
        "tags": ["windows-server", "active-directory", "replication", "resolved"]
    },
    {
        "ticket_id": "TKT-1012",
        "customer_id": "CUST-004",
        "subject": "Ubuntu server high CPU usage - unknown process",
        "description": "Server showing 90%+ CPU usage. Top shows process '[kworker/u8:2]'. System very slow to respond.",
        "status": "in_progress",
        "priority": "high",
        "category": "Performance",
        "os": "Ubuntu 22.04",
        "assignee": "Mike Chen",
        "created_date": "2025-10-04",
        "last_updated": "2025-10-05",
        "tags": ["linux", "cpu", "performance", "kworker"]
    },
    {
        "ticket_id": "TKT-1013",
        "customer_id": "CUST-005",
        "subject": "macOS Monterey unable to connect to VPN",
        "description": "IPSec VPN connection failing after macOS update. Error: 'The VPN connection failed due to unsuccessful domain name resolution'.",
        "status": "open",
        "priority": "medium",
        "category": "Network",
        "os": "macOS Monterey",
        "assignee": "Bob Wilson",
        "created_date": "2025-10-03",
        "last_updated": "2025-10-04",
        "tags": ["macos", "vpn", "ipsec", "dns"]
    },
    {
        "ticket_id": "TKT-1014",
        "customer_id": "CUST-006",
        "subject": "Windows 11 Start Menu and taskbar not responding",
        "description": "Start menu, taskbar, and system tray completely unresponsive. Explorer.exe restart provides only temporary fix (5-10 minutes).",
        "status": "open",
        "priority": "high",
        "category": "OS Issues",
        "os": "Windows 11",
        "assignee": "John Doe",
        "created_date": "2025-10-05",
        "last_updated": "2025-10-05",
        "tags": ["windows", "explorer", "taskbar", "gui"]
    },
    {
        "ticket_id": "TKT-1015",
        "customer_id": "CUST-007",
        "subject": "RHEL 9 - kernel update breaking NVIDIA drivers",
        "description": "After automatic kernel update, NVIDIA drivers fail to load. Display defaults to low resolution. DKMS rebuild failing.",
        "status": "in_progress",
        "priority": "medium",
        "category": "Drivers",
        "os": "RHEL 9",
        "assignee": "Jane Smith",
        "created_date": "2025-10-02",
        "last_updated": "2025-10-05",
        "tags": ["linux", "nvidia", "drivers", "kernel", "dkms"]
    }
]




# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def matches_text_search(ticket, query):
    """Check if ticket matches text search query"""
    query_lower = query.lower()
    searchable_text = " ".join([
        ticket.get("subject", ""),
        ticket.get("description", ""),
        " ".join(ticket.get("tags", []))
    ]).lower()
    return query_lower in searchable_text


def filter_by_date_range(ticket, start_date, end_date):
    """Filter ticket by date range"""
    created = ticket.get("created_date", "")
    if start_date and created < start_date:
        return False
    if end_date and created > end_date:
        return False
    return True


def calculate_metrics(tickets, time_period):
    """Calculate ticket metrics for a time period"""
    # Define time period boundaries
    today = datetime.now()
    if time_period == "last_7_days":
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    elif time_period == "last_30_days":
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    elif time_period == "last_90_days":
        start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    else:
        start_date = "2000-01-01"

    # Filter tickets by date
    period_tickets = [t for t in tickets if t.get("created_date", "") >= start_date]

    # Calculate metrics
    total = len(period_tickets)
    open_count = len([t for t in period_tickets if t["status"] == "open"])
    in_progress = len([t for t in period_tickets if t["status"] == "in_progress"])
    resolved = len([t for t in period_tickets if t["status"] == "resolved"])

    # Calculate average resolution time (simplified)
    resolved_tickets = [t for t in period_tickets if t["status"] == "resolved"]
    avg_resolution_time = 0
    if resolved_tickets:
        total_hours = 0
        for t in resolved_tickets:
            created = datetime.strptime(t["created_date"], "%Y-%m-%d")
            updated = datetime.strptime(t.get("last_updated", t["created_date"]), "%Y-%m-%d")
            hours = (updated - created).total_seconds() / 3600
            total_hours += hours
        avg_resolution_time = round(total_hours / len(resolved_tickets), 1)

    return {
        "time_period": time_period,
        "start_date": start_date,
        "total_tickets": total,
        "open_tickets": open_count,
        "in_progress_tickets": in_progress,
        "resolved_tickets": resolved,
        "avg_resolution_time_hours": avg_resolution_time
    }


def find_similar_tickets(reference_ticket, all_tickets, limit):
    """Find similar tickets based on tags, category, and OS"""
    similar = []
    ref_tags = set(reference_ticket.get("tags", []))
    ref_category = reference_ticket.get("category")
    ref_os = reference_ticket.get("os")

    for ticket in all_tickets:
        if ticket["ticket_id"] == reference_ticket["ticket_id"]:
            continue

        ticket_tags = set(ticket.get("tags", []))
        common_tags = ref_tags & ticket_tags

        # Calculate similarity score
        score = 0
        score += len(common_tags) * 20  # 20 points per common tag
        if ticket.get("category") == ref_category:
            score += 30
        if ticket.get("os") == ref_os:
            score += 20
        if ticket.get("priority") == reference_ticket.get("priority"):
            score += 10

        if score > 0:
            similar.append({
                "ticket": ticket,
                "similarity_score": score,
                "common_tags": list(common_tags)
            })

    # Sort by similarity score and limit
    similar.sort(key=lambda x: x["similarity_score"], reverse=True)
    return similar[:limit]


# ============================================================================
# REGULAR PYTHON FUNCTIONS - Can be called directly without MCP
# ============================================================================

def search_tickets(ticket_id=None, customer_id=None, status=None, priority=None,
                  category=None, os=None, query=None, start_date=None, end_date=None):
    """
    Search for tickets by various criteria.
    
    This is a regular Python function that can be called directly:
        from ticket_server import search_tickets
        results = search_tickets(priority="critical")
    
    Args:
        ticket_id: Specific ticket ID
        customer_id: Filter by customer
        status: Ticket status (open, in_progress, resolved)
        priority: Priority level (critical, high, medium, low)
        category: Ticket category
        os: Operating system (partial match)
        query: Text search (searches subject, description, tags)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        dict: {"tickets": [...], "total_count": int, "filters_applied": {...}}
    """
    # Filter tickets based on criteria
    results = TICKETS.copy()

    # Apply filters
    if ticket_id:
        results = [t for t in results if t["ticket_id"] == ticket_id]

    if customer_id:
        results = [t for t in results if t["customer_id"] == customer_id]

    if status:
        results = [t for t in results if t["status"] == status]

    if priority:
        results = [t for t in results if t["priority"] == priority]

    if category:
        results = [t for t in results if t.get("category") == category]

    if os:
        results = [t for t in results if os.lower() in t.get("os", "").lower()]

    if query:
        results = [t for t in results if matches_text_search(t, query)]

    if start_date or end_date:
        results = [
            t for t in results
            if filter_by_date_range(t, start_date, end_date)
        ]

    return {
        "tickets": results,
        "total_count": len(results),
        "filters_applied": {
            k: v for k, v in {
                "ticket_id": ticket_id, "customer_id": customer_id, "status": status,
                "priority": priority, "category": category, "os": os, "query": query,
                "start_date": start_date, "end_date": end_date
            }.items() if v
        }
    }


def get_ticket_details(ticket_id):
    """
    Get detailed information about a specific ticket.
    
    Can be called directly:
        from ticket_server import get_ticket_details
        ticket = get_ticket_details("TKT-1001")
    
    Args:
        ticket_id: Unique ticket identifier
    
    Returns:
        dict: Ticket details or error dict
    """
    ticket = next((t for t in TICKETS if t["ticket_id"] == ticket_id), None)

    if not ticket:
        return make_error(
            f"Ticket {ticket_id} not found",
            reason="The ticket_id did not match any tickets in the dataset.",
            hints=[
                "Call search_tickets with customer_id or priority filters to rediscover the ticket.",
                "Verify the ticket_id format (e.g., TKT-1001)."
            ],
            retryable=True,
            follow_up_tools=["search_tickets"],
            ticket_id=ticket_id
        )
    return ticket.copy()


def get_ticket_metrics(time_period="last_7_days"):
    """
    Calculate ticket metrics for a time period.
    
    Can be called directly:
        from ticket_server import get_ticket_metrics
        metrics = get_ticket_metrics("last_30_days")
    
    Args:
        time_period: Time period (last_7_days, last_30_days, last_90_days)
    
    Returns:
        dict: Metrics including counts, resolution time, etc.
    """
    return calculate_metrics(TICKETS, time_period)


def find_similar_tickets_to(ticket_id, limit=5):
    """
    Find tickets similar to a given ticket.
    
    Can be called directly:
        from ticket_server import find_similar_tickets_to
        similar = find_similar_tickets_to("TKT-1001", limit=10)
    
    Args:
        ticket_id: Reference ticket ID
        limit: Maximum number of similar tickets to return
    
    Returns:
        dict: Similar tickets with relevance scores
    """
    reference_ticket = next((t for t in TICKETS if t["ticket_id"] == ticket_id), None)

    if not reference_ticket:
        return make_error(
            f"Ticket {ticket_id} not found",
            reason="Cannot compute similarity because the reference ticket is missing.",
            hints=[
                "Search for tickets by subject or tags using search_tickets.",
                "Make sure the ticket_id belongs to the same dataset (TKT-####)."
            ],
            retryable=True,
            follow_up_tools=["search_tickets"],
            ticket_id=ticket_id
        )

    similar = find_similar_tickets(reference_ticket, TICKETS, int(limit))
    return {
        "reference_ticket_id": ticket_id,
        "reference_ticket_subject": reference_ticket.get("subject"),
        "similar_tickets": [
            {
                "ticket_id": s["ticket"]["ticket_id"],
                "subject": s["ticket"]["subject"],
                "status": s["ticket"]["status"],
                "priority": s["ticket"]["priority"],
                "similarity_score": s["similarity_score"],
                "common_tags": s["common_tags"]
            }
            for s in similar
        ],
        "total_found": len(similar)
    }


# ============================================================================
# MCP SERVER SETUP - Wraps the above functions for MCP protocol
# ============================================================================

# Initialize the MCP server
app = Server("ticket-management-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available ticket management tools"""
    return [
        Tool(
            name="search_tickets",
            description="Search for tickets by various criteria (status, priority, assignee, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text search query (searches subject, description, tags)"},
                    "ticket_id": {"type": "string", "description": "Specific ticket ID"},
                    "customer_id": {"type": "string", "description": "Filter by customer ID"},
                    "status": {"type": "string", "description": "Ticket status (open, in_progress, resolved)"},
                    "priority": {"type": "string", "description": "Priority level (critical, high, medium, low)"},
                    "category": {"type": "string", "description": "Ticket category"},
                    "os": {"type": "string", "description": "Operating system"},
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="get_ticket_details",
            description="Retrieve detailed information about a specific ticket by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "Unique ticket identifier"}
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="get_ticket_metrics",
            description="Get metrics and statistics for tickets (resolution time, volume, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_period": {"type": "string", "description": "Time period (last_7_days, last_30_days, last_90_days)"}
                }
            }
        ),
        Tool(
            name="find_similar_tickets",
            description="Find tickets similar to a given ticket based on content and metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "Reference ticket ID"},
                    "limit": {"type": "number", "description": "Maximum number of similar tickets to return"}
                },
                "required": ["ticket_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls - delegates to regular Python functions"""

    if name == "search_tickets":
        result = search_tickets(**arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_ticket_details":
        result = get_ticket_details(arguments.get("ticket_id"))
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_ticket_metrics":
        result = get_ticket_metrics(arguments.get("time_period", "last_7_days"))
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "find_similar_tickets":
        result = find_similar_tickets_to(
            arguments.get("ticket_id"),
            arguments.get("limit", 5)
        )
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the ticket management server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
