import logging
from typing import List
from agents.research.models import RetrievedDocument

logger = logging.getLogger("trust_framework")

class EvidenceRanker:
    """Submodule 4: Ranks documents based on semantic scores, credibility weightings, and publication recency."""
    def __init__(self, w_semantic: float = 0.5, w_credibility: float = 0.3, w_recency: float = 0.2):
        self.w_semantic = w_semantic
        self.w_credibility = w_credibility
        self.w_recency = w_recency

    def rank(self, documents: List[RetrievedDocument]) -> List[RetrievedDocument]:
        if not documents:
            return []

        # Find current year for recency math
        current_year = 2026
        
        ranked_docs = []
        for doc in documents:
            # Recency calculations (linear decay back to 2000)
            doc_year = doc.year if doc.year else 2015
            recency_score = max(0.0, 1.0 - ((current_year - doc_year) / 30.0))
            
            # Composite formula
            composite = (
                self.w_semantic * doc.score +
                self.w_credibility * doc.credibility_score +
                self.w_recency * recency_score
            )
            
            # Assign sorting metric
            doc.score = composite
            ranked_docs.append(doc)
            
        # Sort in descending order of composite score
        ranked_docs.sort(key=lambda d: d.score, reverse=True)
        
        logger.info(f"EvidenceRanker: Ranked {len(ranked_docs)} sources. Top: {ranked_docs[0].id} (Score: {ranked_docs[0].score:.3f})")
        return ranked_docs
