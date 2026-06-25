import logging
from typing import List
from agents.research.models import RetrievedDocument

logger = logging.getLogger("trust_framework")

class SourceManager:
    """Submodule 3: Normalizes bibliographic citations and validates DOI / URLs."""
    def __init__(self):
        pass

    def normalize_sources(self, documents: List[RetrievedDocument]) -> List[RetrievedDocument]:
        normalized = []
        for doc in documents:
            # Enforce clean titles
            doc.title = doc.title.strip()
            
            # Basic validation check for DOI and URL structure
            if doc.doi and not doc.doi.startswith("10."):
                logger.warning(f"SourceManager: Invalid DOI structure detected for {doc.id}: '{doc.doi}'")
                
            if doc.url and not (doc.url.startswith("http://") or doc.url.startswith("https://")):
                logger.warning(f"SourceManager: Invalid URL structure for {doc.id}: '{doc.url}'")
                
            normalized.append(doc)
            
        logger.info(f"SourceManager: Normalized {len(normalized)} document source fields.")
        return normalized
