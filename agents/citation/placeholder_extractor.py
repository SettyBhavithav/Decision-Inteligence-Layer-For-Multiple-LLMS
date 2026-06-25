import re
import logging
from typing import List

logger = logging.getLogger("trust_framework")

class PlaceholderExtractor:
    """Submodule 1: Scans draft text and extracts citation placeholder tags."""
    def __init__(self):
        # Matches patterns like [CITATION_01]
        self.pattern = re.compile(r'\[CITATION_(\d+)\]')

    def extract_placeholders(self, text: str) -> List[str]:
        if not text:
            return []
        matches = self.pattern.findall(text)
        # Map back to full placeholder keys
        keys = [f"[CITATION_{m}]" for m in matches]
        # De-duplicate while preserving order
        unique_keys = []
        for k in keys:
            if k not in unique_keys:
                unique_keys.append(k)
        logger.info(f"PlaceholderExtractor: Extracted {len(unique_keys)} citation placeholders.")
        return unique_keys
