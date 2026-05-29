"""
Founder Psychology Agent — SIOS v2 Tier 2

Scores the founder on dimensions that top VCs say matter more than the idea:
  - Realism Index (overconfidence vs. delusion detection)
  - Adaptability Signal (willingness to pivot based on language)
  - Learning Velocity Indicator
  - Resilience Markers
  - Founder-Market Fit (domain knowledge + passion alignment)
  - Red Flag Phrases (classic delusional founder patterns)

Analysis is based on:
  - Language patterns in the startup description
  - Founder background quality signals
  - Business plan specificity vs. vagueness
  - Founder profile data (LinkedIn/GitHub if provided)

This is not a personality test — it's a VC-lens assessment of whether this founder
will execute through adversity and adapt when the first plan fails.
"""
from agents.base_agent import BaseAgent
from models.startup_input import StartupInput


# ── Red Flag Phrase Library ───────────────────────────────────────────────────
RED_FLAG_PATTERNS = """
RED FLAG PHRASES (delusional founder patterns — check if present):
- "No competitors" / "first in the world" / "no one is doing this" → market awareness failure
- "Viral by nature" / "will go viral" without mechanism → wishful distribution thinking
- "10x better" without specification → vague differentiation
- "Everyone will use this" / "our market is everyone" → no ICP thinking
- "Just need to build it" / "if we build it they will come" → GTM naivety
- "We'll figure out monetization later" → revenue avoidance
- "We just need 1% of the market" → TAM fallacy reasoning
- "Uber/Airbnb for X" without the enabling technology → lazy positioning
- "This will disrupt X industry" without mechanism → disruption theater
- "We have no direct competitors" when obvious ones exist → research gap
- "My friends/family love it" → survivorship bias in validation
- "The technology is proprietary" with no specifics → vague IP claims
- "We'll get to profitability after Series B" without path → profit deferral
"""

# ── Positive Signal Patterns ──────────────────────────────────────────────────
POSITIVE_SIGNALS = """
POSITIVE FOUNDER SIGNALS (mark which are present):
- Specific customer interviews / user research data mentioned
- Revenue or paying customers already (even small amounts)
- Named competitors with clear differentiation logic
- Admits specific weaknesses or gaps in the plan
- Clear regulatory awareness for their sector
- Domain expertise: years in the specific industry
- Previous startup experience (especially failures)
- Specific geographic market knowledge
- Identified a real personal pain point they've lived
- Knows exact unit economics targets
- Clear "unfair advantage" that is specific and defensible
"""


class FounderPsychologyAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Founder Psychology Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        system_prompt = """You are a behavioral analyst and senior venture partner who has interviewed 2,000+
founders over 20 years. You specialize in identifying the psychological and cognitive patterns that
predict founder success — NOT just ideation quality, but execution psychology.

Top VCs often say: "We invest in the founder, not the idea." Your job is to assess whether this
founder has the psychological profile to survive: the first failed pivot, the first key hire departure,
the first regulatory block, the first VC rejection.

Be honest, specific, and evidence-based. You must reference specific language from the founder's
description. You are not here to be encouraging — you are here to give a true assessment."""

        prompt = f"""{context}

=== REFERENCE PATTERNS ===
{RED_FLAG_PATTERNS}

{POSITIVE_SIGNALS}

=== YOUR TASK: FOUNDER PSYCHOLOGY PROFILE ===

Based on the startup description, founder background, and all available context,
produce a comprehensive founder psychology assessment.

Use this exact structure:

## PSYCHOLOGY_OVERVIEW
**Overall Founder Assessment:** [EXCEPTIONAL / STRONG / ADEQUATE / CONCERNING / HIGH_RISK]
**Confidence Level in Assessment:** [HIGH / MEDIUM / LOW — based on data richness]
**One-line verdict:** [The most important thing to know about this founder]

## DIMENSION_SCORES
Rate each dimension 0-100 with reasoning:

### Realism Index: [X/100]
**Red flags detected:** [List any red flag phrases found in their description, or "None detected"]
**Positive signals:** [Specific evidence of realistic thinking]
**Assessment:** [2-3 sentences]

### Adaptability Signal: [X/100]
**Evidence of pivot-readiness:** [What in their language/background suggests they can pivot?]
**Rigidity markers:** [Any signs they're emotionally attached to this exact idea?]
**Assessment:** [2-3 sentences]

### Learning Velocity: [X/100]
**Evidence of rapid learning:** [Prior experience, domain study, research quality]
**Knowledge gaps:** [What they clearly don't know yet]
**Assessment:** [2-3 sentences]

### Resilience Markers: [X/100]
**Adversity evidence:** [Any prior failures, hard pivots, setbacks mentioned?]
**Risk appetite signals:** [How are they framing risk and uncertainty?]
**Assessment:** [2-3 sentences]

### Founder-Market Fit: [X/100]
**Domain expertise depth:** [How deeply do they know this specific market?]
**Personal pain point authenticity:** [Is this a real problem they've lived?]
**Unfair advantage:** [Do they have unique access, relationships, or insight?]
**Assessment:** [2-3 sentences]

### Execution Orientation: [X/100]
**Specificity of plan:** [Are they concrete about next steps or vague?]
**Resource awareness:** [Do they know what it will take?]
**Bias to action:** [Evidence of already-started vs purely conceptual]
**Assessment:** [2-3 sentences]

## RED_FLAG_ALERT
**Red flags found:** [YES / NO]
If yes, list each:
- [Phrase or pattern] → [Why this is a warning signal]

## STRENGTH_PROFILE
Top 3 psychological strengths of this founder:
1. [Strength] — [Evidence from their description]
2. [Strength] — [Evidence from their description]
3. [Strength] — [Evidence from their description]

## BLIND_SPOT_ANALYSIS
Top 3 psychological blind spots or cognitive biases detected:
1. [Blind spot] — [How this will hurt them]
2. [Blind spot] — [How this will hurt them]
3. [Blind spot] — [How this will hurt them]

## VC_INTERVIEW_PREDICTION
**How would this founder perform in a Series A VC interview?**
[2-3 sentences — what would impress, what would concern]

**Toughest question they'd struggle with:**
"[Specific question a VC would ask that this founder is not ready for]"

**Coachability signal:** [HIGH / MEDIUM / LOW]

## TEAM_GAP_ASSESSMENT
Based on this founder's psychology profile, what type of co-founder or early hire
is MOST critical to compensate for their gaps?

**Critical missing archetype:** [e.g., "Operational executor who is detail-obsessed"]
**Reason:** [How this gap could doom the startup if unfilled]
**Where to find them:** [Specific community, network, or platform]

## OVERALL_PSYCHOLOGY_VERDICT
[2-3 paragraph final assessment: founder psychology fit for this specific startup,
probability of surviving first 18 months as a leader, and the one thing they must
do immediately to strengthen their founder profile]"""

        analysis = await self.dual_ai.analyze_with_critique(
            system_prompt=system_prompt,
            user_message=prompt,
            max_tokens=3500,
        )

        return {
            "agent": self.agent_name,
            "analysis": analysis.get("claude_analysis", ""),
            "openai_critique": analysis.get("openai_critique", ""),
            "status": "completed",
        }
