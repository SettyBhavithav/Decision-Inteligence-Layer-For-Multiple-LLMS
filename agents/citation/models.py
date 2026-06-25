from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CitationPlaceholder(BaseModel):
    key: str = Field(..., description="Placeholder key string (e.g. [CITATION_01])")
    matched_source_id: str = Field(..., description="ID of the matching source document")

class CitationRecord(BaseModel):
    id: str = Field(..., description="Unique paper ID")
    title: str = Field(..., description="Title of the paper")
    authors: Optional[str] = Field(None, description="List of author names")
    year: Optional[int] = Field(None, description="Publication year")
    venue: Optional[str] = Field(None, description="Publication venue")
    url: Optional[str] = Field(None, description="Reference URL")
    doi: Optional[str] = Field(None, description="DOI number")

class BibliographyEntry(BaseModel):
    key: str = Field(..., description="Citation key or index (e.g. [1])")
    formatted_reference: str = Field(..., description="Formatted reference string (IEEE, APA style)")
    source_id: str = Field(..., description="Source ID of the matching paper")

class CitationMetadata(BaseModel):
    style: str = Field("IEEE", description="Formatted citation style")
    total_citations: int = Field(0, description="Total references resolved")
    duplicate_count: int = Field(0, description="Duplicates removed count")
    missing_doi_count: int = Field(0, description="Count of sources missing a valid DOI")
    validation_status: str = Field("valid", description="Verification output state")

class CitationMetrics(BaseModel):
    formatting_time: float = Field(0.0, description="Formatting latency in seconds")
    validation_time: float = Field(0.0, description="Validation latency in seconds")
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"prompt": 0, "completion": 0, "total": 0})

class CitationPackage(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID context")
    citations: List[CitationPlaceholder] = Field(..., description="Resolved placeholders list")
    bibliography: List[BibliographyEntry] = Field(..., description="Compiled bibliography entries")
    metadata: CitationMetadata = Field(..., description="Citation stats metadata")
    metrics: CitationMetrics = Field(..., description="Performance telemetry metrics")
