# COMPLETE SYSTEM ARCHITECTURE SPECIFICATION (CSAS)

**Project Title:** Confidence-Calibrated Trust-Aware Dynamic Collaboration Framework for Autonomous Multi-Agent LLM Systems  
**Project Type:** AI Research Framework  
**Technology Stack:** FastAPI, LangGraph, LiteLLM, Streamlit, SQLite/PostgreSQL  
**Version:** 1.0  

---

## 1. High-Level Architecture
```
                    USER
                     │
                     ▼
              Frontend (Web UI)
                     │
                     ▼
             FastAPI Backend Server
                     │
                     ▼
           LangGraph Workflow Engine
                     │
                     ▼
          Decision Intelligence Layer
                     │
 ┌────────────────────────────────────────────┐
 │  Planner Agent         Task Scheduler      │
 │  Trust Engine          Confidence Estimator│
 │  Decision Engine       Communication Mgr   │
 │  Verification Engine   Failure Attribution │
 └────────────────────────────────────────────┘
                     │
                     ▼
             Specialized AI Agents
                     │
 ┌────────────────────────────────────────────┐
 │ Research Agent        Writing Agent        │
 │ Citation Agent        Reviewer Agent       │
 │ Verification Agent                         │
 └────────────────────────────────────────────┘
                     │
                     ▼
          Memory & Knowledge Layer
                     │
 ┌────────────────────────────────────────────┐
 │ Database Store        Conversation Memory  │
 │ Trust History DB      Confidence Logs      │
 │ Failure Logs                               │
 └────────────────────────────────────────────┘
                     │
                     ▼
               Final Response
```

---

## 2. Seven-Layer Architecture

### Layer 1 — Presentation Layer (Web UI)
Renders the chat interface, real-time agent execution traces, communication graphs, and live analytics plots displaying trust score trajectories and confidence calibration curves.

### Layer 2 — Application Layer (API)
An asynchronous REST API built with **FastAPI** that validates request payloads, manages user sessions, and routes requests to the workflow engine.

### Layer 3 — Workflow Layer (LangGraph orchestration)
Responsible for executing the multi-agent task execution graph, maintaining the shared state, and routing control between agents.

### Layer 4 — Decision Intelligence Layer (Research Layer) ⭐
The core research layer. Every intermediate response passes through this layer to evaluate:
1. **Planner Agent:** Task analyzer and decomposer.
2. **Task Scheduler:** Topological execution sorting.
3. **Trust Engine:** Dynamic trust score calculations.
4. **Confidence Estimator:** Platt-scaled confidence calibration.
5. **Decision Engine:** Gating policy (`ACCEPT` / `VERIFY` / `REJECT` / `REGENERATE`).
6. **Communication Manager:** Optimal path routing and dynamic bypasses.
7. **Failure Attribution:** Counterfactual failure audit.

### Layer 5 — Agent Layer (Specialized Agents)
Contains role-specific functional agents (`ResearchAgent`, `WritingAgent`, `CitationAgent`, `ReviewerAgent`, `VerificationAgent`) configured with specialized prompt templates.

### Layer 6 — Memory Layer
Coordinates short-term state memory, long-term semantic context, and stores agent execution histories.

### Layer 7 — Storage Layer (Data persistence)
Saves session states, conversational history, dynamic trust scores, and token logs into a persistent store (SQLite database).

---

## 3. Data Flow
1. **User Query** $\rightarrow$ API Gateway $\rightarrow$ Planner Agent.
2. **Planner Agent** decomposes query into subtasks with dependencies $\rightarrow$ Task Scheduler.
3. **Task Scheduler** executes subtasks in topological order.
4. **Specialized Agent** generates response + raw confidence.
5. **Trust Engine** fetches current trust score $T_i$ for the agent.
6. **Confidence Estimator** calibrates confidence $\hat{c}$ based on self-reported, structural, and history features.
7. **Decision Engine** evaluates gating condition ($\hat{c} \times T_i$):
   * **ACCEPT:** Mark subtask as complete, release downstream dependencies, and update trust score (success path).
   * **VERIFY:** Route response to `VerificationAgent` for cross-validation.
   * **REJECT:** Penalty applied to responsible agent via **Failure Attribution** module; regenerate or route to alternate agent.
8. **Response Aggregator** compiles all accepted subtask outputs into a cohesive output.
9. **Final Response** returned to Presentation Layer.

---

## 4. Communication & Message Model
All inter-agent communication uses structured message payloads to ensure auditability:
```json
{
  "task_id": "task_0",
  "agent_id": "ResearchAgent_01",
  "role": "research",
  "response": "Vision Transformers (ViT) apply self-attention...",
  "raw_confidence": 0.85,
  "calibrated_confidence": 0.82,
  "trust_score": 0.50,
  "verification_status": "NONE",
  "timestamp": 1782806400
}
```

---

## 5. Architectural Objectives & Guardrails
* **Explainability:** Auditable execution traces recording agent outputs, decision outcomes, trust adjustments, and failure reasoning.
* **Fault Tolerance:** Automated retry limit ($N_{retry} = 2$) and dynamic agent rescheduling.
* **Scalability:** Pluggable design via LiteLLM supporting seamless agent model updates and provider switches.
