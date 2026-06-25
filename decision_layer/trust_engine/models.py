from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentTrust(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier (e.g. research, writing)")
    trust_score: float = Field(0.80, description="Current trust rating in range [0.0 - 1.0]")
    success_count: int = Field(0, description="Number of task executions passing verification")
    failure_count: int = Field(0, description="Number of task executions failing verification")

class TrustUpdate(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    previous_trust: float = Field(..., description="Trust score before update")
    updated_trust: float = Field(..., description="Trust score after update")
    change: str = Field(..., description="String sign representation of change (e.g. +0.05, -0.10)")
    reason: str = Field(..., description="Text justification for the change")
    timestamp: str = Field(..., description="ISO formatting timestamp")

class TrustHistory(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    history: List[TrustUpdate] = Field(default_factory=list, description="List of previous updates")

class TrustMetrics(BaseModel):
    current_trust: float = Field(0.80, description="Current trust score value")
    trust_change: float = Field(0.0, description="Last update change amount")
    average_trust: float = Field(0.80, description="Running historical average trust score")
    failed_updates: int = Field(0, description="Count of invalid updates blocked")
    update_time: float = Field(0.0, description="Last calculation latency in seconds")

class TrustPackage(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    trust_score: float = Field(..., description="Current trust score")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological log history")
    metrics: TrustMetrics = Field(..., description="Aggregation telemetry metrics")
