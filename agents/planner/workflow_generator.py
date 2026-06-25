import uuid
from typing import List, Dict, Any

class WorkflowGenerator:
    """Submodule 5: Compiles the final execution plan dictionary with a unique workflow execution UUID."""
    def __init__(self):
        pass

    def generate_plan(self, intent: str, subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        workflow_id = f"wf_{uuid.uuid4()}"
        
        # Standardize task specs
        tasks_list = []
        for t in subtasks:
            tasks_list.append({
                "id": t["id"],
                "description": t["description"],
                "assigned_role": t.get("assigned_role", "writing"),
                "dependencies": t.get("dependencies", [])
            })
            
        return {
            "workflow_id": workflow_id,
            "intent": intent,
            "tasks": tasks_list
        }
