from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Section(BaseModel):
    title: str = Field(..., description="Title of the section")
    goal: str = Field(..., description="Writing objective of this section")
    required_evidence: List[str] = Field(default_factory=list, description="IDs of documents supporting this section")
    target_length: int = Field(200, description="Target word count for the section")

class Placeholder(BaseModel):
    key: str = Field(..., description="Placeholder anchor key (e.g. [CITATION_01])")
    source_id: str = Field(..., description="ID of the matching source document")

class WritingMetrics(BaseModel):
    generation_time: float = Field(0.0, description="Draft generation latency in seconds")
    sections_count: int = Field(0, description="Number of sections generated")
    word_count: int = Field(0, description="Total word count generated")
    placeholder_count: int = Field(0, description="Number of citation placeholders inserted")
    validation_failures: int = Field(0, description="Count of validation loops executed")
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"prompt": 0, "completion": 0, "total": 0})

class DraftPackage(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID context")
    draft: str = Field(..., description="Full compiled draft text (Markdown format)")
    sections: List[Section] = Field(..., description="Decomposed list of section models")
    placeholders: List[Placeholder] = Field(..., description="Standardized citation placeholders map")
    metrics: WritingMetrics = Field(..., description="Execution performance telemetry metrics")
