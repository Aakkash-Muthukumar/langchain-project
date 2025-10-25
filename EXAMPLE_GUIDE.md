# Customer Support Multi-Agent System

This is a complete example of a LangChain-based multi-agent system for customer support automation.

## Architecture

```
Customer Query
     ↓
Triage Agent (routes query)
     ↓
  ┌──┴──┬─────────┐
  ↓     ↓         ↓
Technical  Billing  Escalation
 Agent     Agent     Agent
```

## Agents

### 1. Triage Agent
- **Purpose:** Routes customer queries to appropriate specialists
- **Type:** Zero-shot ReAct
- **Tools:** query_customer_history, search_knowledge_base
- **Relationships:** Hands off to all other agents

### 2. Technical Support Agent
- **Purpose:** Diagnoses and resolves technical issues
- **Type:** Conversational ReAct
- **Tools:** run_diagnostics, check_system_status, search_knowledge_base
- **Relationships:** Can escalate to Escalation Agent

### 3. Billing Agent
- **Purpose:** Handles billing and payment queries
- **Type:** Zero-shot ReAct
- **Tools:** query_billing_history, process_refund, update_subscription
- **Relationships:** Receives queries from Triage Agent

### 4. Escalation Agent
- **Purpose:** Manages complex cases requiring human intervention
- **Type:** Zero-shot ReAct
- **Tools:** create_ticket, assign_to_human, send_email, send_slack_notification
- **Relationships:** Receives escalations from all agents

## Tools

### Database Tools
- `query_customer_history()` - Get customer interaction history
- `get_customer_info()` - Get customer account details
- `update_customer_record()` - Update customer data

### Knowledge Base Tools
- `search_knowledge_base()` - Search documentation
- `get_article_content()` - Get full article content

### Technical Tools
- `run_diagnostics()` - Run system diagnostics
- `check_system_status()` - Check service health
- `restart_service()` - Restart a service
- `check_logs()` - Retrieve service logs

### Billing Tools
- `query_billing_history()` - Get payment history
- `process_refund()` - Process customer refunds
- `update_subscription()` - Modify subscription
- `cancel_subscription()` - Cancel subscription
- `apply_discount()` - Apply discount codes

### Ticket Tools
- `create_ticket()` - Create support ticket
- `assign_to_human()` - Assign to human agent
- `update_ticket()` - Update ticket info
- `close_ticket()` - Close resolved ticket

### Notification Tools
- `send_email()` - Send email notification
- `send_slack_notification()` - Send Slack message
- `send_sms()` - Send SMS notification

## Usage

```python
from agents.main_agents import CustomerSupportOrchestrator

# Initialize the system
orchestrator = CustomerSupportOrchestrator()

# Process a customer query
response = orchestrator.process_query("My login isn't working")
print(response)
```

## Testing with AI Agent Testing Framework

1. Upload this folder to GitHub (or use the local path)
2. Submit the repository URL to the testing framework
3. The framework will:
   - Identify all 4 agents
   - Map relationships between agents
   - Extract all 20+ tools
   - Visualize the architecture
   - Generate 10 comprehensive test cases
   - Test hyperparameters, security, tool calling, etc.

## Example Queries to Test

- "My account login isn't working" → Routes to Technical Agent
- "I was charged twice this month" → Routes to Billing Agent
- "I need to cancel my subscription immediately" → Routes to Billing Agent
- "This is urgent and I need to speak to a manager" → Routes to Escalation Agent
- "Reset my password" → Technical Agent → Uses diagnostics

## Expected Test Results

The testing framework should identify:
- **4 agents** with different types and configurations
- **20+ tools** across 6 categories
- **Multiple relationships:**
  - Triage → Technical (handoff)
  - Triage → Billing (handoff)
  - Triage → Escalation (handoff)
  - Technical → Escalation (escalation)
- **Various configurations:**
  - Different temperature settings (0.7)
  - Max tokens (1024)
  - Different max_iterations per agent
  - Tool availability per agent

## Key Features for Testing

1. **Agent Collaboration:** Agents work together sequentially
2. **Smart Routing:** Triage agent makes routing decisions
3. **Escalation Path:** Complex cases escalate properly
4. **Tool Specialization:** Each agent has specialized tools
5. **Error Handling:** Built-in error handling and retries

This example demonstrates a real-world multi-agent system perfect for testing!
