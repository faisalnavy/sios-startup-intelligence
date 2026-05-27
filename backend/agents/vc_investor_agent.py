from agents.base_agent import BaseAgent
from models.startup_input import StartupInput

SYSTEM_PROMPT = """You are an expert venture capital intelligence researcher with deep knowledge of global VC ecosystems.

Your job is to identify which investors would be interested in this startup and provide actionable fundraising intelligence.

Analyze:
1. Which VCs, angels, family offices, or PE firms match this startup (by thesis, geography, stage, sector)
2. Their typical ticket sizes and check sizes
3. Their preferred equity percentages
4. What they look for before investing
5. Their portfolio companies (similar investments)
6. Red flags that would make them pass
7. Ideal fundraising stage for this startup right now
8. Suggested pre-money valuation range
9. Suggested equity dilution percentage
10. Probability of fundraising success (0-100%)

Be realistic. Not every startup is fundable. Say so clearly if this startup is too early, too niche, or too risky for VC.
Focus on the geography specified."""


class VCInvestorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "VC & Investor Intelligence Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        search_results = await self.tavily.search(
            f"venture capital investors {startup.geography} {startup.target_market or startup.idea_description} seed series A funding",
            max_results=5,
        )
        search_results += "\n\n" + await self.tavily.search(
            f"angel investors {startup.geography} {startup.target_market or startup.idea_description} startup investment 2024",
            max_results=4,
        )

        user_message = f"""Identify investors and fundraising strategy for this startup:

{context}

Web Research:
{search_results}

Provide complete investor intelligence including specific VC names, their typical check sizes, and fundraising probability assessment."""

        result = await self.dual_ai.cross_validate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            startup_context=context,
            domain="venture capital and startup investment",
        )

        return {
            "agent": self.agent_name,
            "analysis": result["final_synthesis"],
            "claude_initial": result["claude_initial"],
            "openai_critique": result["openai_critique"],
        }
