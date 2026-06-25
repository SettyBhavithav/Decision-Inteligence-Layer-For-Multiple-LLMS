from typing import Dict, Any, List
from trust_collaboration.agents.base import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self, name: str = "ResearchAgent", model: str = "gpt-4o-mini", temperature: float = 0.5):
        super().__init__(name, "research", model, temperature)
        self.true_success_rate = 0.85
        self.calibration_bias = 0.05  # slightly overconfident

    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.use_simulation:
            return self._execute_simulation(task)
        
        system_prompt = (
            "You are a specialized Research Agent. Your responsibility is information retrieval, "
            "fact extraction, and evidence collection. You analyze data and summarize findings "
            "with precise facts. Avoid making unsubstantiated claims."
        )
        user_prompt = (
            f"Task: {task.get('description', '')}\n"
            f"Context: {context}\n"
            "Provide detailed research, extract key facts, and assess the reliability of sources."
        )
        return self._execute_llm(system_prompt, user_prompt)


class WritingAgent(BaseAgent):
    def __init__(self, name: str = "WritingAgent", model: str = "gpt-4o-mini", temperature: float = 0.7):
        super().__init__(name, "writing", model, temperature)
        self.true_success_rate = 0.80
        self.calibration_bias = 0.0  # well-calibrated

    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.use_simulation:
            return self._execute_simulation(task)
        
        system_prompt = (
            "You are a specialized Writing Agent. Your responsibility is response generation, "
            "document creation, and report writing. You synthesize information from research, "
            "structure documents logically, and write clean, coherent text."
        )
        user_prompt = (
            f"Task: {task.get('description', '')}\n"
            f"Context: {context}\n"
            "Generate a well-written, structured response or document based on the provided context."
        )
        return self._execute_llm(system_prompt, user_prompt)


class CitationAgent(BaseAgent):
    def __init__(self, name: str = "CitationAgent", model: str = "gpt-4o-mini", temperature: float = 0.3):
        super().__init__(name, "citation", model, temperature)
        self.true_success_rate = 0.90
        self.calibration_bias = -0.05  # slightly underconfident (conservative)

    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.use_simulation:
            return self._execute_simulation(task)
        
        system_prompt = (
            "You are a specialized Citation Agent. Your responsibility is citation verification, "
            "reference formatting, and validation of sources. You ensure everything stated has a "
            "clear, verified bibliographic link and format citations in IEEE style."
        )
        user_prompt = (
            f"Task: {task.get('description', '')}\n"
            f"Context: {context}\n"
            "Validate references, format the citations, and add necessary bibliographic anchors."
        )
        return self._execute_llm(system_prompt, user_prompt)


class ReviewerAgent(BaseAgent):
    def __init__(self, name: str = "ReviewerAgent", model: str = "gpt-4o-mini", temperature: float = 0.4):
        super().__init__(name, "reviewer", model, temperature)
        self.true_success_rate = 0.75
        self.calibration_bias = 0.10  # overconfident

    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.use_simulation:
            return self._execute_simulation(task)
        
        system_prompt = (
            "You are a specialized Reviewer Agent. Your responsibility is to review generated content, "
            "identify logical inconsistencies, detect errors, and suggest improvements. "
            "Critically analyze the input and output."
        )
        user_prompt = (
            f"Task: {task.get('description', '')}\n"
            f"Context: {context}\n"
            "Critique the proposed content and detail any discrepancies, errors, or gaps."
        )
        return self._execute_llm(system_prompt, user_prompt)


class VerificationAgent(BaseAgent):
    def __init__(self, name: str = "VerificationAgent", model: str = "gpt-4o-mini", temperature: float = 0.2):
        super().__init__(name, "verification", model, temperature)
        self.true_success_rate = 0.95
        self.calibration_bias = 0.0  # very well-calibrated

    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.use_simulation:
            return self._execute_simulation(task)
        
        system_prompt = (
            "You are a specialized Verification Agent. Your responsibility is independent verification, "
            "cross-checking claims, and validating facts against trusted reference contexts. "
            "You must return a clear verification status: VERIFIED or FAILED."
        )
        user_prompt = (
            f"Task: Verify the correctness of this content: {task.get('description', '')}\n"
            f"Context to verify against: {context}\n"
            "Perform a rigorous fact-check and output your validation report and verify status."
        )
        return self._execute_llm(system_prompt, user_prompt)
