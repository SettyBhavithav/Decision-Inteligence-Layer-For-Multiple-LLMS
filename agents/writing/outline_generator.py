import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.writing.prompts import OUTLINE_PROMPT
from agents.writing.models import Section

logger = logging.getLogger("trust_framework")

class OutlineGenerator:
    """Submodule 2: Generates a structured outline plan (sections) based on task intent and evidence."""
    def __init__(self, model: str = "stepfun-ai/step-3.7-flash"):
        self.model = model

    def generate_outline(self, summary_context: str) -> List[Section]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": OUTLINE_PROMPT},
                    {"role": "user", "content": f"Factual summary context:\n{summary_context}"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            sections = []
            for s in parsed.get("sections", []):
                sections.append(Section(
                    title=s.get("title", "Untitled Section"),
                    goal=s.get("goal", "Outline objectives."),
                    required_evidence=s.get("required_evidence", []),
                    target_length=int(s.get("target_length", 150))
                ))
            logger.info(f"OutlineGenerator: Created outline with {len(sections)} sections.")
            return sections
        except Exception as e:
            logger.error(f"OutlineGenerator: Generation error: {e}. Falling back to default outline.")
            return [
                Section(title="1. Introduction", goal="Introduce the core topic.", target_length=150),
                Section(title="2. Analysis", goal="Analyze the evidence.", target_length=200),
                Section(title="3. Conclusion", goal="Summarize findings.", target_length=100)
            ]
