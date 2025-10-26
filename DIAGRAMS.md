# Fetch.AI + LangChain Integration - Visual Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Clients & Services                  │
│    (Web Apps, Mobile, Webhooks, 3rd Party Integrations)        │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    REST API        Fetch.AI          Other Protocols
   (HTTP/HTTPS)    Messaging         (WebSocket, etc)
        │                │                │
        └────────────────┼────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              FETCH.AI AGENT (fetch_ai_wrapper.py)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Message Handlers:                                       │  │
│  │  - CustomerQuery Handler                                │  │
│  │  - EscalationRequest Handler                            │  │
│  │  - HealthCheck Handler                                  │  │
│  │  - REST Endpoints                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  LANGCHAIN ORCHESTRATOR (main_agents.py)               │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │  CustomerSupportOrchestrator                     │   │  │
│  │  │  - Coordinates all agents                        │   │  │
│  │  │  - Routes queries to specialists                 │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                          │                               │  │
│  │  ┌──────┬──────────┬─────┴─────┬──────────┐             │  │
│  │  │      │          │           │          │             │  │
│  │  ▼      ▼          ▼           ▼          ▼             │  │
│  │ Triage  Technical Billing   Escalation  Tools/Knowledge │  │
│  │ Agent   Agent      Agent     Agent      Base Access     │  │
│  │  │      │          │           │          │             │  │
│  │  └──────┴──────────┴───────────┴──────────┘             │  │
│  │                    │                                     │  │
│  │  ┌────────────────▼──────────────────┐                 │  │
│  │  │   LLM (Google Gemini)             │                 │  │
│  │  │   - Reasoning & Decision Making   │                 │  │
│  │  │   - Response Generation           │                 │  │
│  │  └───────────────────────────────────┘                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   External Tools  Databases        Notification Systems
   & Services      (Customer DB)    (Email, Slack, etc)
```

---

## Message Flow Sequence

```
┌────────┐                                              ┌──────────┐
│ Client │                                              │ External │
│        │                                              │ Systems  │
└────┬───┘                                              └────┬─────┘
     │                                                       │
     │  1. Send Query                                        │
     │  (REST POST /query)                                   │
     │────────────────────────────────────────────────┐     │
     │                                                 │     │
     │  ┌──────────────────────────────────────────┐  │     │
     │  │ Fetch.AI Wrapper Agent                  │  │     │
     │  │ - Receives CustomerQuery message       │  │     │
     │  │ - Validates input                       │  │     │
     │  │ - Logs transaction                      │  │     │
     │  └────────────┬───────────────────────────┘  │     │
     │               │                               │     │
     │  2. Route to  │ 3. Process Query              │     │
     │  LangChain    │    (Triage/Route)             │     │
     │  ◄─────────────────────────────────────────┐  │     │
     │               │                           │   │     │
     │  ┌────────────▼──────────────────────────┐│  │     │
     │  │ Triage Agent                         ││  │     │
     │  │ ┌───────────────────────────────────┐││  │     │
     │  │ │ 1. Analyze query content        │││  │     │
     │  │ │ 2. Search knowledge base        │││  │     │
     │  │ │ 3. Query customer history      │││  │     │
     │  │ │ 4. Determine routing           │││  │     │
     │  │ └────┬──────────────────┬────────┘││  │     │
     │  └──────┼──────────────────┼────────┘│  │     │
     │         │                  │          │  │     │
     │  ┌──────┴─────┐      ┌──────┴──────┐  │     │
     │  │             │      │             │  │     │
     │  ▼             ▼      ▼             ▼  │     │
     │ Tech Support Billing  Escalation  Other│     │
     │ Agent        Agent    Agent       Agent│     │
     │  │             │      │             │  │     │
     │  │ 4. Execute  │      │             │  │     │
     │  │    with LLM │      │             │  │     │
     │  │             │      │             │  │     │
     │  └─────┬───────┴──────┴─────────────┘  │     │
     │        │                               │     │
     │  ┌─────▼──────────────────────────────┐│     │
     │  │ Format Response                   ││     │
     │  │ - Extract answer from LLM        ││     │
     │  │ - Add metadata                    ││     │
     │  │ - Validate format                 ││     │
     │  └──────────────┬─────────────────────┘│     │
     │                 │                      │     │
     │  5. Send Response                       │     │
     │  (AgentResponse)                        │     │
     │◄────────────────────────────────────────┘     │
     │                                               │
     │  6. Client receives response                  │
     │◄──────────────────────────────────────────────┤
     │                                               │
     │  7. (Optional) Webhook to external system    │
     ├──────────────────────────────────────────────▶
     │
   [End]
```

---

## Query Routing Decision Tree

```
                    ┌─────────────────┐
                    │ Query Received  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Extract Keywords│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    "login"/"password"   "charge"/"payment"  "cancel"/"urgent"
    "technical"         "billing"            "escalate"
    "bug"/"error"       "subscription"       "manager"
        │                    │                    │
        ▼                    ▼                    ▼
    ┌─────────────┐      ┌──────────┐      ┌──────────────┐
    │  Technical  │      │ Billing  │      │ Escalation   │
    │   Support   │      │  Agent   │      │    Agent     │
    │   Agent     │      │          │      │              │
    └─────────────┘      └──────────┘      └──────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
    Run Diagnostics  Process Payment       Create Ticket
    Check Status     Update Subscription   Notify Human
    Search KB        Query Billing          Escalate Case
```

---

## Message Type Relationships

```
┌───────────────────────────────────────────────────────┐
│            BASE MODEL (uagents.Model)                 │
│  - All messages inherit from this                    │
│  - Automatic serialization/validation               │
└────────────────┬────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────────┐
    │            │            │              │
    ▼            ▼            ▼              ▼
┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────────────┐
│Customer │ │Escalat-│ │Escalat- │ │ Health       │
│ Query   │ │ion     │ │ion      │ │ Check        │
│         │ │Request │ │Response │ │              │
├─────────┤ ├────────┤ ├─────────┤ ├──────────────┤
│customer_id
│query    │ │customer_id
│priority │ │reason  │ │ticket_id
│timestamp│ │...     │ │assigned  │ │agent_address │
└─────────┘ └────────┘ └─────────┘ │status        │
    │            │            │     │timestamp     │
    │            │            │     └──────────────┘
    ▼            ▼            ▼
 Wrapper     Wrapper      Wrapper
 Handler     Handler      Handler
```

---

## State Management Flow

```
┌─────────────────────────────────────────┐
│   Agent Startup                         │
│  - Initialize Fetch.AI agent           │
│  - Load LangChain orchestrator         │
│  - Fund agent wallet if needed         │
│  - Register message handlers           │
└────────────────┬────────────────────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │  Waiting for Messages  │
    │  - Listen to mailbox   │
    │  - Wait for REST calls │
    │  - Check intervals     │
    └────────────┬───────────┘
                 │
    ┌────────────▼──────────────┐
    │  Message Received         │
    │  - Validate message type  │
    │  - Extract data           │
    │  - Create context         │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │  Route & Process          │
    │  - Call LangChain agent   │
    │  - Await response         │
    │  - Handle errors          │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │  Send Response            │
    │  - Format AgentResponse   │
    │  - Send back to sender    │
    │  - Log transaction        │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │  Back to Listening        │
    │  (Loop continues)         │
    └───────────────────────────┘
```

---

## Deployment Architecture

### Development
```
Your Computer
├── Python Virtual Environment
├── Fetch.AI Agent (port 8000)
├── LangChain Libraries
└── Google Gemini API (online)
```

### Docker (Local)
```
Docker Host
├── Container 1: Agent (8000)
├── Container 2: Test Client (8001)
├── Shared Network: agent-network
└── Volumes: logs
```

### Production (Cloud)
```
Cloud Provider (AWS/GCP/Azure)
├── Kubernetes Cluster
│   ├── Pod: Fetch.AI Agent (replicas=3)
│   ├── Service: LoadBalancer (port 8000)
│   ├── ConfigMap: Configuration
│   ├── Secret: API Keys & Seed Phrases
│   └── PVC: Persistent Logs
├── External
│   ├── Google Gemini API
│   ├── Database
│   └── Monitoring (Prometheus/Grafana)
└── Network
    ├── Ingress: HTTPS
    ├── Internal: Agent Communication
    └── Fetch.AI: External Network
```

---

## Tool Integration Architecture

```
         ┌──────────────────────┐
         │   LangChain Agent    │
         │   (Any Agent Type)   │
         └──────────┬───────────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
  ┌────────┐  ┌──────────┐  ┌──────────┐
  │  Tool  │  │  Tool    │  │  Tool    │
  │  1     │  │  2       │  │  N       │
  ├────────┤  ├──────────┤  ├──────────┤
  │query_  │  │process_  │  │send_     │
  │customer│  │refund    │  │email     │
  │_history│  │          │  │          │
  └───┬────┘  └────┬─────┘  └────┬─────┘
      │            │             │
      ▼            ▼             ▼
  ┌────────────────────────────────────┐
  │      External Integrations         │
  ├────────────────────────────────────┤
  │ • Database (Customer History)      │
  │ • Payment Gateway                  │
  │ • Email Service                    │
  │ • Slack API                        │
  │ • Knowledge Base                   │
  │ • Ticketing System                 │
  └────────────────────────────────────┘
```

---

## Communication Protocols

```
┌─────────────────────────────────────────┐
│         Communication Methods           │
└─────────────────────────────────────────┘
         │              │             │
         ▼              ▼             ▼
    REST API      Agent Messaging  Internal
    (HTTP/S)      (Fetch.AI)        (Python)
         │              │             │
    ┌────┴───┐      ┌────┴────┐  ┌────┴────┐
    │ POST   │      │ Message │  │ Function│
    │/query  │      │ Model   │  │ Calls   │
    │        │      │ Passing │  │         │
    │ GET    │      │ via     │  │ Direct  │
    │/health │      │ Mailbox │  │ Return  │
    └────────┘      └─────────┘  └─────────┘
```

---

## Error Handling Flow

```
┌──────────────────────┐
│  Exception Occurs    │
└──────────┬───────────┘
           │
    ┌──────▼──────┐
    │  Catch &    │
    │  Log Error  │
    └──────┬──────┘
           │
    ┌──────▼─────────────┐
    │  Error Type?       │
    └──────┬─────┬──────┬┘
           │     │      │
      ┌────▼┐┌───▼──┐┌──▼───┐
      │LLM  ││Network││Input  │
      │Error││Error  ││Error  │
      └────┬┘└───┬──┘└──┬───┘
           │     │      │
    ┌──────▼─────▼──────▼──────┐
    │  Format Error Message     │
    │  - Human readable         │
    │  - Include context        │
    │  - Log for debugging      │
    └──────────┬────────────────┘
               │
    ┌──────────▼──────────┐
    │  Send Error         │
    │  AgentResponse      │
    │  status: "error"    │
    └─────────────────────┘
```

---

These diagrams provide a comprehensive visual understanding of how the Fetch.AI and LangChain integration works together!
