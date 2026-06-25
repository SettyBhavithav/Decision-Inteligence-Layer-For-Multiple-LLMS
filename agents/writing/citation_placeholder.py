import re
import logging
from typing import List, Dict, Tuple
from agents.writing.models import Placeholder

logger = logging.getLogger("trust_framework")

class CitationPlaceholderManager:
    """Submodule 7: Parses custom citation tokens and replaces them with sequential placeholder keys."""
    def __init__(self):
        # Matches patterns like [[CITATION:paper_01]]
        self.citation_pattern = re.compile(r'\[\[CITATION:([^\]]+)\]\]')

    def manage_placeholders(self, text: str) -> Tuple[str, List[Placeholder]]:
        matches = self.citation_pattern.findall(text)
        
        placeholders = []
        replaced_text = text
        
        # Keep track of mappings to generate unique index keys
        unique_sources = []
        for match in matches:
            source_id = match.strip()
            if source_id not in unique_sources:
                unique_sources.append(source_id)
                
        # Generate placeholders and replace inside text
        for idx, source_id in enumerate(unique_sources):
            key = f"[CITATION_{idx+1:02d}]"
            placeholders.append(Placeholder(key=key, source_id=source_id))
            
            # Replace target citation string in text
            target_pattern = re.compile(r'\[\[CITATION:' + re.escape(source_id) + r'\]\]')
            replaced_text = target_pattern.sub(key, replaced_text)
            
        logger.info(f"CitationPlaceholderManager: Mapped and generated {len(placeholders)} citation placeholders.")
        return replaced_text, placeholders
