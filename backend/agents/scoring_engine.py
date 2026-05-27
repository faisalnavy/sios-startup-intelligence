from services import ClaudeService
from models.startup_input import StartupInput
from models.report_output import ScoreBreakdown
import json

SYSTEM_PROMPT = """You are a startup scoring analyst. You receive analysis reports from 6 specialized agents and must calculate a startup viability score.

Scoring Formula:
- Market Demand: 20% weight (score 0-100)
- Founder Capability: 15% weight (score 0-100)
- Unit Economics: 15% weight (score 0-100)
- Scalability: 15% weight (score 0-100)
- Competition Advantage: 10% weight (score 0-100)
- Timing: 10% weight (score 0-100)
- Financial Stability: 10% weight (score 0-100)
- Execution Capability: 5% weight (score 0-100)

Total Score = weighted average of all above.

Score Interpretation:
- 90-100: Exceptional
- 80-89: Strong
- 70-79: Promising
- 60-69: Risky
- Below 60: High Failure Probability

Respond ONLY with JSON in this exact format:
{
  "market_demand": <0-100>,
  "founder_capability": <0-100>,
  "unit_economics": <0-100>,
  "scalability": <0-100>,
  "competition_advantage": <0-100>,
  "timing": <0-100>,
  "financial_stability": <0-100>,
  "execution_capability": <0-100>,
  "total_score": <calculated weighted score>,
  "score_interpretation": "<Exceptional|Strong|Promising|Risky|High Failure Probability>",
  "success_probability": <0-100>,
  "scoring_rationale": "<2-3 sentence explanation of the score>"
}"""


class ScoringEngine:
    def __init__(self):
        self.claude = ClaudeService()

    async def calculate(
        self,
        startup: StartupInput,
        market_analysis: str,
        financial_analysis: str,
        competitor_analysis: str,
        failure_analysis: str,
        trend_analysis: str,
        vc_analysis: str,
    ) -> ScoreBreakdown:
        user_message = f"""Score this startup based on all agent analyses:

STARTUP: {startup.startup_name}
STAGE: {startup.business_stage.value}
FOUNDER: {startup.founder_background or 'Not specified'} ({startup.founder_experience_years or '?'} years exp)
GEOGRAPHY: {startup.geography}

--- MARKET ANALYSIS ---
{market_analysis[:1500]}

--- FINANCIAL ANALYSIS ---
{financial_analysis[:1500]}

--- COMPETITOR ANALYSIS ---
{competitor_analysis[:1000]}

--- FAILURE RISK ANALYSIS ---
{failure_analysis[:1000]}

--- TREND ANALYSIS ---
{trend_analysis[:800]}

--- VC/INVESTOR ANALYSIS ---
{vc_analysis[:800]}

Calculate the startup score using the formula. Be objective and data-driven."""

        result = await self.claude.generate_json(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
        )

        total = (
            result["market_demand"] * 0.20
            + result["founder_capability"] * 0.15
            + result["unit_economics"] * 0.15
            + result["scalability"] * 0.15
            + result["competition_advantage"] * 0.10
            + result["timing"] * 0.10
            + result["financial_stability"] * 0.10
            + result["execution_capability"] * 0.05
        )

        return ScoreBreakdown(
            market_demand=result["market_demand"],
            founder_capability=result["founder_capability"],
            unit_economics=result["unit_economics"],
            scalability=result["scalability"],
            competition_advantage=result["competition_advantage"],
            timing=result["timing"],
            financial_stability=result["financial_stability"],
            execution_capability=result["execution_capability"],
            total_score=round(total, 1),
        ), result.get("success_probability", int(total)), result.get("scoring_rationale", "")
