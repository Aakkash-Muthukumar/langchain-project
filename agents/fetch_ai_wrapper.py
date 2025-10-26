"""
Fetch.AI Agent Wrapper for LangChain Customer Support System

This module wraps the existing LangChain customer support multi-agent system
with Fetch.AI agents to enable decentralized message-based communication.

Architecture:
- Fetch.AI agents receive external messages
- Forward to LangChain orchestrator for processing
- Send responses back via Fetch.AI messaging
"""

from datetime import datetime
from typing import Dict, Any
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Import LangChain orchestrator
from agents.main_agents import CustomerSupportOrchestrator

load_dotenv()

# ============================================================================
# Message Models for Fetch.AI Communication
# ============================================================================

class CustomerQuery(Model):
    """Incoming customer query message"""
    customer_id: str
    query: str
    timestamp: str
    priority: str = "normal"  # normal, high, urgent


class AgentResponse(Model):
    """Response from agent processing"""
    customer_id: str
    response: str
    agent_type: str
    timestamp: str
    status: str = "success"  # success, partial, error


class EscalationRequest(Model):
    """Request to escalate to human agent"""
    customer_id: str
    original_query: str
    reason: str
    timestamp: str


class EscalationResponse(Model):
    """Response from escalation"""
    customer_id: str
    ticket_id: str
    assigned_agent: str
    timestamp: str


class HealthCheck(Model):
    """Health check message"""
    agent_address: str
    timestamp: str
    status: str = "healthy"


# ============================================================================
# Fetch.AI Wrapper Agent
# ============================================================================

class FetchAILangChainWrapper:
    """
    Wraps LangChain agents with Fetch.AI framework for decentralized
    message-based communication.
    """
    
    def __init__(self, agent_name: str = "langchain_support_agent"):
        """
        Initialize the Fetch.AI wrapper
        
        Args:
            agent_name: Name of the agent in the Fetch.AI network
        """
        self.agent_name = agent_name
        
        # Create Fetch.AI agent
        self.agent = Agent(
            name=agent_name,
            seed=os.getenv("AGENT_SEED_PHRASE", "default_seed_phrase"),
            port=int(os.getenv("AGENT_PORT", 8000)),
            mailbox=True,  # Use mailbox for always-on capability
            endpoint=[os.getenv("AGENT_ENDPOINT", "http://localhost:8000/submit")]
        )
        
        # Initialize LangChain orchestrator
        self.orchestrator = CustomerSupportOrchestrator()
        
        # Message routing table
        self.handlers = {}
        
        # Setup message handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all message handlers"""
        
        @self.agent.on_message(model=CustomerQuery)
        async def handle_customer_query(ctx: Context, sender: str, msg: CustomerQuery):
            """Handle incoming customer queries"""
            ctx.logger.info(f"Received query from {sender}: {msg.query}")
            
            try:
                # Process query through LangChain orchestrator
                result = self.orchestrator.process_query(msg.query)
                
                # Extract response details
                response_text = result.get("output", "Unable to process query")
                agent_type = self._extract_agent_type(result)
                
                # Create response message
                response = AgentResponse(
                    customer_id=msg.customer_id,
                    response=response_text,
                    agent_type=agent_type,
                    timestamp=str(datetime.now()),
                    status="success"
                )
                
                # Send response back
                await ctx.send(sender, response)
                ctx.logger.info(f"Sent response to {sender}")
                
            except Exception as e:
                ctx.logger.error(f"Error processing query: {str(e)}")
                
                # Send error response
                error_response = AgentResponse(
                    customer_id=msg.customer_id,
                    response=f"Error processing query: {str(e)}",
                    agent_type="error_handler",
                    timestamp=str(datetime.now()),
                    status="error"
                )
                await ctx.send(sender, error_response)
        
        @self.agent.on_message(model=EscalationRequest)
        async def handle_escalation_request(ctx: Context, sender: str, msg: EscalationRequest):
            """Handle escalation requests"""
            ctx.logger.info(f"Received escalation request from {sender}")
            
            try:
                # Process through escalation agent
                escalation_input = f"""
                Customer ID: {msg.customer_id}
                Original Query: {msg.original_query}
                Reason for Escalation: {msg.reason}
                Please create a ticket and assign to human agent.
                """
                
                result = self.orchestrator.escalation_agent.handle_escalation(
                    escalation_input,
                    {"original_query": msg.original_query}
                )
                
                # Send escalation response
                response = EscalationResponse(
                    customer_id=msg.customer_id,
                    ticket_id=result.get("ticket_id", "TKT_AUTO_" + msg.customer_id),
                    assigned_agent=result.get("assigned_agent", "human_support_team"),
                    timestamp=str(datetime.now())
                )
                await ctx.send(sender, response)
                ctx.logger.info(f"Escalation processed for {msg.customer_id}")
                
            except Exception as e:
                ctx.logger.error(f"Escalation error: {str(e)}")
        
        @self.agent.on_message(model=HealthCheck)
        async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
            """Handle health check requests"""
            ctx.logger.info(f"Health check from {sender}")
            
            response = HealthCheck(
                agent_address=ctx.agent.address,
                timestamp=str(datetime.now()),
                status="healthy"
            )
            await ctx.send(sender, response)
    
    def _extract_agent_type(self, result: Dict[str, Any]) -> str:
        """Extract agent type from result"""
        output = result.get("output", "").lower()
        
        if "technical" in output:
            return "technical_support_agent"
        elif "billing" in output or "payment" in output or "subscription" in output:
            return "billing_agent"
        elif "escalat" in output or "human" in output:
            return "escalation_agent"
        else:
            return "triage_agent"
    
    @property
    def address(self) -> str:
        """Get agent address on Fetch.AI network"""
        return self.agent.address
    
    def run(self):
        """Start the agent"""
        self.agent.run()


# ============================================================================
# REST API Endpoints
# ============================================================================

def setup_rest_api(wrapper: FetchAILangChainWrapper):
    """
    Setup REST API endpoints for the agent.
    
    This allows external systems to interact with the agent via HTTP.
    """
    
    class QueryRequest(Model):
        """REST endpoint request model"""
        customer_id: str
        query: str
    
    @wrapper.agent.on_rest_post("/query", QueryRequest, AgentResponse)
    async def handle_rest_query(ctx: Context, req: QueryRequest) -> AgentResponse:
        """Handle REST POST query"""
        ctx.logger.info(f"REST query from {req.customer_id}: {req.query}")
        
        try:
            result = wrapper.orchestrator.process_query(req.query)
            
            return AgentResponse(
                customer_id=req.customer_id,
                response=result.get("output", "Unable to process"),
                agent_type=wrapper._extract_agent_type(result),
                timestamp=str(datetime.now()),
                status="success"
            )
        except Exception as e:
            ctx.logger.error(f"REST query error: {str(e)}")
            return AgentResponse(
                customer_id=req.customer_id,
                response=f"Error: {str(e)}",
                agent_type="error_handler",
                timestamp=str(datetime.now()),
                status="error"
            )
    
    class HealthStatus(Model):
        """Health status response"""
        agent_address: str
        agent_name: str
        status: str
        timestamp: str
    
    @wrapper.agent.on_rest_get("/health", HealthStatus)
    async def handle_health(ctx: Context) -> HealthStatus:
        """Handle health check"""
        return HealthStatus(
            agent_address=ctx.agent.address,
            agent_name=wrapper.agent_name,
            status="healthy",
            timestamp=str(datetime.now())
        )


# ============================================================================
# Scheduled Tasks
# ============================================================================

def setup_scheduled_tasks(wrapper: FetchAILangChainWrapper):
    """
    Setup scheduled/periodic tasks.
    """
    
    @wrapper.agent.on_event("startup")
    async def startup_handler(ctx: Context):
        """Handle agent startup"""
        ctx.logger.info(f"Agent '{wrapper.agent_name}' started")
        ctx.logger.info(f"Agent address: {ctx.agent.address}")
        
        # Fund agent if balance is low
        try:
            fund_agent_if_low(str(ctx.agent.address))
            ctx.logger.info("Agent funding check completed")
        except Exception as e:
            ctx.logger.warning(f"Could not fund agent: {str(e)}")
    
    @wrapper.agent.on_interval(period=300.0)  # Every 5 minutes
    async def periodic_health_check(ctx: Context):
        """Periodic health check"""
        ctx.logger.info(f"Health check - Agent is running")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    
    print("=" * 60)
    print("Fetch.AI LangChain Wrapper - Customer Support Agent")
    print("=" * 60)
    
    # Create wrapper
    wrapper = FetchAILangChainWrapper(
        agent_name=os.getenv("AGENT_NAME", "langchain_support_agent")
    )
    
    # Setup REST API
    setup_rest_api(wrapper)
    
    # Setup scheduled tasks
    setup_scheduled_tasks(wrapper)
    
    print(f"\nAgent Name: {wrapper.agent_name}")
    print(f"Agent Address: {wrapper.address}")
    print(f"Agent Port: {os.getenv('AGENT_PORT', 8000)}")
    print(f"Mailbox Mode: Enabled")
    print("\n" + "=" * 60)
    print("Starting agent... Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    # Run the agent
    wrapper.run()


if __name__ == "__main__":
    main()
