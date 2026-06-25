import json
import logging
from typing import Dict, Any, List
import litellm

logger = logging.getLogger("trust_framework")

class FailureAttribution:
    """
    Failure Attribution Module.
    Identifies the decisive error step and the agent role responsible for task failure.
    Supports both simulated ground truth extraction and LLM-as-a-judge trace inspection.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def attribute_failure(self, 
                          trajectory: List[Dict[str, Any]], 
                          error_feedback: str, 
                          is_simulation: bool = False) -> Dict[str, Any]:
        """
        Pinpoints the failure-responsible agent and step.
        """
        if is_simulation:
            return self._attribute_failure_simulation(trajectory)
        else:
            return self._attribute_failure_llm(trajectory, error_feedback)

    def _attribute_failure_simulation(self, trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scans the simulated execution trace to find the first step where simulated_success is False.
        This provides perfect failure attribution for benchmarking.
        """
        for step_idx, step in enumerate(trajectory):
            # Check if this step was simulated and failed
            if step.get("simulated", False) and not step.get("simulated_success", True):
                return {
                    "responsible_role": step.get("role", "unknown").lower(),
                    "failure_step": step_idx,
                    "reason": f"Simulated agent failure (hallucination) occurred during subtask execution."
                }
        
        # If no explicit simulated failure was recorded, default to the last active agent before reviewer/verifier
        for step in reversed(trajectory):
            role = step.get("role", "").lower()
            if role not in ["reviewer", "verification", "planner"]:
                return {
                    "responsible_role": role,
                    "failure_step": trajectory.index(step),
                    "reason": f"Fallback attribution to the primary generator agent."
                }
                
        return {
            "responsible_role": "unknown",
            "failure_step": -1,
            "reason": "Could not identify any simulated failure."
        }

    def _attribute_failure_llm(self, trajectory: List[Dict[str, Any]], error_feedback: str) -> Dict[str, Any]:
        """
        Uses an LLM as a judge to trace the decisive error in the trajectory logs.
        """
        # Format the trajectory in a readable form
        formatted_trace = []
        for i, step in enumerate(trajectory):
            formatted_trace.append(
                f"Step {i}: Agent={step.get('agent_name')} (Role={step.get('role')})\n"
                f"Task Description: {step.get('task_description')}\n"
                f"Agent Response: {step.get('response')}\n"
                f"Agent Reasoning: {step.get('reasoning')}\n"
                "----------------------------------------"
            )
            
        trace_str = "\n".join(formatted_trace)
        
        system_prompt = (
            "You are an expert Multi-Agent Failure Attribution Auditor. Your task is to inspect "
            "an execution trace of a collaborative agent workflow and identify which agent and step "
            "was the ROOT CAUSE (decisive error) of the final failure. Ignore downstream errors that "
            "propagated from an upstream mistake—identify the earliest critical error."
        )
        
        user_prompt = (
            f"Execution Trace:\n{trace_str}\n\n"
            f"Final Failure Feedback:\n{error_feedback}\n\n"
            "Analyze the trace step-by-step. Return ONLY a valid JSON object matching this schema:\n"
            "{\n"
            '  "responsible_role": "<role of responsible agent: research/writing/citation/reviewer/verification>",\n'
            '  "failure_step": <integer index of the step where error was introduced>,\n'
            '  "reason": "Clear explanation of why this step caused the failure"\n'
            "}"
        )

        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            return {
                "responsible_role": parsed.get("responsible_role", "unknown").lower(),
                "failure_step": int(parsed.get("failure_step", -1)),
                "reason": parsed.get("reason", "LLM-as-a-judge completed analysis.")
            }
        except Exception as e:
            logger.error(f"Failure Attribution: LLM audit failed: {e}")
            # Default to the writing agent if audit fails
            return {
                "responsible_role": "writing",
                "failure_step": max(0, len(trajectory) - 1),
                "reason": f"Fallback attribution due to audit exception: {str(e)}"
            }
