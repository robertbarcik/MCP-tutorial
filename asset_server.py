"""
Asset Management MCP Server
Provides tools for managing and tracking hardware/software assets
"""

import asyncio
import json
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Sample asset data
ASSETS = [
    {
        "asset_id": "AST-WKS-001",
        "serial_number": "5CD23456ABC",
        "hostname": "wks-techcorp-01.techcorp.local",
        "asset_type": "workstation",
        "customer_id": "CUST-001",
        "manufacturer": "Dell",
        "model": "OptiPlex 7090",
        "status": "active",
        "location": "TechCorp HQ - Floor 3",
        "purchase_date": "2024-01-15",
        "warranty": {
            "status": "active",
            "start_date": "2024-01-15",
            "end_date": "2027-01-15",
            "coverage_type": "ProSupport Plus",
            "remaining_days": 450
        },
        "specs": {
            "cpu": "Intel Core i7-11700",
            "ram_gb": 32,
            "storage": "512GB NVMe SSD",
            "os": "Windows 11 Pro"
        },
        "assigned_to": "david.chen@techcorp.com",
        "last_maintenance": "2025-08-10"
    },
    {
        "asset_id": "AST-SRV-001",
        "serial_number": "VMW-789-XYZ-456",
        "hostname": "sql-prod-01.dataflow.local",
        "asset_type": "server",
        "customer_id": "CUST-002",
        "manufacturer": "HPE",
        "model": "ProLiant DL380 Gen10",
        "status": "active",
        "location": "DataFlow Data Center - Rack 12",
        "purchase_date": "2023-06-20",
        "warranty": {
            "status": "active",
            "start_date": "2023-06-20",
            "end_date": "2026-06-20",
            "coverage_type": "24x7 4-hour response",
            "remaining_days": 258
        },
        "specs": {
            "cpu": "2x Intel Xeon Gold 6226R",
            "ram_gb": 256,
            "storage": "8x 1.2TB SAS HDD (RAID 10)",
            "os": "Ubuntu Server 22.04 LTS"
        },
        "assigned_to": "Infrastructure Team",
        "last_maintenance": "2025-09-15",
        "software_licenses": [
            {
                "software": "Microsoft SQL Server 2022 Enterprise",
                "license_key": "XXXXX-XXXXX-XXXXX-XXXXX",
                "expiration": "2026-06-01",
                "type": "perpetual"
            }
        ]
    },
    {
        "asset_id": "AST-WKS-002",
        "serial_number": "C02YZ8JKLVCG",
        "hostname": "mbp-globalent-exec",
        "asset_type": "laptop",
        "customer_id": "CUST-003",
        "manufacturer": "Apple",
        "model": "MacBook Pro 16-inch M3 Max",
        "status": "active",
        "location": "Remote - Executive",
        "purchase_date": "2024-11-10",
        "warranty": {
            "status": "active",
            "start_date": "2024-11-10",
            "end_date": "2025-11-10",
            "coverage_type": "AppleCare+",
            "remaining_days": 36
        },
        "specs": {
            "cpu": "Apple M3 Max",
            "ram_gb": 64,
            "storage": "2TB SSD",
            "os": "macOS Sonoma 14.6"
        },
        "assigned_to": "robert.t@globalent.com",
        "last_maintenance": "2025-09-01"
    },
    {
        "asset_id": "AST-SRV-002",
        "serial_number": "SRV-INV-2023-445",
        "hostname": "web-app-01.innovatesys.net",
        "asset_type": "server",
        "customer_id": "CUST-004",
        "manufacturer": "Supermicro",
        "model": "SuperServer 1029P",
        "status": "active",
        "location": "AWS us-east-1 (Virtual)",
        "purchase_date": "2023-08-22",
        "warranty": {
            "status": "active",
            "start_date": "2023-08-22",
            "end_date": "2025-08-22",
            "coverage_type": "Standard support",
            "remaining_days": -45
        },
        "specs": {
            "cpu": "Intel Xeon Silver 4210R",
            "ram_gb": 64,
            "storage": "2TB NVMe SSD",
            "os": "Ubuntu 24.04 LTS"
        },
        "assigned_to": "DevOps Team",
        "last_maintenance": "2025-07-20",
        "software_licenses": [
            {
                "software": "NGINX Plus",
                "license_key": "NGX-PLUS-2024-XXX",
                "expiration": "2025-12-31",
                "type": "subscription"
            }
        ]
    },
    {
        "asset_id": "AST-WKS-003",
        "serial_number": "DT-CF-789-2022",
        "hostname": "dev-wks-cloudfirst-05",
        "asset_type": "workstation",
        "customer_id": "CUST-005",
        "manufacturer": "Lenovo",
        "model": "ThinkStation P620",
        "status": "active",
        "location": "CloudFirst - Development Lab",
        "purchase_date": "2022-11-05",
        "warranty": {
            "status": "expired",
            "start_date": "2022-11-05",
            "end_date": "2025-11-05",
            "coverage_type": "Premier Support",
            "remaining_days": -31
        },
        "specs": {
            "cpu": "AMD Threadripper PRO 5975WX",
            "ram_gb": 128,
            "storage": "2TB NVMe SSD + 4TB HDD",
            "os": "Windows 11 Pro for Workstations"
        },
        "assigned_to": "tom.w@cloudfirst.cloud",
        "last_maintenance": "2025-06-15",
        "software_licenses": [
            {
                "software": "VMware Workstation Pro",
                "license_key": "VMW-XXXXX-XXXXX",
                "expiration": "perpetual",
                "type": "perpetual"
            },
            {
                "software": "Visual Studio Enterprise 2022",
                "license_key": "VS-ENT-XXXXX",
                "expiration": "2026-01-15",
                "type": "subscription"
            }
        ]
    },
    {
        "asset_id": "AST-NET-001",
        "serial_number": "CISCO-C9300-48P-SN123",
        "hostname": "sw-core-01.securenet.local",
        "asset_type": "network",
        "customer_id": "CUST-006",
        "manufacturer": "Cisco",
        "model": "Catalyst 9300-48P",
        "status": "active",
        "location": "SecureNet - Main IDF",
        "purchase_date": "2024-06-01",
        "warranty": {
            "status": "active",
            "start_date": "2024-06-01",
            "end_date": "2027-06-01",
            "coverage_type": "SMARTnet 8x5xNBD",
            "remaining_days": 604
        },
        "specs": {
            "ports": "48x 1G PoE+",
            "uplinks": "4x 10G SFP+",
            "power": "Dual redundant PSU",
            "firmware": "IOS-XE 17.9.4"
        },
        "assigned_to": "Network Infrastructure",
        "last_maintenance": "2025-09-20"
    },
    {
        "asset_id": "AST-SRV-003",
        "serial_number": "HPE-DL360-G10-789456",
        "hostname": "dc01.megacorp.local",
        "asset_type": "server",
        "customer_id": "CUST-007",
        "manufacturer": "HPE",
        "model": "ProLiant DL360 Gen10",
        "status": "active",
        "location": "MegaCorp HQ - Server Room A",
        "purchase_date": "2022-03-10",
        "warranty": {
            "status": "active",
            "start_date": "2022-03-10",
            "end_date": "2027-03-10",
            "coverage_type": "5-year 24x7 4-hour response",
            "remaining_days": 521
        },
        "specs": {
            "cpu": "2x Intel Xeon Gold 6230",
            "ram_gb": 192,
            "storage": "4x 900GB SAS (RAID 5)",
            "os": "Windows Server 2019 Standard"
        },
        "assigned_to": "IT Infrastructure",
        "last_maintenance": "2025-08-25",
        "software_licenses": [
            {
                "software": "Windows Server 2019 Standard",
                "license_key": "WIN-SRV-2019-XXX",
                "expiration": "perpetual",
                "type": "perpetual"
            },
            {
                "software": "Veeam Backup & Replication",
                "license_key": "VEEAM-XXX-YYY",
                "expiration": "2026-03-01",
                "type": "subscription"
            }
        ]
    },
    {
        "asset_id": "AST-SRV-004",
        "serial_number": "DELL-R740-XD-998877",
        "hostname": "docker-host-01.megacorp.local",
        "asset_type": "server",
        "customer_id": "CUST-007",
        "manufacturer": "Dell",
        "model": "PowerEdge R740xd",
        "status": "active",
        "location": "MegaCorp HQ - Server Room B",
        "purchase_date": "2023-07-15",
        "warranty": {
            "status": "active",
            "start_date": "2023-07-15",
            "end_date": "2026-07-15",
            "coverage_type": "ProSupport Plus 24x7",
            "remaining_days": 283
        },
        "specs": {
            "cpu": "2x Intel Xeon Gold 6248R",
            "ram_gb": 384,
            "storage": "12x 4TB SATA (RAID 6)",
            "os": "Red Hat Enterprise Linux 9"
        },
        "assigned_to": "Container Platform Team",
        "last_maintenance": "2025-09-10",
        "software_licenses": [
            {
                "software": "Red Hat Enterprise Linux",
                "license_key": "RHEL-SUB-XXXXX",
                "expiration": "2026-07-15",
                "type": "subscription"
            },
            {
                "software": "Docker Enterprise",
                "license_key": "DOCKER-EE-XXXXX",
                "expiration": "2026-01-01",
                "type": "subscription"
            }
        ]
    },
    {
        "asset_id": "AST-WKS-004",
        "serial_number": "ASUS-PN64-456789",
        "hostname": "kiosk-startuphub-lobby",
        "asset_type": "workstation",
        "customer_id": "CUST-008",
        "manufacturer": "ASUS",
        "model": "PN64 Mini PC",
        "status": "active",
        "location": "StartupHub - Lobby",
        "purchase_date": "2024-02-28",
        "warranty": {
            "status": "active",
            "start_date": "2024-02-28",
            "end_date": "2027-02-28",
            "coverage_type": "3-year on-site",
            "remaining_days": 511
        },
        "specs": {
            "cpu": "Intel Core i5-12500H",
            "ram_gb": 16,
            "storage": "256GB NVMe SSD",
            "os": "Ubuntu 22.04 LTS"
        },
        "assigned_to": "Public Kiosk",
        "last_maintenance": "2025-09-01"
    },
    {
        "asset_id": "AST-SRV-005",
        "serial_number": "SH-VM-CLUSTER-01",
        "hostname": "k8s-master-01.startuphub.local",
        "asset_type": "server",
        "customer_id": "CUST-008",
        "manufacturer": "Dell",
        "model": "PowerEdge R650",
        "status": "active",
        "location": "Colocation - Digital Realty SJC",
        "purchase_date": "2024-03-15",
        "warranty": {
            "status": "active",
            "start_date": "2024-03-15",
            "end_date": "2027-03-15",
            "coverage_type": "ProSupport 24x7",
            "remaining_days": 526
        },
        "specs": {
            "cpu": "2x Intel Xeon Silver 4314",
            "ram_gb": 128,
            "storage": "4x 960GB SSD (RAID 10)",
            "os": "Ubuntu Server 22.04 LTS"
        },
        "assigned_to": "Platform Team",
        "last_maintenance": "2025-08-30",
        "software_licenses": [
            {
                "software": "Rancher Enterprise",
                "license_key": "RANCHER-XXX-YYY",
                "expiration": "2026-03-15",
                "type": "subscription"
            }
        ]
    },
    {
        "asset_id": "AST-STOR-001",
        "serial_number": "SYNOLOGY-RS2421-887654",
        "hostname": "nas-backup-01.dataflow.local",
        "asset_type": "storage",
        "customer_id": "CUST-002",
        "manufacturer": "Synology",
        "model": "RackStation RS2421+",
        "status": "active",
        "location": "DataFlow - Backup Room",
        "purchase_date": "2023-09-10",
        "warranty": {
            "status": "active",
            "start_date": "2023-09-10",
            "end_date": "2026-09-10",
            "coverage_type": "3-year warranty",
            "remaining_days": 340
        },
        "specs": {
            "cpu": "AMD Ryzen V1500B",
            "ram_gb": 32,
            "bays": "12-bay",
            "capacity": "96TB usable (RAID 6)",
            "os": "DSM 7.2"
        },
        "assigned_to": "Backup Infrastructure",
        "last_maintenance": "2025-07-15"
    },
    {
        "asset_id": "AST-WKS-005",
        "serial_number": "FRAMEWORK-13-GEN3-55443",
        "hostname": "laptop-innovate-mobile",
        "asset_type": "laptop",
        "customer_id": "CUST-004",
        "manufacturer": "Framework",
        "model": "Framework Laptop 13 (Intel 13th Gen)",
        "status": "active",
        "location": "Remote - Field Engineer",
        "purchase_date": "2024-05-20",
        "warranty": {
            "status": "active",
            "start_date": "2024-05-20",
            "end_date": "2025-05-20",
            "coverage_type": "Standard 1-year",
            "remaining_days": 7
        },
        "specs": {
            "cpu": "Intel Core i7-1370P",
            "ram_gb": 32,
            "storage": "1TB NVMe SSD",
            "os": "Fedora 40 Workstation"
        },
        "assigned_to": "michael.d@innovatesys.net",
        "last_maintenance": "2025-08-10",
        "software_licenses": [
            {
                "software": "JetBrains All Products Pack",
                "license_key": "JETBRAINS-XXX",
                "expiration": "2026-05-20",
                "type": "subscription"
            }
        ]
    }
]




# ============================================================================
# REGULAR PYTHON FUNCTIONS - Can be called directly without MCP
# ============================================================================

def lookup_asset(asset_id=None, serial_number=None, hostname=None, customer_id=None):
    """Look up asset(s). Can be called directly."""
    assets = search_assets(asset_id=asset_id, serial_number=serial_number, hostname=hostname, customer_id=customer_id)
    if not assets:
        return {"error": "No assets found matching criteria", "search_criteria": {k: v for k, v in {"asset_id": asset_id, "serial_number": serial_number, "hostname": hostname, "customer_id": customer_id}.items() if v}}
    elif len(assets) == 1:
        result = assets[0].copy()
        if "warranty" in result:
            result["warranty"]["remaining_days"] = calculate_warranty_days(result["warranty"]["end_date"])
        return result
    else:
        return {"assets": [{"asset_id": a["asset_id"], "serial_number": a["serial_number"], "hostname": a["hostname"], "asset_type": a["asset_type"], "customer_id": a["customer_id"], "manufacturer": a["manufacturer"], "model": a["model"], "status": a["status"]} for a in assets], "total_count": len(assets)}


def check_warranty(asset_id):
    """Check warranty status. Can be called directly."""
    asset = next((a for a in ASSETS if a["asset_id"] == asset_id), None)
    if not asset:
        return {"error": f"Asset {asset_id} not found", "asset_id": asset_id}
    warranty = asset.get("warranty", {})
    remaining = calculate_warranty_days(warranty.get("end_date"))
    return {
        "asset_id": asset["asset_id"], "serial_number": asset["serial_number"], "hostname": asset["hostname"],
        "manufacturer": asset["manufacturer"], "model": asset["model"],
        "warranty": {**warranty, "remaining_days": remaining, "is_expired": remaining < 0, "expires_soon": 0 <= remaining <= 30}
    }


def get_software_licenses(asset_id=None, customer_id=None):
    """Get software licenses. Can be called directly."""
    if asset_id:
        asset = next((a for a in ASSETS if a["asset_id"] == asset_id), None)
        if not asset:
            return {"error": f"Asset {asset_id} not found", "asset_id": asset_id}
        licenses = asset.get("software_licenses", [])
        return {"asset_id": asset_id, "hostname": asset["hostname"], "licenses": licenses, "total_licenses": len(licenses)}
    elif customer_id:
        customer_assets = [a for a in ASSETS if a["customer_id"] == customer_id]
        all_licenses = []
        for asset in customer_assets:
            for lic in asset.get("software_licenses", []):
                all_licenses.append({"asset_id": asset["asset_id"], "hostname": asset["hostname"], **lic})
        return {"customer_id": customer_id, "licenses": all_licenses, "total_licenses": len(all_licenses), "total_assets_with_licenses": len([a for a in customer_assets if a.get("software_licenses")])}
    else:
        return {"error": "Please provide either asset_id or customer_id"}


def get_asset_history(asset_id):
    """Get asset history. Can be called directly."""
    asset = next((a for a in ASSETS if a["asset_id"] == asset_id), None)
    if not asset:
        return {"error": f"Asset {asset_id} not found", "asset_id": asset_id}
    history = []
    history.append({"date": asset["purchase_date"], "event_type": "purchase", "description": f"Asset purchased - {asset['manufacturer']} {asset['model']}", "details": {"purchase_date": asset["purchase_date"], "location": asset["location"]}})
    warranty = asset.get("warranty", {})
    if warranty:
        history.append({"date": warranty["start_date"], "event_type": "warranty_start", "description": f"Warranty coverage started - {warranty['coverage_type']}", "details": warranty})
    if asset.get("last_maintenance"):
        history.append({"date": asset["last_maintenance"], "event_type": "maintenance", "description": "Scheduled maintenance performed", "details": {"maintenance_date": asset["last_maintenance"]}})
    history.sort(key=lambda x: x["date"], reverse=True)
    return {
        "asset_id": asset["asset_id"], "serial_number": asset["serial_number"], "hostname": asset["hostname"],
        "current_status": asset["status"], "history": history, "total_events": len(history),
        "asset_age_days": (datetime.now() - parse_date(asset["purchase_date"])).days if parse_date(asset["purchase_date"]) else 0
    }


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# Initialize the MCP server
app = Server("asset-management-server")


# Helper functions
def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def calculate_warranty_days(warranty_end_date):
    """Calculate remaining warranty days"""
    end_date = parse_date(warranty_end_date)
    if end_date:
        delta = end_date - datetime.now()
        return delta.days
    return 0


def search_assets(asset_id=None, serial_number=None, hostname=None, customer_id=None):
    """Search for assets by various criteria"""
    results = []

    for asset in ASSETS:
        match = False

        if asset_id and asset["asset_id"] == asset_id:
            match = True
        if serial_number and asset["serial_number"].lower() == serial_number.lower():
            match = True
        if hostname and hostname.lower() in asset["hostname"].lower():
            match = True
        if customer_id and asset["customer_id"] == customer_id:
            match = True

        if match or (not asset_id and not serial_number and not hostname and not customer_id):
            results.append(asset)

    return results


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available asset management tools"""
    return [
        Tool(
            name="lookup_asset",
            description="Look up detailed information about an asset by asset ID, serial number, hostname, or customer ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string", "description": "Unique asset identifier"},
                    "serial_number": {"type": "string", "description": "Asset serial number"},
                    "hostname": {"type": "string", "description": "Asset hostname (partial match supported)"},
                    "customer_id": {"type": "string", "description": "Get all assets for a customer"}
                }
            }
        ),
        Tool(
            name="check_warranty",
            description="Check warranty status and coverage details for an asset",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string", "description": "Unique asset identifier"}
                },
                "required": ["asset_id"]
            }
        ),
        Tool(
            name="get_software_licenses",
            description="Retrieve software license information for an asset or customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string", "description": "Asset identifier"},
                    "customer_id": {"type": "string", "description": "Customer identifier"}
                }
            }
        ),
        Tool(
            name="get_asset_history",
            description="Get the complete history of an asset including maintenance, transfers, and related tickets",
            inputSchema={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string", "description": "Unique asset identifier"}
                },
                "required": ["asset_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls - delegates to regular Python functions"""
    if name == "lookup_asset":
        result = lookup_asset(**arguments)
    elif name == "check_warranty":
        result = check_warranty(arguments.get("asset_id"))
    elif name == "get_software_licenses":
        result = get_software_licenses(**arguments)
    elif name == "get_asset_history":
        result = get_asset_history(arguments.get("asset_id"))
    else:
        raise ValueError(f"Unknown tool: {name}")
    return [TextContent(type="text", text=json.dumps(result, indent=2))]



async def main():
    """Run the asset management server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
