import logging
from typing import List
from agents.research.models import RetrievedDocument

logger = logging.getLogger("trust_framework")

class DuplicateRemoval:
    """Submodule 5: Removes duplicate documents or overlapping paragraph strings."""
    def __init__(self, jaccard_threshold: float = 0.75):
        self.jaccard_threshold = jaccard_threshold
        self.removed_count = 0

    def remove_duplicates(self, documents: List[RetrievedDocument]) -> List[RetrievedDocument]:
        self.removed_count = 0
        unique_docs = []
        
        for doc in documents:
            is_dup = False
            for u_doc in unique_docs:
                if self._compute_jaccard(doc.content, u_doc.content) > self.jaccard_threshold:
                    is_dup = True
                    self.removed_count += 1
                    logger.debug(f"DuplicateRemoval: Filtering redundant document {doc.id} (matches {u_doc.id})")
                    break
            if not is_dup:
                unique_docs.append(doc)
                
        logger.info(f"DuplicateRemoval: Deduplicated documents. Retained: {len(unique_docs)} | Removed: {self.removed_count}")
        return unique_docs

    def _compute_jaccard(self, text_a: str, text_b: str) -> float:
        set_a = set(text_a.lower().split())
        set_b = set(text_b.lower().split())
        if not set_a or not set_b:
            return 0.0
        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        return len(intersection) / len(union)
