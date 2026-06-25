import logging
from typing import Dict, Any

logger = logging.getLogger("trust_framework")

class ContextLoader:
    """Submodule 1: Loads and normalizes incoming Evidence Packages for drafting context."""
    def __init__(self):
        pass

    def load_context(self, evidence_package: Dict[str, Any]) -> Dict[str, Any]:
        if not evidence_package:
            logger.warning("ContextLoader: Received empty evidence package!")
            return {"summary": "", "evidence": [], "workflow_id": "wf_none", "task_id": "task_none"}
            
        normalized = {
            "summary": evidence_package.get("summary", ""),
            "evidence": evidence_package.get("evidence", []),
            "workflow_id": evidence_package.get("workflow_id", "wf_global"),
            "task_id": evidence_package.get("task_id", "task_0")
        }
        logger.info(f"ContextLoader: Normalized evidence package containing {len(normalized['evidence'])} references.")
        return normalized
