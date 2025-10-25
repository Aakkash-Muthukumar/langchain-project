"""
Customer Support Multi-Agent System

This module implements a multi-agent system for automated customer support
using LangChain. It includes multiple specialized agents that work together
to handle customer queries efficiently.
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from typing import Dict, List, Any
import os

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=1024,
    api_key=os.getenv("GEMINI_API_KEY")
)


class TriageAgent:
    """
    Triage Agent - Routes customer queries to appropriate specialist agents
    
    This agent analyzes incoming customer queries and determines which
    specialist agent should handle the request based on the query content.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "triage_agent"
        self.type = "zero-shot-react-description"
        
        # System instruction for the triage agent
        self.system_instruction = """You are a customer support triage agent.
Your role is to analyze customer queries and route them to the appropriate specialist:
- Technical issues → Technical Support Agent
- Billing/payment issues → Billing Agent
- Complex or escalated cases → Escalation Agent

Be professional, empathetic, and efficient in your routing decisions."""

        # Prompt template
        self.prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template="""Answer the following question as best you can.

Question: {input}

{agent_scratchpad}"""
        )
        
        # Tools available to triage agent
        from tools.database_tools import query_customer_history
        from tools.knowledge_tools import search_knowledge_base
        
        self.tools = [
            Tool(
                name="query_customer_history",
                func=query_customer_history,
                description="Query customer history and previous interactions"
            ),
            Tool(
                name="search_knowledge_base",
                func=search_knowledge_base,
                description="Search the knowledge base for relevant articles"
            )
        ]
        
        # Create the agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Route customer query to appropriate agent
        
        Args:
            query: Customer query text
            
        Returns:
            Dict containing routing decision and reasoning
        """
        result = self.executor.invoke({"input": query})
        return result
    
    def handoff_to_technical(self, query: str):
        """Hand off query to technical support agent"""
        # This creates a relationship with TechnicalSupportAgent
        from agents.technical_agent import TechnicalSupportAgent
        tech_agent = TechnicalSupportAgent(self.llm)
        return tech_agent.handle_query(query)
    
    def handoff_to_billing(self, query: str):
        """Hand off query to billing agent"""
        # This creates a relationship with BillingAgent
        from agents.billing_agent import BillingAgent
        billing_agent = BillingAgent(self.llm)
        return billing_agent.handle_query(query)


class TechnicalSupportAgent:
    """
    Technical Support Agent - Handles technical issues and troubleshooting
    
    This agent specializes in diagnosing and resolving technical problems,
    providing step-by-step troubleshooting guidance.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "technical_support_agent"
        self.type = "conversational-react-description"
        
        self.system_instruction = """You are a technical support specialist.
Your role is to diagnose and resolve technical issues efficiently.
Provide clear, step-by-step instructions and be patient with customers.
If an issue is too complex, escalate to the Escalation Agent."""

        self.prompt = PromptTemplate(
            input_variables=["input", "chat_history", "agent_scratchpad"],
            template="""You are a helpful technical support agent.

Chat History:
{chat_history}

Question: {input}

{agent_scratchpad}"""
        )
        
        # Technical support tools
        from tools.technical_tools import run_diagnostics, check_system_status
        from tools.knowledge_tools import search_knowledge_base
        
        self.tools = [
            Tool(
                name="run_diagnostics",
                func=run_diagnostics,
                description="Run system diagnostics to identify technical issues"
            ),
            Tool(
                name="check_system_status",
                func=check_system_status,
                description="Check current system status and health"
            ),
            Tool(
                name="search_knowledge_base",
                func=search_knowledge_base,
                description="Search technical documentation and solutions"
            )
        ]
        
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle technical support query"""
        result = self.executor.invoke({"input": query})
        
        # Check if escalation is needed
        if self._needs_escalation(result):
            return self.escalate(query, result)
        
        return result
    
    def _needs_escalation(self, result: Dict[str, Any]) -> bool:
        """Determine if issue needs escalation"""
        # Simple heuristic - check if solution was found
        return "unable to resolve" in result.get("output", "").lower()
    
    def escalate(self, query: str, context: Dict[str, Any]):
        """Escalate to escalation agent"""
        from agents.escalation_agent import EscalationAgent
        escalation_agent = EscalationAgent(self.llm)
        return escalation_agent.handle_escalation(query, context)


class BillingAgent:
    """
    Billing Agent - Manages billing, payments, and subscription queries
    
    This agent handles all financial transactions, subscription management,
    and billing-related customer inquiries.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "billing_agent"
        self.type = "zero-shot-react-description"
        
        self.system_instruction = """You are a billing and payments specialist.
Your role is to handle billing inquiries, process payments, and manage subscriptions.
Be accurate with financial information and follow security protocols.
Verify customer identity before discussing sensitive financial data."""

        self.prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template="""Handle the following billing inquiry professionally.

Inquiry: {input}

{agent_scratchpad}"""
        )
        
        # Billing tools
        from tools.billing_tools import query_billing_history, process_refund, update_subscription
        from tools.database_tools import query_customer_history
        
        self.tools = [
            Tool(
                name="query_billing_history",
                func=query_billing_history,
                description="Query customer's billing and payment history"
            ),
            Tool(
                name="process_refund",
                func=process_refund,
                description="Process a refund for the customer"
            ),
            Tool(
                name="update_subscription",
                func=update_subscription,
                description="Update or modify customer subscription"
            ),
            Tool(
                name="query_customer_history",
                func=query_customer_history,
                description="Query customer's account information"
            )
        ]
        
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=8,
            handle_parsing_errors=True
        )
    
    def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle billing query"""
        return self.executor.invoke({"input": query})


class EscalationAgent:
    """
    Escalation Agent - Handles complex cases requiring human intervention
    
    This agent manages escalated cases, creates tickets for human agents,
    and ensures proper handoff of complex issues.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "escalation_agent"
        self.type = "zero-shot-react-description"
        
        self.system_instruction = """You are an escalation specialist.
Your role is to handle complex cases that require human intervention.
Create detailed tickets, summarize context, and ensure smooth handoff to human agents.
Prioritize cases appropriately and maintain professional communication."""

        self.prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template="""Handle this escalated case with care and professionalism.

Case: {input}

{agent_scratchpad}"""
        )
        
        # Escalation tools
        from tools.ticket_tools import create_ticket, assign_to_human
        from tools.notification_tools import send_email, send_slack_notification
        
        self.tools = [
            Tool(
                name="create_ticket",
                func=create_ticket,
                description="Create a support ticket for human agents"
            ),
            Tool(
                name="assign_to_human",
                func=assign_to_human,
                description="Assign case to a human support agent"
            ),
            Tool(
                name="send_email",
                func=send_email,
                description="Send email notification to customer or team"
            ),
            Tool(
                name="send_slack_notification",
                func=send_slack_notification,
                description="Send notification to support team via Slack"
            )
        ]
        
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=6,
            handle_parsing_errors=True
        )
    
    def handle_escalation(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle escalated case"""
        escalation_input = f"""
Query: {query}
Context: {context}
Please create a ticket and assign to appropriate human agent.
"""
        return self.executor.invoke({"input": escalation_input})


# Agent orchestrator
class CustomerSupportOrchestrator:
    """
    Main orchestrator that coordinates all agents
    """
    
    def __init__(self):
        self.llm = llm
        self.triage_agent = TriageAgent(self.llm)
        self.technical_agent = TechnicalSupportAgent(self.llm)
        self.billing_agent = BillingAgent(self.llm)
        self.escalation_agent = EscalationAgent(self.llm)
    
    def process_query(self, customer_query: str) -> Dict[str, Any]:
        """
        Process customer query through the multi-agent system
        
        Args:
            customer_query: The customer's question or issue
            
        Returns:
            Response from the appropriate agent
        """
        # Start with triage
        routing_decision = self.triage_agent.route_query(customer_query)
        
        # Route to appropriate specialist
        if "technical" in routing_decision["output"].lower():
            return self.technical_agent.handle_query(customer_query)
        elif "billing" in routing_decision["output"].lower():
            return self.billing_agent.handle_query(customer_query)
        else:
            return self.escalation_agent.handle_escalation(customer_query, routing_decision)


if __name__ == "__main__":
    # Example usage
    orchestrator = CustomerSupportOrchestrator()
    
    # Test queries
    queries = [
        "My account login isn't working",
        "I was charged twice this month",
        "I need to cancel my subscription immediately"
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        response = orchestrator.process_query(query)
        print(f"Response: {response}")
