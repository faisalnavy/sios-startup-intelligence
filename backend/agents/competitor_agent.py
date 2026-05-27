from agents.base_agent import BaseAgent
from models.startup_input import StartupInput

SYSTEM_PROMPT = """You are an elite global competitive intelligence analyst.

Your job is to map the full competitive landscape for a startup.

Analyze:
1. Direct competitors (same product/service, same market)
2. Indirect competitors (alternative solutions customers use)
3. Failed startups in this space (why they failed — very important)
4. Successful competitors — what made them win
5. Pricing comparison
6. Customer acquisition methods comparison
7. Funding history of key competitors
8. Market share estimates
9. Competitive moat possibilities for this startup
10. Strategic weaknesses to exploit
11. Biggest competitive threats
12. Time to build a defensible position

SWOT Analysis:
- Strengths vs competitors
- Weaknesses vs competitors
- Opportunities the competition is missing
- Threats from existing and incoming players

Be honest. If the market is dominated by well-funded incumbents, say so clearly."""


class CompetitorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Global Competitor Analysis Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        search_results = await self.tavily.search(
            f"companies similar to {startup.idea_description} competitors {startup.geography}",
            max_results=6,
        )
        search_results += "\n\n" + await self.tavily.search(
            f"startups failed {startup.idea_description} similar business lessons why failed",
            max_results=4,
        )
        search_results += "\n\n" + await self.tavily.search(
            f"{startup.startup_name} competitors alternatives {startup.target_market or ''}",
            max_results=3,
        )

        user_message = f"""Map the competitive landscape for this startup:

{context}

Web Research:
{search_results}

Produce a complete competitor analysis including:
- Named competitors with their status (active/failed/pivot)
- SWOT analysis
- Competitive moat strategy recommendation"""

        result = await self.dual_ai.cross_validate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            startup_context=context,
            domain="competitive intelligence and market analysis",
        )

        return {
            "agent": self.agent_name,
            "analysis": result["final_synthesis"],
            "claude_initial": result["claude_initial"],
            "openai_critique": result["openai_critique"],
        }
