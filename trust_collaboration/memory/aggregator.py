import logging
from typing import Dict, Any, List
import litellm

logger = logging.getLogger("trust_framework")

class ResponseAggregator:
    """
    Response Aggregation Layer (Layer 8).
    Combines agent outputs, resolves differences, and compiles the final user response.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.use_simulation: bool = False

    def aggregate(self, 
                  query: str, 
                  trajectory: List[Dict[str, Any]], 
                  trust_engine_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Synthesize the final response.
        In simulation mode, compiles the results using structured formatting.
        In real mode, uses the LLM to write a clean report using facts from the trajectory.
        """
        if self.use_simulation:
            return self._aggregate_simulation(query, trajectory, trust_engine_scores)
            
        # Format facts gathered along the trajectory
        facts_summary = []
        for step in trajectory:
            role = step.get("role", "unknown")
            resp = step.get("response", "")
            facts_summary.append(f"[{role.upper()}]: {resp}")
            
        facts_str = "\n\n".join(facts_summary)
        
        system_prompt = (
            "You are a specialized Response Aggregator. Your task is to compile a single, coherent, "
            "comprehensive final response to a user query, synthesizing all inputs, code, citation, "
            "and review text generated during the multi-agent execution pipeline. Ensure all parts "
            "flow logically and citations are integrated."
        )
        
        user_prompt = (
            f"User Original Query: {query}\n\n"
            f"Generated Agent Context:\n{facts_str}\n\n"
            "Generate the final publication-ready report. Ensure citations are formatted."
        )

        try:
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            final_text = response.choices[0].message.content
        except Exception as e:
            logger.error(f"Response Aggregator: LLM synthesis failed: {e}. Falling back to template synthesis.")
            final_text = "\n\n".join([step.get("response", "") for step in trajectory if step.get("role") in ["writing", "citation"]])
            
        # Calculate stats for transparency
        avg_confidence = sum(s.get("calibrated_conf", 0.0) for s in trajectory) / max(1, len(trajectory))
        
        return {
            "query": query,
            "response": final_text,
            "average_confidence": avg_confidence,
            "agent_trust_scores": trust_engine_scores,
            "trajectory_steps": len(trajectory)
        }

    def _aggregate_simulation(self, 
                              query: str, 
                              trajectory: List[Dict[str, Any]], 
                              trust_engine_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Concatenate simulated responses with metrics for execution output.
        """
        sections = [f"# Final Report: {query}\n"]
        
        for step in trajectory:
            role = step.get("role", "unknown").capitalize()
            resp = step.get("response", "")
            conf = step.get("calibrated_conf", 0.0)
            sections.append(f"## {role} Output (Calibrated Confidence: {conf:.2f})\n{resp}\n")
            
        final_text = "\n".join(sections)
        avg_confidence = sum(s.get("calibrated_conf", 0.0) for s in trajectory) / max(1, len(trajectory))
        
        return {
            "query": query,
            "response": final_text,
            "average_confidence": avg_confidence,
            "agent_trust_scores": trust_engine_scores,
            "trajectory_steps": len(trajectory)
        }
