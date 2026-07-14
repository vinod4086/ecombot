# eComBot - Comprehensive E-Commerce Support Agent

![eComBot](https://img.shields.io/badge/version-5.0.0-blue)
![Status](https://img.shields.io/badge/status-production--ready-green)

An advanced e-commerce support agent implementing the complete Google ADK journey from Day 01 through Day 13. Features multi-agent orchestration, Chainlit UI, guardrails, observability, evaluation scaffolding, and voice loop integration.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Day-by-Day Implementation](#day-by-day-implementation)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)

---

## 🎯 Overview

eComBot is a production-ready e-commerce support agent that demonstrates:

- **Day 01-02**: Agent initialization with prompt engineering
- **Day 03**: Tool calling with in-memory session state
- **Day 04**: Redis and PostgreSQL integration
- **Day 05-06**: RAG-based knowledge grounding with ChromaDB
- **Day 07**: LiteLLM gateway with intelligent routing
- **Day 08**: FastMCP external service integrations
- **Day 09**: Multi-agent orchestration (Orchestrator + Support + Sales)
- **Day 10**: Chainlit generative UI with cards, steps, and actions
- **Day 11**: Voice loop scaffold (STT -> Agents -> TTS)
- **Day 12**: ReAct-style reasoning and observability hooks
- **Day 13**: Guardrails and production-readiness checklist

### Key Features

✅ Multi-turn conversation with context awareness  
✅ Order and product lookup tools  
✅ Persistent session management  
✅ Knowledge-grounded answers with hallucination guards  
✅ Intelligent LLM routing  
✅ External service integrations via FastMCP  
✅ Full conversation history  
✅ Production-ready error handling  

---

## 🏗️ Architecture

```
┌─────────────────┐
│    eComBot      │ (Support Agent)
└────────┬────────┘
         │
    ┌────┴──────────┬──────────────┬──────────────┐
    │               │              │              │
┌───▼───┐     ┌────▼────┐    ┌───▼────┐    ┌──▼────┐
│Tools  │     │Sessions │    │History │    │ RAG   │
│       │     │ (Redis) │    │(PgSQL) │    │(Chroma)
└───────┘     └─────────┘    └────────┘    └──┬─────┘
                   │              │            │
            ┌──────┴──────────────┴────────────┘
            │
    ┌───────▼────────┐
    │ LiteLLM Gateway│ (Day 07)
    └────────────────┘
            │
    ┌───────▼────────┐
    │  LLM Provider  │
    │ (OpenRouter)   │
    └────────────────┘
            │
    ┌───────▼──────────┐
    │ FastMCP Services │ (Day 08)
    │ (Orders, Inv)    │
    └──────────────────┘
```

---

## 📁 Project Structure

```
ecombot/
├── src/
│   ├── agents/
│   │   ├── support_agent.py          # Support specialist agent
│   │   ├── sales_agent.py            # Sales specialist with reasoning loop
│   │   ├── orchestrator.py           # Primary entrypoint router
│   │   ├── support_instructions_v1.txt # Professional variant
│   │   ├── support_instructions_v2.txt # Friendly variant
│   │   └── support_instructions_v3.txt # Technical variant
│   ├── tools/
│   │   ├── order_tools.py            # Order operations (Day 03-04)
│   │   └── product_tools.py          # Product lookup (Day 04)
│   ├── services/
│   │   ├── db.py                     # PostgreSQL service (Day 04)
│   │   ├── session_service.py        # Redis sessions (Day 04)
│   │   ├── history_service.py        # Conversation history (Day 04)
│   │   └── mcp_server.py             # FastMCP server (Day 08)
│   ├── rag/
│   │   ├── embed_catalog.py          # ChromaDB embedding (Day 05-06)
│   │   └── retriever.py              # RAG retrieval (Day 05-06)
│   ├── guards/
│   │   ├── input_guard.py            # Prompt-injection checks
│   │   └── output_guard.py           # PII/off-topic output controls
│   ├── ui/
│   │   └── chainlit_app.py           # Chainlit UI entrypoint
│   ├── voice/
│   │   └── voice_loop.py             # Voice interaction loop scaffold
│   └── config/
│       └── settings.py               # Configuration management
├── data/
│   ├── products.json                 # Product knowledge base
│   └── faq.json                      # FAQ knowledge base
├── scripts/
│   ├── setup.py                      # Setup script
│   ├── run.py                        # Main runner
│   ├── test_agent.py                 # Agent tests
│   └── init_db.sql                   # Database initialization
├── tests/
│   ├── test_support_agent_manual_day03.md
│   ├── test_support_agent_manual_day04.md
│   ├── test_rag_manual_day05_06.md
│   └── test_litellm_day07.md
├── docker-compose.yml                # Service orchestration
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git
- OpenRouter API key

### Step 1: Clone and Setup

```bash
cd ecombot
cp .env.example .env
# Edit .env with your API keys
pip install -r requirements.txt
```

### Step 2: Start Infrastructure

```bash
docker-compose up -d
# Verify services are healthy
docker-compose ps
```

### Step 3: Initialize Database

```bash
# Database auto-initializes, but can manually verify:
docker-compose exec postgres psql -U ecombot_user -d ecombot_db -c "\dt"
```

### Step 4: Setup RAG

```bash
python -m src.rag.embed_catalog
```

### Step 5: Run Agent

**Interactive Mode:**
```bash
python scripts/run.py --mode interactive
```

**Batch Mode:**
```bash
python scripts/run.py --mode batch --queries "Hello" "Where is my order?"
```

**Chainlit UI (Day 10):**
```bash
chainlit run src/ui/chainlit_app.py
```

**Voice Loop Demo (Day 11):**
```bash
python -m src.voice.voice_loop
```

---

## 📅 Day-by-Day Implementation

### Day 01-02: Agent Initialization & Prompt Engineering

**Objectives:**
- Create basic agent structure
- Implement prompt variants
- Test instruction effectiveness

**Key Files:**
- `src/agents/support_agent.py` (core agent)
- `src/agents/support_instructions_v*.txt` (variants)

**Test:**
```bash
python scripts/test_agent.py
```

### Day 03: Tool Calling & Session State

**Objectives:**
- Implement order status tools with `@tool` decorator
- Add in-memory session state management
- Support multi-turn conversations

**Key Features:**
- `get_order_status(order_id)` tool
- `cancel_order(order_id)` tool
- Session state: `customer_name`, `last_order_id`

**Test File:**
- `tests/test_support_agent_manual_day03.md`

### Day 04: PostgreSQL & Redis Integration

**Objectives:**
- Persistent database for orders/products
- Redis-backed session continuity
- Durable conversation history

**Services:**
- PostgreSQL: Orders, products, session history
- Redis: Short-lived session state
- Automatic backup and recovery

**Test File:**
- `tests/test_support_agent_manual_day04.md`

### Day 05-06: RAG with ChromaDB

**Objectives:**
- Index product catalog and FAQs
- Semantic retrieval for grounded answers
- Hallucination prevention

**Features:**
- ChromaDB vector store
- Metadata-aware chunking
- Confidence scoring
- Graceful fallback

**Test File:**
- `tests/test_rag_manual_day05_06.md`

### Day 07: LiteLLM Gateway & Routing

**Objectives:**
- Route through LiteLLM proxy
- Intelligent model selection
- Fallback behavior

**Configuration:**
```python
# Fast FAQ route
route_hint = "fast-faq"

# Deep support route
route_hint = "deep-support"
```

### Day 08: FastMCP External Integrations

**Objectives:**
- Connect to external order backend
- Connect to inventory system
- Handle service failures gracefully

**MCP Server Endpoints:**
- `GET /health` - Health check
- `POST /tools/get_order_status` - Order lookup
- `POST /tools/cancel_order` - Order cancellation
- `POST /tools/check_stock` - Inventory check
- `GET /tools` - Tool listing

**Start MCP Server:**
```bash
python -m src.services.mcp_server
```

### Day 09: Multi-Agent Orchestration

- Added `OrchestratorAgent` as main entrypoint for routing.
- Added dedicated `SalesAgent` with recommendation responsibilities.
- Added mixed intent planner-executor flow.

### Day 10: Chainlit Generative UI

- Added `src/ui/chainlit_app.py` with:
        - Structured cards for order and product outputs
        - Visible route step rendering
        - Action buttons for common follow-up flows

### Day 11: Voice Interface Scaffold

- Added `src/voice/voice_loop.py`:
        - Turn-based voice interaction loop
        - Stage latency logging (capture/STT/orchestration/TTS)
        - Critical order ID confirmation flow

### Day 12: Reasoning + Observability

- Sales agent now records reasoning steps across recommendation flow.
- Added `src/services/observability.py` for trace IDs and latency logs.
- Added PromptFoo scaffold: `promptfooconfig.json`.

### Day 13: Guardrails + Production Readiness

- Added input and output guardrails under `src/guards/`.
- Added destructive action confirmation in support cancellation flow.
- Added `PRODUCTION_CHECKLIST.md` for handoff readiness.

---

## 🧪 Testing

### Automated Tests

```bash
# Run all agent tests
python scripts/test_agent.py

# Run specific test scenario
python -c "from scripts.test_agent import test_session_state; test_session_state()"
```

### Manual Testing

Each day includes manual test documentation:

| Day | Test File | Coverage |
|-----|-----------|----------|
| 03 | `test_support_agent_manual_day03.md` | Tool calling, session state |
| 04 | `test_support_agent_manual_day04.md` | DB persistence, Redis |
| 05-06 | `test_rag_manual_day05_06.md` | Knowledge grounding |

### Test Interactive Mode

```bash
python scripts/run.py --mode interactive

# Example conversation:
# > Hi, my name is Priya
# > Where is my order ORD-001?
# > What about that same order?
# > exit
```

---

## 🐳 Docker Deployment

### Start All Services

```bash
docker-compose up -d
```

### Check Service Status

```bash
docker-compose ps
docker-compose logs postgres
docker-compose logs redis
docker-compose logs chroma
```

### Stop Services

```bash
docker-compose down

# With volume cleanup
docker-compose down -v
```

### Access Services

- PostgreSQL: `localhost:5432` (user: `ecombot_user`)
- Redis: `localhost:6379` (password: `redis_password`)
- ChromaDB: `http://localhost:8000`
- MCP Server: `http://localhost:8001`

---

## 📊 Configuration

### Environment Variables (.env)

```bash
# API Keys
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecombot_db
POSTGRES_USER=ecombot_user
POSTGRES_PASSWORD=ecombot_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# LLM
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LITELLM_PROXY_URL=http://localhost:8000

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

---

## 📡 API Documentation

### Support Agent API

```python
from src.agents.support_agent import create_support_agent

# Create agent with default instruction
agent = create_support_agent()

# Process user input
response = agent.process_user_input("Where is my order ORD-001?")

# Access session state
customer_name = agent.get_session_state("customer_name")

# Update session state
agent.update_session_state("last_product_id", "PRD-101")
```

### Order Tools API

```python
from src.tools.order_tools import get_order_status, cancel_order

# Get order status
result = get_order_status.invoke({"order_id": "ORD-001"})
# Returns: {order_id, status, eta, carrier, items, total}

# Cancel order
result = cancel_order.invoke({"order_id": "ORD-002"})
# Returns: {success, message, refund_amount}
```

### RAG Retriever API

```python
from src.rag.retriever import get_retriever

retriever = get_retriever()

# Retrieve documents
docs, metadata = retriever.retrieve("What is your return policy?", n_results=3)

# Retrieve with scores
results = retriever.retrieve_with_scores("return policy")
# Returns: [(document, metadata, score), ...]

# Check match strength
is_strong = retriever.is_strong_match(0.78, threshold=0.5)
```

### Session Service API

```python
from src.services.session_service import get_session_service

session_service = get_session_service()

# Store session
session_service.set_session("session_123", {
    "customer_name": "Priya",
    "last_order_id": "ORD-001"
})

# Retrieve session
data = session_service.get_session("session_123")

# Update specific key
session_service.update_session("session_123", "last_order_id", "ORD-002")

# Delete session
session_service.delete_session("session_123")
```

---

## 🔍 Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if service is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify connection
docker-compose exec postgres psql -U ecombot_user -d ecombot_db -c "SELECT 1"
```

### Redis Connection Issues

```bash
# Check Redis
docker-compose exec redis redis-cli -a redis_password ping

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

### RAG/ChromaDB Issues

```bash
# Check ChromaDB health
curl http://localhost:8000/api/v1/heartbeat

# Rebuild knowledge base
python -m src.rag.embed_catalog
```

---

## 📈 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Agent Response Time | < 500ms | Including tool calls |
| RAG Retrieval Time | < 100ms | ChromaDB query |
| Session Lookup | < 50ms | Redis read |
| Database Query | < 100ms | PostgreSQL optimized |
| Tool Call Latency | < 200ms | Network + processing |

---

## 🔐 Security Considerations

✅ All secrets externalized to `.env`  
✅ Database passwords protected  
✅ Redis password authentication  
✅ No sensitive data in logs  
✅ Input validation on all tools  
✅ SQL injection protection (parameterized queries)  
✅ XSS prevention (no user data in HTML)  

---

## 📝 License

This project is part of the Google ADK Workshop training material.

---

## 🤝 Support

For issues or questions about implementation:

1. Check the relevant day's test documentation
2. Review the specific module's docstrings
3. Consult the lab guide in `lab/capstone-project/`

---

## 🎓 Learning Outcomes

By completing this project, you will have:

- ✅ Built a multi-turn conversational agent
- ✅ Implemented tool calling with LangChain
- ✅ Set up production databases (PostgreSQL, Redis)
- ✅ Implemented RAG with semantic search
- ✅ Configured LLM routing and fallback
- ✅ Integrated external services via MCP
- ✅ Understood conversation state management
- ✅ Gained production deployment experience

---

**Version:** 5.0.0 (eComBot v5)  
**Status:** Production Ready  
**Last Updated:** June 2026
