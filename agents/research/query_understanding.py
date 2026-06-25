import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from agents.research.prompts import QUERY_UNDERSTANDING_PROMPT

logger = logging.getLogger("trust_framework")

class QueryUnderstanding:
    """Submodule 1: Parses subtask description and user query into search parameters."""
    def __init__(self, model: str = "deepseek-ai/deepseek-v4-flash"):
        self.model = model

    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": QUERY_UNDERSTANDING_PROMPT},
                    {"role": "user", "content": f"Task description to parse: '{task_description}'"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            logger.info(f"QueryUnderstanding: Extracted search keywords: {parsed.get('keywords', [])}")
            return parsed
        except Exception as e:
            logger.error(f"QueryUnderstanding: Error parsing query: {e}. Falling back to default.")
            return {
                "intent": "general",
                "keywords": [task_description[:50]],
                "domain": "general",
                "expected_output": "evidence summary"
            }
