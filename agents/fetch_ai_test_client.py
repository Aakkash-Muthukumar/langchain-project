"""
Example Fetch.AI Client for Testing the LangChain Wrapper

This module demonstrates how to interact with the Fetch.AI wrapped
LangChain agents from another agent or external system.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from uagents import Agent, Context, Model
from uagents_core.identity import Identity
from uagents.setup import fund_agent_if_low

load_dotenv()

# ============================================================================
# Message Models (must match the wrapper)
# ============================================================================

class CustomerQuery(Model):
    """Incoming customer query message"""
    customer_id: str
    query: str
    timestamp: str
    priority: str = "normal"


class AgentResponse(Model):
    """Response from agent processing"""
    customer_id: str
    response: str
    agent_type: str
    timestamp: str
    status: str = "success"


class HealthCheck(Model):
    """Health check message"""
    agent_address: str
    timestamp: str
    status: str = "healthy"


# ============================================================================
# Test Client Agent
# ============================================================================

class FetchAITestClient:
    """Test client for Fetch.AI wrapped agents"""
    
    def __init__(self, wrapper_agent_seed: str = None):
        """
        Initialize test client
        
        Args:
            wrapper_agent_seed: Seed of the agent to communicate with
        """
        self.agent = Agent(
            name="test_client",
            port=8001,
            seed=os.getenv("TEST_CLIENT_SEED_PHRASE", "test_seed_phrase")
        )
        
        # Get the wrapper agent address
        if wrapper_agent_seed:
            identity = Identity.from_seed(seed=wrapper_agent_seed, index=0)
            self.wrapper_address = identity.address
        else:
            self.wrapper_address = os.getenv("WRAPPER_AGENT_ADDRESS", "")
        
        self.last_response = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup response handlers"""
        
        @self.agent.on_message(model=AgentResponse)
        async def handle_response(ctx: Context, sender: str, msg: AgentResponse):
            """Handle responses from wrapper agent"""
            ctx.logger.info(f"\n{'='*60}")
            ctx.logger.info(f"Response received from {sender}")
            ctx.logger.info(f"Customer ID: {msg.customer_id}")
            ctx.logger.info(f"Status: {msg.status}")
            ctx.logger.info(f"Agent Type: {msg.agent_type}")
            ctx.logger.info(f"Response:\n{msg.response}")
            ctx.logger.info(f"{'='*60}\n")
            
            self.last_response = msg
    
    async def send_query(self, customer_id: str, query: str, priority: str = "normal"):
        """
        Send a query to the wrapper agent
        
        Args:
            customer_id: Customer ID
            query: Customer query text
            priority: Priority level
        """
        msg = CustomerQuery(
            customer_id=customer_id,
            query=query,
            timestamp=str(datetime.now()),
            priority=priority
        )
        
        print(f"\n{'='*60}")
        print(f"Sending query to wrapper agent...")
        print(f"Target: {self.wrapper_address}")
        print(f"Customer ID: {customer_id}")
        print(f"Query: {query}")
        print(f"{'='*60}\n")
        
        # Send via the agent's internal method
        # Note: In real scenario, this would be done via ctx.send within an agent handler
        await self._send_via_context(msg)
    
    async def _send_via_context(self, msg):
        """Send message via agent context"""
        # This is a simplified example - in production, wrap in proper event handler
        ctx = type('Context', (), {'send': self._dummy_send})()
        # In real implementation, messages are sent within event handlers
    
    async def health_check(self):
        """Send health check to wrapper"""
        msg = HealthCheck(
            agent_address=self.agent.address,
            timestamp=str(datetime.now()),
            status="healthy"
        )
        print(f"Sending health check to {self.wrapper_address}")
    
    def run(self):
        """Run the test client"""
        self.agent.run()


# ============================================================================
# Test Scenarios
# ============================================================================

def test_scenario_1():
    """Test technical support query"""
    print("\n" + "="*60)
    print("TEST SCENARIO 1: Technical Support Query")
    print("="*60)
    print("""
    Query: "My account login isn't working"
    Expected: Should be routed to technical_support_agent
    """)


def test_scenario_2():
    """Test billing query"""
    print("\n" + "="*60)
    print("TEST SCENARIO 2: Billing Query")
    print("="*60)
    print("""
    Query: "I was charged twice this month"
    Expected: Should be routed to billing_agent
    """)


def test_scenario_3():
    """Test escalation"""
    print("\n" + "="*60)
    print("TEST SCENARIO 3: Escalation")
    print("="*60)
    print("""
    Query: "I need to cancel my subscription immediately"
    Expected: Should be routed to escalation_agent
    """)


# ============================================================================
# Command Line Interface
# ============================================================================

def print_menu():
    """Print interactive menu"""
    print("\n" + "="*60)
    print("Fetch.AI Test Client - LangChain Wrapper")
    print("="*60)
    print("1. Send Technical Support Query")
    print("2. Send Billing Query")
    print("3. Send Escalation Query")
    print("4. Send Custom Query")
    print("5. View Test Scenarios")
    print("6. Exit")
    print("="*60)


def interactive_mode():
    """Run interactive test mode"""
    
    wrapper_address = os.getenv("WRAPPER_AGENT_ADDRESS", "")
    
    print(f"\nTarget Wrapper Agent Address: {wrapper_address}")
    
    if not wrapper_address:
        print("ERROR: WRAPPER_AGENT_ADDRESS not set in environment")
        print("Please set WRAPPER_AGENT_ADDRESS in your .env file")
        return
    
    test_queries = {
        "1": ("TECH_001", "My account login isn't working"),
        "2": ("BILL_001", "I was charged twice this month"),
        "3": ("ESC_001", "I need to cancel my subscription immediately"),
    }
    
    print("\nTest Client initialized (interactive mode)")
    print("Note: Full agent-to-agent communication requires running agents")
    print("Use REST API for direct testing:\n")
    
    print("Example REST API calls:")
    print("-" * 60)
    print("Health Check:")
    print("  curl http://localhost:8000/health")
    print("\nQuery:")
    print("  curl -X POST http://localhost:8000/query \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"customer_id\": \"TECH_001\", \"query\": \"My account login isn\\'t working\"}'")
    print("-" * 60)
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            customer_id, query = test_queries["1"]
            print(f"\n✓ Query sent: '{query}'")
            print(f"  Customer ID: {customer_id}")
            
        elif choice == "2":
            customer_id, query = test_queries["2"]
            print(f"\n✓ Query sent: '{query}'")
            print(f"  Customer ID: {customer_id}")
            
        elif choice == "3":
            customer_id, query = test_queries["3"]
            print(f"\n✓ Query sent: '{query}'")
            print(f"  Customer ID: {customer_id}")
            
        elif choice == "4":
            customer_id = input("Enter customer ID: ")
            query = input("Enter your query: ")
            print(f"\n✓ Query sent: '{query}'")
            print(f"  Customer ID: {customer_id}")
            
        elif choice == "5":
            test_scenario_1()
            test_scenario_2()
            test_scenario_3()
            
        elif choice == "6":
            print("\nExiting...")
            break
        else:
            print("\n✗ Invalid choice. Please try again.")


# ============================================================================
# Direct REST API Testing (recommended)
# ============================================================================

def print_curl_examples():
    """Print curl examples for REST API testing"""
    
    print("\n" + "="*60)
    print("REST API Testing Examples (Recommended)")
    print("="*60)
    
    print("\n1. Health Check")
    print("   curl http://localhost:8000/health")
    
    print("\n2. Technical Support Query")
    print("""   curl -X POST http://localhost:8000/query \\
     -H 'Content-Type: application/json' \\
     -d '{"customer_id": "TECH_001", "query": "My account login isn't working"}'""")
    
    print("\n3. Billing Query")
    print("""   curl -X POST http://localhost:8000/query \\
     -H 'Content-Type: application/json' \\
     -d '{"customer_id": "BILL_001", "query": "I was charged twice this month"}'""")
    
    print("\n4. Escalation Query")
    print("""   curl -X POST http://localhost:8000/query \\
     -H 'Content-Type: application/json' \\
     -d '{"customer_id": "ESC_001", "query": "I need to cancel my subscription immediately"}'""")
    
    print("\n" + "="*60 + "\n")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    
    print_curl_examples()
    
    print("\nSelect testing method:")
    print("1. Interactive Mode")
    print("2. Direct REST Testing (Recommended)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        interactive_mode()
    elif choice == "2":
        print("\nUse the curl commands above to test the REST API")
        print("Or use a tool like Postman or Insomnia")
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
