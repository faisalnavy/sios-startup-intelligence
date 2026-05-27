from agents.base_agent import BaseAgent
from models.startup_input import StartupInput

SYSTEM_PROMPT = """You are a startup failure analysis expert who has studied 10,000+ startup post-mortems.

Your job is to identify every possible reason this startup could fail — BEFORE money is wasted.

The 10 root causes of startup failure to always check:
1. Wrong market timing
2. Weak founder-market fit
3. No distribution system
4. Wrong pricing model
5. Poor cashflow management
6. Low market demand
7. Bad geography selection
8. Weak unit economics
9. Lack of retention
10. Fundraising without profitability path

For each risk you identify, provide:
- Risk description (specific to this startup)
- Severity: HIGH / MEDIUM / LOW
- Probability of occurring: HIGH / MEDIUM / LOW
- Specific mitigation strategy

Identify at least 15 risks. Be brutally honest. Be specific — not generic.
Conclude with a survival probability score (0-100%) with your reasoning."""


class FailureAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Startup Failure Analysis Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        search_results = await self.tavily.search(
            f"why {startup.idea_description} startups fail common mistakes {startup.geography}",
            max_results=5,
        )
        search_results += "\n\n" + await self.tavily.search(
            f"{startup.target_market or startup.idea_description} startup failure reasons post-mortem",
            max_results=4,
        )

        user_message = f"""Perform a comprehensive failure risk analysis for this startup:

{context}

Web Research on failures in this space:
{search_results}

Identify all failure risks with severity ratings and specific mitigation strategies.
End with a survival probability assessment."""

        result = await self.dual_ai.cross_validate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            startup_context=context,
            domain="startup failure analysis and risk assessment",
        )

        return {
            "agent": self.agent_name,
            "analysis": result["final_synthesis"],
            "claude_initial": result["claude_initial"],
            "openai_critique": result["openai_critique"],
        }
