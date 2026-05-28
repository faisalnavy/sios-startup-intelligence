"""
Alternative Strategy Agent — SIOS v2

When risk is detected, this agent answers: "What SHOULD they do instead?"

Generates:
  - 3-5 concrete pivot paths
  - MVP scope (V1 / V2 / DO NOT BUILD YET classification)
  - Product-first vs partnership-first vs geography-first recommendation
  - Scope reduction guidance for over-engineered ideas
"""
from agents.base_agent import BaseAgent
from models.startup_input import StartupInput


class AlternativeStrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Alternative Strategy Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        system_prompt = """You are a world-class startup strategy consultant — part McKinsey, part Y Combinator partner.

Your job is NOT to evaluate the startup as presented. Your job is to answer:
"If this idea has serious flaws, what are the best alternative paths forward?"

You think like a battle-tested operator who has seen 1000 startups fail. You give honest, actionable,
specific strategic alternatives — not generic advice. Every recommendation must be grounded in:
- Market realities
- Regulatory landscape
- Founder's actual capabilities
- Capital efficiency

Avoid vague advice like "build an MVP." Be specific about WHAT to build, WHO to target first, and WHY."""

        prompt = f"""{context}

=== YOUR TASK: ALTERNATIVE STRATEGY ANALYSIS ===

Analyze this startup's current strategy and generate a comprehensive strategic alternatives report.

Structure your response with these exact sections:

## STRATEGY_OVERVIEW
In 2-3 sentences: What is the core strategic problem with the current approach? What is being over-engineered or mis-sequenced?

## PIVOT_PATHS
Generate exactly 3-5 concrete pivot paths. For each, provide:

### PIVOT_1: [Name]
- Description: [What exactly to do differently]
- Why this works: [Market/regulatory/capital logic]
- First customer: [Who is the exact first customer to sign]
- Revenue path: [How does this make money in 6 months]
- Effort: LOW / MEDIUM / HIGH
- Potential: LOW / MEDIUM / HIGH

[Repeat for PIVOT_2, PIVOT_3, etc.]

## MVP_SCOPE
### V1 — Build NOW (Month 0-3)
[Specific features that must exist to get first paying customer]

### V2 — Build AFTER first revenue (Month 4-9)
[Features that come after proving V1]

### DO_NOT_BUILD_YET
[Features the founder wants but should be deferred — be specific and explain why]

## RECOMMENDED_APPROACH
One paragraph: If you were the founder, what single path would you take and why?

## ENTRY_STRATEGY
Product-first OR Partnership-first OR Geography-first?
Explain in 2-3 sentences with specific action.

## SCOPE_REDUCTION_ALERT
[If the founder is over-scoping, call it out directly. Be brutally honest.]"""

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
