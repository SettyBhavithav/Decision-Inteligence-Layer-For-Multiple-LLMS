from typing import Dict, Any, Optional
from trust_collaboration.agents.base import BaseAgent

class AgentRegistry:
    """
    Registry for managing agent instances.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance.agents = {}
        return cls._instance

    def register(self, role: str, agent: BaseAgent) -> None:
        """Register an agent under a specific role."""
        self.agents[role.lower()] = agent

    def get_agent(self, role: str) -> Optional[BaseAgent]:
        """Retrieve an agent for a specific role."""
        return self.agents.get(role.lower())

    def list_roles(self) -> list:
        """List all registered agent roles."""
        return list(self.agents.keys())

    def clear(self) -> None:
        """Clear all registered agents."""
        self.agents.clear()
