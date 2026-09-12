"""
Asset server for the IT help desk: hardware, warranties, software licenses.

Same four parts as every server in this course:
  1. DATA  2. PRIVATE HELPERS  3. TOOLS (plain functions)  4. MCP LAYER

Run:    python servers/asset_server.py [--http]
Import: from servers.asset_server import lookup_asset
"""

import copy
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import READ_ONLY, days_ago, days_from_now, make_error
from mcp.server import MCPServer

# =============================================================================
# 1. DATA
# =============================================================================

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
        "purchase_date": days_ago(629),
        "warranty": {
            "start_date": days_ago(629),
            "end_date": days_from_now(467),
            "coverage_type": "ProSupport Plus"
        },
        "specs": {"cpu": "Intel Core i7-11700", "ram_gb": 32, "storage": "512GB NVMe SSD", "os": "Windows 11 Pro"},
        "assigned_to": "david.chen@techcorp.com",
        "last_maintenance": days_ago(60)
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
        "purchase_date": days_ago(838),
        "warranty": {
            "start_date": days_ago(838),
            "end_date": days_from_now(258),
            "coverage_type": "24x7 4-hour response"
        },
        "specs": {"cpu": "2x Intel Xeon Gold 6226R", "ram_gb": 256, "storage": "8x 1.2TB SAS HDD (RAID 10)", "os": "Ubuntu Server 22.04 LTS"},
        "assigned_to": "Infrastructure Team",
        "last_maintenance": days_ago(25),
        "software_licenses": [
            {"software": "Microsoft SQL Server 2022 Enterprise", "license_key": "XXXXX-XXXXX-XXXXX-XXXXX", "expiration": days_from_now(240), "type": "perpetual"}
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
        "purchase_date": days_ago(329),
        "warranty": {
            "start_date": days_ago(329),
            "end_date": days_from_now(36),
            "coverage_type": "AppleCare+"
        },
        "specs": {"cpu": "Apple M3 Max", "ram_gb": 64, "storage": "2TB SSD", "os": "macOS Sonoma 14.6"},
        "assigned_to": "robert.t@globalent.com",
        "last_maintenance": days_ago(40)
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
        "purchase_date": days_ago(775),
        "warranty": {
            "start_date": days_ago(775),
            "end_date": days_from_now(320),
            "coverage_type": "Standard support"
        },
        "specs": {"cpu": "Intel Xeon Silver 4210R", "ram_gb": 64, "storage": "2TB NVMe SSD", "os": "Ubuntu 24.04 LTS"},
        "assigned_to": "DevOps Team",
        "last_maintenance": days_ago(80),
        "software_licenses": [
            {"software": "NGINX Plus", "license_key": "NGX-PLUS-XXX", "expiration": days_from_now(100), "type": "subscription"}
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
        "purchase_date": days_ago(1065),
        "warranty": {
            "start_date": days_ago(1065),
            "end_date": days_ago(120),
            "coverage_type": "Premier Support"
        },
        "specs": {"cpu": "AMD Threadripper PRO 5975WX", "ram_gb": 128, "storage": "2TB NVMe SSD + 4TB HDD", "os": "Windows 11 Pro for Workstations"},
        "assigned_to": "tom.w@cloudfirst.cloud",
        "last_maintenance": days_ago(110),
        "software_licenses": [
            {"software": "VMware Workstation Pro", "license_key": "VMW-XXXXX-XXXXX", "expiration": "perpetual", "type": "perpetual"},
            {"software": "Visual Studio Enterprise 2022", "license_key": "VS-ENT-XXXXX", "expiration": days_from_now(125), "type": "subscription"}
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
        "purchase_date": days_ago(491),
        "warranty": {
            "start_date": days_ago(491),
            "end_date": days_from_now(604),
            "coverage_type": "SMARTnet 8x5xNBD"
        },
        "specs": {"ports": "48x 1G PoE+", "uplinks": "4x 10G SFP+", "power": "Dual redundant PSU", "firmware": "IOS-XE 17.9.4"},
        "assigned_to": "Network Infrastructure",
        "last_maintenance": days_ago(20)
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
        "purchase_date": days_ago(1305),
        "warranty": {
            "start_date": days_ago(1305),
            "end_date": days_from_now(521),
            "coverage_type": "5-year 24x7 4-hour response"
        },
        "specs": {"cpu": "2x Intel Xeon Gold 6230", "ram_gb": 192, "storage": "4x 900GB SAS (RAID 5)", "os": "Windows Server 2019 Standard"},
        "assigned_to": "IT Infrastructure",
        "last_maintenance": days_ago(45),
        "software_licenses": [
            {"software": "Windows Server 2019 Standard", "license_key": "WIN-SRV-2019-XXX", "expiration": "perpetual", "type": "perpetual"},
            {"software": "Veeam Backup & Replication", "license_key": "VEEAM-XXX-YYY", "expiration": days_from_now(170), "type": "subscription"}
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
        "purchase_date": days_ago(813),
        "warranty": {
            "start_date": days_ago(813),
            "end_date": days_from_now(283),
            "coverage_type": "ProSupport Plus 24x7"
        },
        "specs": {"cpu": "2x Intel Xeon Gold 6248R", "ram_gb": 384, "storage": "12x 4TB SATA (RAID 6)", "os": "Red Hat Enterprise Linux 9"},
        "assigned_to": "Container Platform Team",
        "last_maintenance": days_ago(30),
        "software_licenses": [
            {"software": "Red Hat Enterprise Linux", "license_key": "RHEL-SUB-XXXXX", "expiration": days_from_now(300), "type": "subscription"},
            {"software": "Docker Enterprise", "license_key": "DOCKER-EE-XXXXX", "expiration": days_from_now(110), "type": "subscription"}
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
        "purchase_date": days_ago(585),
        "warranty": {
            "start_date": days_ago(585),
            "end_date": days_from_now(511),
            "coverage_type": "3-year on-site"
        },
        "specs": {"cpu": "Intel Core i5-12500H", "ram_gb": 16, "storage": "256GB NVMe SSD", "os": "Ubuntu 22.04 LTS"},
        "assigned_to": "Public Kiosk",
        "last_maintenance": days_ago(40)
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
        "purchase_date": days_ago(569),
        "warranty": {
            "start_date": days_ago(569),
            "end_date": days_from_now(526),
            "coverage_type": "ProSupport 24x7"
        },
        "specs": {"cpu": "2x Intel Xeon Silver 4314", "ram_gb": 128, "storage": "4x 960GB SSD (RAID 10)", "os": "Ubuntu Server 22.04 LTS"},
        "assigned_to": "Platform Team",
        "last_maintenance": days_ago(35),
        "software_licenses": [
            {"software": "Rancher Enterprise", "license_key": "RANCHER-XXX-YYY", "expiration": days_from_now(185), "type": "subscription"}
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
        "purchase_date": days_ago(756),
        "warranty": {
            "start_date": days_ago(756),
            "end_date": days_from_now(340),
            "coverage_type": "3-year warranty"
        },
        "specs": {"cpu": "AMD Ryzen V1500B", "ram_gb": 32, "bays": "12-bay", "capacity": "96TB usable (RAID 6)", "os": "DSM 7.2"},
        "assigned_to": "Backup Infrastructure",
        "last_maintenance": days_ago(85)
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
        "purchase_date": days_ago(503),
        "warranty": {
            "start_date": days_ago(503),
            "end_date": days_from_now(21),
            "coverage_type": "Standard 1-year"
        },
        "specs": {"cpu": "Intel Core i7-1370P", "ram_gb": 32, "storage": "1TB NVMe SSD", "os": "Fedora 40 Workstation"},
        "assigned_to": "michael.d@innovatesys.net",
        "last_maintenance": days_ago(60),
        "software_licenses": [
            {"software": "JetBrains All Products Pack", "license_key": "JETBRAINS-XXX", "expiration": days_from_now(250), "type": "subscription"}
        ]
    }
]

# =============================================================================
# 2. PRIVATE HELPERS
# =============================================================================

def _parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _warranty_days_left(end_date):
    end = _parse_date(end_date)
    return (end - datetime.now()).days if end else 0


def _warranty_view(warranty):
    remaining = _warranty_days_left(warranty.get("end_date"))
    return {**warranty, "remaining_days": remaining, "status": "expired" if remaining < 0 else "active",
            "is_expired": remaining < 0, "expires_soon": 0 <= remaining <= 30}


def _find_asset(asset_id):
    return next((a for a in ASSETS if a["asset_id"] == asset_id), None)


def _search_assets(asset_id=None, serial_number=None, hostname=None, customer_id=None):
    """All assets matching any given identifier; with no identifiers, every asset."""
    if not any([asset_id, serial_number, hostname, customer_id]):
        return list(ASSETS)
    results = []
    for asset in ASSETS:
        if (asset_id and asset["asset_id"] == asset_id) \
                or (serial_number and asset["serial_number"].lower() == serial_number.lower()) \
                or (hostname and hostname.lower() in asset["hostname"].lower()) \
                or (customer_id and asset["customer_id"] == customer_id):
            results.append(asset)
    return results


def _not_found(asset_id, reason, hints):
    return make_error(f"Asset {asset_id} not found", reason=reason, hints=hints, retryable=True,
                      follow_up_tools=["lookup_asset"], asset_id=asset_id)

# =============================================================================
# 3. TOOLS - plain Python functions, importable without MCP
# =============================================================================

def lookup_asset(asset_id: str | None = None, serial_number: str | None = None,
                 hostname: str | None = None, customer_id: str | None = None) -> dict:
    """Find assets by ID, serial number, hostname (partial match) or customer. One match
    returns the full record; several matches return a short list.

    Args:
        asset_id: unique asset identifier (e.g. AST-WKS-001)
        serial_number: exact serial number
        hostname: hostname or part of it
        customer_id: every asset of this customer (e.g. CUST-002)
    """
    assets = _search_assets(asset_id=asset_id, serial_number=serial_number, hostname=hostname, customer_id=customer_id)
    if not assets:
        return make_error(
            "No assets found matching criteria",
            reason="The identifiers did not match any assets in the dataset.",
            hints=[
                "Provide asset_id or serial_number for an exact match.",
                "Use customer_id alone to list all assets for a customer."
            ],
            retryable=True,
            follow_up_tools=["lookup_asset"],
            search_criteria={k: v for k, v in {"asset_id": asset_id, "serial_number": serial_number, "hostname": hostname, "customer_id": customer_id}.items() if v}
        )
    if len(assets) == 1:
        result = copy.deepcopy(assets[0])
        if "warranty" in result:
            result["warranty"] = _warranty_view(result["warranty"])
        return result
    return {
        "assets": [
            {"asset_id": a["asset_id"], "serial_number": a["serial_number"], "hostname": a["hostname"], "asset_type": a["asset_type"],
             "customer_id": a["customer_id"], "manufacturer": a["manufacturer"], "model": a["model"], "status": a["status"]}
            for a in assets
        ],
        "total_count": len(assets)
    }


def check_warranty(asset_id: str) -> dict:
    """Warranty coverage of one asset: end date, remaining days, whether it is expired or expiring within 30 days.

    Args:
        asset_id: unique asset identifier (e.g. AST-WKS-001)
    """
    asset = _find_asset(asset_id)
    if not asset:
        return _not_found(asset_id, "Warranty information is only available for known assets.", [
            "Call lookup_asset with customer_id to find valid asset IDs.",
            "Confirm the asset_id spelling (e.g., AST-WKS-001)."
        ])
    return {
        "asset_id": asset["asset_id"], "serial_number": asset["serial_number"], "hostname": asset["hostname"],
        "manufacturer": asset["manufacturer"], "model": asset["model"],
        "warranty": _warranty_view(asset.get("warranty", {}))
    }


def get_software_licenses(asset_id: str | None = None, customer_id: str | None = None) -> dict:
    """Software licenses installed on one asset, or across all assets of a customer. Give one of the two arguments.

    Args:
        asset_id: unique asset identifier (e.g. AST-SRV-001)
        customer_id: aggregate licenses for this customer (e.g. CUST-007)
    """
    if asset_id:
        asset = _find_asset(asset_id)
        if not asset:
            return _not_found(asset_id, "Software license details require a valid asset_id.", [
                "Use lookup_asset to retrieve the correct asset_id.",
                "Search by customer_id if you do not know the asset_id."
            ])
        licenses = asset.get("software_licenses", [])
        return {"asset_id": asset_id, "hostname": asset["hostname"], "licenses": licenses, "total_licenses": len(licenses)}
    if customer_id:
        customer_assets = [a for a in ASSETS if a["customer_id"] == customer_id]
        all_licenses = [
            {"asset_id": a["asset_id"], "hostname": a["hostname"], **lic}
            for a in customer_assets for lic in a.get("software_licenses", [])
        ]
        return {"customer_id": customer_id, "licenses": all_licenses, "total_licenses": len(all_licenses),
                "total_assets_with_licenses": len([a for a in customer_assets if a.get("software_licenses")])}
    return make_error(
        "Missing software license lookup criteria",
        reason="Neither asset_id nor customer_id was supplied.",
        hints=[
            "Provide asset_id to see licenses for a single asset.",
            "Provide customer_id to aggregate licenses across that customer."
        ],
        retryable=True,
        follow_up_tools=["get_software_licenses"],
        expected_arguments=["asset_id", "customer_id"]
    )


def get_asset_history(asset_id: str) -> dict:
    """Timeline of one asset: purchase, warranty start, last maintenance, and its age in days.

    Args:
        asset_id: unique asset identifier (e.g. AST-SRV-003)
    """
    asset = _find_asset(asset_id)
    if not asset:
        return _not_found(asset_id, "History is only tracked for assets listed in the dataset.", [
            "Query lookup_asset to confirm the asset exists.",
            "Use customer_id to find assets for the relevant organisation."
        ])
    history = [{"date": asset["purchase_date"], "event_type": "purchase",
                "description": f"Asset purchased - {asset['manufacturer']} {asset['model']}",
                "details": {"purchase_date": asset["purchase_date"], "location": asset["location"]}}]
    warranty = asset.get("warranty")
    if warranty:
        history.append({"date": warranty["start_date"], "event_type": "warranty_start",
                        "description": f"Warranty coverage started - {warranty['coverage_type']}", "details": warranty})
    if asset.get("last_maintenance"):
        history.append({"date": asset["last_maintenance"], "event_type": "maintenance",
                        "description": "Scheduled maintenance performed", "details": {"maintenance_date": asset["last_maintenance"]}})
    history.sort(key=lambda x: x["date"], reverse=True)
    purchased = _parse_date(asset["purchase_date"])
    return {
        "asset_id": asset["asset_id"], "serial_number": asset["serial_number"], "hostname": asset["hostname"],
        "current_status": asset["status"], "history": history, "total_events": len(history),
        "asset_age_days": (datetime.now() - purchased).days if purchased else 0
    }

# =============================================================================
# 4. MCP LAYER - the only part of this file that knows MCP exists
# =============================================================================
# Never print() in a server: on stdio, stdout IS the wire to the client.

mcp = MCPServer("assets")

mcp.tool(annotations=READ_ONLY)(lookup_asset)
mcp.tool(annotations=READ_ONLY)(check_warranty)
mcp.tool(annotations=READ_ONLY)(get_software_licenses)
mcp.tool(annotations=READ_ONLY)(get_asset_history)

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run()
