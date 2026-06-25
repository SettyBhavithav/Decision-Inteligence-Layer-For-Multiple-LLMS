from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ClaimRecord(BaseModel):
    claim_id: int = Field(..., description="Unique claim index")
    claim: str = Field(..., description="Factual claim sentence extracted from text")
    paragraph: int = Field(0, description="Paragraph index position")

class EvidenceMatch(BaseModel):
    claim: str = Field(..., description="Extracted claim text")
    supporting_sources: List[str] = Field(default_factory=list, description="Matched supporting reference IDs")

class VerificationScore(BaseModel):
    claim_accuracy: float = Field(1.0, description="Claim accuracy score [0.0 - 1.0]")
    citation_accuracy: float = Field(1.0, description="Citation accuracy score [0.0 - 1.0]")
    evidence_coverage: float = Field(1.0, description="Evidence coverage score [0.0 - 1.0]")
    hallucination_risk: float = Field(0.0, description="Hallucination risk probability [0.0 - 1.0]")
    overall_verification: float = Field(1.0, description="Overall verification score [0.0 - 1.0]")

class VerificationIssue(BaseModel):
    claim_id: Optional[int] = Field(None, description="Index of associated claim")
    description: str = Field(..., description="Factual error description")
    severity: str = Field(..., description="Severity level: critical, warning")

class VerificationMetrics(BaseModel):
    claims_verified: int = Field(0, description="Count of claims audited")
    hallucinations_detected: int = Field(0, description="Count of hallucinated claims caught")
    verification_latency: float = Field(0.0, description="Latency in seconds")
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"prompt": 0, "completion": 0, "total": 0})

class VerificationPackage(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID context")
    verified: bool = Field(True, description="Verification validation status (True/False)")
    scores: VerificationScore = Field(..., description="Factual correctness scores")
    issues: List[VerificationIssue] = Field(default_factory=list, description="Factual errors or missing evidence list")
    verified_claims: List[ClaimRecord] = Field(default_factory=list, description="Audited claims index list")
    metrics: VerificationMetrics = Field(..., description="Verification speed and token telemetry")
