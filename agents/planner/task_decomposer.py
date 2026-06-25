import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.planner.prompts import DECOMPOSITION_PROMPT

logger = logging.getLogger("trust_framework")

class TaskDecomposer:
    """Submodule 2: Decomposes the user query into structured subtasks with ID tags and dependency anchors."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def decompose(self, query: str) -> List[Dict[str, Any]]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DECOMPOSITION_PROMPT},
                    {"role": "user", "content": f"Decompose query: '{query}'"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            subtasks = parsed.get("subtasks", [])
            logger.info(f"TaskDecomposer: Decomposed query into {len(subtasks)} subtasks.")
            return subtasks
        except Exception as e:
            logger.error(f"TaskDecomposer: Decomposition error: {e}. Returning empty list.")
            return []
