"""
Intent Mapping Test Framework

Tests whether the MCP orchestrator correctly maps user queries to the right tools.
This validates that GPT-4 is selecting appropriate tools for different query variations.

Usage:
    python test_intents.py

    or with API key:

    OPENAI_API_KEY=sk-... python test_intents.py
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from mcp_client import MCPOrchestrator


# ============================================================================
# TEST CASE DEFINITIONS
# ============================================================================

TEST_CASES = [
    {
        "intent": "search_critical_tickets",
        "description": "User wants to find critical priority tickets",
        "variations": [
            "What are the critical tickets?",
            "Show me all critical priority tickets",
            "List tickets with critical priority",
            "Find all tickets marked as critical",
            "Which tickets are critical right now?",
        ],
        "expected_tools": ["search_tickets"],
        "expected_args_contain": {"priority": "critical"},
    },
    {
        "intent": "customer_with_tickets",
        "description": "User wants customer info and their tickets",
        "variations": [
            "Show me all tickets for customer CUST-002 and their invoices",
            "Get CUST-001 information and their open tickets",
            "What tickets does customer CUST-003 have?",
            "Tell me about CUST-002 and show their tickets",
            "I need to see customer CUST-001's profile and tickets",
        ],
        "expected_tools": ["lookup_customer", "search_tickets"],
        "min_tool_calls": 2,
    },
    {
        "intent": "billing_status",
        "description": "User wants to check billing/payment status",
        "variations": [
            "What's the outstanding balance for customer CUST-002?",
            "Does CUST-001 have any unpaid invoices?",
            "Show me the billing status for TechCorp",
            "Check if customer CUST-003 owes us money",
            "What invoices are overdue?",
        ],
        "expected_tools": ["calculate_outstanding_balance", "get_invoice", "check_payment_status"],
        "min_tool_calls": 1,
        "match_any": True,  # Any of the expected tools is acceptable
    },
    {
        "intent": "knowledge_base_search",
        "description": "User wants KB articles about a topic",
        "variations": [
            "Find KB articles about BSOD",
            "Search knowledge base for Windows blue screen",
            "What solutions do we have for kernel panics?",
            "Show me documentation about disk space issues",
            "Look up articles on network troubleshooting",
        ],
        "expected_tools": ["search_solutions"],
        "expected_args_contain": {"query": ""},  # Should have query arg (any value)
    },
    {
        "intent": "asset_warranty_check",
        "description": "User wants to check asset warranty status",
        "variations": [
            "Check warranty for asset AST-SRV-001",
            "Is AST-SRV-001 still under warranty?",
            "When does the warranty expire for AST-SRV-002?",
            "Show me warranty status for server AST-SRV-003",
            "Which assets have warranties expiring soon?",
        ],
        "expected_tools": ["check_warranty", "lookup_asset"],
        "min_tool_calls": 1,
    },
    {
        "intent": "multi_server_customer_analysis",
        "description": "User wants comprehensive customer view (tickets, billing, assets)",
        "variations": [
            "Give me a complete overview of customer CUST-001",
            "Show me everything about CUST-002: tickets, invoices, and assets",
            "I need full customer analysis for CUST-003",
            "What's the status of customer CUST-001 across all systems?",
            "Pull up all information for customer CUST-002",
        ],
        "expected_tools": ["lookup_customer", "search_tickets", "get_invoice", "lookup_asset"],
        "min_tool_calls": 3,  # Should call at least 3 different tools
    },
    {
        "intent": "ticket_metrics",
        "description": "User wants ticket statistics and metrics",
        "variations": [
            "What are the ticket metrics for last 7 days?",
            "Show me ticket statistics",
            "How many tickets were resolved last month?",
            "Give me a summary of ticket volume",
            "What's the average resolution time?",
        ],
        "expected_tools": ["get_ticket_metrics"],
    },
    {
        "intent": "similar_tickets",
        "description": "User wants to find similar tickets",
        "variations": [
            "Find tickets similar to TKT-1001",
            "Are there other tickets like TKT-1002?",
            "Show me related tickets to TKT-1003",
            "What tickets are similar to this BSOD issue?",
            "Find duplicate or related tickets for TKT-1005",
        ],
        "expected_tools": ["find_similar_tickets", "get_ticket_details"],
        "min_tool_calls": 1,
    },
]


# ============================================================================
# TEST RUNNER
# ============================================================================

class IntentTestRunner:
    """Runs intent mapping tests against the MCP orchestrator"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.orchestrator = None
        self.results = []

    def setup(self):
        """Initialize orchestrator and start servers"""
        print("🚀 Setting up test environment...\n")
        self.orchestrator = MCPOrchestrator()
        self.orchestrator.start_servers()
        self.orchestrator.get_available_tools()
        print("✅ All servers started\n")

    def teardown(self):
        """Stop servers and clean up"""
        if self.orchestrator:
            print("\n🧹 Cleaning up...")
            self.orchestrator.stop_servers()
            print("✅ All servers stopped\n")

    def run_single_query(self, query: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single query and capture which tools were called

        Returns dict with:
            - query: the test query
            - tools_called: list of tool names that were called
            - success: whether the test passed
            - reason: explanation of pass/fail
        """
        # Monkey-patch to capture tool calls
        captured_tools = []
        original_call_tool = self.orchestrator._async_call_mcp_tool

        async def capturing_call_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
            captured_tools.append({
                "tool": tool_name,
                "arguments": arguments
            })
            return await original_call_tool(tool_name, arguments)

        self.orchestrator._async_call_mcp_tool = capturing_call_tool

        try:
            # Run the query
            print(f"  Testing: '{query}'")
            response = self.orchestrator.query(query, self.api_key, max_iterations=5)

            # Analyze results
            tool_names = [t["tool"] for t in captured_tools]
            result = self.validate_result(test_case, captured_tools)
            result["query"] = query
            result["tools_called"] = tool_names
            result["response_preview"] = response[:100] + "..." if len(response) > 100 else response

            return result

        finally:
            # Restore original method
            self.orchestrator._async_call_mcp_tool = original_call_tool

    def validate_result(self, test_case: Dict[str, Any], captured_tools: List[Dict]) -> Dict[str, Any]:
        """Validate if the captured tools match expectations"""
        tool_names = [t["tool"] for t in captured_tools]
        expected_tools = test_case["expected_tools"]

        # Check minimum tool calls
        min_calls = test_case.get("min_tool_calls", len(expected_tools))
        if len(captured_tools) < min_calls:
            return {
                "success": False,
                "reason": f"Too few tool calls ({len(captured_tools)} < {min_calls})"
            }

        # Check if expected tools were called
        match_any = test_case.get("match_any", False)

        if match_any:
            # At least one expected tool should be called
            if not any(tool in tool_names for tool in expected_tools):
                return {
                    "success": False,
                    "reason": f"None of expected tools {expected_tools} were called. Got: {tool_names}"
                }
        else:
            # All expected tools should be called
            for expected_tool in expected_tools:
                if expected_tool not in tool_names:
                    return {
                        "success": False,
                        "reason": f"Expected tool '{expected_tool}' was not called. Got: {tool_names}"
                    }

        # Check expected arguments if specified
        if "expected_args_contain" in test_case:
            expected_args = test_case["expected_args_contain"]
            found_args = False

            for tool_call in captured_tools:
                if all(key in tool_call["arguments"] for key in expected_args.keys()):
                    # Check if values match (if specified)
                    matches = True
                    for key, value in expected_args.items():
                        if value and tool_call["arguments"].get(key) != value:
                            matches = False
                            break
                    if matches:
                        found_args = True
                        break

            if not found_args:
                return {
                    "success": False,
                    "reason": f"Expected arguments {expected_args} not found in tool calls"
                }

        return {
            "success": True,
            "reason": "All validations passed"
        }

    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run all variations of a test case"""
        print(f"\n{'='*80}")
        print(f"Test Case: {test_case['intent']}")
        print(f"Description: {test_case['description']}")
        print(f"Expected Tools: {', '.join(test_case['expected_tools'])}")
        print(f"{'='*80}\n")

        results = []
        for variation in test_case["variations"]:
            result = self.run_single_query(variation, test_case)
            results.append(result)

            # Print result
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"    {status}: {result['reason']}")
            print(f"    Tools: {', '.join(result['tools_called']) if result['tools_called'] else 'None'}")
            print()

        # Calculate success rate
        passed = sum(1 for r in results if r["success"])
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0

        print(f"  📊 Success Rate: {passed}/{total} ({success_rate:.1f}%)\n")

        return {
            "intent": test_case["intent"],
            "description": test_case["description"],
            "total_variations": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": success_rate,
            "results": results
        }

    def run_all_tests(self):
        """Run all test cases"""
        print("\n" + "="*80)
        print("  MCP INTENT MAPPING TEST SUITE")
        print("="*80 + "\n")

        for test_case in TEST_CASES:
            result = self.run_test_case(test_case)
            self.results.append(result)

        self.print_summary()

    def print_summary(self):
        """Print overall test summary"""
        print("\n" + "="*80)
        print("  OVERALL TEST SUMMARY")
        print("="*80 + "\n")

        total_tests = sum(r["total_variations"] for r in self.results)
        total_passed = sum(r["passed"] for r in self.results)
        total_failed = sum(r["failed"] for r in self.results)
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Test Variations: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%\n")

        # Print per-intent breakdown
        print("Per-Intent Breakdown:")
        print("-" * 80)
        for result in self.results:
            status = "✅" if result["success_rate"] >= 80 else "⚠️" if result["success_rate"] >= 60 else "❌"
            print(f"{status} {result['intent']:40} {result['passed']}/{result['total_variations']:2} ({result['success_rate']:5.1f}%)")

        print("\n" + "="*80 + "\n")

        # Return exit code
        return 0 if overall_success_rate >= 80 else 1


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main test runner entry point"""
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("\nUsage:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  python test_intents.py")
        sys.exit(1)

    # Run tests
    runner = IntentTestRunner(api_key)

    try:
        runner.setup()
        runner.run_all_tests()
        exit_code = runner.print_summary()

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit_code = 130

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1

    finally:
        runner.teardown()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
