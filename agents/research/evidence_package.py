from typing import List, Dict, Any
from agents.research.models import EvidencePackage, RetrievedDocument, ProvenanceRecord, ResearchMetrics

class EvidencePackageGenerator:
    """Submodule 9: Compiles the final verified structured Evidence Package."""
    def __init__(self):
        pass

    def build_package(self, 
                      workflow_id: str, 
                      task_id: str, 
                      summary: str, 
                      key_findings: List[str], 
                      evidence: List[RetrievedDocument], 
                      provenance: List[ProvenanceRecord], 
                      metrics: ResearchMetrics) -> EvidencePackage:
                      
        return EvidencePackage(
            workflow_id=workflow_id,
            task_id=task_id,
            summary=summary,
            key_findings=key_findings,
            evidence=evidence,
            provenance=provenance,
            metrics=metrics
        )
