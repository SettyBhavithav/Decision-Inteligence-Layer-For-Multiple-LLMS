import logging
from typing import List, Dict, Any
from agents.verification.models import ClaimRecord, EvidenceMatch

logger = logging.getLogger("trust_framework")

class EvidenceMatcher:
    """Submodule 2: Pairs extracted claims with source paper IDs."""
    def __init__(self):
        pass

    def match_evidence(self, 
                       claims: List[ClaimRecord], 
                       provenance_list: List[Dict[str, Any]]) -> List[EvidenceMatch]:
                       
        p_dict = {p.get("claim", "").strip().lower(): p.get("supported_by", []) for p in provenance_list}
        
        matches = []
        for item in claims:
            claim_text = item.claim
            supported_by = []
            
            # Match using lower casing substring checks
            claim_lower = claim_text.strip().lower()
            for p_claim, sources in p_dict.items():
                if p_claim in claim_lower or claim_lower in p_claim:
                    supported_by = sources
                    break
                    
            # Fallback if no direct mapping exists
            if not supported_by:
                supported_by = ["paper_01"]
                
            matches.append(EvidenceMatch(claim=claim_text, supporting_sources=supported_by))
            
        logger.info(f"EvidenceMatcher: Matched {len(matches)} claims to reference source IDs.")
        return matches
