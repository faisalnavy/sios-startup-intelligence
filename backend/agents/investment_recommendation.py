from services import ClaudeService
from models.startup_input import StartupInput
from models.report_output import Verdict, InvestorMatch

SYSTEM_PROMPT = """You are a world-class investment decision engine combining VC partner, PE analyst, and startup advisor expertise.

Based on all startup intelligence gathered, produce the final investment recommendation.

Your analysis must determine:
1. FINAL VERDICT — one of exactly:
   - STRONG BUY (90-100 score, exceptional opportunity)
   - BUY WITH CAUTION (70-89 score, good but with noted risks)
   - WAIT & WATCH (50-69 score, potential but too early or too risky now)
   - PIVOT REQUIRED (any score, fundamental model problems)
   - DO NOT INVEST (below 50 or fundamental flaws found)

2. Investment stage recommendation (Pre-Seed / Seed / Series A / Growth)
3. Suggested equity percentage for investment
4. Suggested investment amount range
5. Conditions under which investment makes sense
6. Top 3 investor types most likely to invest
7. Key milestones investor should require before releasing capital
8. Exit strategy analysis (M&A / IPO / Strategic sale probability)

Investor Decision Matrix (apply):
- Strong founder + large market → Invest aggressively
- Weak unit economics → Avoid
- Strong retention → Positive signal
- Fast burn + no moat → Dangerous
- High CAC + low LTV → Reject
- Strong distribution advantage → Valuable
- Strong network effects → Very valuable

Be decisive. Give a clear recommendation, not a wishy-washy answer.

Respond in JSON format:
{
  "verdict": "<one of the 5 verdicts>",
  "verdict_reasoning": "<2-3 sentences>",
  "investment_stage": "<Pre-Seed|Seed|Series A|Growth>",
  "suggested_equity": "<e.g. 15-20%>",
  "suggested_amount": "<e.g. ₹1-2 Crore or $200K-$500K>",
  "key_conditions": ["condition1", "condition2", "condition3"],
  "investor_types": ["type1", "type2", "type3"],
  "milestones_required": ["milestone1", "milestone2", "milestone3"],
  "exit_probability": {"acquisition": <0-100>, "ipo": <0-100>, "strategic_sale": <0-100>},
  "funding_recommendation": "<2-3 paragraph detailed funding strategy>"
}"""


class InvestmentRecommendationEngine:
    def __init__(self):
        self.claude = ClaudeService()

    async def generate(
        self,
        startup: StartupInput,
        total_score: float,
        market_analysis: str,
        financial_analysis: str,
        failure_analysis: str,
        vc_analysis: str,
        scoring_rationale: str,
    ) -> dict:
        user_message = f"""Generate the final investment recommendation for this startup:

Startup: {startup.startup_name}
Stage: {startup.business_stage.value}
Geography: {startup.geography}
Total Score: {total_score}/100

Scoring Rationale: {scoring_rationale}

Key Findings:
MARKET: {market_analysis[:800]}
FINANCIAL: {financial_analysis[:800]}
RISKS: {failure_analysis[:600]}
VC LANDSCAPE: {vc_analysis[:600]}

Apply the investor decision matrix and produce the final verdict and recommendation."""

        result = await self.claude.generate_json(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
        )

        return result
