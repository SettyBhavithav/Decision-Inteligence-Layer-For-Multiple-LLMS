import logging
from typing import List, Dict, Any
from agents.verification.models import VerificationIssue

logger = logging.getLogger("trust_framework")

class CitationVerifier:
    """Submodule 5: Verifies citation alignments and flags missing references."""
    def __init__(self):
        pass

    def verify_citations(self, text: str, bibliography: List[Dict[str, Any]]) -> List[VerificationIssue]:
        issues = []
        # Basic check to see if each citation number used in the text appears in the bibliography
        import re
        citation_indices = re.findall(r'\[(\d+)\]', text)
        
        seen_keys = {entry.get("key") if isinstance(entry, dict) else getattr(entry, "key", "") 
                     for entry in bibliography}
                     
        for idx in set(citation_indices):
            key = f"[{idx}]"
            # Exclude standard headers or formatting items
            if key not in seen_keys:
                issues.append(VerificationIssue(
                    description=f"In-text citation '{key}' has no matching reference entry in bibliography.",
                    severity="critical"
                ))
                
        logger.info(f"CitationVerifier: Checked in-text citations. Found {len(issues)} discrepancy issues.")
        return issues
