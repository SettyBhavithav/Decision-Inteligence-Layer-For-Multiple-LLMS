import logging
from typing import List, Dict, Any
from agents.citation.models import BibliographyEntry, CitationPlaceholder
from agents.citation.citation_formatter import CitationFormatter

logger = logging.getLogger("trust_framework")

class BibliographyGenerator:
    """Submodule 6: Compiles bibliography lists in sorted order."""
    def __init__(self):
        self.formatter = CitationFormatter()

    def generate_bibliography(self, 
                             resolved: List[CitationPlaceholder], 
                             evidence_list: List[Dict[str, Any]], 
                             style: str = "IEEE") -> List[BibliographyEntry]:
                             
        e_dict = {doc.get("id") if isinstance(doc, dict) else getattr(doc, "id", None): doc 
                  for doc in evidence_list}
                  
        bibliography = []
        
        # Enforce chronological sequence of appearance
        seen_sources = []
        for idx, item in enumerate(resolved):
            source_id = item.matched_source_id
            
            # Match metadata
            paper = e_dict.get(source_id)
            if not paper:
                paper = {"id": source_id, "title": "External Citation", "year": 2026}
                
            # If paper is a Pydantic model (RetrievedDocument), cast to dict
            if hasattr(paper, "dict"):
                paper = paper.dict()
                
            # Formatting index key
            key = f"[{idx + 1}]"
            
            # Format text
            formatted = self.formatter.format_citation(paper, idx + 1, style)
            
            bibliography.append(BibliographyEntry(
                key=key,
                formatted_reference=formatted,
                source_id=source_id
            ))
            
        logger.info(f"BibliographyGenerator: Generated {len(bibliography)} bibliography entries.")
        return bibliography
