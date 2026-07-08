# eComBot Architecture & Design Document

## System Architecture Overview

### 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                            │
│                   (Chat/Interactive Mode)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    eComBot Agent Core                            │
│  • Session management                                            │
│  • Instruction loading                                           │
│  • Context building                                              │
└──────┬────────────────┬────────────────────┬────────────────────┘
       │                │                    │
       ▼                ▼                    ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Tools      │ │   RAG        │ │   Routing    │
│              │ │   Retrieval  │ │   Hints      │
│ • Orders     │ │              │ │              │
│ • Products   │ │ • ChromaDB   │ │ • fast-faq   │
│ • Inventory  │ │ • Embeddings │ │ • deep-supp  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
         ┌──────────────▼───────────────┐
         │    LiteLLM Gateway           │
         │  (Model Routing & Fallback)  │
         └──────────────┬───────────────┘
                        │
         ┌──────────────▼───────────────┐
         │   LLM Provider               │
         │  (OpenRouter, OpenAI)        │
         └──────────────────────────────┘
```

### 2. Data Flow Architecture

```
User Query
    │
    ▼
┌─────────────────────────┐
│ Input Processing        │
│ • Tokenization          │
│ • Entity extraction     │
│ • Intent detection      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Session Context Retrieval               │
│ Redis: customer_name, last_order_id     │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ RAG Retrieval (if needed)               │
│ ChromaDB: relevant KB chunks            │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Build Context for LLM                   │
│ • System prompt                         │
│ • Session history                       │
│ • Retrieved documents                   │
│ • Routing hints                         │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Call LLM via LiteLLM Gateway            │
│ • Route to fast-faq or deep-support     │
│ • Include tool definitions              │
│ • Set model parameters                  │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Process LLM Response                    │
│ • Detect tool calls                     │
│ • Execute tools via MCP                 │
│ • Format response                       │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Save Session & History                  │
│ Redis: updated context                  │
│ PostgreSQL: full conversation           │
└──────────┬──────────────────────────────┘
           │
           ▼
User Response
```

---

## Component Details

### 1. eComBot Agent (`src/agents/support_agent.py`)

**Responsibilities:**
- Load and manage instructions
- Maintain session state
- Build prompts with context
- Coordinate tool calling
- Format responses

**Key Methods:**
```python
class SupportAgent:
    process_user_input(message: str) -> str
    update_session_state(key: str, value: Any) -> None
    get_session_state(key: str) -> Any
    _build_system_prompt() -> str
    _generate_response(message: str, prompt: str) -> str
```

### 2. Tools (`src/tools/`)

**Order Tools (`order_tools.py`):**
- `get_order_status(order_id)` - Retrieve order status
- `cancel_order(order_id)` - Cancel an order

**Product Tools (`product_tools.py`):**
- `lookup_product(product_name)` - Find product by name
- `check_stock(product_id)` - Check inventory level

**Implementation Pattern:**
```python
@tool
def tool_name(param: str) -> dict:
    """Tool description"""
    # Input validation
    if not param:
        return {"error": "Invalid input"}
    
    # Business logic
    result = perform_operation(param)
    
    # Return structured result
    return result
```

### 3. Services (`src/services/`)

**Database Service (`db.py`):**
- Connection pooling
- Query execution
- Error handling
- Tables: orders, products, session_history

**Session Service (`session_service.py`):**
- Redis connection management
- Session storage/retrieval
- TTL management
- Session keys: customer_name, last_order_id

**History Service (`history_service.py`):**
- Save conversation messages
- Retrieve history by session
- Store tool call metadata
- Database schema: session_history

**MCP Server (`mcp_server.py`):**
- Order management endpoints
- Inventory endpoints
- Error handling
- Health check

### 4. RAG Layer (`src/rag/`)

**Embedding (`embed_catalog.py`):**
- Load products.json and faq.json
- Create embeddings
- Store in ChromaDB
- Metadata attachment

**Retrieval (`retriever.py`):**
- Query embedding
- Semantic search
- Score calculation
- Confidence thresholding

**Knowledge Base:**
- Products (5 items): name, price, features, warranty
- FAQs (10 items): Q&A pairs with categories

### 5. Configuration (`src/config/settings.py`)

**Environment Variables:**
- API keys (OpenRouter, OpenAI, LangSmith)
- Database credentials (PostgreSQL, Redis)
- Service URLs (LiteLLM, ChromaDB)
- Application settings (debug, log level)

---

## Day-by-Day Component Integration

### Day 01-02: Foundation
- ✓ Agent initialization
- ✓ Instruction loading
- ✓ Basic response generation

### Day 03: Tool Calling
- ✓ Tool registration
- ✓ In-memory session state
- ✓ Tool execution

### Day 04: Persistence
- ✓ PostgreSQL database
- ✓ Redis sessions
- ✓ History tracking

### Day 05-06: Knowledge Grounding
- ✓ ChromaDB integration
- ✓ Semantic retrieval
- ✓ Hallucination guards

### Day 07: Model Routing
- ✓ LiteLLM proxy
- ✓ Route hints
- ✓ Fallback behavior

### Day 08: External Services
- ✓ FastMCP server
- ✓ Tool endpoints
- ✓ Error handling

---

## Error Handling Strategy

### Tool-Level Errors
```python
try:
    result = tool_function(param)
    return result
except ValueError as e:
    return {"error": str(e)}
except Exception as e:
    logger.error(f"Tool error: {e}")
    return {"error": "Tool execution failed"}
```

### Service-Level Errors
```python
try:
    connection = db.get_connection()
    result = db.execute_query(sql)
except psycopg2.OperationalError:
    return {"error": "Database unavailable"}
except redis.ConnectionError:
    return {"error": "Session service unavailable"}
```

### Agent-Level Fallback
```python
def process_user_input(message):
    try:
        response = generate_response(message)
    except LLMError:
        response = "Sorry, I'm having trouble right now. Please try again."
    except ToolError:
        response = "I couldn't retrieve that information right now."
    return response
```

---

## Data Structures

### Session State (Redis)
```json
{
  "session:abc123": {
    "customer_name": "Priya",
    "last_order_id": "ORD-001",
    "last_product_id": "PRD-101",
    "conversation_count": 3,
    "created_at": "2026-06-15T10:30:00Z"
  }
}
```

### Conversation History (PostgreSQL)
```sql
CREATE TABLE session_history (
  id SERIAL,
  session_id VARCHAR(255),
  role VARCHAR(50),          -- 'user' or 'assistant'
  content TEXT,
  tool_calls JSONB,
  created_at TIMESTAMP
);
```

### ChromaDB Document
```json
{
  "id": "faq_0",
  "document": "Q: What is your return policy? A: 30-day guarantee...",
  "metadata": {
    "type": "faq",
    "category": "Returns & Refunds",
    "source": "data/faq.json"
  }
}
```

### Tool Call Result
```json
{
  "success": true,
  "data": {
    "order_id": "ORD-001",
    "status": "Shipped",
    "eta": "2026-06-05"
  }
}
```

---

## Security Architecture

### 1. Secrets Management
- .env file (excluded from git)
- Environment variable loading
- No hardcoded credentials

### 2. Input Validation
- Type checking
- Format validation
- SQL injection prevention (parameterized queries)

### 3. Output Sanitization
- Error messages don't leak internals
- No stack traces to users
- Sensitive data redaction

### 4. Authentication
- Redis password protection
- PostgreSQL user authentication
- API key validation

### 5. Data Protection
- Database connections encrypted
- Session data TTL
- History retention policy

---

## Performance Optimization

### Caching Strategy
```python
# RAG result caching
lru_cache(maxsize=100)(retriever.retrieve)

# Session lookup caching
redis.get(session_id)  # < 50ms

# Database connection pooling
pool.getconn()  # Reuse connections
```

### Database Optimization
```sql
-- Indexes for fast queries
CREATE INDEX idx_session_id ON session_history(session_id);
CREATE INDEX idx_order_id ON orders(order_id);
CREATE INDEX idx_product_id ON products(product_id);
```

### RAG Optimization
```python
# Batch embeddings
embeddings = model.encode(documents, batch_size=32)

# Similarity caching
@functools.lru_cache
def query_embedding(text):
    return embedder.encode(text)
```

---

## Scalability Considerations

### Horizontal Scaling
- Stateless agent design
- Redis for distributed sessions
- PostgreSQL read replicas
- Load balancing ready

### Vertical Scaling
- Connection pooling
- Batch processing
- Memory optimization
- Query optimization

### Future Enhancements
- Multi-agent orchestration
- Agent-to-agent communication
- Distributed tool calling
- Cloud vector storage
- Microservices architecture

---

## Testing Strategy

### Unit Tests
- Tool functionality
- Configuration loading
- Error handling

### Integration Tests
- Agent + tools
- Agent + RAG
- Agent + services

### End-to-End Tests
- Full conversation flows
- Multi-turn scenarios
- Error recovery

### Performance Tests
- Latency benchmarks
- Throughput measurement
- Resource monitoring

---

## Deployment Architecture

### Development
```
Local machine
├── Python venv
├── Docker containers (local)
├── In-memory ChromaDB
└── SQLite (optional)
```

### Staging
```
Staging server
├── Python environment
├── Docker with volumes
├── Persistent PostgreSQL
├── Persistent Redis
└── ChromaDB with backups
```

### Production
```
Production cluster
├── Multiple agent instances
├── Managed PostgreSQL (RDS)
├── Managed Redis (ElastiCache)
├── Cloud vector store
├── Load balancer
└── Monitoring & logging
```

---

## Conclusion

eComBot is designed with:
- ✓ **Modularity**: Independent, reusable components
- ✓ **Scalability**: Ready for growth
- ✓ **Reliability**: Error handling and fallbacks
- ✓ **Security**: Secrets and input validation
- ✓ **Performance**: Optimized data access
- ✓ **Maintainability**: Clear separation of concerns
- ✓ **Extensibility**: Easy to add new tools/features

This architecture forms a solid foundation for production e-commerce support systems.
