import json
import logging
from agents.base_agent import client
from agents.planner.prompts import INTENT_PROMPT

logger = logging.getLogger("trust_framework")

class IntentAnalyzer:
    """Submodule 1: Classifies the primary intent of the user query."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def analyze(self, query: str) -> str:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": INTENT_PROMPT},
                    {"role": "user", "content": f"Query to analyze: '{query}'"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            intent = parsed.get("intent", "general").strip().lower()
            logger.info(f"IntentAnalyzer: Classified query intent as: '{intent}'")
            return intent
        except Exception as e:
            logger.error(f"IntentAnalyzer: Classification error: {e}. Falling back to 'general'.")
            return "general"
