from abc import ABC, abstractmethod
from services import DualAIService, TavilyService
from models.startup_input import StartupInput


class BaseAgent(ABC):
    def __init__(self):
        self.dual_ai = DualAIService()
        self.tavily = TavilyService()
        self.agent_name = "Base Agent"

    def _startup_context(self, startup: StartupInput) -> str:
        return f"""Startup: {startup.startup_name}
Idea: {startup.idea_description}
Geography: {startup.geography}
Stage: {startup.business_stage.value}
Revenue Model: {startup.revenue_model or 'Not specified'}
Funding Required: {startup.funding_required or 'Not specified'}
Founder Background: {startup.founder_background or 'Not specified'}
Known Competitors: {startup.competitors_known or 'Not specified'}
Unique Advantage: {startup.unique_advantage or 'Not specified'}"""

    @abstractmethod
    async def run(self, startup: StartupInput) -> dict:
        """Execute this agent's analysis and return structured result dict."""
        pass
