import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from agents.writing.prompts import DRAFT_PROMPT

logger = logging.getLogger("trust_framework")

class DraftGenerator:
    """Submodule 4: Writes draft text for a planned section, incorporating evidence and citations."""
    def __init__(self, model: str = "stepfun-ai/step-3.7-flash"):
        self.model = model

    def generate_draft(self, section_plan: Dict[str, Any]) -> str:
        title = section_plan["title"]
        goal = section_plan["goal"]
        
        # Format evidence list
        evidence_snippets = []
        for doc in section_plan["evidence"]:
            doc_id = doc.get("id") if isinstance(doc, dict) else getattr(doc, "id", None)
            content = doc.get("content") if isinstance(doc, dict) else getattr(doc, "content", "")
            evidence_snippets.append(f"[{doc_id}]: {content}")
            
        evidence_str = "\n\n".join(evidence_snippets)
        
        user_prompt = (
            f"Section Title: {title}\n"
            f"Writing Goal: {goal}\n"
            f"Target Length: {section_plan['target_length']} words\n\n"
            f"Factual Evidence Snippets to use:\n{evidence_str}"
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DRAFT_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            draft_text = parsed.get("draft", "").strip()
            logger.info(f"DraftGenerator: Successfully generated draft for '{title}' ({len(draft_text.split())} words).")
            return f"## {title}\n\n{draft_text}\n"
        except Exception as e:
            logger.error(f"DraftGenerator: Draft generation error for '{title}': {e}")
            return f"## {title}\n\n[Generation failed due to exception: {str(e)}]\n"
