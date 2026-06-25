import logging
from typing import Dict

logger = logging.getLogger("trust_framework")

class DOIValidator:
    """Submodule 3: Validates DOI formats and tracks missing/invalid items."""
    def __init__(self):
        pass

    def validate_doi(self, doi: str) -> Dict[str, str]:
        if not doi:
            return {"status": "missing", "reason": "No DOI value provided."}
            
        doi_clean = doi.strip()
        # DOIs must begin with "10."
        if doi_clean.startswith("10."):
            return {"status": "valid", "doi": doi_clean}
            
        logger.warning(f"DOIValidator: Invalid DOI format detected: '{doi}'")
        return {"status": "invalid", "reason": "DOI must begin with 10."}
