import logging
from typing import List, Dict, Any
from agents.writing.models import Section

logger = logging.getLogger("trust_framework")

class SectionPlanner:
    """Submodule 3: Formulates detailed execution parameters for each outline section."""
    def __init__(self):
        pass

    def plan_section(self, section: Section, evidence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Filter evidence matching this section's requirements
        assigned_evidence = []
        for doc in evidence_list:
            doc_id = doc.get("id") if isinstance(doc, dict) else getattr(doc, "id", None)
            if doc_id and doc_id in section.required_evidence:
                assigned_evidence.append(doc)
                
        # If no specific evidence was mapped, assign all as fallback
        if not assigned_evidence:
            assigned_evidence = evidence_list

        logger.debug(f"SectionPlanner: Planned '{section.title}' with {len(assigned_evidence)} source records.")
        return {
            "title": section.title,
            "goal": section.goal,
            "evidence": assigned_evidence,
            "target_length": section.target_length
        }
