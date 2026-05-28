"""
Moat Analysis Agent — SIOS v2

Answers the question elite investors ask: "How does this startup WIN and stay winning?"

Generates:
  - Defensibility score (0-100)
  - Network effect classification
  - Data moat opportunity
  - Switching cost analysis
  - Distribution moat
  - Partnership moat
  - AI moat potential
"""
from agents.base_agent import BaseAgent
from models.startup_input import StartupInput


class MoatAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Moat Analysis Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        system_prompt = """You are a competitive strategy expert and venture capitalist specializing in
identifying defensible business models. You think like Hamilton Helmer (7 Powers), Peter Thiel (Zero to One),
and top Sequoia partners.

Your job is to rigorously analyze whether this startup can build durable competitive advantages —
and HOW specifically it can create moats that will prevent competition from eroding its market position.

Be specific, quantitative where possible, and honest. Not all startups can build great moats — say so clearly."""

        prompt = f"""{context}

=== YOUR TASK: COMPETITIVE MOAT ANALYSIS ===

Perform a comprehensive moat analysis. Use this exact structure:

## DEFENSIBILITY_SCORE
Overall Defensibility Score: [X/100]
Reasoning: [2-3 sentences explaining the score]

## MOAT_TYPE_ANALYSIS
Analyze each of the 7 moat types and rate each:

### 1. Network Effects [NONE / WEAK / MODERATE / STRONG]
[Does this business become more valuable as more users join? How specifically?]

### 2. Switching Costs [NONE / WEAK / MODERATE / STRONG]
[How hard is it for a customer to switch to a competitor? What keeps them locked in?]

### 3. Data Moat [NONE / WEAK / MODERATE / STRONG]
[What proprietary data does this company accumulate? How does data compound defensibility?]

### 4. Scale Economies [NONE / WEAK / MODERATE / STRONG]
[Do unit economics improve materially at scale? By how much?]

### 5. Brand Moat [NONE / WEAK / MODERATE / STRONG]
[Can this brand command pricing power? In what timeframe?]

### 6. Distribution Moat [NONE / WEAK / MODERATE / STRONG]
[Does distribution become harder for competitors to replicate over time?]

### 7. AI / Technology Moat [NONE / WEAK / MODERATE / STRONG]
[Is there a proprietary algorithmic advantage that compounds with data?]

## MOAT_CREATION_ROADMAP
### Phase 1 (0-12 months): Build the foundation moat
[Specific actions to create the first defensible advantage]

### Phase 2 (12-36 months): Compound the moat
[How to deepen and stack multiple moat types]

### Phase 3 (36+ months): Fortress position
[End-state competitive position if everything works]

## BIGGEST_MOAT_OPPORTUNITY
[In this specific market, which single moat type has the highest potential and why?]

## MOAT_KILLER_RISKS
[What 2-3 things could destroy any moat this startup builds?]

## VERDICT
Strong Moat Potential / Moderate Moat Potential / Weak Moat Potential / Commodity Business Risk
[1 paragraph summary]"""

        analysis = await self.dual_ai.analyze_with_critique(
            system_prompt=system_prompt,
            user_message=prompt,
            max_tokens=3000,
        )

        return {
            "agent": self.agent_name,
            "analysis": analysis.get("claude_analysis", ""),
            "openai_critique": analysis.get("openai_critique", ""),
            "status": "completed",
        }
