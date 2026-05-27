from agents.base_agent import BaseAgent
from models.startup_input import StartupInput

SYSTEM_PROMPT = """You are an elite market intelligence researcher with 20+ years of experience.

Your job is to perform a rigorous market analysis for a startup idea.

Analyze:
1. Total Addressable Market (TAM), Serviceable Addressable Market (SAM), Serviceable Obtainable Market (SOM)
2. Market growth rate (CAGR)
3. Industry maturity stage (emerging / growing / mature / declining)
4. Key demand drivers
5. Customer pain points and willingness to pay
6. Market saturation level
7. Entry barriers
8. Underserved segments and gaps
9. Geographic market differences
10. Future market trajectory (3-5 years)

Be data-driven. Use real numbers when available. Cite market research sources.
Be honest about market risks — do not inflate opportunity."""


class MarketResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Market Research Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        # Research first
        search_results = await self.tavily.search(
            f"{startup.idea_description} market size TAM CAGR {startup.geography} industry analysis 2024 2025",
            max_results=6,
        )
        search_results += "\n\n" + await self.tavily.search(
            f"{startup.target_market or startup.idea_description} customer pain points demand {startup.geography}",
            max_results=4,
        )

        user_message = f"""Analyze the market for this startup:

{context}

Web Research Data:
{search_results}

Provide a comprehensive market analysis covering all 10 points in your system instructions.
Include specific numbers for TAM/SAM/SOM, CAGR, and market size estimates."""

        result = await self.dual_ai.cross_validate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            startup_context=context,
            domain="market research and industry analysis",
        )

        return {
            "agent": self.agent_name,
            "analysis": result["final_synthesis"],
            "claude_initial": result["claude_initial"],
            "openai_critique": result["openai_critique"],
        }
