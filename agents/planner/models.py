from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SubtaskSpec(BaseModel):
    id: str = Field(..., description="Unique subtask identifier (e.g. task_0, task_1)")
    description: str = Field(..., description="Actionable description of the subtask")
    assigned_role: str = Field(..., description="Assigned agent role (research, writing, citation, reviewer, verification)")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this subtask depends on")

class ExecutionPlan(BaseModel):
    workflow_id: str = Field(..., description="Unique UUID for this workflow execution")
    intent: str = Field(..., description="Classified intent of the user query")
    tasks: List[SubtaskSpec] = Field(..., description="List of decomposed subtasks in topological sequence")
