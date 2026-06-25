import logging
from typing import Dict, Any

logger = logging.getLogger("trust_framework")

class DocumentLoader:
    """Submodule 1: Loads and normalizes drafts, citations, and evidence collections."""
    def __init__(self):
        pass

    def load_document(self, draft_package: Dict[str, Any], citation_package: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            "draft": draft_package.get("draft", ""),
            "sections": draft_package.get("sections", []),
            "citations": citation_package.get("citations", []),
            "bibliography": citation_package.get("bibliography", []),
            "workflow_id": draft_package.get("workflow_id", "wf_global")
        }
        logger.info(f"DocumentLoader: Loaded document containing {len(normalized['sections'])} sections and {len(normalized['bibliography'])} citations.")
        return normalized
