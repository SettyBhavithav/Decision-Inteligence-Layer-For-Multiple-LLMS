import abc
import json
import logging
from typing import Dict, Any, List
import litellm

logger = logging.getLogger("trust_framework")

class BaseAgent(abc.ABC):
    """
    Abstract base class for all agents in the framework, supporting both
    real LLM execution (via LiteLLM) and synthetic simulation execution.
    """
    def __init__(self, name: str, role: str, model: str = "gpt-4o-mini", temperature: float = 0.7):
        self.name = name
        self.role = role
        self.model = model
        self.temperature = temperature
        
        # Simulation parameters
        self.use_simulation: bool = False
        self.true_success_rate: float = 0.8  # Prob. that the agent's answer is correct in simulation
        self.calibration_bias: float = 0.0   # Bias added to simulated self-confidence (over/underconfidence)

    @abc.abstractmethod
    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a subtask given context.
        Returns:
            Dict containing:
                - "response": The text output
                - "confidence": Self-reported raw confidence score [0.0 - 1.0]
                - "reasoning": Reasoning trace explaining the output
        """
        pass

    def _execute_llm(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Helper method to call real LLM via LiteLLM and parse JSON response.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # We append a instruction requesting JSON formatting
        json_instruction = (
            "\n\nYou MUST respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "response": "Your actual answer content here",\n'
            '  "confidence": <float between 0.0 and 1.0 indicating your confidence in correctness>,\n'
            '  "reasoning": "Brief explanation of how you reached this answer and confidence"\n'
            "}"
        )
        messages[-1]["content"] += json_instruction

        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # Ensure required keys exist
            return {
                "response": parsed.get("response", ""),
                "confidence": float(parsed.get("confidence", 0.5)),
                "reasoning": parsed.get("reasoning", ""),
                "simulated": False
            }
        except Exception as e:
            logger.error(f"Error executing LLM call for agent {self.name}: {e}")
            # Return a default fallback
            return {
                "response": f"Failed to execute agent {self.name} due to: {str(e)}",
                "confidence": 0.1,
                "reasoning": f"Exception raised: {str(e)}",
                "simulated": False
            }

    def _execute_simulation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to simulate agent output deterministically based on agent performance metrics.
        """
        import random
        # Determine success
        is_success = random.random() < self.true_success_rate
        
        # Confidence logic:
        # If success, confidence tends to be high (e.g. 0.7 - 1.0)
        # If failure, confidence could still be high (if overconfident) or low (if calibrated)
        if is_success:
            base_confidence = random.uniform(0.7, 0.95)
        else:
            base_confidence = random.uniform(0.3, 0.8)
            
        # Apply calibration bias (clamped to 0.0 - 1.0)
        confidence = max(0.0, min(1.0, base_confidence + self.calibration_bias))
        
        task_id = task.get("id", "task")
        if is_success:
            response = f"[Simulated Success] Correct result from {self.name} for task {task_id}."
            reasoning = f"Simulated success execution based on true success rate of {self.true_success_rate}."
        else:
            response = f"[Simulated Hallucination] Erroneous result from {self.name} for task {task_id}."
            reasoning = f"Simulated failure execution based on true failure rate of {1 - self.true_success_rate}."
            
        return {
            "response": response,
            "confidence": confidence,
            "reasoning": reasoning,
            "simulated": True,
            "simulated_success": is_success
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, role={self.role}, model={self.model})"
