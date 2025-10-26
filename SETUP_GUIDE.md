# Fetch.AI Integration Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# LangChain Configuration
GEMINI_API_KEY=your_gemini_api_key

# Fetch.AI Configuration
AGENT_NAME=langchain_support_agent
AGENT_SEED_PHRASE=generate_your_secure_seed_phrase
AGENT_PORT=8000
AGENT_ENDPOINT=http://localhost:8000/submit

# Test Client (optional)
TEST_CLIENT_SEED_PHRASE=generate_another_seed_phrase
WRAPPER_AGENT_ADDRESS=agent1q2f78szsejde4...
```

### 3. Generate Seed Phrases

Generate secure seed phrases using:

```bash
python -c "from uagents import Agent; print(Agent().address)"
```

Or use Fetch.AI's CLI:

```bash
uagent seed
```

## Running the Integration

### Option A: Run Wrapper Agent (Recommended for Production)

```bash
python agents/fetch_ai_wrapper.py
```

This will:
- Start the Fetch.AI agent
- Initialize the LangChain orchestrator
- Enable REST API endpoints
- Begin listening for messages

### Option B: Test via REST API

```bash
# Health check
curl http://localhost:8000/health

# Send query
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"customer_id": "TEST_001", "query": "My account login isn'\''t working"}'
```

### Option C: Run Test Client

```bash
python agents/fetch_ai_test_client.py
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│     External Client/Service         │
└──────────────┬──────────────────────┘
               │
        HTTP REST API
               │
┌──────────────▼──────────────────────┐
│   Fetch.AI Agent (fetch_ai_wrapper) │
├──────────────────────────────────────┤
│  - Receives messages                │
│  - Routes to LangChain              │
│  - Returns responses                │
└──────────────┬──────────────────────┘
               │
     Agent-to-Agent Messaging
               │
┌──────────────▼──────────────────────┐
│  LangChain Orchestrator             │
├──────────────────────────────────────┤
│  - Triage Agent                     │
│  - Technical Support Agent          │
│  - Billing Agent                    │
│  - Escalation Agent                 │
└──────────────────────────────────────┘
```

## Key Components

### 1. FetchAILangChainWrapper (`fetch_ai_wrapper.py`)

Main wrapper that:
- Creates Fetch.AI agent
- Initializes LangChain orchestrator
- Routes messages between systems
- Handles different query types

**Usage:**
```python
from agents.fetch_ai_wrapper import FetchAILangChainWrapper

wrapper = FetchAILangChainWrapper()
wrapper.run()
```

### 2. Message Models

All inter-agent communication uses typed models:

```python
# Query from client
CustomerQuery(
    customer_id="CUST_001",
    query="How do I reset my password?",
    timestamp="2025-01-15T10:30:00",
    priority="normal"
)

# Response from agent
AgentResponse(
    customer_id="CUST_001",
    response="Please follow these steps...",
    agent_type="technical_support_agent",
    timestamp="2025-01-15T10:30:05",
    status="success"
)
```

### 3. REST API Endpoints

#### GET /health
Returns agent health status
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "agent_address": "agent1q2f78szsejde4...",
  "agent_name": "langchain_support_agent",
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00"
}
```

#### POST /query
Process a customer query
```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d {
    "customer_id": "CUST_001",
    "query": "How do I reset my password?"
  }
```

Response:
```json
{
  "customer_id": "CUST_001",
  "response": "To reset your password, follow these steps...",
  "agent_type": "technical_support_agent",
  "timestamp": "2025-01-15T10:30:05",
  "status": "success"
}
```

## Testing

### 1. Health Check Test

```bash
curl http://localhost:8000/health
```

Expected: 200 OK with agent status

### 2. Basic Query Test

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "TEST_001",
    "query": "My account login isn'\''t working"
  }'
```

Expected: Response from technical support agent

### 3. Billing Query Test

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "TEST_002",
    "query": "I was charged twice this month"
  }'
```

Expected: Response from billing agent

### 4. Escalation Test

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "TEST_003",
    "query": "I need to cancel my subscription immediately"
  }'
```

Expected: Response from escalation agent

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "agents/fetch_ai_wrapper.py"]
```

### Environment Variables

Set these in your deployment platform:

```env
GEMINI_API_KEY=your_api_key
AGENT_SEED_PHRASE=your_seed_phrase
AGENT_PORT=8000
AGENT_ENDPOINT=your_public_endpoint
```

### Running with Docker

```bash
# Build image
docker build -t langchain-fetchai .

# Run container
docker run -d \
  -e GEMINI_API_KEY=your_key \
  -e AGENT_SEED_PHRASE=your_seed \
  -p 8000:8000 \
  langchain-fetchai
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langchain-fetchai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: langchain-fetchai
  template:
    metadata:
      labels:
        app: langchain-fetchai
    spec:
      containers:
      - name: agent
        image: langchain-fetchai:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: gemini-api-key
        - name: AGENT_SEED_PHRASE
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: agent-seed
```

## Monitoring & Logging

### View Logs

```bash
# If running locally
python agents/fetch_ai_wrapper.py 2>&1 | tee agent.log

# If running in Docker
docker logs -f <container_id>
```

### Key Log Messages

- Agent startup: "Agent 'langchain_support_agent' started"
- Received query: "Received query from {sender}: {query}"
- Sent response: "Sent response to {sender}"
- Errors: "Error processing query: {error}"

### Monitoring Checklist

- [ ] Agent health endpoint returns 200
- [ ] Responses within 5 seconds
- [ ] No error messages in logs
- [ ] LangChain API rate limits not exceeded
- [ ] Fetch.AI network connectivity working

## Troubleshooting

### Agent fails to start

**Error:** `ImportError: No module named 'uagents'`

**Solution:**
```bash
pip install uagents==0.10.0
```

### Cannot connect to Fetch.AI network

**Error:** `Connection refused` or timeout

**Solution:**
1. Check internet connection
2. Verify seed phrase is valid
3. Check if port is available: `lsof -i :8000`
4. Try different port: `AGENT_PORT=8001`

### LangChain API key issues

**Error:** `ApiKeyError` or `Unauthenticated`

**Solution:**
1. Verify GEMINI_API_KEY is set: `echo $GEMINI_API_KEY`
2. Check API key validity in Google Cloud Console
3. Ensure key has proper permissions

### REST API not responding

**Error:** `curl: (7) Failed to connect`

**Solution:**
1. Verify agent is running
2. Check port: `curl localhost:8000/health`
3. Check firewall: `sudo ufw allow 8000`
4. Try different endpoint

## Advanced Configuration

### Custom Message Handlers

Edit `fetch_ai_wrapper.py` to add custom handlers:

```python
@wrapper.agent.on_message(model=CustomModel)
async def handle_custom(ctx: Context, sender: str, msg: CustomModel):
    ctx.logger.info(f"Custom message: {msg}")
```

### Agent-to-Agent Communication

Enable communication between multiple agents:

```python
@wrapper.agent.on_message(model=EscalationRequest)
async def handle_escalation(ctx: Context, sender: str, msg: EscalationRequest):
    # Forward to specialist agent
    await ctx.send(SPECIALIST_AGENT_ADDRESS, msg)
```

### Scheduled Tasks

Add periodic background tasks:

```python
@wrapper.agent.on_interval(period=300.0)  # Every 5 minutes
async def background_task(ctx: Context):
    ctx.logger.info("Running background task")
```

## Performance Tuning

### Concurrency

Adjust LangChain executor settings in `main_agents.py`:

```python
self.executor = AgentExecutor(
    agent=self.agent,
    tools=self.tools,
    verbose=True,
    max_iterations=10,  # Adjust based on complexity
    handle_parsing_errors=True
)
```

### Caching

Implement response caching:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def process_query(query: str):
    return orchestrator.process_query(query)
```

### Rate Limiting

Add rate limiting to REST API:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@wrapper.agent.on_rest_post("/query", limiter.limit("30/minute"))
async def handle_rest_query(ctx: Context, req: QueryRequest):
    ...
```

## Integration with External Systems

### Webhook Integration

Forward responses to external system:

```python
import httpx

async def send_webhook(event_data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://your-service.com/webhook",
            json=event_data
        )
```

### Database Integration

Store conversations:

```python
@wrapper.agent.on_message(model=AgentResponse)
async def store_response(ctx: Context, sender: str, msg: AgentResponse):
    # Save to database
    await db.store_response(msg)
```

## Security Considerations

1. **Seed Phrases**: Keep seed phrases secret, use environment variables
2. **API Keys**: Never commit API keys to version control
3. **Network**: Use HTTPS in production
4. **Authentication**: Add API key authentication to REST endpoints
5. **Rate Limiting**: Implement rate limiting on public endpoints
6. **Input Validation**: Validate all incoming messages

## Support & Resources

- [Fetch.AI Documentation](https://docs.fetch.ai/)
- [uagents Framework](https://github.com/fetchai/uagents)
- [LangChain Documentation](https://python.langchain.com/)
- [Fetch.AI Playground Examples](https://github.com/harvest7777/fetchai-playground)

