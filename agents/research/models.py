from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RetrievedDocument(BaseModel):
    id: str = Field(..., description="Unique ID for the retrieved document")
    title: str = Field(..., description="Document or paper title")
    authors: Optional[str] = Field(None, description="Author names")
    year: Optional[int] = Field(None, description="Publication year")
    venue: Optional[str] = Field(None, description="Publication venue or journal")
    url: Optional[str] = Field(None, description="URL of the document source")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    content: str = Field(..., description="Raw text snippet or content of the document")
    score: float = Field(0.5, description="Semantic similarity relevance score [0.0 - 1.0]")
    credibility_score: float = Field(0.5, description="Credibility weight score [0.0 - 1.0]")

class ProvenanceRecord(BaseModel):
    claim: str = Field(..., description="Specific factual claim or assertion made in the summary")
    supported_by: List[str] = Field(..., description="List of source document IDs supporting this claim")

class ResearchMetrics(BaseModel):
    retrieval_time: float = Field(0.0, description="Retrieval phase latency in seconds")
    synthesis_time: float = Field(0.0, description="Synthesis phase latency in seconds")
    num_sources: int = Field(0, description="Number of sources processed")
    num_claims: int = Field(0, description="Number of facts extracted")
    num_citations: int = Field(0, description="Number of citations inserted")
    duplicates_removed: int = Field(0, description="Count of duplicate items filtered out")
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"prompt": 0, "completion": 0, "total": 0})

class EvidencePackage(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID context")
    task_id: str = Field(..., description="Task ID context")
    summary: str = Field(..., description="Consolidated research summary of findings")
    key_findings: List[str] = Field(default_factory=list, description="Extracted crucial findings")
    evidence: List[RetrievedDocument] = Field(..., description="Ranked, deduplicated list of source documents")
    provenance: List[ProvenanceRecord] = Field(..., description="List of provenance mappings linking sentences to source IDs")
    metrics: ResearchMetrics = Field(..., description="Execution performance telemetry metrics")
