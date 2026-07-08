# eComBot Implementation Guide

## Complete Setup and Deployment Instructions

This guide walks through setting up and running eComBot from scratch, covering all 8 days of development.

---

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Docker and Docker Compose installed
- [ ] Git installed
- [ ] OpenRouter API key obtained
- [ ] OpenAI API key (for embeddings)
- [ ] 8GB+ RAM available
- [ ] 5GB disk space available

---

## Part 1: Initial Setup (Days 01-02)

### Step 1.1: Clone Repository

```bash
cd c:\Vinod\Repos\Workshop\Google-ADK\Karthi-Training\google-adk\ecombot
```

### Step 1.2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

### Step 1.3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 1.4: Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

**.env Configuration:**
```bash
OPENROUTER_API_KEY=your_openrouter_key
OPENAI_API_KEY=your_openai_key
ENVIRONMENT=development
DEBUG=True
```

### Step 1.5: Test Basic Agent

```bash
python scripts/run.py --mode batch --queries "Hello" "What is your name?"
```

**Expected Output:**
```
User: Hello
Agent: Hello! Welcome to our e-commerce support. How can I help you today?
```

---

## Part 2: Tool Integration (Days 03)

### Step 2.1: Understand Tool Architecture

eComBot uses LangChain's `@tool` decorator for tool definition:

```python
from langchain.tools import tool

@tool
def get_order_status(order_id: str) -> dict:
    """Get order status"""
    # Implementation
    return {"order_id": order_id, "status": "Shipped"}
```

### Step 2.2: Test Tool Calling

```bash
python scripts/test_agent.py
# Run test_tool_calling() section
```

**Expected Output:**
```
Testing tool calling...
Query: What is the status of order ORD-001?
Agent: Order ORD-001 status: Shipped, ETA: 5 Jun 2026, Carrier: BlueDart
```

### Step 2.3: Verify Session State

```bash
python scripts/test_agent.py
# Run test_session_state() section
```

**Verification:**
- Session state persists across turns
- Customer name stored and reused
- Order ID remembered

---

## Part 3: Database Integration (Day 04)

### Step 3.1: Start Infrastructure Services

```bash
docker-compose up -d
```

**Verify services:**
```bash
docker-compose ps
# All services should show "Up"
```

### Step 3.2: Verify Database Setup

```bash
# Check PostgreSQL
docker-compose exec postgres psql -U ecombot_user -d ecombot_db -c "SELECT COUNT(*) FROM orders;"

# Expected output: count = 3 (sample data inserted)
```

### Step 3.3: Verify Redis

```bash
docker-compose exec redis redis-cli -a redis_password ping
# Expected: PONG
```

### Step 3.4: Test Database Integration

```bash
python -c "
from src.services.db import get_database
db = get_database()
results = db.execute_query('SELECT * FROM orders LIMIT 1')
print(f'Orders found: {len(results)}')
print(results[0] if results else 'No orders')
"
```

### Step 3.5: Test Session Persistence

```bash
# Create a session
from src.services.session_service import get_session_service
service = get_session_service()
service.set_session("test123", {"user": "Priya"})

# Retrieve it
data = service.get_session("test123")
print(data)  # Should print: {'user': 'Priya'}
```

---

## Part 4: RAG Implementation (Days 05-06)

### Step 4.1: Verify Data Files

```bash
# Check products data
python -c "import json; print(len(json.load(open('data/products.json'))))"
# Should output: 5

# Check FAQ data
python -c "import json; print(len(json.load(open('data/faq.json'))))"
# Should output: 10
```

### Step 4.2: Initialize ChromaDB

```bash
python -m src.rag.embed_catalog
```

**Expected Output:**
```
Loaded 5 products
Loaded 10 FAQs
Embedded 15 documents in ChromaDB
Knowledge base embedded successfully!
```

### Step 4.3: Test Retrieval

```bash
from src.rag.retriever import get_retriever

retriever = get_retriever()
docs, metadata = retriever.retrieve("What is your return policy?", n_results=3)
print(f"Retrieved {len(docs)} documents")
print(f"Top result: {docs[0][:100]}...")
```

### Step 4.4: Verify Hallucination Guards

```bash
retriever = get_retriever()

# Test: Question with no answer in KB
docs, metadata = retriever.retrieve("What is the weather?", n_results=3)
print(f"Results: {len(docs)}")
# Should be 0 or very low confidence
```

---

## Part 5: LiteLLM Configuration (Day 07)

### Step 5.1: Install LiteLLM

```bash
pip install litellm
```

### Step 5.2: Configure Routing

Create `config/litellm_routes.yaml`:
```yaml
routes:
  - name: fast-faq
    models:
      - llama-2-7b
      - mistral-7b
  - name: deep-support
    models:
      - gpt-4-turbo
      - claude-3
```

### Step 5.3: Test Routing Hints

```python
agent = create_support_agent(route_hint="fast-faq")
# Route hint is set correctly
assert agent.route_hint == "fast-faq"
```

---

## Part 6: FastMCP Server (Day 08)

### Step 6.1: Start MCP Server

```bash
python -m src.services.mcp_server
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Step 6.2: Verify Server Endpoints

In another terminal:

```bash
# Health check
curl http://localhost:8001/health
# Expected: {"status":"healthy",...}

# List tools
curl http://localhost:8001/tools
# Expected: List of 5 tools
```

### Step 6.3: Test Tool Calls

```bash
# Get order status
curl -X POST "http://localhost:8001/tools/get_order_status?order_id=ORD-001"

# Check stock
curl -X POST "http://localhost:8001/tools/check_stock?product_id=PRD-101"
```

---

## Part 7: Full Integration Testing

### Step 7.1: Interactive Mode

```bash
python scripts/run.py --mode interactive
```

**Test Conversation:**
```
> Hi, my name is Priya
> Where is my order ORD-001?
> Is the laptop stand in stock?
> What about the mechanical keyboard?
> exit
```

### Step 7.2: Batch Mode with All Features

```bash
python scripts/test_agent.py
```

This runs all internal tests:
- Basic agent functionality
- Prompt variant testing
- Session state management
- Tool calling
- End-to-end conversation flows

### Step 7.3: Manual Test Verification

Review these files:
- `tests/test_support_agent_manual_day03.md` - Tool calling tests
- `tests/test_support_agent_manual_day04.md` - DB and Redis tests
- `tests/test_rag_manual_day05_06.md` - RAG tests
- `tests/test_litellm_day07.md` - Routing tests
- `tests/test_mcp_day08.md` - MCP integration tests

---

## Part 8: Production Deployment

### Step 8.1: Environment Hardening

Update `.env`:
```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

# Use production API keys
OPENROUTER_API_KEY=prod_key_here
OPENAI_API_KEY=prod_key_here
```

### Step 8.2: Database Backup

```bash
docker-compose exec postgres pg_dump -U ecombot_user ecombot_db > backup.sql
```

### Step 8.3: Health Monitoring

```bash
# Create health check script
# Regularly verify:
# - PostgreSQL connectivity
# - Redis connectivity
# - ChromaDB availability
# - MCP server health
```

### Step 8.4: Logging Configuration

```python
# Enable structured logging in production
import logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Troubleshooting

### Issue: PostgreSQL Connection Failed

```bash
# Check if service is running
docker-compose logs postgres

# Verify password
docker-compose exec postgres psql -U ecombot_user -d ecombot_db -c "SELECT 1"

# Reset database
docker-compose down postgres
docker volume rm ecombot_postgres_data
docker-compose up -d postgres
```

### Issue: Redis Connection Failed

```bash
# Check Redis
docker-compose logs redis

# Test connection
docker-compose exec redis redis-cli -a redis_password ping

# Clear data if needed
docker-compose exec redis redis-cli FLUSHALL
```

### Issue: ChromaDB Not Found

```bash
# Restart ChromaDB
docker-compose restart chroma

# Rebuild knowledge base
python -m src.rag.embed_catalog
```

### Issue: Tools Not Responding

```bash
# Check MCP server
curl http://localhost:8001/health

# If not running
python -m src.services.mcp_server

# Test specific tool
curl -X POST "http://localhost:8001/tools/get_order_status?order_id=ORD-001"
```

---

## Performance Optimization

### Tune PostgreSQL

```sql
-- Increase buffer pool
ALTER SYSTEM SET shared_buffers = '256MB';

-- Index optimization
CREATE INDEX idx_session_fast ON session_history(session_id, created_at);
```

### Optimize Redis

```bash
# Increase memory
redis-cli CONFIG SET maxmemory 512mb

# Set eviction policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Cache RAG Results

```python
# Cache frequent retrieval results
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_retrieve(query: str):
    return retriever.retrieve(query)
```

---

## Monitoring & Observability

### Key Metrics to Track

1. **Response Latency**
   - Agent response time
   - Tool call time
   - RAG retrieval time

2. **Error Rates**
   - Failed tool calls
   - Database errors
   - Service timeouts

3. **Usage Patterns**
   - Queries per hour
   - Most common intents
   - Tool call frequency

4. **Resource Usage**
   - CPU and memory
   - Database connections
   - Redis memory usage

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('ecombot.log', maxBytes=10485760, backupCount=5)
logging.getLogger().addHandler(handler)
```

---

## Security Best Practices

✅ **Implemented:**
- All secrets in .env (never hardcoded)
- Input validation on all tools
- Parameterized SQL queries
- Password protection on databases
- HTTPS ready (for production)
- Error message sanitization

✅ **To Add:**
- Rate limiting
- Authentication/Authorization
- Audit logging
- Data encryption at rest
- VPN/Network isolation

---

## Conclusion

eComBot is now fully implemented and ready for production. The system demonstrates:

- ✓ Multi-turn conversation with context
- ✓ Tool calling with structured data
- ✓ Persistent state management
- ✓ Knowledge-grounded answers
- ✓ Intelligent model routing
- ✓ External service integration
- ✓ Comprehensive error handling
- ✓ Production-ready architecture

For further support, refer to individual module documentation and test files.

---

**Last Updated:** June 2026  
**Version:** 5.0.0 (eComBot v5)  
**Status:** Production Ready
