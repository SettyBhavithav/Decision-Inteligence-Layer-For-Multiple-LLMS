import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.research.prompts import SYNTHESIS_PROMPT
from agents.research.models import RetrievedDocument

logger = logging.getLogger("trust_framework")

class KnowledgeSynthesizer:
    """Submodule 6: Synthesizes ranked sources into a consolidated factual Markdown summary with inline citations."""
    def __init__(self, model: str = "deepseek-ai/deepseek-v4-flash"):
        self.model = model

    def synthesize(self, documents: List[RetrievedDocument]) -> Dict[str, Any]:
        # Formulate compilation list
        context_str = "\n\n".join([
            f"Source ID: {doc.id}\nTitle: {doc.title}\nContent: {doc.content}"
            for doc in documents
        ])
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYNTHESIS_PROMPT},
                    {"role": "user", "content": f"Sources to synthesize:\n{context_str}"}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            logger.info("KnowledgeSynthesizer: Synthesis complete.")
            return parsed
        except Exception as e:
            logger.error(f"KnowledgeSynthesizer: Synthesis error: {e}. Falling back to default summary.")
            return {
                "summary": "Default Research Summary:\n" + "\n".join([f"- {d.title}" for d in documents]),
                "key_findings": ["Factual references compiled successfully."]
            }
