# PROJECT REPOSITORY & CODEBASE DESIGN (PRCD)

**Project Title:** Confidence-Calibrated Trust-Aware Dynamic Collaboration Framework for Autonomous Multi-Agent LLM Systems  
**Project Type:** AI Research Framework  
**Version:** 1.0  

---

## 1. Repository Directory Layout
The project repository is structured as a monolithic repository dividing the Frontend (Next.js), Backend (FastAPI), the core Agentic Workflow (LangGraph), and the Decision Intelligence Layer into modular, self-contained directories.

```
TrustAware-MultiAgent-Framework/
│
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
│
├── docs/                       # Architectural specs, paper, thesis drafts
├── backend/                    # FastAPI server code
│   ├── api/                    # API endpoints
│   ├── core/                   # Security, middleware, dependency injection
│   ├── services/               # DB connection, LLM and workflow wrappers
│   ├── utils/                  # Timers, validators, formatting helpers
│   ├── main.py
│   └── app.py
│
├── frontend/                   # Next.js web application
│
├── database/                   # SQLite/PostgreSQL models and connection mappings
│   ├── models/
│   ├── migrations/
│   └── connection.py
│
├── memory/                     # Semantic, episodic, and short-term memory logic
│   ├── short_term.py
│   ├── long_term.py
│   └── retrieval.py
│
├── embeddings/                 # Vectorizer integrations (SentenceTransformers)
│
├── workflows/                  # LangGraph workflow definition (states, edges, checkpointer)
│   ├── graph.py
│   ├── state.py
│   └── routing.py
│
├── agents/                     # Specialized agent implementations and prompt bindings
│   ├── base_agent.py
│   ├── planner/
│   ├── scheduler/
│   ├── research/
│   ├── writing/
│   ├── citation/
│   ├── reviewer/
│   └── verification/
│
├── decision_layer/             # Proposed Research Decision Intelligence Layer
│   ├── trust_engine/
│   ├── confidence_engine/
│   ├── decision_engine/
│   ├── communication_manager/
│   ├── verification_manager/
│   └── failure_attribution/
│
├── algorithms/                 # Mathematical implementation files for research engines
│
├── prompts/                    # Externalized prompt library (text templates)
│
├── evaluation/                 # Metrics logging (ECE, Brier, token counts)
│
├── experiments/                # Research script folders (baseline, ablation, sensitivity)
│
├── benchmarks/                 # Standard QA, coding, and planning task datasets
│
├── configs/                    # YAML-based execution configurations
│
├── scripts/                    # Automation and batch simulation scripts
│
├── logs/                       # System and agent execution output files
│
└── tests/                      # Automated unit, integration, and E2E tests
```

---

## 2. Key Architecture Mappings

### 2.1 Backend Services (`backend/services/`)
* `llm_service.py`: Wraps LiteLLM to route prompt payloads to target models.
* `trust_service.py`: Exposes database transaction APIs to update and retrieve historical trust scores.
* `workflow_service.py`: Starts and manages active LangGraph task execution threads.

### 2.2 Decision Intelligence Layer (`decision_layer/`)
Decoupled from direct LangGraph workflow nodes. Nodes in `workflows/nodes.py` intercept control and invoke `decision_layer/` engines to validate states before routing execution to the next node.

### 2.3 Evaluation & Metrics (`evaluation/`)
* Tracks Expected Calibration Error (ECE) and Brier scores.
* Calculates communication overhead efficiency percentage compared to uncalibrated static baseline runs.
