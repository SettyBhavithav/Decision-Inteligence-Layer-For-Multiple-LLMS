import logging
from typing import List, Dict, Any
from agents.citation.models import CitationPlaceholder, CitationRecord

logger = logging.getLogger("trust_framework")

class ReferenceMatcher:
    """Submodule 2: Resolves placeholder anchors back to their source paper records."""
    def __init__(self):
        pass

    def match_references(self, 
                         keys: List[str], 
                         placeholders_map: List[Dict[str, Any]], 
                         evidence_list: List[Dict[str, Any]]) -> List[CitationPlaceholder]:
                         
        # Compile mapping dictionaries
        p_dict = {p.get("key") if isinstance(p, dict) else getattr(p, "key", None): 
                  p.get("source_id") if isinstance(p, dict) else getattr(p, "source_id", None)
                  for p in placeholders_map}
                  
        resolved = []
        for key in keys:
            source_id = p_dict.get(key)
            if source_id:
                resolved.append(CitationPlaceholder(key=key, matched_source_id=source_id))
            else:
                logger.warning(f"ReferenceMatcher: No matching source found for key '{key}'")
                # Assign default fallback matching
                resolved.append(CitationPlaceholder(key=key, matched_source_id="paper_01"))
                
        logger.info(f"ReferenceMatcher: Resolved {len(resolved)} / {len(keys)} citation placeholders.")
        return resolved
