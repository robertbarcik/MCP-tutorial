"""
Knowledge base server for the IT help desk: troubleshooting articles.

Same four parts as every server in this course:
  1. DATA  2. PRIVATE HELPERS  3. TOOLS (plain functions)  4. MCP LAYER

Run:    python servers/kb_server.py [--http]
Import: from servers.kb_server import search_solutions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import READ_ONLY, days_ago, make_error
from mcp.server import MCPServer

# =============================================================================
# 1. DATA
# =============================================================================

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
        "last_updated": days_ago(25),
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
        "last_updated": days_ago(9),
        "views": 2341,
        "helpful_count": 203
    },
    {
        "article_id": "KB-003",
        "title": "macOS Kernel Panic Troubleshooting Guide",
        "category": "macOS Support",
        "content": """
# Diagnosing Kernel Panics

1. Check panic logs: Console.app -> System Reports
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
        "last_updated": days_ago(12),
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
1. Device Manager -> Network Adapters
2. Properties -> Advanced
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
- Resource Monitor -> Network tab
- Performance Monitor -> Network Interface counters

## Common Issues
- RSS (Receive Side Scaling) misconfiguration
- Antivirus scanning network traffic
- Outdated NIC drivers
- Network cable issues
""",
        "tags": ["windows-server", "network", "performance", "troubleshooting"],
        "related_products": ["Windows Server 2019", "Windows Server 2022"],
        "last_updated": days_ago(7),
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
        "last_updated": days_ago(10),
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
        "last_updated": days_ago(6),
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
        "last_updated": days_ago(5),
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
manage-bde -protectors -get C: > C:\\bitlocker-key.txt
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
        "last_updated": days_ago(8),
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
        "last_updated": days_ago(11),
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
        "last_updated": days_ago(6),
        "views": 1543,
        "helpful_count": 134
    }
]

# =============================================================================
# 2. PRIVATE HELPERS
# =============================================================================

def _find_article(article_id):
    return next((a for a in KB_ARTICLES if a["article_id"] == article_id), None)


def _search_articles(query, category=None, limit=10):
    """Keyword search over title, tags, content and category; higher score = better match."""
    results = []
    query_lower = query.lower() if query else ""
    for article in KB_ARTICLES:
        if category and article["category"].lower() != category.lower():
            continue
        score = 0
        if query_lower in article["title"].lower():
            score += 10
        for tag in article["tags"]:
            if query_lower in tag.lower():
                score += 5
        if query_lower in article["content"].lower():
            score += 3
        if query_lower in article["category"].lower():
            score += 4
        if score > 0:
            results.append({"article": article, "relevance_score": score})
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:limit]


def _find_related(article_id=None, topic=None, limit=5):
    """Articles sharing tags or category with a reference article, or a topic search."""
    if article_id:
        reference = _find_article(article_id)
        if not reference:
            return []
        ref_tags = set(reference["tags"])
        related = []
        for article in KB_ARTICLES:
            if article["article_id"] == article_id:
                continue
            common_tags = set(article["tags"]) & ref_tags
            score = len(common_tags) * 3
            if article["category"] == reference["category"]:
                score += 5
            if score > 0:
                related.append({"article": article, "relevance_score": score, "common_tags": list(common_tags)})
        related.sort(key=lambda x: x["relevance_score"], reverse=True)
        return related[:limit]
    if topic:
        return _search_articles(topic, limit=limit)
    return []


def _score_common_fixes(product=None, issue_type=None):
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


def _summary(entry, extra=()):
    a = entry["article"]
    out = {"article_id": a["article_id"], "title": a["title"], "category": a["category"],
           "relevance_score": entry["relevance_score"], "tags": a["tags"], "helpful_count": a["helpful_count"]}
    for key in extra:
        out[key] = entry.get(key, [])
    return out

# =============================================================================
# 3. TOOLS - plain Python functions, importable without MCP
# =============================================================================

def search_solutions(query: str, category: str | None = None, limit: int = 10) -> dict:
    """Search the knowledge base by keyword. An empty result is normal: it means no
    article matches, so try a different or shorter keyword.

    Args:
        query: keyword or phrase (e.g. "bsod", "ssh", "disk space")
        category: optional exact category filter (e.g. "Linux Administration")
        limit: maximum number of results
    """
    results = _search_articles(query, category, int(limit))
    return {"query": query, "category": category, "results": [_summary(r) for r in results], "total_count": len(results)}


def get_article(article_id: str) -> dict:
    """The full text of one knowledge base article.

    Args:
        article_id: unique article identifier (e.g. KB-001)
    """
    article = _find_article(article_id)
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
    return dict(article)


def find_related_articles(article_id: str | None = None, topic: str | None = None, limit: int = 5) -> dict:
    """Articles related to a given article (shared tags or category) or to a topic.

    Args:
        article_id: reference article (e.g. KB-001)
        topic: free-text topic if you have no article ID
        limit: maximum number of related articles
    """
    related = _find_related(article_id, topic, int(limit))
    if article_id and not related and not _find_article(article_id):
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
        "related_articles": [_summary(r, extra=("common_tags",)) for r in related],
        "total_found": len(related)
    }


def get_common_fixes(product: str | None = None, issue_type: str | None = None) -> dict:
    """The most helpful articles for a product and/or an issue type.

    Args:
        product: product name (e.g. "Windows 11", "Ubuntu")
        issue_type: kind of problem (e.g. "bsod", "network", "performance")
    """
    fixes = _score_common_fixes(product, issue_type)
    return {"product": product, "issue_type": issue_type, "common_fixes": [_summary(f) for f in fixes], "total_found": len(fixes)}

# =============================================================================
# 4. MCP LAYER - the only part of this file that knows MCP exists
# =============================================================================
# Never print() in a server: on stdio, stdout IS the wire to the client.

mcp = MCPServer("knowledge-base")

mcp.tool(annotations=READ_ONLY)(search_solutions)
mcp.tool(annotations=READ_ONLY)(get_article)
mcp.tool(annotations=READ_ONLY)(find_related_articles)
mcp.tool(annotations=READ_ONLY)(get_common_fixes)

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run()
