# Fetch.AI Integration with LangChain Agents

## Overview

This document explains how to integrate Fetch.AI agents with your existing LangChain-based customer support multi-agent system. Fetch.AI provides decentralized agent infrastructure using the `uagents` framework, enabling autonomous agents to communicate and collaborate.

## Key Differences: LangChain vs Fetch.AI

### LangChain Agents
- **Framework**: OpenAI-compatible framework for building agent systems
- **Communication**: Synchronous, single-process orchestration
- **Deployment**: Typically runs on a single machine or server
- **Tools**: Tightly coupled with LLMs via function calling
- **State Management**: In-memory or external databases

### Fetch.AI Agents (uagents)
- **Framework**: Decentralized autonomous agent framework
- **Communication**: Asynchronous message-passing between agents
- **Deployment**: Distributed across the network (with mailbox support)
- **Tools**: Agent-to-agent communication via structured protocols
- **State Management**: Built-in with wallet/identity system

## Architecture for Integration

### Option 1: Fetch.AI Agents as API Wrappers (Recommended)
Wrap your LangChain agents with Fetch.AI agents that:
1. Receive messages from the Fetch.AI network
2. Invoke corresponding LangChain agents
3. Send responses back via Fetch.AI messaging

### Option 2: Direct Fetch.AI Implementation
Rewrite agents to use Fetch.AI's native async framework while preserving business logic.

## Integration Pattern

```
┌─────────────────────────────────────────────────────┐
│         External Users / Services                    │
└──────────────┬──────────────────────────────────────┘
               │
       Fetch.AI Network (uagents)
               │
┌──────────────▼──────────────────────────────────────┐
│     Fetch.AI Agent Wrapper                          │
│  (Receives messages, routes to LangChain)           │
└──────────────┬──────────────────────────────────────┘
               │
     LangChain Agent Orchestrator
               │
     ┌─────────┴─────────┐
     │                   │
┌────▼────┐      ┌──────▼──────┐
│ Triage  │      │ Technical   │
│ Agent   │      │ Agent       │
└─────────┘      └─────────────┘
```

## Setup Requirements

### 1. Install Dependencies

```bash
pip install uagents
pip install cosmpy  # For blockchain interactions
```

### 2. Environment Variables

Create a `.env` file with:

```env
# LangChain Configuration
GEMINI_API_KEY=your_gemini_api_key

# Fetch.AI Configuration
AGENT_SEED_PHRASE=your_secure_seed_phrase
BOB_SEED_PHRASE=another_agent_seed_phrase
ALICE_SEED_PHRASE=third_agent_seed_phrase
```

## Implementation Steps

### Step 1: Create Message Models

Define structured message types for Fetch.AI communication:

```python
from uagents import Model

class CustomerQuery(Model):
    customer_id: str
    query: str
    timestamp: str

class AgentResponse(Model):
    customer_id: str
    response: str
    agent_type: str
    timestamp: str
```

### Step 2: Create Fetch.AI Wrapper Agent

Wrap your LangChain orchestrator with a Fetch.AI agent:

```python
from uagents import Agent, Context
from datetime import datetime

agent = Agent(
    name="langchain_wrapper",
    seed=os.getenv("AGENT_SEED_PHRASE"),
    port=8000,
    mailbox=True  # Use mailbox for always-on capability
)

# Initialize LangChain orchestrator
orchestrator = CustomerSupportOrchestrator()

@agent.on_message(model=CustomerQuery)
async def handle_query(ctx: Context, sender: str, msg: CustomerQuery):
    # Invoke LangChain agent
    result = orchestrator.process_query(msg.query)
    
    # Send response back
    await ctx.send(
        sender,
        AgentResponse(
            customer_id=msg.customer_id,
            response=result["output"],
            agent_type=result.get("agent_name", "unknown"),
            timestamp=str(datetime.now())
        )
    )
```

### Step 3: Agent-to-Agent Communication

For multi-agent scenarios:

```python
from uagents_core.identity import Identity

# Define other agent addresses
TRIAGE_AGENT_ADDRESS = "agent1q2f78szsejde4..."
TECHNICAL_AGENT_ADDRESS = "agent1q3g89tztfjef5..."

@agent.on_message(model=EscalationRequest)
async def handle_escalation(ctx: Context, sender: str, msg: EscalationRequest):
    # Forward to specialized agent
    await ctx.send(
        TECHNICAL_AGENT_ADDRESS,
        msg
    )

@agent.on_message(model=EscalationResponse)
async def handle_escalation_response(ctx: Context, sender: str, msg: EscalationResponse):
    # Handle response
    ctx.logger.info(f"Escalation resolved: {msg}")
```

### Step 4: Running the Agent

```python
if __name__ == "__main__":
    agent.run()
```

## Advanced Features

### 1. REST API Integration

Expose your agents via REST:

```python
from uagents import Model

class QueryRequest(Model):
    query: str

@agent.on_rest_post("/query", QueryRequest, AgentResponse)
async def handle_rest_query(ctx: Context, req: QueryRequest) -> AgentResponse:
    result = orchestrator.process_query(req.query)
    return AgentResponse(
        customer_id="rest_user",
        response=result["output"],
        agent_type=result.get("agent_name", "unknown"),
        timestamp=str(datetime.now())
    )
```

### 2. Scheduled Tasks

Use intervals for periodic operations:

```python
@agent.on_interval(period=60.0)  # Every 60 seconds
async def periodic_health_check(ctx: Context):
    ctx.logger.info("Agent is running...")
```

### 3. Event Handling

Listen to lifecycle events:

```python
@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Agent started at {agent.address}")
    fund_agent_if_low(agent.wallet.address())

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("Agent shutting down...")
```

## Deployment Considerations

### Local Development
```bash
python fetch_ai_wrapper.py
```

### Production (Mailbox Mode)
- Enable `mailbox=True` in agent configuration
- Agent receives messages from Fetch.AI's hosted mailbox service
- No need for port forwarding or public IP
- Automatic message persistence

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "fetch_ai_wrapper.py"]
```

## Testing

### Unit Testing

```python
import pytest

@pytest.mark.asyncio
async def test_customer_query():
    query = CustomerQuery(
        customer_id="test_123",
        query="My account isn't working",
        timestamp=str(datetime.now())
    )
    
    # Simulate agent handling
    result = await handle_query(ctx, "test_sender", query)
    assert result.agent_type in ["technical_support_agent", "billing_agent"]
```

### Integration Testing

Use Fetch.AI's test utilities to simulate message passing:

```python
# Send test message from one agent to another
await ctx.send(target_agent_address, test_message)
```

## Monitoring & Logging

Fetch.AI agents have built-in logging:

```python
# Available via ctx.logger
ctx.logger.info("Information message")
ctx.logger.warning("Warning message")
ctx.logger.error("Error message")
```

## Migration Checklist

- [ ] Install Fetch.AI dependencies
- [ ] Create message models for communication
- [ ] Wrap LangChain agents with Fetch.AI wrapper
- [ ] Configure agent seed phrases and environment
- [ ] Test message passing between agents
- [ ] Implement REST endpoints if needed
- [ ] Set up logging and monitoring
- [ ] Deploy with mailbox enabled
- [ ] Verify inter-agent communication
- [ ] Load test and optimize

## Additional Resources

- [Fetch.AI Documentation](https://docs.fetch.ai/)
- [uagents Python Framework](https://github.com/fetchai/uagents)
- [Fetch.AI Playground Examples](https://github.com/harvest7777/fetchai-playground)
- [AgentVerse](https://agentverse.ai/) - Agent marketplace and registry

## Example Use Cases

1. **Multi-tenant Support**: Each customer organization has dedicated agents
2. **Microservices**: Agents communicate with microservices via REST hooks
3. **Hybrid Approach**: LangChain for reasoning, Fetch.AI for coordination
4. **Real-time Updates**: Push-based messaging instead of polling
5. **Decentralized Services**: Multiple independent service providers

