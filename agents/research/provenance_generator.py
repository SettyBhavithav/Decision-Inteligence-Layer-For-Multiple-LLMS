import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.research.prompts import PROVENANCE_PROMPT
from agents.research.models import ProvenanceRecord

logger = logging.getLogger("trust_framework")

class ProvenanceGenerator:
    """Submodule 8: Links generated sentences/claims to supporting source document IDs for explainability."""
    def __init__(self, model: str = "deepseek-ai/deepseek-v4-flash"):
        self.model = model

    def generate_provenance(self, summary: str, source_ids: List[str]) -> List[ProvenanceRecord]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PROVENANCE_PROMPT},
                    {"role": "user", "content": f"Summary text:\n{summary}\n\nAllowed Source IDs: {source_ids}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            records = []
            for item in parsed.get("provenance", []):
                claim = item.get("claim", "")
                supported_by = item.get("supported_by", [])
                
                # Filter out unauthorized/hallucinated source IDs
                valid_sources = [sid for sid in supported_by if sid in source_ids]
                
                if claim and valid_sources:
                    records.append(ProvenanceRecord(claim=claim, supported_by=valid_sources))
                    
            logger.info(f"ProvenanceGenerator: Logged {len(records)} provenance records.")
            return records
        except Exception as e:
            logger.error(f"ProvenanceGenerator: Generation error: {e}. Generating default record.")
            # Fallback mapping the entire summary to the first source
            if source_ids:
                return [ProvenanceRecord(claim=summary[:100] + "...", supported_by=[source_ids[0]])]
            return []
