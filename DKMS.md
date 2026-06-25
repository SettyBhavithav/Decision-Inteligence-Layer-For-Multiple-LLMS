# DATA & KNOWLEDGE MODEL SPECIFICATION (DKMS)

**Project Title:** Confidence-Calibrated Trust-Aware Dynamic Collaboration Framework for Autonomous Multi-Agent LLM Systems  
**Project Type:** AI Research Framework  
**Version:** 1.0  

---

## 1. Overview of Data Architecture
The data model persists structural application metadata (users, sessions, workflows), runtime agent execution data (inputs, outputs, tokens), research layer telemetry (trust adjustments, calibrated confidence metrics, decision gates), and vector-based semantic memories.

```
PostgreSQL / SQLite (Relational Store)
├── Users & Sessions
├── Workflows & Tasks
├── Agent Executions (Inputs, outputs, tokens, latency)
├── Trust History (Dynamic scores, updates, reasoning)
├── Confidence History (Raw confidence, structural scores, calibration outcomes)
├── Decisions (Trust/Confidence used, decision actions: ACCEPT/VERIFY/REJECT)
├── Verification Records (Fact-check outputs, verification agent, status)
├── Failure Attribution logs (Decisive error steps, failed agent, cause)
├── Communication Logs (Sender, receiver, message payload size)
└── Prompt Versions & Experiments (YAML settings, ECE/F1 evaluations)

ChromaDB (Vector Memory Store)
└── Semantic Memory (Documents, text embeddings, source metadata)

Redis (Caching Layer)
└── Caches (Session states, temporary trust cache, active graph state)
```

---

## 2. Core Relational Database Schemas

### 2.1 Users & Sessions
* **`users`:** `user_id` (PK), `name`, `email`, `role`, `created_at`, `status`.
* **`sessions`:** `session_id` (PK), `user_id` (FK), `start_time`, `end_time`, `status`.

### 2.2 Workflows & Tasks
* **`workflows`:** `workflow_id` (PK), `session_id` (FK), `name`, `current_state`, `status`, `duration_seconds`.
* **`tasks`:** `task_id` (PK), `workflow_id` (FK), `parent_task_id`, `description`, `priority`, `status`.

### 2.3 Agent Executions
* **`agents`:** `agent_id` (PK), `name`, `role`, `llm_model`, `version`, `status`.
* **`agent_executions`:** `execution_id` (PK), `task_id` (FK), `agent_id` (FK), `prompt_version_id`, `input_text`, `output_text`, `start_time`, `end_time`, `tokens_used`, `latency_seconds`.

### 2.4 Research Layer Telemetry (DIL)
* **`trust_history`:** `trust_id` (PK), `agent_id` (FK), `prev_trust`, `updated_trust`, `reason`, `timestamp`.
* **`confidence_history`:** `confidence_id` (PK), `execution_id` (FK), `confidence_score`, `calibration_status`, `timestamp`.
* **`decisions`:** `decision_id` (PK), `execution_id` (FK), `trust_used`, `confidence_used`, `decision` (ACCEPT/VERIFY/REJECT), `reason`.
* **`verifications`:** `verification_id` (PK), `execution_id` (FK), `verification_agent_id`, `result` (VERIFIED/FAILED), `evidence`, `timestamp`.
* **`failures`:** `failure_id` (PK), `execution_id` (FK), `failed_agent_id`, `cause`, `failure_type`, `corrective_action`, `timestamp`.
* **`communications`:** `communication_id` (PK), `sender_agent_id`, `receiver_agent_id`, `message_type`, `tokens_used`, `timestamp`.

### 2.5 Reproducibility & Evaluation
* **`prompt_versions`:** `prompt_id` (PK), `agent_role`, `version_tag`, `prompt_text`, `created_at`.
* **`experiments`:** `experiment_id` (PK), `name`, `configuration_json`, `baseline_framework`, `dataset_name`, `timestamp`.
* **`evaluations`:** `evaluation_id` (PK), `experiment_id` (FK), `accuracy`, `precision`, `recall`, `f1_score`, `trust_accuracy`, `calibration_quality_ece`, `latency_seconds`, `total_tokens`.

---

## 3. Vector Memory Schema (ChromaDB)
For each chunk written to the semantic memory database:
* **Document ID:** Unique UUID string.
* **Vector Embedding:** 384-dimensional or 768-dimensional float array.
* **Metadata Dict:**
  ```json
  {
    "source_task_id": "task_0",
    "agent_role": "research",
    "session_id": "session_123",
    "timestamp": 1782806400
  }
  ```
* **Text Content:** Source document string.
