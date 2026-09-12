"""
Bits every server in this course shares.

- days_ago / days_from_now: the mock data uses dates relative to "today", so
  the demos (time windows, overdue invoices, warranties) keep working no matter
  when you run the course.
- make_error: the structured error payload. Errors are written for the MODEL,
  not for a human: what went wrong, what to try next, which tool to call.
- READ_ONLY / WRITES: the two annotation presets we attach to tools, so a host
  (Claude Code, Claude Desktop, ...) can tell a harmless lookup from a change.
"""

from datetime import datetime, timedelta

from mcp.types import ToolAnnotations


def days_ago(days: int) -> str:
    """ISO date string for `days` days before today."""
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


def days_from_now(days: int) -> str:
    """ISO date string for `days` days after today."""
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")


def make_error(message, *, reason=None, hints=None, retryable=False, follow_up_tools=None, **extra):
    """
    Build an error the model can act on.

    Returned as an ordinary result (not raised), so the model reads it like any
    other tool output and can decide what to do next.
    """
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


# Tool annotations are hints for the host application, not rules for the model.
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
WRITES = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
