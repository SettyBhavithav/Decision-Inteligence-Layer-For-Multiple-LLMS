from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentConfidence(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    confidence_score: float = Field(0.85, description="Current confidence rating in range [0.0 - 1.0]")
    algorithm_used: str = Field("proposed", description="Active calculation algorithm")
    timestamp: str = Field(..., description="ISO formatted timestamp")

class ConfidenceUpdate(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    previous_confidence: float = Field(..., description="Confidence score before update")
    updated_confidence: float = Field(..., description="Confidence score after update")
    change: str = Field(..., description="String sign representation of change (e.g. +0.04, -0.05)")
    reason: str = Field(..., description="Text justification for the change")
    timestamp: str = Field(..., description="ISO formatted timestamp")

class ConfidenceHistory(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    history: List[ConfidenceUpdate] = Field(default_factory=list, description="List of previous updates")

class ConfidenceMetrics(BaseModel):
    current_confidence: float = Field(0.85, description="Current confidence score value")
    confidence_change: float = Field(0.0, description="Last update change amount")
    average_confidence: float = Field(0.85, description="Running historical average confidence score")
    failed_estimations: int = Field(0, description="Count of invalid updates blocked")
    estimation_latency: float = Field(0.0, description="Last calculation speed in seconds")

class ConfidencePackage(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    confidence: float = Field(..., description="Current confidence score")
    algorithm: str = Field(..., description="Algorithm name used")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological log history")
    metrics: ConfidenceMetrics = Field(..., description="Aggregation telemetry metrics")
