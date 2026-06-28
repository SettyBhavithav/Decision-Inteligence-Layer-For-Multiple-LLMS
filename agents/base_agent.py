import abc
import json
import logging
import os
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger("trust_framework")

# Configure the global client to point to the NVIDIA NIM Integration API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY", os.environ.get("NIM_API_KEY", "")),
    timeout=5.0
)

class BaseAgent(abc.ABC):
    """
    Abstract base class for all specialized framework agents.
    Uses the NVIDIA NIM Integration API via the OpenAI client wrapper.
    """
    def __init__(self, 
                 name: str, 
                 role: str, 
                 model: str, 
                 temperature: float = 0.7,
                 extra_body: Dict[str, Any] = None):
        self.name = name
        self.role = role
        self.model = model
        self.temperature = temperature
        self.extra_body = extra_body or {}
        
        # Simulation options
        self.use_simulation: bool = False
        self.true_success_rate: float = 0.85
        self.calibration_bias: float = 0.0

    @abc.abstractmethod
    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass

    def _execute_llm(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Calls the NVIDIA NIM API requesting JSON structure.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        json_schema_prompt = (
            "\n\nYou MUST respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "response": "Your detailed answer goes here",\n'
            '  "confidence": <float between 0.0 and 1.0 indicating your confidence in correctness>,\n'
            '  "reasoning": "Brief explanation of how you reached this answer and confidence"\n'
            "}"
        )
        messages[-1]["content"] += json_schema_prompt

        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "stream": False
            }
            if self.extra_body:
                params["extra_body"] = self.extra_body

            completion = client.chat.completions.create(**params)
            content = completion.choices[0].message.content
            
            # Extract reasoning text if returned by NVIDIA reasoning model
            reasoning = getattr(completion.choices[0].message, "reasoning", None) or getattr(completion.choices[0].message, "reasoning_content", None)
            
            # Clean markdown JSON block formatting if present
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            parsed = json.loads(cleaned_content)
            
            # Combine API thinking trace and agent reasoning
            agent_reasoning = parsed.get("reasoning", "")
            if reasoning:
                agent_reasoning = f"[NVIDIA NIM Thinking:\n{reasoning}]\n{agent_reasoning}"
            
            return {
                "response": parsed.get("response", ""),
                "confidence": float(parsed.get("confidence", 0.5)),
                "reasoning": agent_reasoning,
                "simulated": False,
                "token_usage": {
                    "prompt": completion.usage.prompt_tokens if completion.usage else 0,
                    "completion": completion.usage.completion_tokens if completion.usage else 0
                }
            }
        except Exception as e:
            logger.error(f"Error calling NVIDIA NIM API for agent {self.name}: {e}")
            return {
                "response": f"Error: Agent execution failed due to API exception: {str(e)}",
                "confidence": 0.1,
                "reasoning": f"Exception details: {str(e)}",
                "simulated": False,
                "token_usage": {"prompt": 0, "completion": 0}
            }

    def _execute_simulation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates execution behavior for testing and evaluation.
        """
        import random
        is_success = random.random() < self.true_success_rate
        
        if is_success:
            base_confidence = random.uniform(0.75, 0.95)
        else:
            base_confidence = random.uniform(0.20, 0.65)
            
        confidence = max(0.0, min(1.0, base_confidence + self.calibration_bias))
        
        task_id = task.get("id", "task")
        if is_success:
            response = f"[Simulated Success] Completed subtask {task_id} correctly by {self.name}."
            reasoning = f"Simulated success with target true_success_rate of {self.true_success_rate}."
        else:
            response = f"[Simulated Error] Simulated failure/hallucination in task {task_id} by {self.name}."
            reasoning = f"Simulated failure occurrence based on error probability: {1.0 - self.true_success_rate:.2f}."
            
        return {
            "response": response,
            "confidence": confidence,
            "reasoning": reasoning,
            "simulated": True,
            "simulated_success": is_success,
            "token_usage": {"prompt": 100, "completion": 50}
        }

class AgentRegistry:
    """
    Dynamic agent instance registry.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance.agents = {}
        return cls._instance

    def register(self, role: str, agent: BaseAgent) -> None:
        self.agents[role.lower()] = agent

    def get_agent(self, role: str) -> BaseAgent:
        return self.agents.get(role.lower())

    def list_roles(self) -> list:
        return list(self.agents.keys())

    def clear(self) -> None:
        self.agents.clear()

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation

# created base agent abstract class and AgentState model

# created dynamic router picking best LLM based on prompt difficulty

# created demo script running sample multi-agent research workflow

# built citation verification agent to cross-check factual claims

# added voting consensus logic between multiple LLM agents

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation

# created base agent abstract class and AgentState model

# created dynamic router picking best LLM based on prompt difficulty

# created demo script running sample multi-agent research workflow

# built citation verification agent to cross-check factual claims

# added voting consensus logic between multiple LLM agents

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation

# created base agent abstract class and AgentState model

# created dynamic router picking best LLM based on prompt difficulty

# created demo script running sample multi-agent research workflow

# built citation verification agent to cross-check factual claims

# added voting consensus logic between multiple LLM agents

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation
