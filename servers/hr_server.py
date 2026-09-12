"""
HR server: the small server we use to show RESOURCES and PROMPTS.

- A resource is a document with an address (a URI). The host shows it to the
  user, who can attach it to a conversation. The model does not decide to read
  it; the person does.
- A prompt is a reusable message template the host offers as a menu item or a
  slash command. The person picks it and fills in the blanks.
- Tools stay what they were: functions the model decides to call.

This file uses the decorator spelling (@mcp.resource / @mcp.prompt / @mcp.tool)
so you see both ways of registering things. The five help-desk servers use
mcp.tool(...)(function) at the bottom of the file instead; same result.

Run:    python servers/hr_server.py [--http]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import READ_ONLY, make_error
from mcp.server import MCPServer

# =============================================================================
# 1. DATA
# =============================================================================

HR_POLICIES = {
    "benefits": {
        "title": "Employee Benefits Guide",
        "content": """Employee Benefits Guide
=======================

Health Insurance:
- Medical: 100% premium covered for employees, 75% for dependents
- Dental: 100% premium covered for employees and dependents
- Vision: available with no employee contribution

Retirement:
- Pension plan with 6% company match
- Immediate vesting

Time Off:
- 20 days paid time off per year
- 10 paid holidays
- Unlimited sick days
"""
    },
    "remote-work": {
        "title": "Remote Work Policy",
        "content": """Remote Work Policy
==================

Eligibility:
- All full-time employees after 3 months of employment
- Manager approval required

Remote Work Options:
- Fully remote: work from anywhere in the country
- Hybrid: minimum 2 days per week in the office
- Flexible: choose your schedule with team coordination

Equipment:
- Company provides laptop, monitor, keyboard, mouse
- 500 EUR annual home office allowance

Requirements:
- Reliable high-speed internet (minimum 25 Mbps)
- Dedicated workspace
- Available during core hours (10:00 to 15:00 local time)
"""
    },
    "pto-accrual": {
        "title": "Paid Time Off Accrual Policy",
        "content": """Paid Time Off Accrual Policy
============================

Accrual Rate:
- Years 0-2: 15 days per year (1.25 days per month)
- Years 3-5: 20 days per year (1.67 days per month)
- Years 6+: 25 days per year (2.08 days per month)

Rollover:
- Maximum 40 days can be carried to the next year
- Unused days beyond 40 are forfeited

Payout:
- Upon termination: up to 20 days paid out
- Voluntary resignation: 2 weeks notice required for payout
"""
    },
}

EMPLOYEES = {
    "EMP-001": {
        "name": "Alice Johnson",
        "role": "Senior Software Engineer",
        "department": "Engineering",
        "hire_date": "2021-03-15",
        "manager": "Sarah Chen",
        "projects": ["Payment API Redesign", "Database Migration"],
        "skills": ["Python", "PostgreSQL", "Kubernetes"]
    },
    "EMP-002": {
        "name": "Michael Rodriguez",
        "role": "Product Designer",
        "department": "Design",
        "hire_date": "2022-06-01",
        "manager": "Emily Johnson",
        "projects": ["Mobile App Redesign", "Design System v2"],
        "skills": ["Figma", "User Research", "Prototyping"]
    },
    "EMP-003": {
        "name": "Jennifer Park",
        "role": "Data Analyst",
        "department": "Analytics",
        "hire_date": "2023-01-10",
        "manager": "Kevin Wilson",
        "projects": ["Customer Churn Analysis", "Revenue Dashboard"],
        "skills": ["SQL", "Python", "Tableau", "Statistics"]
    },
}

# =============================================================================
# 4. MCP LAYER (this server is small enough to have no helpers of its own)
# =============================================================================
# Never print() in a server: on stdio, stdout IS the wire to the client.

mcp = MCPServer("hr")


@mcp.resource("hr://policy-index")
def policy_index() -> str:
    """List of all HR policy documents and their addresses."""
    return "\n".join(f"hr://policy/{key}  -  {doc['title']}" for key, doc in HR_POLICIES.items())


@mcp.resource("hr://policy/{name}")
def policy(name: str) -> str:
    """One HR policy document by its short name: benefits, remote-work or pto-accrual."""
    if name not in HR_POLICIES:
        return f"No policy called '{name}'. Known policies: {', '.join(HR_POLICIES)}."
    return HR_POLICIES[name]["content"]


@mcp.prompt()
def performance_review(employee_id: str, review_period: str) -> str:
    """Structured brief for writing an employee's performance review."""
    emp = EMPLOYEES.get(employee_id)
    who = (f"{emp['name']} ({emp['role']}, {emp['department']}, manager {emp['manager']}, hired {emp['hire_date']}). "
           f"Recent projects: {', '.join(emp['projects'])}. Skills: {', '.join(emp['skills'])}."
           if emp else f"employee {employee_id} (no record found; ask for details)")
    return f"""Write a performance review for {who}
Review period: {review_period}.

Follow this structure:
1. Achievements: 3 to 5 concrete accomplishments from the period.
2. Core competencies: rate technical skills, communication, collaboration, initiative and quality of work
   as Needs Improvement / Meets Expectations / Exceeds Expectations, with one example each.
3. Growth areas: 2 or 3, phrased constructively with a specific suggestion.
4. Goals for the next period: 3 SMART goals aligned with the department.
5. Overall rating and a one-paragraph summary.
Be specific, fair and constructive."""


@mcp.tool(annotations=READ_ONLY)
def get_employee(employee_id: str) -> dict:
    """Basic record of one employee: name, role, department, manager, hire date, projects, skills.

    Args:
        employee_id: employee identifier (e.g. EMP-001)
    """
    emp = EMPLOYEES.get(employee_id)
    if not emp:
        return make_error(
            f"Employee {employee_id} not found",
            reason="The employee_id is not in the HR dataset.",
            hints=[f"Known IDs: {', '.join(EMPLOYEES)}."],
            retryable=True,
            employee_id=employee_id
        )
    return {"employee_id": employee_id, **emp}


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run()
