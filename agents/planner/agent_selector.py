import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.planner.prompts import SELECTION_PROMPT

logger = logging.getLogger("trust_framework")

class AgentSelector:
    """Submodule 4: Assigns specialized agent roles (research, writing, citation, reviewer, verification) to each subtask."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def select_agents(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not subtasks:
            return []

        # Prepare subtasks as query payload
        payload = [{"id": t["id"], "description": t["description"]} for t in subtasks]
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SELECTION_PROMPT},
                    {"role": "user", "content": f"Select roles for tasks: {json.dumps(payload)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # Map roles back to tasks
            mapped = []
            for t in subtasks:
                t_id = t["id"]
                assigned = parsed.get(t_id, parsed.get("assignments", {}).get(t_id, "writing")).strip().lower()
                
                # Enforce valid role fallback
                if assigned not in ["research", "writing", "citation", "reviewer", "verification"]:
                    assigned = self._fallback_rule_selector(t["description"])
                    
                task_copy = dict(t)
                task_copy["assigned_role"] = assigned
                mapped.append(task_copy)
                
            logger.info("AgentSelector: Finished assigning specialized agent roles.")
            return mapped
        except Exception as e:
            logger.error(f"AgentSelector: Selection error: {e}. Falling back to rule-based selection.")
            return self._fallback_all_subtasks(subtasks)

    def _fallback_rule_selector(self, description: str) -> str:
        desc = description.lower()
        if any(w in desc for w in ["collect", "gather", "search", "retrieve", "evidence", "find", "extract"]):
            return "research"
        elif any(w in desc for w in ["citation", "reference", "bibliography", "cite", "ieee", "apa"]):
            return "citation"
        elif any(w in desc for w in ["verify", "fact-check", "validate", "cross-check", "hallucination"]):
            return "verification"
        elif any(w in desc for w in ["review", "critique", "evaluate", "check", "inconsistency"]):
            return "reviewer"
        return "writing"

    def _fallback_all_subtasks(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        mapped = []
        for t in subtasks:
            task_copy = dict(t)
            task_copy["assigned_role"] = self._fallback_rule_selector(t["description"])
            mapped.append(task_copy)
        return mapped
