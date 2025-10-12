"""
Knowledge Base MCP Server
Provides tools for searching and accessing knowledge base articles and solutions
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


def make_error(message, *, reason=None, hints=None, retryable=False, follow_up_tools=None, **extra):
    """Return a structured error payload for LLM consumption."""
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


# Sample knowledge base articles
KB_ARTICLES = [
    {
        "article_id": "KB-001",
        "title": "Resolving Windows BSOD DRIVER_IRQL_NOT_LESS_OR_EQUAL",
        "category": "Windows Troubleshooting",
        "content": """
# Resolution Steps

1. Boot into Safe Mode
2. Open Device Manager
3. Update or roll back recently updated drivers
4. Run Windows Memory Diagnostic
5. Check for Windows Updates
6. Use Driver Verifier to identify problematic drivers

## Common Causes
- Faulty RAM
- Outdated or incompatible drivers (especially network and graphics)
- Corrupted system files
- Hardware conflicts

## Prevention
- Keep drivers up to date
- Test RAM periodically
- Avoid installing unsigned drivers
""",
        "tags": ["windows", "bsod", "driver", "critical", "blue-screen"],
        "related_products": ["Windows 10", "Windows 11", "Windows Server"],
        "last_updated": "2025-09-15",
        "views": 1523,
        "helpful_count": 142
    },
    {
        "article_id": "KB-002",
        "title": "Linux Disk Space Management - Cleaning /var/log",
        "category": "Linux Administration",
        "content": """
# Quick Fix for Full /var/log

1. Check disk usage: `df -h`
2. Find large files: `du -sh /var/log/* | sort -h`
3. Compress old logs: `gzip /var/log/*.log`
4. Clear journal logs: `journalctl --vacuum-time=7d`

## Configure Log Rotation

Edit /etc/logrotate.conf:
```
/var/log/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## Emergency Cleanup
- `truncate -s 0 /var/log/large-file.log` (use with caution)
- Delete old compressed logs: `find /var/log -name "*.gz" -mtime +30 -delete`
""",
        "tags": ["linux", "disk-space", "logs", "logrotate", "administration"],
        "related_products": ["Ubuntu", "Debian", "CentOS", "RHEL"],
        "last_updated": "2025-10-01",
        "views": 2341,
        "helpful_count": 203
    },
    {
        "article_id": "KB-003",
        "title": "macOS Kernel Panic Troubleshooting Guide",
        "category": "macOS Support",
        "content": """
# Diagnosing Kernel Panics

1. Check panic logs: Console.app → System Reports
2. Identify panic pattern (wake from sleep, specific app, etc.)
3. Note error codes and responsible processes

## Common Solutions

### Reset SMC (System Management Controller)
- Shut down Mac
- Press Shift+Control+Option+Power for 10 seconds
- Release and boot normally

### Reset NVRAM/PRAM
- Restart and hold Command+Option+P+R
- Hold until you hear startup sound twice

### Remove Kernel Extensions
```bash
sudo kextcache --clear-staging
sudo kextcache -i /
```

## Update Related Software
- macOS system updates
- Third-party kernel extensions
- Security software
""",
        "tags": ["macos", "kernel-panic", "troubleshooting", "smc", "nvram"],
        "related_products": ["macOS Sonoma", "macOS Ventura", "macOS Monterey"],
        "last_updated": "2025-09-28",
        "views": 987,
        "helpful_count": 88
    },
    {
        "article_id": "KB-004",
        "title": "Network Performance Troubleshooting on Windows Server",
        "category": "Network Issues",
        "content": """
# Diagnosing Slow Network Performance

## Check Network Adapter Settings
1. Device Manager → Network Adapters
2. Properties → Advanced
3. Verify settings:
   - Speed & Duplex: Auto Negotiation
   - Flow Control: Enabled
   - Jumbo Frames: Match network config

## Disable Power Management
- Uncheck "Allow computer to turn off this device"

## Test Network Speed
```powershell
Test-NetConnection -ComputerName target -Port 445
iperf3 -c server-ip -t 60
```

## Check for Bandwidth Hogs
- Resource Monitor → Network tab
- Performance Monitor → Network Interface counters

## Common Issues
- RSS (Receive Side Scaling) misconfiguration
- Antivirus scanning network traffic
- Outdated NIC drivers
- Network cable issues
""",
        "tags": ["windows-server", "network", "performance", "troubleshooting"],
        "related_products": ["Windows Server 2019", "Windows Server 2022"],
        "last_updated": "2025-10-03",
        "views": 1654,
        "helpful_count": 156
    },
    {
        "article_id": "KB-005",
        "title": "Ubuntu APT Package Manager Issues and Solutions",
        "category": "Linux Administration",
        "content": """
# Fixing APT Update/Upgrade Errors

## Common Error: 404 Not Found
```bash
# Update sources list
sudo sed -i 's/archive.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
sudo apt update
```

## Fix Broken Packages
```bash
sudo apt --fix-broken install
sudo dpkg --configure -a
sudo apt clean
sudo apt update
```

## Reset APT Cache
```bash
sudo rm -rf /var/lib/apt/lists/*
sudo apt clean
sudo apt update
```

## Handle Lock Files
```bash
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/cache/apt/archives/lock
sudo dpkg --configure -a
```

## Repository Management
- Disable problematic PPAs: /etc/apt/sources.list.d/
- Use official mirrors for stability
""",
        "tags": ["linux", "ubuntu", "apt", "package-management", "troubleshooting"],
        "related_products": ["Ubuntu 22.04", "Ubuntu 24.04", "Debian"],
        "last_updated": "2025-09-30",
        "views": 3210,
        "helpful_count": 287
    },
    {
        "article_id": "KB-006",
        "title": "Windows NTFS File System Corruption Repair",
        "category": "Windows Troubleshooting",
        "content": """
# Fixing NTFS Corruption and Freezing

## Run CHKDSK
```cmd
chkdsk C: /f /r /x
```
- /f: Fixes errors
- /r: Locates bad sectors and recovers data
- /x: Forces volume dismount

## Check SMART Status
```powershell
Get-PhysicalDisk | Get-StorageReliabilityCounter
wmic diskdrive get status
```

## Use DISM and SFC
```cmd
DISM /Online /Cleanup-Image /RestoreHealth
sfc /scannow
```

## Event Viewer Checks
- Look for Disk errors (Event ID 7, 11, 15)
- NTFS warnings (Event ID 55)

## Prevention
- Regular disk health monitoring
- Keep disk usage under 80%
- Enable write caching properly
- Update storage controller drivers
""",
        "tags": ["windows", "ntfs", "filesystem", "corruption", "chkdsk"],
        "related_products": ["Windows 10", "Windows 11", "Windows Server"],
        "last_updated": "2025-10-04",
        "views": 1876,
        "helpful_count": 165
    },
    {
        "article_id": "KB-007",
        "title": "SSH Slow Authentication on Linux - Solutions",
        "category": "Linux Administration",
        "content": """
# Fixing Slow SSH Login

## Disable DNS Lookup
Edit /etc/ssh/sshd_config:
```
UseDNS no
```
Restart SSH: `sudo systemctl restart sshd`

## Disable GSSAPI Authentication
In sshd_config:
```
GSSAPIAuthentication no
```

## Client-Side Optimization
Edit ~/.ssh/config or /etc/ssh/ssh_config:
```
GSSAPIAuthentication no
UseDNS no
```

## Check for Slow DNS
```bash
time nslookup your-server
time dig your-server
```

## Verify PAM Modules
Check /etc/pam.d/sshd for slow modules

## Debug Connection
```bash
ssh -v user@host
```
Look for delays in output

## Common Causes
- Reverse DNS timeout
- GSSAPI/Kerberos timeout
- Slow PAM modules
- MTU issues
""",
        "tags": ["linux", "ssh", "authentication", "performance", "network"],
        "related_products": ["Debian", "Ubuntu", "CentOS", "RHEL"],
        "last_updated": "2025-10-05",
        "views": 1432,
        "helpful_count": 128
    },
    {
        "article_id": "KB-008",
        "title": "BitLocker Recovery Key Issues After BIOS Update",
        "category": "Windows Security",
        "content": """
# Resolving BitLocker Recovery Prompt

## Immediate Recovery
1. Enter recovery key from Microsoft account or backup
2. Boot into Windows

## Prevent Future Prompts

### Suspend BitLocker Before BIOS Updates
```powershell
Suspend-BitLocker -MountPoint "C:" -RebootCount 1
```

### Clear TPM and Reinitialize
```powershell
Clear-Tpm
Initialize-Tpm
```

### Re-seal BitLocker to New TPM State
```powershell
manage-bde -protectors -delete C:
manage-bde -protectors -add C: -tpm
```

## Backup Recovery Keys
```powershell
manage-bde -protectors -get C:
# Save to file
manage-bde -protectors -get C: > C:\bitlocker-key.txt
```

## Verify TPM Status
```powershell
Get-Tpm
```

## Best Practices
- Always suspend BitLocker before firmware updates
- Backup recovery keys to multiple locations
- Document TPM version and PCR values
""",
        "tags": ["windows", "bitlocker", "encryption", "tpm", "security"],
        "related_products": ["Windows 10", "Windows 11"],
        "last_updated": "2025-10-02",
        "views": 2103,
        "helpful_count": 189
    },
    {
        "article_id": "KB-009",
        "title": "Active Directory Replication Troubleshooting",
        "category": "Active Directory",
        "content": """
# Fixing AD Replication Issues

## Check Replication Status
```powershell
repadmin /replsummary
repadmin /showrepl
```

## Force Replication
```powershell
repadmin /syncall /AdeP
```

## Verify DNS Configuration
```powershell
dcdiag /test:dns
nslookup -type=SRV _ldap._tcp.dc._msdcs.yourdomain.com
```

## Check Replication Links
```powershell
repadmin /bridgeheads
repadmin /kcc
```

## Common Event IDs
- 2042: Long time since replication
- 1311: Knowledge Consistency Checker errors
- 1925: Failed replication attempt

## Resolution Steps
1. Verify network connectivity between DCs
2. Check DNS is pointing to itself and other DCs
3. Verify time synchronization (w32tm /query /status)
4. Check firewall rules (ports 389, 636, 3268, 88, 135, 445)
5. Force Knowledge Consistency Checker: `repadmin /kcc`

## Reset Replication
```powershell
repadmin /removelingeringobjects
repadmin /replicate DC2 DC1 DC=domain,DC=com
```
""",
        "tags": ["active-directory", "windows-server", "replication", "dcdiag"],
        "related_products": ["Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "last_updated": "2025-09-29",
        "views": 1765,
        "helpful_count": 172
    },
    {
        "article_id": "KB-010",
        "title": "Linux High CPU from kworker Processes",
        "category": "Linux Administration",
        "content": """
# Diagnosing kworker High CPU Usage

## Identify the Culprit
```bash
# Find which kworker is using CPU
top
ps aux | grep kworker

# Check what it's doing
cat /proc/interrupts
watch -n1 "cat /proc/interrupts"
```

## Common Causes

### 1. Buggy Kernel Module
```bash
lsmod
# Remove suspicious modules
sudo modprobe -r module_name
```

### 2. Broken Hardware/Driver
```bash
dmesg | tail -50
journalctl -xef
```

### 3. I/O Wait Issues
```bash
iotop -o
iostat -x 1
```

## Solutions

### Update Kernel
```bash
sudo apt update && sudo apt upgrade linux-generic
```

### Disable Problematic Devices
```bash
# Find IRQ causing issues
cat /proc/interrupts
# Investigate corresponding device
```

### Check for Filesystem Issues
```bash
sudo fsck /dev/sdX
```

## Workqueue Analysis
```bash
echo 1 | sudo tee /sys/module/workqueue/parameters/debug_workqueue
dmesg | grep workqueue
```
""",
        "tags": ["linux", "cpu", "performance", "kworker", "kernel"],
        "related_products": ["Ubuntu", "Debian", "CentOS", "RHEL"],
        "last_updated": "2025-10-04",
        "views": 1543,
        "helpful_count": 134
    }
]




# ============================================================================
# REGULAR PYTHON FUNCTIONS - Can be called directly without MCP
# ============================================================================

def search_solutions(query, category=None, limit=10):
    """Search KB articles. Can be called directly."""
    search_results = search_articles(query, category, limit)
    return {
        "query": query, "category": category,
        "results": [{"article_id": r["article"]["article_id"], "title": r["article"]["title"], "category": r["article"]["category"], "relevance_score": r["relevance_score"], "tags": r["article"]["tags"], "views": r["article"]["views"], "helpful_count": r["article"]["helpful_count"]} for r in search_results],
        "total_count": len(search_results)
    }


def get_article(article_id):
    """Get full article content. Can be called directly."""
    article = next((a for a in KB_ARTICLES if a["article_id"] == article_id), None)
    if not article:
        return make_error(
            f"Article {article_id} not found",
            reason="The knowledge base does not include that article_id.",
            hints=[
                "Call search_solutions with keywords related to the issue.",
                "Use find_related_articles starting from a known article to explore similar topics."
            ],
            retryable=True,
            follow_up_tools=["search_solutions", "find_related_articles"],
            article_id=article_id
        )
    return article.copy()


def find_related_articles(article_id=None, topic=None, limit=5):
    """Find related articles. Can be called directly."""
    related = find_related(article_id, topic, limit)
    if article_id and not related and not any(a["article_id"] == article_id for a in KB_ARTICLES):
        return make_error(
            f"Article {article_id} not found",
            reason="Cannot recommend related content because the source article does not exist.",
            hints=[
                "Run search_solutions using the article topic to find existing entries.",
                "Confirm the article_id format (e.g., KB-001)."
            ],
            retryable=True,
            follow_up_tools=["search_solutions"],
            article_id=article_id
        )
    return {
        "article_id": article_id, "topic": topic,
        "related_articles": [{"article_id": r["article"]["article_id"], "title": r["article"]["title"], "category": r["article"]["category"], "relevance_score": r["relevance_score"], "common_tags": r.get("common_tags", [])} for r in related],
        "total_found": len(related)
    }


def get_common_fixes(product=None, issue_type=None):
    """Get common fixes for product/issue. Can be called directly."""
    fixes = get_common_fixes_internal(product, issue_type)
    return {
        "product": product, "issue_type": issue_type,
        "common_fixes": [{"article_id": f["article"]["article_id"], "title": f["article"]["title"], "category": f["article"]["category"], "relevance_score": f["relevance_score"], "helpful_count": f["article"]["helpful_count"], "tags": f["article"]["tags"]} for f in fixes],
        "total_found": len(fixes)
    }

# Rename internal helper to avoid conflict
def get_common_fixes_internal(product=None, issue_type=None):
    results = []
    for article in KB_ARTICLES:
        score = 0
        if product:
            for prod in article.get("related_products", []):
                if product.lower() in prod.lower():
                    score += 10
                    break
        if issue_type:
            if issue_type.lower() in article["title"].lower():
                score += 8
            for tag in article["tags"]:
                if issue_type.lower() in tag.lower():
                    score += 5
        if score > 0:
            results.append({"article": article, "relevance_score": score})
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:10]


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# Initialize the MCP server
app = Server("knowledge-base-server")


# Helper functions
def search_articles(query, category=None, limit=10):
    """Search articles by keyword in title, content, and tags"""
    results = []
    query_lower = query.lower() if query else ""

    for article in KB_ARTICLES:
        score = 0

        # Search in title (highest weight)
        if query_lower in article["title"].lower():
            score += 10

        # Search in tags
        for tag in article["tags"]:
            if query_lower in tag.lower():
                score += 5

        # Search in content
        if query_lower in article["content"].lower():
            score += 3

        # Search in category
        if query_lower in article["category"].lower():
            score += 4

        # Apply category filter
        if category and article["category"].lower() != category.lower():
            continue

        if score > 0:
            results.append({
                "article": article,
                "relevance_score": score
            })

    # Sort by relevance and limit results
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:limit]


def find_related(article_id=None, topic=None, limit=5):
    """Find related articles based on tags and category"""
    if article_id:
        reference = next((a for a in KB_ARTICLES if a["article_id"] == article_id), None)
        if not reference:
            return []

        ref_tags = set(reference["tags"])
        ref_category = reference["category"]

        related = []
        for article in KB_ARTICLES:
            if article["article_id"] == article_id:
                continue

            score = 0
            common_tags = set(article["tags"]) & ref_tags
            score += len(common_tags) * 3

            if article["category"] == ref_category:
                score += 5

            if score > 0:
                related.append({
                    "article": article,
                    "relevance_score": score,
                    "common_tags": list(common_tags)
                })

        related.sort(key=lambda x: x["relevance_score"], reverse=True)
        return related[:limit]

    elif topic:
        return search_articles(topic, limit=limit)

    return []




@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available knowledge base tools"""
    return [
        Tool(
            name="search_solutions",
            description="Search knowledge base for solutions and articles by keyword or topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query or keywords"},
                    "category": {"type": "string", "description": "Article category filter"},
                    "limit": {"type": "number", "description": "Maximum number of results to return"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_article",
            description="Retrieve the full content of a knowledge base article by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_id": {"type": "string", "description": "Unique article identifier"}
                },
                "required": ["article_id"]
            }
        ),
        Tool(
            name="find_related_articles",
            description="Find articles related to a given article or topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_id": {"type": "string", "description": "Reference article ID"},
                    "topic": {"type": "string", "description": "Topic to find related articles for"},
                    "limit": {"type": "number", "description": "Maximum number of related articles"}
                }
            }
        ),
        Tool(
            name="get_common_fixes",
            description="Get a list of common fixes and solutions for a specific product or issue type",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Product name or identifier"},
                    "issue_type": {"type": "string", "description": "Type of issue (e.g., 'bsod', 'network', 'performance')"}
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls - delegates to regular Python functions"""
    if name == "search_solutions":
        result = search_solutions(arguments.get("query"), arguments.get("category"), int(arguments.get("limit", 10)))
    elif name == "get_article":
        result = get_article(arguments.get("article_id"))
    elif name == "find_related_articles":
        result = find_related_articles(arguments.get("article_id"), arguments.get("topic"), int(arguments.get("limit", 5)))
    elif name == "get_common_fixes":
        result = get_common_fixes(arguments.get("product"), arguments.get("issue_type"))
    else:
        raise ValueError(f"Unknown tool: {name}")
    return [TextContent(type="text", text=json.dumps(result, indent=2))]



async def main():
    """Run the knowledge base server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
