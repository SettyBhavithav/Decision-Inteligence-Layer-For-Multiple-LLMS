import logging
from typing import List, Dict, Any

logger = logging.getLogger("trust_framework")

class DuplicateCitationChecker:
    """Submodule 4: Filters out duplicate citations based on source ID or DOI."""
    def __init__(self):
        self.duplicate_count = 0

    def remove_duplicates(self, references: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.duplicate_count = 0
        unique_refs = []
        seen_ids = set()
        seen_dois = set()
        
        for ref in references:
            ref_id = ref.get("id")
            doi = ref.get("doi")
            
            is_dup = False
            if ref_id in seen_ids:
                is_dup = True
            elif doi and doi in seen_dois:
                is_dup = True
                
            if is_dup:
                self.duplicate_count += 1
                logger.debug(f"DuplicateCitationChecker: Filtering duplicate reference: {ref_id}")
            else:
                unique_refs.append(ref)
                seen_ids.add(ref_id)
                if doi:
                    seen_dois.add(doi)
                    
        logger.info(f"DuplicateCitationChecker: Screened references. Retained: {len(unique_refs)} | Duplicates: {self.duplicate_count}")
        return unique_refs
