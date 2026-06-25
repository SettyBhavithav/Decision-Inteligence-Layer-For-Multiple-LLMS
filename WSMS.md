# WORKFLOW & STATE MACHINE SPECIFICATION (WSMS)

**Project Title:** Confidence-Calibrated Trust-Aware Dynamic Collaboration Framework for Autonomous Multi-Agent LLM Systems  
**Project Type:** AI Research Framework  
**Version:** 1.0  

---

## 1. Overview of Workflow
The system orchestrates multi-agent tasks using a state-machine workflow. This workflow ensures that agent actions are evaluated by the Decision Intelligence Layer (DIL) before propagating, allowing dynamic retry, verification, and failure attribution.

```
[INITIALIZED]
      │
      ▼
  [PLANNING] ──(PlannerAgent)──► [TASK_SPLIT]
                                      │
                                      ▼
                                [SCHEDULING] (DynamicTaskScheduler)
                                      │
                                      ▼
                                 [EXECUTING] (SpecializedAgent)
                                      │
                                      ▼
                             [TRUST_EVALUATION]
                                      │
                                      ▼
                           [CONFIDENCE_EVALUATION]
                                      │
                                      ▼
                                  [DECISION] (DecisionEngine Gate)
                                  ├── Accept ──► [COMMUNICATION] ──► [REVIEW]
                                  ├── Verify ──► [VERIFICATION] (VerifyAgent)
                                  │                   ├── Passed ──► [ACCEPT]
                                  │                   └── Failed ──► [REJECT]
                                  └── Reject ──► [FAILURE_ANALYSIS] (Attribution)
                                                      │
                                                      ▼
                                                [REGENERATE] (Retry)
                                                      │ (Retries Exceeded)
                                                      ▼
                                                  [FAILED]
                                      │
                                      ▼
                               [MEMORY_UPDATE]
                                      │
                                      ▼
                                  [LOGGING]
                                      │
                                      ▼
                                 [COMPLETED]
```

---

## 2. LangGraph Nodes & State Definition
The LangGraph workflow maintains a shared state dictionary passed between nodes:
```python
class AgentWorkflowState(dict):
    query: str
    subtasks: list
    active_task_id: str
    trajectory: list
    resolved_context: dict
    trust_scores: dict
    accumulated_failures: int
    current_step: int
    final_output: str
```

### Graph Nodes:
1. **`planner_node`:** Invokes PlannerAgent to populate `subtasks`.
2. **`scheduler_node`:** Decides the next active `subtask` based on dependencies.
3. **`agent_node`:** Invokes the specialized agent assigned to the active subtask.
4. **`trust_node`:** Computes active trust score from memory.
5. **`confidence_node`:** Calibrates confidence score.
6. **`decision_node`:** Jointly gates the reliability score and returns routing action.
7. **`verification_node`:** Fact-checks suspicious outputs.
8. **`failure_node`:** Attributes mistakes and penalizes trust scores.
9. **`aggregator_node`:** Compiles accepted outputs into the final response.

---

## 3. Gating & Retry Policies
* **Dynamic Verification Gating:** Under verification state, control routes to `verification_node`. If fact-checking returns `VERIFIED`, the task state moves to completion. If `FAILED`, task state transitions to rejection.
* **Retry Bounds:** Each subtask has a maximum retry allowance ($N_{max\_retry} = 2$). If a subtask fails more than twice, the orchestrator reports a global trajectory execution failure, logs the failure attribution trace, and halts execution.
* **Fault Recovery:** When a node encounters an API exception, the checkpointer persists state, logs the connection error, and retries the API call after an exponential delay.
