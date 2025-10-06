# Intent Mapping Testing Guide

## Overview

The **intent mapping test framework** validates whether the MCP orchestrator correctly maps user queries to the appropriate tools. This helps ensure GPT-4 is selecting the right tools for different query variations.

## Why Intent Mapping Tests?

When building AI-powered systems with tool calling, you need to ensure:
1. **Correct tool selection** - GPT-4 chooses the right tools for user queries
2. **Robustness** - System works across different phrasings of the same intent
3. **Multi-tool coordination** - Complex queries trigger multiple appropriate tools
4. **Consistency** - Similar queries produce similar tool call patterns

## How It Works

The test framework:
1. Defines **test cases** with multiple query variations
2. Specifies **expected tool calls** for each intent
3. Runs queries through the orchestrator
4. Captures which tools were actually called
5. Validates against expectations
6. Reports success rates and failures

## Running Tests

### Basic Usage

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='sk-...'

# Run all tests
python test_intents.py
```

### Expected Output

```
🚀 Setting up test environment...

✅ All servers started

================================================================================
  MCP INTENT MAPPING TEST SUITE
================================================================================

================================================================================
Test Case: search_critical_tickets
Description: User wants to find critical priority tickets
Expected Tools: search_tickets
================================================================================

  Testing: 'What are the critical tickets?'
    ✅ PASS: All validations passed
    Tools: search_tickets

  Testing: 'Show me all critical priority tickets'
    ✅ PASS: All validations passed
    Tools: search_tickets

  📊 Success Rate: 5/5 (100.0%)

...

================================================================================
  OVERALL TEST SUMMARY
================================================================================

Total Test Variations: 40
Passed: 38
Failed: 2
Overall Success Rate: 95.0%

Per-Intent Breakdown:
--------------------------------------------------------------------------------
✅ search_critical_tickets                      5/5  (100.0%)
✅ customer_with_tickets                        5/5  (100.0%)
⚠️  billing_status                              4/5  ( 80.0%)
✅ knowledge_base_search                        5/5  (100.0%)
...
```

## Test Case Structure

Each test case defines:

```python
{
    "intent": "search_critical_tickets",  # Unique identifier
    "description": "User wants to find critical priority tickets",
    "variations": [  # Different ways users might ask
        "What are the critical tickets?",
        "Show me all critical priority tickets",
        ...
    ],
    "expected_tools": ["search_tickets"],  # Tools that should be called
    "expected_args_contain": {"priority": "critical"},  # Optional: expected arguments
    "min_tool_calls": 1,  # Optional: minimum number of tool calls
    "match_any": False,  # Optional: if True, any expected tool is acceptable
}
```

### Validation Options

**`expected_tools`** (required): List of tool names that should be called
```python
"expected_tools": ["search_tickets"]
```

**`expected_args_contain`** (optional): Arguments that should be present
```python
"expected_args_contain": {"priority": "critical"}
# Checks that tool was called with priority="critical"
```

**`min_tool_calls`** (optional): Minimum number of tools that should be called
```python
"min_tool_calls": 3
# Expects at least 3 tool calls (useful for complex multi-step queries)
```

**`match_any`** (optional): Accept any of the expected tools
```python
"expected_tools": ["get_invoice", "check_payment_status", "calculate_outstanding_balance"],
"match_any": True
# Any one of these tools is acceptable
```

## Adding New Test Cases

### Example 1: Simple Single-Tool Intent

```python
{
    "intent": "get_customer_contacts",
    "description": "User wants to see customer contact list",
    "variations": [
        "Show me contacts for customer CUST-001",
        "Who are the contacts at TechCorp?",
        "List all contacts for CUST-002",
        "Get contact information for customer CUST-003",
    ],
    "expected_tools": ["list_customer_contacts"],
}
```

### Example 2: Multi-Tool Complex Intent

```python
{
    "intent": "ticket_analysis_with_customer",
    "description": "User wants ticket analysis including customer context",
    "variations": [
        "Analyze tickets for customer CUST-001 and show their SLA",
        "Give me ticket metrics and customer info for CUST-002",
        "Show customer profile and ticket statistics for TechCorp",
    ],
    "expected_tools": ["lookup_customer", "get_sla_terms", "search_tickets", "get_ticket_metrics"],
    "min_tool_calls": 2,  # Should call at least 2 tools
}
```

### Example 3: Flexible Tool Selection

```python
{
    "intent": "payment_inquiry",
    "description": "User asking about payment status (multiple valid approaches)",
    "variations": [
        "Has customer CUST-001 paid their invoices?",
        "Check payment status for TechCorp",
        "Are there any outstanding payments?",
    ],
    "expected_tools": ["check_payment_status", "calculate_outstanding_balance", "get_invoice"],
    "match_any": True,  # Any of these tools would be valid
    "min_tool_calls": 1,
}
```

## Interpreting Results

### Success Rates

- **100%**: Perfect - all query variations trigger correct tools
- **80-99%**: Good - most variations work, minor issues
- **60-79%**: Concerning - inconsistent tool selection
- **<60%**: Poor - needs attention

### Common Failure Patterns

**1. Tool Not Called**
```
❌ FAIL: Expected tool 'search_tickets' was not called. Got: ['lookup_customer']
```
**Possible causes:**
- Query wording unclear
- GPT-4 misinterpreting intent
- Similar tools confusing the model

**2. Wrong Arguments**
```
❌ FAIL: Expected arguments {'priority': 'critical'} not found in tool calls
```
**Possible causes:**
- Query doesn't clearly specify the parameter
- GPT-4 using different parameter interpretation

**3. Too Few Tool Calls**
```
❌ FAIL: Too few tool calls (1 < 3)
```
**Possible causes:**
- Query complexity unclear
- GPT-4 being too conservative
- Need more explicit multi-step request

## Integration with Student Workflow

### ✅ Doesn't Affect Interactive Experience

The test framework is **completely separate** from:
- Jupyter notebooks (`MCP_Demo.ipynb`)
- Interactive client (`interactive_client.py`)
- Direct function calls

Students can continue using the system normally. Tests are **opt-in** for validation.

### When to Run Tests

**As a Student:**
- After modifying prompts or system messages
- When adding new tools
- To understand query variations that work well

**As an Instructor:**
- To validate system behavior
- To create grading rubrics
- To demonstrate robustness

## Extending the Framework

### Custom Validation Logic

You can add custom validation methods to `IntentTestRunner`:

```python
def validate_custom(self, test_case, captured_tools):
    """Custom validation logic"""
    # Example: Check that tools were called in specific order
    tool_names = [t["tool"] for t in captured_tools]

    if test_case["intent"] == "my_custom_intent":
        if tool_names[0] != "lookup_customer":
            return {
                "success": False,
                "reason": "Should call lookup_customer first"
            }

    return {"success": True, "reason": "Custom validation passed"}
```

### Export Results to JSON

Add to `IntentTestRunner`:

```python
def save_results(self, filename="test_results.json"):
    """Save results to JSON file"""
    with open(filename, 'w') as f:
        json.dump(self.results, f, indent=2)
    print(f"Results saved to {filename}")
```

### Integration with CI/CD

```bash
#!/bin/bash
# test_ci.sh - Run in CI pipeline

export OPENAI_API_KEY=$CI_OPENAI_KEY

python test_intents.py
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed - check logs"
fi

exit $exit_code
```

## Best Practices

### 1. Query Variation Design

**Good variations:**
```python
"variations": [
    "What are the critical tickets?",           # Direct
    "Show me all critical priority tickets",    # Explicit
    "List tickets with critical priority",      # Different verb
    "Find all tickets marked as critical",      # Different phrasing
    "Which tickets are critical right now?",    # Conversational
]
```

**Poor variations:**
```python
"variations": [
    "critical tickets",                         # Too terse
    "tickets",                                  # Too vague
    "show critical",                            # Incomplete
]
```

### 2. Expected Tool Selection

Be realistic about GPT-4's behavior:
- Some queries can legitimately use multiple approaches
- Use `match_any=True` when appropriate
- Set `min_tool_calls` rather than exact counts

### 3. Test Case Organization

Group related intents:
```python
# Basic single-tool intents
- search_critical_tickets
- get_customer_info
- check_warranty

# Multi-tool intents
- customer_with_tickets
- comprehensive_analysis

# Complex reasoning intents
- troubleshooting_workflow
- escalation_decision
```

## Troubleshooting

### Tests Failing Due to GPT-4 Updates

GPT-4's behavior can change over time. If tests start failing:

1. Review actual tool calls - are they reasonable alternatives?
2. Update test expectations if GPT-4's approach is valid
3. Consider making tests more flexible with `match_any`

### Rate Limiting

If you hit OpenAI rate limits:

```python
# Add delay between queries
import time

def run_single_query(self, query: str, test_case: Dict[str, Any]):
    time.sleep(1)  # 1 second delay
    # ... rest of method
```

### Inconsistent Results

GPT-4 can be non-deterministic. If a test passes sometimes:

1. Run the test multiple times
2. Calculate pass rate over multiple runs
3. Adjust expectations or query wording

## Summary

The intent mapping test framework provides:

✅ **Automated validation** of tool selection
✅ **Robustness testing** across query variations
✅ **Non-intrusive** - doesn't affect student experience
✅ **Extensible** - easy to add new test cases
✅ **Informative** - detailed pass/fail reporting

Use it to ensure your MCP orchestrator reliably maps user intents to the correct tools!
