from agents.base_agent import BaseAgent
from models.startup_input import StartupInput

SYSTEM_PROMPT = """You are a global startup feasibility expert with deep knowledge of business ecosystems across 50+ countries.

Your job is to determine the best countries/regions to launch this startup and evaluate the feasibility of the specified geography.

For each country analysis, evaluate:
1. Market demand in that geography
2. Regulatory environment (ease of doing business)
3. Taxation structure for this business type
4. Startup ecosystem quality (investors, accelerators, talent)
5. Competition intensity in that market
6. Labor and operational costs
7. Customer digital adoption rate
8. Payment infrastructure
9. Ease of scaling
10. Localization requirements

Rank the top 5 countries for this startup.
Specifically evaluate the founder's chosen geography first.

Provide:
- Country ranking with scores (1-100)
- Key challenges per country
- Market entry strategy per country
- Country-specific legal/compliance considerations"""


class CountryFeasibilityAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Country Feasibility Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        search_results = await self.tavily.search(
            f"{startup.idea_description} business {startup.geography} regulations startup ecosystem",
            max_results=5,
        )
        search_results += "\n\n" + await self.tavily.search(
            f"best countries launch {startup.target_market or startup.idea_description} startup 2024 2025",
            max_results=4,
        )

        user_message = f"""Evaluate country feasibility for this startup:

{context}

Country Research:
{search_results}

Rank the top 5 countries for this startup. Evaluate {startup.geography} in detail as the chosen geography.
Include specific legal, regulatory, and market entry considerations."""

        result = await self.dual_ai.cross_validate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            startup_context=context,
            domain="global market entry and country feasibility",
        )

        return {
            "agent": self.agent_name,
            "analysis": result["final_synthesis"],
            "claude_initial": result["claude_initial"],
            "openai_critique": result["openai_critique"],
        }
