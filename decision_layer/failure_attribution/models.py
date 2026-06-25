from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RootCause(BaseModel):
    responsible_agent: str = Field(..., description="Likeliest agent role origin of the failure")
    attribution_confidence: float = Field(..., description="Engine confidence rating [0.0 - 1.0]")
    alternative_candidates: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative culprit agents and their confidences")

class RecoveryPlan(BaseModel):
    recommended_action: str = Field(..., description="Action to recover (RETRY, REGENERATE, ESCALATE, REJECT)")
    steps: List[str] = Field(default_factory=list, description="Sequence steps to execute recovery")

class FailureRecord(BaseModel):
    failure_id: str = Field(..., description="Unique failure record ID")
    failure_type: str = Field(..., description="Category of failure")
    severity: str = Field(..., description="Severity level rating (LOW, MEDIUM, HIGH)")
    timestamp: str = Field(..., description="ISO formatted timestamp")

class FailureMetrics(BaseModel):
    total_failures: int = Field(0, description="Count of total failures logged")
    type_distribution: Dict[str, int] = Field(default_factory=dict, description="Counts per failure category")
    agent_distribution: Dict[str, int] = Field(default_factory=dict, description="Counts per culprit agent")
    attribution_latency: float = Field(0.0, description="Attribution calculation speed duration in seconds")
    trust_penalties: float = Field(0.0, description="Sum total of trust penalties applied")

class FailurePackage(BaseModel):
    workflow_id: str = Field(..., description="Workflow execution ID context")
    failure_detected: bool = Field(..., description="Flag indicating if a failure occurred")
    failure_type: str = Field(..., description="Assigned category description")
    root_cause: RootCause = Field(..., description="Structured root cause details")
    propagation_graph: List[str] = Field(default_factory=list, description="Sequence path of failure propagation")
    recovery_plan: RecoveryPlan = Field(..., description="Actionable recovery recommendation steps")
    metrics: FailureMetrics = Field(..., description="Aggregate execution speed metrics")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological log history")
