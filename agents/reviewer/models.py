from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ReviewIssue(BaseModel):
    category: str = Field(..., description="Category of the issue (structure, logic, claim, citation, consistency)")
    severity: str = Field(..., description="Severity level: critical, warning, suggestion")
    description: str = Field(..., description="Detailed issue description")
    location: Optional[str] = Field(None, description="Heading or location where the issue occurred")

class QualityScore(BaseModel):
    structure_score: float = Field(1.0, description="Structure Score [0.0 - 1.0]")
    logic_score: float = Field(1.0, description="Logic Score [0.0 - 1.0]")
    evidence_score: float = Field(1.0, description="Evidence Score [0.0 - 1.0]")
    citation_score: float = Field(1.0, description="Citation Score [0.0 - 1.0]")
    overall_quality: float = Field(1.0, description="Overall Quality Score [0.0 - 1.0]")

class ReviewSuggestion(BaseModel):
    issue_id: Optional[str] = Field(None, description="Reference ID to matching issue")
    suggestion: str = Field(..., description="Actionable suggestion for correcting the issue")
    example: Optional[str] = Field(None, description="Concrete rewritten example text if applicable")

class ReviewMetrics(BaseModel):
    review_time: float = Field(0.0, description="Total review phase latency in seconds")
    issues_count: int = Field(0, description="Total count of issues detected")
    suggestions_count: int = Field(0, description="Total count of suggestions produced")
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"prompt": 0, "completion": 0, "total": 0})

class ReviewPackage(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID context")
    review_status: str = Field("approved", description="Overall review status: approved, revision_needed")
    quality_scores: QualityScore = Field(..., description="Component quality scores")
    issues: List[ReviewIssue] = Field(default_factory=list, description="List of detected review issues")
    suggestions: List[ReviewSuggestion] = Field(default_factory=list, description="List of suggested fixes")
    metrics: ReviewMetrics = Field(..., description="Review latency metrics")
