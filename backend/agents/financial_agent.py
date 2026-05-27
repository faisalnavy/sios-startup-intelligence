from agents.base_agent import BaseAgent
from models.startup_input import StartupInput

SYSTEM_PROMPT = """You are a Chartered Accountant + CFO + FP&A expert with deep startup finance experience.

Your job is to analyze the financial viability of a startup with the rigor of a CA combined with VC-level business model analysis.

Analyze:
1. Business model strength (how money is made and retained)
2. Unit economics:
   - Customer Acquisition Cost (CAC) estimate
   - Lifetime Value (LTV) estimate
   - LTV:CAC ratio (must be >3 for viability)
   - Payback period
3. Gross margin estimate (%)
4. EBITDA path (when can this become profitable?)
5. Burn rate estimate for first 24 months
6. Runway calculation for different funding amounts
7. Revenue projections (Year 1, Year 2, Year 3) — conservative and optimistic
8. Break-even analysis
9. Cashflow forecast summary
10. Capital efficiency (how much ₹ needed per ₹ revenue)
11. Total funding required to reach profitability
12. Financial red flags and risks

Be realistic. Most startups underestimate costs and overestimate revenue.
Use India-appropriate numbers if geography is India."""


class FinancialCAAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Financial & CA Analysis Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        search_results = await self.tavily.search(
            f"{startup.idea_description} startup unit economics CAC LTV gross margin benchmark",
            max_results=4,
        )
        search_results += "\n\n" + await self.tavily.search(
            f"{startup.revenue_model or startup.idea_description} revenue model profitability timeline startup",
            max_results=3,
        )

        user_message = f"""Perform CA-level financial analysis for this startup:

{context}

Industry Financial Benchmarks:
{search_results}

Provide complete financial analysis including unit economics, projections (3 years), burn rate, runway, and break-even analysis.
Give specific numbers, not just ranges."""

        result = await self.dual_ai.cross_validate(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            startup_context=context,
            domain="startup financial analysis and chartered accountancy",
        )

        return {
            "agent": self.agent_name,
            "analysis": result["final_synthesis"],
            "claude_initial": result["claude_initial"],
            "openai_critique": result["openai_critique"],
        }
