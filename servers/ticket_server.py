"""
Ticket server for the IT help desk.

The file has four parts, in this order:
  1. DATA            the "database" is a list of dicts
  2. PRIVATE HELPERS small functions the tools use (underscore = not a tool)
  3. TOOLS           plain Python functions; importable and callable without MCP
  4. MCP LAYER       the only part that knows MCP exists

Run it as a server:   python servers/ticket_server.py          (stdio)
                      python servers/ticket_server.py --http   (Streamable HTTP on port 8000)
Import it as a module: from servers.ticket_server import search_tickets
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # so `from common import ...` works both imported and as a script
from common import READ_ONLY, WRITES, days_ago, make_error
from mcp.server import MCPServer

# =============================================================================
# 1. DATA
# =============================================================================

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
        "created_date": days_ago(4),
        "last_updated": days_ago(1),
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
        "created_date": days_ago(3),
        "last_updated": days_ago(0),
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
        "created_date": days_ago(7),
        "last_updated": days_ago(2),
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
        "created_date": days_ago(2),
        "last_updated": days_ago(0),
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
        "created_date": days_ago(5),
        "last_updated": days_ago(4),
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
        "created_date": days_ago(1),
        "last_updated": days_ago(0),
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
        "created_date": days_ago(0),
        "last_updated": days_ago(0),
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
        "created_date": days_ago(4),
        "last_updated": days_ago(3),
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
        "created_date": days_ago(3),
        "last_updated": days_ago(0),
        "tags": ["windows", "bitlocker", "encryption", "tpm"]
    },
    {
        "ticket_id": "TKT-1010",
        "customer_id": "CUST-003",
        "subject": "CentOS 7 EOL - migration planning assistance",
        "description": "Customer needs help planning migration from CentOS 7 (end of life) to Rocky Linux or AlmaLinux. 12 production servers affected.",
        "status": "open",
        "priority": "high",
        "category": "Migration",
        "os": "CentOS 7",
        "assignee": "Mike Chen",
        "created_date": days_ago(10),
        "last_updated": days_ago(1),
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
        "created_date": days_ago(6),
        "last_updated": days_ago(5),
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
        "created_date": days_ago(1),
        "last_updated": days_ago(0),
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
        "created_date": days_ago(2),
        "last_updated": days_ago(1),
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
        "created_date": days_ago(0),
        "last_updated": days_ago(0),
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
        "created_date": days_ago(3),
        "last_updated": days_ago(0),
        "tags": ["linux", "nvidia", "drivers", "kernel", "dkms"]
    }
]

VALID_STATUSES = ("open", "in_progress", "resolved")

# =============================================================================
# 2. PRIVATE HELPERS
# =============================================================================

def _matches_text(ticket, query):
    """True if the query appears in the subject, description or tags."""
    haystack = " ".join([
        ticket.get("subject", ""),
        ticket.get("description", ""),
        " ".join(ticket.get("tags", []))
    ]).lower()
    return query.lower() in haystack


def _in_date_range(ticket, start_date, end_date):
    created = ticket.get("created_date", "")
    if start_date and created < start_date:
        return False
    if end_date and created > end_date:
        return False
    return True


def _calculate_metrics(tickets, time_period):
    today = datetime.now()
    if time_period == "last_7_days":
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    elif time_period == "last_30_days":
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    elif time_period == "last_90_days":
        start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    else:
        start_date = "2000-01-01"

    period_tickets = [t for t in tickets if t.get("created_date", "") >= start_date]
    resolved_tickets = [t for t in period_tickets if t["status"] == "resolved"]

    avg_resolution_time = 0
    if resolved_tickets:
        total_hours = 0
        for t in resolved_tickets:
            created = datetime.strptime(t["created_date"], "%Y-%m-%d")
            updated = datetime.strptime(t.get("last_updated", t["created_date"]), "%Y-%m-%d")
            total_hours += (updated - created).total_seconds() / 3600
        avg_resolution_time = round(total_hours / len(resolved_tickets), 1)

    return {
        "time_period": time_period,
        "start_date": start_date,
        "total_tickets": len(period_tickets),
        "open_tickets": len([t for t in period_tickets if t["status"] == "open"]),
        "in_progress_tickets": len([t for t in period_tickets if t["status"] == "in_progress"]),
        "resolved_tickets": len(resolved_tickets),
        "avg_resolution_time_hours": avg_resolution_time
    }


def _rank_similar(reference_ticket, all_tickets, limit):
    """Score other tickets by shared tags, category, OS and priority."""
    similar = []
    ref_tags = set(reference_ticket.get("tags", []))
    for ticket in all_tickets:
        if ticket["ticket_id"] == reference_ticket["ticket_id"]:
            continue
        common_tags = ref_tags & set(ticket.get("tags", []))
        score = len(common_tags) * 20
        if ticket.get("category") == reference_ticket.get("category"):
            score += 30
        if ticket.get("os") == reference_ticket.get("os"):
            score += 20
        if ticket.get("priority") == reference_ticket.get("priority"):
            score += 10
        if score > 0:
            similar.append({"ticket": ticket, "similarity_score": score, "common_tags": list(common_tags)})
    similar.sort(key=lambda x: x["similarity_score"], reverse=True)
    return similar[:limit]


def _find_ticket(ticket_id):
    return next((t for t in TICKETS if t["ticket_id"] == ticket_id), None)

# =============================================================================
# 3. TOOLS - plain Python functions, importable without MCP
# =============================================================================

def search_tickets(query: str | None = None, ticket_id: str | None = None, customer_id: str | None = None,
                   status: str | None = None, priority: str | None = None, category: str | None = None,
                   os: str | None = None, start_date: str | None = None, end_date: str | None = None) -> dict:
    """Search support tickets by any combination of filters. All filters are optional;
    with no filters you get every ticket.

    Args:
        query: text search over subject, description and tags (e.g. "bitlocker")
        ticket_id: exact ticket ID (e.g. TKT-1001)
        customer_id: only tickets of this customer (e.g. CUST-001)
        status: open, in_progress or resolved
        priority: critical, high, medium or low
        category: e.g. Network, Security, OS Issues
        os: operating system, partial match (e.g. "Windows", "Ubuntu")
        start_date, end_date: created between these dates (YYYY-MM-DD)

    Returns:
        {"tickets": [...], "total_count": int, "filters_applied": {...}}
    """
    results = list(TICKETS)
    if ticket_id:
        results = [t for t in results if t["ticket_id"] == ticket_id]
    if customer_id:
        results = [t for t in results if t["customer_id"] == customer_id]
    if status:
        results = [t for t in results if t["status"] == status]
    if priority:
        results = [t for t in results if t["priority"] == priority]
    if category:
        results = [t for t in results if t.get("category", "").lower() == category.lower()]
    if os:
        results = [t for t in results if os.lower() in t.get("os", "").lower()]
    if query:
        results = [t for t in results if _matches_text(t, query)]
    if start_date or end_date:
        results = [t for t in results if _in_date_range(t, start_date, end_date)]

    filters = {"query": query, "ticket_id": ticket_id, "customer_id": customer_id, "status": status,
               "priority": priority, "category": category, "os": os, "start_date": start_date, "end_date": end_date}
    return {
        "tickets": results,
        "total_count": len(results),
        "filters_applied": {k: v for k, v in filters.items() if v}
    }


def get_ticket_details(ticket_id: str) -> dict:
    """Get the full record of one ticket by its ID.

    Args:
        ticket_id: unique ticket identifier (e.g. TKT-1001)

    Returns:
        the ticket dict, or an error dict with suggested next steps
    """
    ticket = _find_ticket(ticket_id)
    if not ticket:
        return make_error(
            f"Ticket {ticket_id} not found",
            reason="The ticket_id did not match any tickets in the dataset.",
            hints=[
                "Call search_tickets with a query, customer_id or priority filter to rediscover the ticket.",
                "Verify the ticket_id format (e.g., TKT-1001)."
            ],
            retryable=True,
            follow_up_tools=["search_tickets"],
            ticket_id=ticket_id
        )
    return dict(ticket)


def get_ticket_metrics(time_period: str = "last_7_days") -> dict:
    """Ticket counts and average resolution time for a time window.

    Args:
        time_period: last_7_days, last_30_days or last_90_days

    Returns:
        {"total_tickets", "open_tickets", "in_progress_tickets", "resolved_tickets", "avg_resolution_time_hours", ...}
    """
    return _calculate_metrics(TICKETS, time_period)


def find_similar_tickets(ticket_id: str, limit: int = 5) -> dict:
    """Find tickets similar to a given ticket (shared tags, category, OS, priority).

    Args:
        ticket_id: the reference ticket (e.g. TKT-1001)
        limit: maximum number of similar tickets to return

    Returns:
        {"reference_ticket_id", "similar_tickets": [{"ticket_id", "subject", "similarity_score", ...}], "total_found"}
    """
    reference = _find_ticket(ticket_id)
    if not reference:
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
    similar = _rank_similar(reference, TICKETS, int(limit))
    return {
        "reference_ticket_id": ticket_id,
        "reference_ticket_subject": reference.get("subject"),
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


def update_ticket_status(ticket_id: str, status: str) -> dict:
    """Change the status of a ticket. This CHANGES data (in memory, for the duration
    of the server process).

    Args:
        ticket_id: the ticket to update (e.g. TKT-1004)
        status: the new status: open, in_progress or resolved

    Returns:
        the updated ticket, or an error dict
    """
    ticket = _find_ticket(ticket_id)
    if not ticket:
        return make_error(
            f"Ticket {ticket_id} not found",
            reason="Only existing tickets can be updated.",
            hints=["Call search_tickets to find the right ticket_id first."],
            retryable=True,
            follow_up_tools=["search_tickets"],
            ticket_id=ticket_id
        )
    if status not in VALID_STATUSES:
        return make_error(
            f"Invalid status '{status}'",
            reason="Status must be one of the known values.",
            hints=[f"Use one of: {', '.join(VALID_STATUSES)}."],
            retryable=True,
            valid_statuses=list(VALID_STATUSES)
        )
    previous = ticket["status"]
    ticket["status"] = status
    ticket["last_updated"] = days_ago(0)
    return {"ticket_id": ticket_id, "previous_status": previous, "status": status, "last_updated": ticket["last_updated"]}

# =============================================================================
# 4. MCP LAYER - the only part of this file that knows MCP exists
# =============================================================================
# Never print() in a server: on stdio, stdout IS the wire to the client.

mcp = MCPServer("tickets")

mcp.tool(annotations=READ_ONLY)(search_tickets)
mcp.tool(annotations=READ_ONLY)(get_ticket_details)
mcp.tool(annotations=READ_ONLY)(get_ticket_metrics)
mcp.tool(annotations=READ_ONLY)(find_similar_tickets)
mcp.tool(annotations=WRITES)(update_ticket_status)

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)   # http://127.0.0.1:8000/mcp
    else:
        mcp.run()                                                          # stdio: the host starts us
