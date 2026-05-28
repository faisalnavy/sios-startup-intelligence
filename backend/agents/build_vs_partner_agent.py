"""
Build vs Partner Agent — SIOS v2

Generates a McKinsey-style capability matrix showing which components
the startup should build internally vs partner/license vs acquire.

This prevents the most common startup mistake: building what can be partnered,
and partnering what needs to be proprietary.
"""
from agents.base_agent import BaseAgent
from models.startup_input import StartupInput


class BuildVsPartnerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Build vs Partner Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        system_prompt = """You are a startup strategy and technology architecture expert who specializes in
build vs buy vs partner decisions for early-stage companies.

You understand deeply that startups must be ruthlessly capital-efficient. Building everything in-house
destroys runway. But outsourcing your core proprietary advantage destroys your moat.

Your job is to create a clear, actionable BUILD vs PARTNER vs BUY decision matrix for this startup.

Rules:
- BUILD: Only if it's a proprietary advantage, data flywheel, or core customer experience
- PARTNER: If commodity infrastructure, regulated service, or faster to market via existing player
- BUY: If there's an acqui-hire or small tool that accelerates 12 months of build in 1 acquisition
- Be specific about WHICH partners/vendors/platforms to use

Your output should look like a McKinsey slide that a founder could show investors."""

        prompt = f"""{context}

=== YOUR TASK: BUILD vs PARTNER vs BUY MATRIX ===

Identify all the core capabilities this startup needs to operate and classify each one.

## CAPABILITY_OVERVIEW
[2-3 sentences: What are the 3-4 most critical capability decisions this startup faces?]

## DECISION_MATRIX

For each capability, provide:
| Capability | Decision | Reasoning | Suggested Partner/Vendor | Timeline |

Format EXACTLY like this for each capability:

### CAPABILITY: [Name]
Decision: BUILD ✅ / PARTNER 🤝 / BUY 💰
Reasoning: [Why this decision — be specific]
If PARTNER: Suggested vendors: [Name 2-3 specific companies]
If BUY: Acquisition target type: [describe]
Timeline: [When to do this — Month 1 / Month 3 / Year 2, etc.]
Risk if wrong decision: [What happens if they do the opposite?]

[Provide 8-15 capabilities covering the full tech, ops, and business stack]

## CRITICAL_BUILD_DECISION
[The single most important BUILD decision — what is the core proprietary thing they MUST build themselves?]

## BIGGEST_PARTNERSHIP_WIN
[The single partnership that would save the most time and money and should be done FIRST]

## CAPITAL_EFFICIENCY_IMPACT
[How many months of runway does the right build/partner strategy save vs building everything?]

## EXECUTION_SEQUENCE
Phase 1 (Month 1-3): [Which partnerships to close first and why]
Phase 2 (Month 4-9): [What to start building internally]
Phase 3 (Month 10+): [What to bring in-house after traction]

## MATRIX_SUMMARY
[1 paragraph: The overall philosophy — what does this startup need to own vs leverage?]"""

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
