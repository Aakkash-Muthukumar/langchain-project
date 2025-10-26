# Fetch.AI Integration - Quick Reference

## 📋 Files Created

| File | Purpose |
|------|---------|
| `agents/fetch_ai_wrapper.py` | Main Fetch.AI wrapper around LangChain |
| `agents/fetch_ai_test_client.py` | Test client for the agent |
| `FETCHAI_INTEGRATION.md` | Detailed integration architecture |
| `SETUP_GUIDE.md` | Installation & deployment guide |
| `INTEGRATION_SUMMARY.md` | Overview & next steps |
| `Dockerfile` | Docker image for containerization |
| `docker-compose.yml` | Local development stack |

---

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
# Generate seed phrase
python -c "from uagents import Agent; a = Agent(); print(f'Address: {a.address}')"

# Update .env
echo "GEMINI_API_KEY=your_key" >> .env
echo "AGENT_SEED_PHRASE=your_seed" >> .env
```

### 3. Run
```bash
python agents/fetch_ai_wrapper.py
```

### 4. Test
```bash
# Health check
curl http://localhost:8000/health

# Send query
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"customer_id":"USER_1","query":"help with login"}'
```

---

## 🏗️ Architecture

```
Client → REST API / Fetch.AI Network → Wrapper Agent
              ↓
         LangChain Orchestrator
              ↓
    ┌────────┬────────┬─────────┐
    ↓        ↓        ↓         ↓
  Triage  Technical Billing  Escalation
```

---

## 📨 Message Types

### CustomerQuery
```python
{
  "customer_id": "CUST_001",
  "query": "My account isn't working",
  "timestamp": "2025-01-15T10:30:00",
  "priority": "normal"
}
```

### AgentResponse
```python
{
  "customer_id": "CUST_001",
  "response": "To fix this...",
  "agent_type": "technical_support_agent",
  "timestamp": "2025-01-15T10:30:05",
  "status": "success"
}
```

---

## 🔌 REST API Endpoints

### GET /health
Check agent status
```bash
curl http://localhost:8000/health
```

### POST /query
Process a customer query
```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "CUST_001",
    "query": "help with billing"
  }'
```

---

## 🐳 Docker

### Build & Run
```bash
docker-compose up
```

### With Logs
```bash
docker-compose up -d
docker logs -f langchain-fetchai-agent
```

### Stop
```bash
docker-compose down
```

---

## 🧪 Test Scenarios

### Technical Support
```bash
curl -X POST http://localhost:8000/query \
  -d '{"customer_id":"T1","query":"My account login isn'\''t working"}'
```

### Billing
```bash
curl -X POST http://localhost:8000/query \
  -d '{"customer_id":"B1","query":"I was charged twice"}'
```

### Escalation
```bash
curl -X POST http://localhost:8000/query \
  -d '{"customer_id":"E1","query":"Cancel my subscription immediately"}'
```

---

## 🔑 Key Concepts

| Concept | Explanation |
|---------|-------------|
| **Wrapper** | Fetch.AI agent that wraps LangChain orchestrator |
| **Mailbox Mode** | Always-on message receiving via Fetch.AI |
| **Seed Phrase** | Secret key for agent identity |
| **Agent Address** | Public identity on Fetch.AI network |
| **Context** | Runtime object for logging & communication |
| **Protocol** | Message handling specification |

---

## 📊 Routing Logic

```
Query Received
    ↓
Contains "technical" → Technical Support Agent
Contains "billing"   → Billing Agent
Contains "payment"   → Billing Agent
Contains "cancel"    → Escalation Agent
Contains "urgent"    → Escalation Agent
Otherwise           → Triage Agent (default)
```

---

## 🛠️ Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_key
AGENT_SEED_PHRASE=your_seed_phrase

# Optional (defaults provided)
AGENT_PORT=8000
AGENT_NAME=langchain_support_agent
AGENT_ENDPOINT=http://localhost:8000/submit
```

---

## 📝 File Structure

```
langchain-project/
├── agents/
│   ├── main_agents.py           # Existing LangChain agents
│   ├── fetch_ai_wrapper.py      # NEW: Fetch.AI wrapper
│   ├── fetch_ai_test_client.py  # NEW: Test client
│   └── *.py                     # Other agent files
├── tools/
│   └── *.py                     # Tool implementations
├── FETCHAI_INTEGRATION.md       # NEW: Integration guide
├── SETUP_GUIDE.md               # NEW: Setup guide
├── INTEGRATION_SUMMARY.md       # NEW: Overview
├── Dockerfile                   # NEW: Docker config
├── docker-compose.yml           # NEW: Docker compose
├── requirements.txt             # UPDATED: Added Fetch.AI deps
├── .env                         # Configuration (create from example)
└── README.md                    # Original docs
```

---

## 🐛 Troubleshooting

### Error: `ImportError: No module named 'uagents'`
```bash
pip install uagents==0.10.0 cosmpy==0.9.0
```

### Error: `Connection refused`
```bash
# Check if port 8000 is available
lsof -i :8000
# Or use different port
AGENT_PORT=8001 python agents/fetch_ai_wrapper.py
```

### Error: `API key invalid`
```bash
# Verify environment variable
echo $GEMINI_API_KEY
# Re-add to .env if missing
```

### Agent not responding
```bash
# Check agent is running
ps aux | grep fetch_ai_wrapper.py

# Check logs
docker logs -f langchain-fetchai-agent  # if using Docker
```

---

## 📚 Documentation

1. **FETCHAI_INTEGRATION.md** - Deep dive on architecture
2. **SETUP_GUIDE.md** - Installation & deployment
3. **INTEGRATION_SUMMARY.md** - Overview & benefits
4. **This file** - Quick reference
5. **Code comments** - In-file documentation

---

## ✅ Implementation Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Generate seed phrase
- [ ] Create .env file with credentials
- [ ] Run locally: `python agents/fetch_ai_wrapper.py`
- [ ] Test REST endpoints
- [ ] Review logs for errors
- [ ] Test with provided curl examples
- [ ] Review SETUP_GUIDE.md for production deployment
- [ ] Set up Docker if containerizing
- [ ] Configure monitoring/logging
- [ ] Deploy to production

---

## 🎯 What's New

### vs Original LangChain
- ✅ Decentralized agent communication
- ✅ Always-on message receiving (mailbox)
- ✅ REST API for external clients
- ✅ Agent discovery & registration
- ✅ Production-ready packaging
- ✅ Docker containerization

### vs Plain Fetch.AI
- ✅ Powerful LLM reasoning (LangChain)
- ✅ Multi-agent orchestration
- ✅ Tool integration framework
- ✅ Proven enterprise patterns

---

## 🚢 Deployment Options

### Development
```bash
python agents/fetch_ai_wrapper.py
```

### Docker (Recommended)
```bash
docker-compose up
```

### Production
```bash
# With environment variables set
docker run -e GEMINI_API_KEY=xxx -e AGENT_SEED_PHRASE=xxx langchain-fetchai
```

### Kubernetes
See SETUP_GUIDE.md for Kubernetes YAML

---

## 💡 Tips & Tricks

1. **Faster Testing**: Use REST API, don't need full Fetch.AI network
2. **Debugging**: Set LOG_LEVEL=DEBUG in .env
3. **Agent Identity**: Address is deterministic from seed phrase
4. **Message Size**: Keep queries < 10KB for best performance
5. **Caching**: Implement LRU cache for repeated queries
6. **Rate Limiting**: Add slowapi for production endpoints

---

## 📞 Support Resources

- [Fetch.AI Docs](https://docs.fetch.ai/)
- [uagents GitHub](https://github.com/fetchai/uagents)
- [LangChain Docs](https://python.langchain.com/)
- [Fetch.AI Playground](https://github.com/harvest7777/fetchai-playground)

---

**Version:** 1.0  
**Date:** 2025-01-15  
**Status:** Production Ready

For detailed information, refer to the comprehensive documentation files.
