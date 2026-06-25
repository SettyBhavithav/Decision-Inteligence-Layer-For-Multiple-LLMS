import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from workflows.graph import FrameworkOrchestrator
from evaluation.evaluator import BaselineEvaluator

app = FastAPI(
    title="Confidence-Calibrated Trust-Aware Dynamic Collaboration API",
    description="Backend API for managing trust-aware multi-agent LLM systems.",
    version="1.0.0"
)

# Models
class TaskRequest(BaseModel):
    query: str
    complexity: Optional[str] = "medium"
    use_simulation: Optional[bool] = True

class EvalRequest(BaseModel):
    num_runs: Optional[int] = 10
    research_skill: Optional[float] = 0.85
    writer_skill: Optional[float] = 0.75
    reviewer_skill: Optional[float] = 0.70

# Global instance of orchestrator (defaults to simulation)
orchestrator = FrameworkOrchestrator(use_simulation=True)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "mode": "simulation" if orchestrator.use_simulation else "real"}

@app.post("/api/query")
def submit_query(request: TaskRequest):
    """
    Submits a query to the multi-agent framework.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        # Re-initialize orchestrator if execution mode changes
        global orchestrator
        if orchestrator.use_simulation != request.use_simulation:
            orchestrator = FrameworkOrchestrator(use_simulation=request.use_simulation)
            
        res = orchestrator.run_task(request.query, complexity=request.complexity)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

@app.get("/api/trust")
def get_trust_scores():
    """
    Retrieves current agent trust scores.
    """
    return {
        "trust_scores": orchestrator.trust_engine.get_all_trust_scores(),
        "history": {
            role: orchestrator.trust_engine.get_history(role)
            for role in orchestrator.registry.list_roles()
        }
    }

@app.get("/api/evaluation")
def get_evaluation_metrics():
    """
    Retrieves ECE, Brier, and token statistics from the current session.
    """
    return orchestrator.logger_layer.get_summary()

@app.post("/api/evaluate")
def run_batch_evaluation(request: EvalRequest):
    """
    Triggers a comparative simulation evaluation (Baseline vs Proposed).
    """
    try:
        evaluator = BaselineEvaluator()
        skills = {
            "research": request.research_skill,
            "writing": request.writer_skill,
            "citation": 0.90,
            "reviewer": request.reviewer_skill,
            "verification": 0.95
        }
        res = evaluator.run_comparative_experiment(num_runs=request.num_runs, skills=skills)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
