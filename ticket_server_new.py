"""
Ticket Management MCP Server
Provides tools for searching and managing support tickets

Functions can be called directly OR via MCP protocol
"""

import asyncio
import json
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Sample ticket data - can be imported by other modules
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

