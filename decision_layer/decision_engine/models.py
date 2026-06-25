from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DecisionInput(BaseModel):
    agent_id: str = Field(..., description="Unique collaborator agent role ID")
    trust_score: float = Field(0.80, description="Collaborator trust score [0.0 - 1.0]")
    confidence_score: float = Field(0.85, description="Collaborator confidence score [0.0 - 1.0]")
    verification_score: float = Field(1.0, description="Factual correctness verification score [0.0 - 1.0]")
    quality_score: float = Field(1.0, description="Reviewer quality score [0.0 - 1.0]")
    hallucination_risk: float = Field(0.0, description="Hallucination risk probability [0.0 - 1.0]")
    evidence_coverage: float = Field(1.0, description="Evidence coverage rating [0.0 - 1.0]")

class DecisionResult(BaseModel):
    decision: str = Field(..., description="Action decision (ACCEPT, VERIFY, REGENERATE, RETRY, ESCALATE, REJECT)")
    reason: str = Field(..., description="Text explanation justifying the action outcome")
    timestamp: str = Field(..., description="ISO formatted timestamp")

class DecisionHistory(BaseModel):
    workflow_id: str = Field(..., description="Workflow execution ID context")
    decisions: List[DecisionResult] = Field(default_factory=list, description="Chronological list of decisions")

class DecisionMetrics(BaseModel):
    accept_count: int = Field(0, description="Count of ACCEPT choices")
    verify_count: int = Field(0, description="Count of VERIFY choices")
    regenerate_count: int = Field(0, description="Count of REGENERATE choices")
    retry_count: int = Field(0, description="Count of RETRY choices")
    escalate_count: int = Field(0, description="Count of ESCALATE choices")
    decision_latency: float = Field(0.0, description="Processing speed duration in seconds")

class DecisionPackage(BaseModel):
    workflow_id: str = Field(..., description="Workflow execution ID context")
    decision: str = Field(..., description="Calculated action decision")
    algorithm: str = Field(..., description="Active decision strategy name")
    explanation: str = Field(..., description="User-facing justification summary text")
    inputs: Dict[str, float] = Field(..., description="Dictionary representation of input scores")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological log history")
    metrics: DecisionMetrics = Field(..., description="Aggregate execution speed metrics")
