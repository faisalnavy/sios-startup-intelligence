from agents.base_agent import BaseAgent
from models.startup_input import StartupInput

SYSTEM_PROMPT = """You are a global technology and business trend analyst tracking emerging opportunities and disruptions.

Your job is to analyze how macro trends affect this startup's timing, opportunity, and risk.

Analyze:
1. Is this startup riding a rising trend or fighting a declining one?
2. AI/automation impact on this industry (threat or enabler?)
3. Consumer behavior shifts relevant to this business
4. Technology waves that affect this space (5G, AI, blockchain, etc.)
5. Geopolitical and economic trends affecting this market
6. Post-COVID behavioral shifts relevant to this startup
7. Regulatory trends (upcoming laws that could help or hurt)
8. Investor sentiment trend for this sector (hot/cold)
9. Emerging competing technologies that could disrupt this model
10. Timing assessment: Is now the right time? Too early? Too late?

Conclude with:
- Timing Score (1-10): Is the timing right?
- 3 biggest trend opportunities for this startup
- 3 biggest trend threats
- 2-year and 5-year market outlook"""


class TrendAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Global Trend Analysis Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        search_results = await self.tavily.search(
            f"{startup.idea_description} industry trends 2024 2025 AI disruption growth",
            max_results=5,
        )
        search_results += "\n\n" + await self.tavily.search(
            f"{startup.target_market or startup.idea_description} emerging technology market shift {startup.geography}",
            max_results=4,
        )

        user_message = f"""Analyze trends and timing for this startup:

{context}

Trend Research:
{search_results}

Provide a comprehensive trend analysis including timing assessment, key opportunities and threats, and market outlook for 2 and 5 years."""

        result = await self.dual_ai.cross_validate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            startup_context=context,
            domain="technology trends and market timing analysis",
        )

        return {
            "agent": self.agent_name,
            "analysis": result["final_synthesis"],
            "claude_initial": result["claude_initial"],
            "openai_critique": result["openai_critique"],
        }
