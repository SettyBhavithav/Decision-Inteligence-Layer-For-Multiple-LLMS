from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CommunicationNode(BaseModel):
    agent_id: str = Field(..., description="Unique collaborator agent role ID")
    active: bool = Field(True, description="Active connection state status")

class CommunicationEdge(BaseModel):
    source: str = Field(..., description="Source agent node ID")
    target: str = Field(..., description="Target agent node ID")
    weight: float = Field(1.0, description="Connection strength probability rating")

class CommunicationRoute(BaseModel):
    route_id: str = Field(..., description="Route unique ID")
    path: List[str] = Field(..., description="Sequence path of agent nodes")
    efficiency: float = Field(1.0, description="Routing path efficiency rating [0.0 - 1.0]")

class CommunicationMetrics(BaseModel):
    total_messages: int = Field(0, description="Count of total message events")
    filtered_messages: int = Field(0, description="Count of filtered duplicate updates")
    average_payload_size: float = Field(0.0, description="Average message size in bytes")
    communication_latency: float = Field(0.0, description="Accumulated transaction speed duration")
    token_consumption: int = Field(0, description="Accumulated token count")
    graph_density: float = Field(0.0, description="Connection graph density rating")

class CommunicationPackage(BaseModel):
    workflow_id: str = Field(..., description="Workflow execution ID context")
    route: List[str] = Field(..., description="Calculated routing path sequence")
    strategy: str = Field(..., description="Active communication strategy name")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="List of messages exchanged")
    metrics: CommunicationMetrics = Field(..., description="Aggregate execution speed metrics")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological log history")
