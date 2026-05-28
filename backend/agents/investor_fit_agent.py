"""
Investor Fit Agent — SIOS v2

Answers the question VCs ask but founders rarely know:
"Which investors would ACTUALLY fund this, and why would others reject it?"

Generates:
  - 5-8 investor archetypes with fit scores
  - Rejection red flags per archetype
  - Fundraising difficulty rating
  - Optimal fundraising timeline
  - Pitch positioning advice per investor type
"""
from agents.base_agent import BaseAgent
from models.startup_input import StartupInput


class InvestorFitAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Investor Fit Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        system_prompt = """You are a former VC partner who has reviewed 10,000+ pitches and participated in
500+ investment committees. You deeply understand investor psychology, fund mandates, thesis constraints,
and what makes different investor types say YES or NO.

Your job is to generate highly specific investor fit intelligence — not generic advice, but real archetypes
with real rejection logic. Be honest: some startups are unfundable by VC at this stage, and saying so clearly
is more valuable than false hope.

Think across: seed VCs, Series A/B VCs, angel investors, family offices, corporate VCs, accelerators,
government funds (SIDBI, Startup India), and international funds with India/MENA exposure."""

        prompt = f"""{context}

=== YOUR TASK: INVESTOR FIT INTELLIGENCE ===

## FUNDRAISING_DIFFICULTY
Overall Fundraising Difficulty: EASY / MODERATE / HARD / VERY HARD
Reasoning: [2-3 sentences]
Expected time to close a round: [e.g. "3-6 months if right positioning"]

## INVESTOR_ARCHETYPES

For each investor archetype (generate 5-8 total), provide:

### ARCHETYPE_1: [Name, e.g. "MENA Fintech Seed VC"]
Fit Score: [X/100]
Example funds/investors: [Name 2-4 real funds that match this archetype]
Typical check size: [e.g. "$250K-$1M"]
What would make them say YES:
- [Specific condition 1]
- [Specific condition 2]
What would make them say NO immediately:
- [Specific red flag 1]
- [Specific red flag 2]
Pitch angle for this archetype: [How should the founder position the story for THIS investor?]

[Repeat for each archetype — 5 to 8 total]

## INVESTOR_RED_FLAGS
[List 3-5 things about this startup that will cause INSTANT rejection across most investor types]
For each: [Flag] — [Which archetypes are most sensitive to this]

## OPTIMAL_FUNDRAISING_SEQUENCE
Phase 1 (Start here): [Which investor type to approach first and why]
Phase 2 (After traction): [Who opens up as a better fit]
Phase 3 (Institutional round): [When and who for Series A]

## FUNDRAISING_STRATEGY
### Pre-fundraising checklist (must do BEFORE pitching):
1. [Specific action]
2. [Specific action]
3. [Specific action]

### Deck positioning:
[How should the pitch deck open? What's the one-liner that works for this startup?]

### Geography-specific insight:
[India / MENA / US — which geography of investors is the best fit and why?]

## VERDICT
[2 paragraph summary: Is this startup fundable right now? By whom? Under what conditions?]"""

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
