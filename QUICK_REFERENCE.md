# eComBot Quick Reference Guide

## Command Reference

### Setup

```bash
# Initial setup
python scripts/setup.py

# Start services
docker-compose up -d

# Initialize RAG
python -m src.rag.embed_catalog

# Run tests
python scripts/test_agent.py
```

### Running eComBot

```bash
# Interactive mode (default)
python scripts/run.py

# Batch mode
python scripts/run.py --mode batch --queries "Hello" "Help"

# With custom instruction
python scripts/run.py --instruction-file src/agents/support_instructions_v2.txt

# With routing hint
python scripts/run.py --route-hint deep-support
```

### Starting MCP Server

```bash
python -m src.services.mcp_server
# Available on http://localhost:8001
```

### Docker Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f chroma

# Access database
docker-compose exec postgres psql -U ecombot_user -d ecombot_db

# Access Redis
docker-compose exec redis redis-cli -a redis_password

# Health check
docker-compose ps
```

---

## API Endpoints

### MCP Server (http://localhost:8001)

- `GET /health` - Server health
- `GET /tools` - List available tools
- `POST /tools/get_order_status?order_id=ORD-001`
- `POST /tools/get_order_details?order_id=ORD-001`
- `POST /tools/cancel_order?order_id=ORD-001`
- `POST /tools/check_stock?product_id=PRD-101`
- `POST /tools/list_variants?product_id=PRD-101`

### Agent API

```python
from src.agents.support_agent import create_support_agent

agent = create_support_agent()
response = agent.process_user_input("Your question here")
```

---

## File Structure Quick Map

```
ecombot/
├── src/agents/              # Agent core logic
├── src/tools/               # Tool definitions
├── src/services/            # Database, session, history
├── src/rag/                 # Knowledge base indexing/retrieval
├── src/config/              # Configuration
├── data/                    # Knowledge base files
├── scripts/                 # Setup, test, run scripts
├── tests/                   # Test documentation
├── README.md                # Main documentation
├── IMPLEMENTATION_GUIDE.md  # Setup walkthrough
├── ARCHITECTURE.md          # Design documentation
└── docker-compose.yml       # Service orchestration
```

---

## Key Concepts

### Session State
Data persisted across turns in a single conversation:
- `customer_name` - User's name
- `last_order_id` - Most recent order queried
- `last_product_id` - Most recent product queried

### Tools
Callable functions registered with the agent:
- Order tools: status, cancellation, details
- Product tools: lookup, stock checking, variants

### RAG
Retrieval-Augmented Generation:
- Knowledge base: products.json + faq.json
- Storage: ChromaDB
- Retrieval: Semantic search with similarity scoring

### Routing Hints
Indicate query complexity to LLM gateway:
- `fast-faq` - Simple FAQ-type queries (cheaper)
- `deep-support` - Complex support issues (better quality)

---

## Example Conversation

```
User: Hi, my name is Priya
Agent: Hello Priya! Welcome to our e-commerce support. How can I help?
[Session state: customer_name = "Priya"]

User: Where is my order ORD-001?
Agent: Your order ORD-001 is Shipped via BlueDart, arriving June 5th.
[Tools used: get_order_status]
[Session state: last_order_id = "ORD-001"]

User: Is the Laptop Stand still in stock?
Agent: Yes! The Laptop Stand is in stock with 45 units available.
[Tools used: check_stock]
[RAG used: Product information retrieved]
[Session state: last_product_id = "PRD-101"]

User: What's your return policy?
Agent: We offer a 30-day money-back guarantee...
[RAG used: FAQ retrieval]
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| PostgreSQL won't start | Check `docker-compose logs postgres` |
| Redis connection error | Verify password in .env |
| RAG returns nothing | Run `python -m src.rag.embed_catalog` |
| MCP server not responding | Ensure `python -m src.services.mcp_server` is running |
| Tools not found | Check tool imports in support_agent.py |

---

## Performance Tips

- Use `fast-faq` route for simple queries to reduce latency
- Cache frequent RAG queries
- Keep session TTL balanced (24h default)
- Monitor database connections (pool size: 1-20)
- Batch RAG embeddings for faster indexing

---

## Testing Checklist

- [ ] Basic agent responds to greetings
- [ ] Tools return structured data
- [ ] Session state persists across turns
- [ ] RAG retrieves knowledge base chunks
- [ ] Database stores and retrieves data
- [ ] Redis stores sessions
- [ ] MCP server responds to all endpoints
- [ ] Error handling works gracefully

---

## Production Checklist

- [ ] .env configured with production keys
- [ ] DEBUG=False in .env
- [ ] Database backups scheduled
- [ ] Redis AOF persistence enabled
- [ ] Monitoring/logging configured
- [ ] Security group rules restricted
- [ ] SSL/TLS certificates deployed
- [ ] Load balancer configured

---

## Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check agent state:
```python
agent = create_support_agent()
print(agent.session_state)
print(agent.instruction[:100])
```

Test RAG:
```python
from src.rag.retriever import get_retriever
r = get_retriever()
docs, meta = r.retrieve("test query")
print(f"Retrieved {len(docs)} docs")
```

---

## Resources

- [Main README](README.md)
- [Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [Architecture Document](ARCHITECTURE.md)
- Lab guides: `lab/capstone-project/Day0X_LabGuide.md`
- Test results: `tests/test_*.md`

---

**Quick Version:** eComBot v5.0.0
