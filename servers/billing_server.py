"""
Billing server for the IT help desk: invoices, payments, outstanding balances.

Same four parts as every server in this course:
  1. DATA  2. PRIVATE HELPERS  3. TOOLS (plain functions)  4. MCP LAYER

Run:    python servers/billing_server.py [--http]
Import: from servers.billing_server import get_invoice
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import READ_ONLY, days_ago, days_from_now, make_error
from mcp.server import MCPServer

# =============================================================================
# 1. DATA
# =============================================================================

INVOICES = [
    {
        "invoice_id": "INV-1001",
        "customer_id": "CUST-001",
        "ticket_id": "TKT-1001",
        "amount": 450.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": days_ago(20),
        "due_date": days_from_now(10),
        "paid_date": days_ago(12),
        "description": "Premium support - Windows BSOD investigation and resolution",
        "line_items": [
            {"description": "Senior engineer hours (3h)", "amount": 450.00}
        ]
    },
    {
        "invoice_id": "INV-1002",
        "customer_id": "CUST-002",
        "ticket_id": "TKT-1002",
        "amount": 850.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": days_ago(4),
        "due_date": days_from_now(26),
        "paid_date": None,
        "description": "Critical incident - Linux server disk space emergency response",
        "line_items": [
            {"description": "Emergency response fee", "amount": 250.00},
            {"description": "Engineer hours (4h)", "amount": 600.00}
        ]
    },
    {
        "invoice_id": "INV-1003",
        "customer_id": "CUST-003",
        "ticket_id": "TKT-1003",
        "amount": 300.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": days_ago(7),
        "due_date": days_from_now(23),
        "paid_date": days_ago(3),
        "description": "macOS kernel panic diagnosis and fix",
        "line_items": [
            {"description": "Standard support hours (2h)", "amount": 300.00}
        ]
    },
    {
        "invoice_id": "INV-1004",
        "customer_id": "CUST-001",
        "ticket_id": "TKT-1004",
        "amount": 600.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": days_ago(2),
        "due_date": days_from_now(28),
        "paid_date": None,
        "description": "Network performance troubleshooting - Windows Server",
        "line_items": [
            {"description": "Network analysis (4h)", "amount": 600.00}
        ]
    },
    {
        "invoice_id": "INV-1005",
        "customer_id": "CUST-004",
        "ticket_id": "TKT-1005",
        "amount": 200.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": days_ago(5),
        "due_date": days_from_now(25),
        "paid_date": days_ago(4),
        "description": "Ubuntu repository configuration fix",
        "line_items": [
            {"description": "Standard support (1.5h)", "amount": 200.00}
        ]
    },
    {
        "invoice_id": "INV-1006",
        "customer_id": "CUST-005",
        "ticket_id": "TKT-1006",
        "amount": 500.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": days_ago(1),
        "due_date": days_from_now(29),
        "paid_date": None,
        "description": "Windows filesystem troubleshooting - ongoing",
        "line_items": [
            {"description": "Investigation and diagnostics (3h)", "amount": 500.00}
        ]
    },
    {
        "invoice_id": "INV-1007",
        "customer_id": "CUST-002",
        "ticket_id": "TKT-1007",
        "amount": 350.00,
        "currency": "USD",
        "status": "overdue",
        "issue_date": days_ago(45),
        "due_date": days_ago(15),
        "paid_date": None,
        "description": "SSH performance optimization - Debian server",
        "line_items": [
            {"description": "Performance tuning (2.5h)", "amount": 350.00}
        ]
    },
    {
        "invoice_id": "INV-1008",
        "customer_id": "CUST-006",
        "ticket_id": "TKT-1008",
        "amount": 150.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": days_ago(4),
        "due_date": days_from_now(26),
        "paid_date": None,
        "description": "macOS Time Machine backup troubleshooting",
        "line_items": [
            {"description": "Basic support (1h)", "amount": 150.00}
        ]
    },
    {
        "invoice_id": "INV-1009",
        "customer_id": "CUST-007",
        "ticket_id": "TKT-1009",
        "amount": 750.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": days_ago(3),
        "due_date": days_from_now(27),
        "paid_date": None,
        "description": "Critical BitLocker recovery - Windows 11",
        "line_items": [
            {"description": "Emergency support", "amount": 200.00},
            {"description": "Senior engineer (3.5h)", "amount": 550.00}
        ]
    },
    {
        "invoice_id": "INV-1010",
        "customer_id": "CUST-003",
        "ticket_id": "TKT-1010",
        "amount": 1500.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": days_ago(10),
        "due_date": days_from_now(20),
        "paid_date": None,
        "description": "CentOS migration planning and consultation",
        "line_items": [
            {"description": "Migration assessment", "amount": 500.00},
            {"description": "Planning consultation (6h)", "amount": 1000.00}
        ]
    },
    {
        "invoice_id": "INV-1011",
        "customer_id": "CUST-008",
        "ticket_id": "TKT-1011",
        "amount": 900.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": days_ago(6),
        "due_date": days_from_now(24),
        "paid_date": days_ago(5),
        "description": "Active Directory replication fix - critical",
        "line_items": [
            {"description": "Emergency AD repair (5h)", "amount": 900.00}
        ]
    },
    {
        "invoice_id": "INV-1012",
        "customer_id": "CUST-004",
        "ticket_id": "TKT-1012",
        "amount": 400.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": days_ago(1),
        "due_date": days_from_now(29),
        "paid_date": None,
        "description": "Ubuntu high CPU investigation - ongoing",
        "line_items": [
            {"description": "System analysis (2.5h)", "amount": 400.00}
        ]
    },
    {
        "invoice_id": "INV-0988",
        "customer_id": "CUST-005",
        "ticket_id": None,
        "amount": 2500.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": days_ago(308),
        "due_date": days_ago(278),
        "paid_date": days_ago(290),
        "description": "Monthly premium support retainer",
        "line_items": [
            {"description": "Premium support package", "amount": 2500.00}
        ]
    },
    {
        "invoice_id": "INV-0975",
        "customer_id": "CUST-002",
        "ticket_id": None,
        "amount": 1800.00,
        "currency": "USD",
        "status": "overdue",
        "issue_date": days_ago(324),
        "due_date": days_ago(294),
        "paid_date": None,
        "description": "Quarterly infrastructure review",
        "line_items": [
            {"description": "Infrastructure audit", "amount": 1800.00}
        ]
    },
    {
        "invoice_id": "INV-1013",
        "customer_id": "CUST-006",
        "ticket_id": "TKT-1014",
        "amount": 275.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": days_ago(0),
        "due_date": days_from_now(30),
        "paid_date": None,
        "description": "Windows 11 taskbar troubleshooting",
        "line_items": [
            {"description": "Support hours (2h)", "amount": 275.00}
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


def _is_overdue(invoice):
    if invoice["status"] == "paid":
        return False
    due = _parse_date(invoice["due_date"])
    return bool(due) and datetime.now() > due


def _days_overdue(invoice):
    if invoice["status"] == "paid":
        return 0
    due = _parse_date(invoice["due_date"])
    return max(0, (datetime.now() - due).days) if due else 0


def _find_invoice(invoice_id):
    return next((inv for inv in INVOICES if inv["invoice_id"] == invoice_id), None)


def _customer_invoices(customer_id):
    return [inv for inv in INVOICES if inv["customer_id"] == customer_id]

# =============================================================================
# 3. TOOLS - plain Python functions, importable without MCP
# =============================================================================

def get_invoice(invoice_id: str | None = None, customer_id: str | None = None) -> dict:
    """One invoice by ID, or all invoices of a customer. Give exactly one of the two arguments.

    Args:
        invoice_id: unique invoice identifier (e.g. INV-1001)
        customer_id: list every invoice of this customer (e.g. CUST-001)
    """
    if invoice_id:
        invoice = _find_invoice(invoice_id)
        if not invoice:
            return make_error(
                f"Invoice {invoice_id} not found",
                reason="The provided invoice_id does not exist in the billing dataset.",
                hints=[
                    "Call get_invoice with customer_id to browse a customer's invoices.",
                    "Call calculate_outstanding_balance to see unpaid invoices by customer."
                ],
                retryable=True,
                follow_up_tools=["get_invoice", "calculate_outstanding_balance"],
                invoice_id=invoice_id
            )
        result = dict(invoice)
        result["is_overdue"] = _is_overdue(invoice)
        result["days_overdue"] = _days_overdue(invoice)
        return result
    if customer_id:
        invoices = _customer_invoices(customer_id)
        return {"customer_id": customer_id, "invoices": invoices, "total_invoices": len(invoices)}
    return make_error(
        "Missing invoice lookup criteria",
        reason="Neither invoice_id nor customer_id was supplied.",
        hints=[
            "Provide invoice_id to retrieve a single invoice.",
            "Provide customer_id to list all invoices for that customer."
        ],
        retryable=True,
        follow_up_tools=["get_invoice"],
        expected_arguments=["invoice_id", "customer_id"]
    )


def check_payment_status(invoice_id: str | None = None, customer_id: str | None = None) -> dict:
    """Payment status of one invoice, or a paid/pending/overdue summary for a customer.

    Args:
        invoice_id: unique invoice identifier (e.g. INV-1001)
        customer_id: summarise all invoices of this customer (e.g. CUST-002)
    """
    if invoice_id:
        invoice = _find_invoice(invoice_id)
        if not invoice:
            return make_error(
                f"Invoice {invoice_id} not found",
                reason="Payment details require a valid invoice_id.",
                hints=[
                    "List invoices by passing customer_id to get_invoice.",
                    "Double-check the invoice_id spelling (e.g., INV-1001)."
                ],
                retryable=True,
                follow_up_tools=["get_invoice"],
                invoice_id=invoice_id
            )
        return {
            "invoice_id": invoice["invoice_id"], "customer_id": invoice["customer_id"],
            "payment_status": invoice["status"], "amount": invoice["amount"], "currency": invoice["currency"],
            "issue_date": invoice["issue_date"], "due_date": invoice["due_date"], "paid_date": invoice["paid_date"],
            "is_overdue": _is_overdue(invoice), "days_overdue": _days_overdue(invoice)
        }
    if customer_id:
        invoices = _customer_invoices(customer_id)
        pending = [inv for inv in invoices if inv["status"] == "pending" and not _is_overdue(inv)]
        overdue = [inv for inv in invoices if inv["status"] == "overdue" or _is_overdue(inv)]
        paid = [inv for inv in invoices if inv["status"] == "paid"]
        return {
            "customer_id": customer_id,
            "summary": {"total_invoices": len(invoices), "paid": len(paid), "pending": len(pending), "overdue": len(overdue)},
            "overdue_invoices": [
                {"invoice_id": inv["invoice_id"], "amount": inv["amount"], "due_date": inv["due_date"], "days_overdue": _days_overdue(inv)}
                for inv in overdue
            ]
        }
    return make_error(
        "Missing payment status lookup criteria",
        reason="No invoice_id or customer_id was provided to scope the request.",
        hints=[
            "Use invoice_id for a specific invoice payment status.",
            "Use customer_id to summarise billing status across invoices."
        ],
        retryable=True,
        follow_up_tools=["check_payment_status"],
        expected_arguments=["invoice_id", "customer_id"]
    )


def get_billing_history(customer_id: str, start_date: str | None = None, end_date: str | None = None) -> dict:
    """All invoices of a customer, optionally limited to an issue-date window, with totals.

    Args:
        customer_id: unique customer identifier (e.g. CUST-001)
        start_date, end_date: only invoices issued between these dates (YYYY-MM-DD)
    """
    invoices = _customer_invoices(customer_id)
    if start_date or end_date:
        kept = []
        for inv in invoices:
            issued = _parse_date(inv["issue_date"])
            if not issued:
                continue
            if start_date and issued < _parse_date(start_date):
                continue
            if end_date and issued > _parse_date(end_date):
                continue
            kept.append(inv)
        invoices = kept
    return {
        "customer_id": customer_id, "start_date": start_date, "end_date": end_date,
        "invoices": invoices,
        "summary": {
            "total_invoices": len(invoices),
            "total_billed": sum(inv["amount"] for inv in invoices),
            "total_paid": sum(inv["amount"] for inv in invoices if inv["status"] == "paid"),
            "total_pending": sum(inv["amount"] for inv in invoices if inv["status"] in ("pending", "overdue")),
            "currency": "USD"
        }
    }


def calculate_outstanding_balance(customer_id: str) -> dict:
    """What a customer still owes: unpaid total, overdue total, and the unpaid invoices.

    Args:
        customer_id: unique customer identifier (e.g. CUST-002)
    """
    unpaid = [inv for inv in _customer_invoices(customer_id) if inv["status"] != "paid"]
    overdue = [inv for inv in unpaid if _is_overdue(inv)]
    return {
        "customer_id": customer_id,
        "outstanding_balance": sum(inv["amount"] for inv in unpaid),
        "currency": "USD",
        "overdue_amount": sum(inv["amount"] for inv in overdue),
        "number_of_unpaid_invoices": len(unpaid),
        "number_of_overdue_invoices": len(overdue),
        "unpaid_invoices": [
            {"invoice_id": inv["invoice_id"], "amount": inv["amount"], "status": inv["status"], "due_date": inv["due_date"],
             "is_overdue": _is_overdue(inv), "days_overdue": _days_overdue(inv)}
            for inv in unpaid
        ]
    }

# =============================================================================
# 4. MCP LAYER - the only part of this file that knows MCP exists
# =============================================================================
# Never print() in a server: on stdio, stdout IS the wire to the client.

mcp = MCPServer("billing")

mcp.tool(annotations=READ_ONLY)(get_invoice)
mcp.tool(annotations=READ_ONLY)(check_payment_status)
mcp.tool(annotations=READ_ONLY)(get_billing_history)
mcp.tool(annotations=READ_ONLY)(calculate_outstanding_balance)

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run()
