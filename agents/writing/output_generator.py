from typing import List, Dict, Any
from agents.writing.models import DraftPackage, Section, Placeholder, WritingMetrics

class OutputGenerator:
    """Submodule 9: Compiles the finalized draft package schema container."""
    def __init__(self):
        pass

    def build_package(self, 
                      workflow_id: str, 
                      draft: str, 
                      sections: List[Section], 
                      placeholders: List[Placeholder], 
                      metrics: WritingMetrics) -> DraftPackage:
                      
        return DraftPackage(
            workflow_id=workflow_id,
            draft=draft,
            sections=sections,
            placeholders=placeholders,
            metrics=metrics
        )
