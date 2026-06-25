# TECHNOLOGY STACK SPECIFICATION (TSS)

**Project Title:** Confidence-Calibrated Trust-Aware Dynamic Collaboration Framework for Autonomous Multi-Agent LLM Systems  
**Project Type:** AI Research Framework  
**Version:** 1.0  

---

## 1. Overall Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js (React) + TypeScript + Tailwind CSS | Interactive research dashboard & chat interface |
| **Backend** | FastAPI (Python) | High-performance REST APIs & system orchestration |
| **Workflow** | LangGraph | State-based multi-agent execution & graph routing |
| **LLM Provider** | LiteLLM + Configurable APIs (Gemini, OpenAI, Anthropic, DeepSeek) | Unified LLM abstraction layer |
| **Vector DB** | ChromaDB (Chroma-client) | Semantic long-term memory & document retrieval |
| **Relational DB**| PostgreSQL (with fallback to SQLite for local execution) | Structured data storage (trust history, logs, tasks) |
| **Cache/Queue**  | Redis (with local dict fallback) | Session management & caching |
| **ORM** | SQLAlchemy | Relational database abstraction layer |
| **Logging** | Standard Logging + Loguru | Audit trails and event tracing |
| **Configuration**| Pydantic Settings + `.env` | Environment configuration & threshold management |
| **Testing** | Pytest | Automated unit and integration testing |
| **Deployment** | Docker & Docker Compose | Containerized reproducible execution environment |

---

## 2. Component Specifications

### 2.1 Frontend: Next.js + Tailwind CSS
* Renders the real-time agent workflow graph.
* Renders visual trust score timelines and confidence calibration graphs.
* Provides a configuration panel to tune decision thresholds ($\theta_{accept}, \theta_{verify}$) and select active models.

### 2.2 Backend API: FastAPI
* Exposes REST endpoints to submit user queries and stream agent logs.
* Exposes analytical endpoints to retrieve historical calibration data (ECE, Brier scores).

### 2.3 Workflow Orchestration: LangGraph
* Orchestrates state transitions between Specialized Agents using state graphs.
* Implements dynamic graph branching based on outputs from the Decision intelligence layer.

### 2.4 Database & Memory Layer: PostgreSQL + ChromaDB
* **PostgreSQL:** Tracks user sessions, task histories, dynamic trust history records, and failure logs. Uses SQLite as a zero-config local backup.
* **ChromaDB:** Stores vector embeddings of task context for long-term semantic retrieval.

---

## 3. Deployment & Caching Strategy
* **Docker Compose:** Bundles the Next.js frontend, FastAPI backend, PostgreSQL, and Redis into a single-command reproducible container stack.
* **Redis Caching:** Accelerates repetitive subtask execution and stores active session states.
