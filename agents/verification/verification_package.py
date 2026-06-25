from typing import List
from agents.verification.models import VerificationPackage, VerificationScore, VerificationIssue, ClaimRecord, VerificationMetrics

class VerificationPackageGenerator:
    """Submodule 9: Compiles the completed verified Verification Package container."""
    def __init__(self):
        pass

    def build_package(self, 
                      workflow_id: str, 
                      verified: bool, 
                      score: VerificationScore, 
                      issues: List[VerificationIssue], 
                      verified_claims: List[ClaimRecord], 
                      metrics: VerificationMetrics) -> VerificationPackage:
                      
        return VerificationPackage(
            workflow_id=workflow_id,
            verified=verified,
            scores=score,
            issues=issues,
            verified_claims=verified_claims,
            metrics=metrics
        )
