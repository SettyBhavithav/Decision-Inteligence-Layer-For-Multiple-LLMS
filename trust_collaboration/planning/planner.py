import json
import logging
from typing import Dict, Any, List
import litellm

logger = logging.getLogger("trust_framework")

class PlannerAgent:
    """
    Decomposes user queries into a list of structured subtasks with dependencies and assigned roles.
    """
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2):
        self.model = model
        self.temperature = temperature
        self.use_simulation: bool = False

    def decompose(self, query: str) -> List[Dict[str, Any]]:
        """
        Decompose a query into a structured execution plan.
        Each subtask:
            {
                "id": str,
                "description": str,
                "assigned_role": str (research/writing/citation/reviewer/verification),
                "dependencies": List[str]
            }
        """
        if self.use_simulation:
            return self._decompose_simulation(query)
            
        system_prompt = (
            "You are a specialized Planner Agent. Your job is to analyze a user query and decompose "
            "it into a logical sequence of subtasks. Assign each subtask to a specialized agent role:\n"
            "- 'research': for gathering facts and evidence\n"
            "- 'writing': for creating reports, code, or synthesis\n"
            "- 'citation': for adding references and formatting bibliography\n"
            "- 'reviewer': for checking consistency and identifying errors\n"
            "- 'verification': for cross-checking uncertain facts\n\n"
            "Map dependencies carefully so that downstream tasks reference the outputs of upstream tasks."
        )
        
        user_prompt = (
            f"Query: {query}\n\n"
            "Decompose this query into subtasks. Return ONLY a valid JSON array of objects, where each object has:\n"
            '- "id": unique string identifier (e.g. "task_0", "task_1")\n'
            '- "description": description of the subtask\n'
            '- "assigned_role": agent role name (research, writing, citation, reviewer, verification)\n'
            '- "dependencies": list of task IDs this task depends on (e.g. ["task_0"])\n'
        )

        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # If the response is a dictionary with a subtasks key, unpack it
            if isinstance(parsed, dict) and "subtasks" in parsed:
                return parsed["subtasks"]
            elif isinstance(parsed, dict) and "tasks" in parsed:
                return parsed["tasks"]
            elif isinstance(parsed, list):
                return parsed
            else:
                # If parsed is a dictionary without a direct array, wrap it if possible or use default
                if isinstance(parsed, dict):
                    # check if any value is a list
                    for k, v in parsed.items():
                        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                            return v
                raise ValueError("Could not parse subtask list from JSON.")
        except Exception as e:
            logger.error(f"Planner decomposition error: {e}. Falling back to default plan.")
            return self._decompose_simulation(query)

    def _decompose_simulation(self, query: str) -> List[Dict[str, Any]]:
        """
        Generate a default structured plan for simulation mode.
        """
        return [
            {
                "id": "task_0",
                "description": f"Gather research data and relevant evidence for: '{query}'",
                "assigned_role": "research",
                "dependencies": []
            },
            {
                "id": "task_1",
                "description": f"Draft the report and compile research findings for: '{query}'",
                "assigned_role": "writing",
                "dependencies": ["task_0"]
            },
            {
                "id": "task_2",
                "description": "Cross-check details and format bibliography in IEEE style.",
                "assigned_role": "citation",
                "dependencies": ["task_1"]
            },
            {
                "id": "task_3",
                "description": "Conduct a critical review, check for logical consistency and accuracy.",
                "assigned_role": "reviewer",
                "dependencies": ["task_2"]
            }
        ]
