"""
Execution Simulation Agent — SIOS v2

Models OPERATIONAL failure modes with probability estimates.
This is one of the most valuable outputs for VCs — it answers:
"WHERE exactly will this startup hit the wall, and when?"

Generates:
  - Licensing/regulatory delay probability
  - CAC explosion risk
  - Cash runway death scenario
  - Hiring bottleneck probability
  - Infrastructure scaling risk
  - Execution simulation timeline
"""
from agents.base_agent import BaseAgent
from models.startup_input import StartupInput


class ExecutionSimulationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Execution Simulation Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        system_prompt = """You are a startup operations expert and risk modeler with deep experience in
operational due diligence. You've seen hundreds of startups fail — not because of bad ideas, but because
of predictable operational bottlenecks that founders underestimate.

Your job is to simulate the EXECUTION of this startup and model the probability of each failure mode.

Be realistic and precise. Use benchmark data from similar companies where possible.
Express probabilities as percentages (0-100%). Don't be optimistic — VCs need honest execution risk modeling."""

        prompt = f"""{context}

=== YOUR TASK: EXECUTION RISK SIMULATION ===

Simulate the operational execution of this startup over 18 months and identify all major failure modes.

## EXECUTION_HEALTH_SCORE
Overall Execution Risk Score: [X/100] (100 = highest execution risk)
Risk Level: LOW / MODERATE / HIGH / CRITICAL

## FAILURE_MODE_SIMULATION

For each failure mode, provide:
- Probability %
- Likely timeline
- Impact level (HIGH / MEDIUM / LOW)
- Early warning sign
- Mitigation action

### 1. REGULATORY / LICENSING DELAY
Probability: [X%]
Timeline: [e.g. "will hit within 4-6 months"]
Impact: HIGH / MEDIUM / LOW
Early warning: [What signal appears first?]
Mitigation: [Specific action]

### 2. CAC EXPLOSION (Customer Acquisition Cost spirals)
Probability: [X%]
Timeline:
Impact:
Early warning:
Mitigation:

### 3. CASH RUNWAY DEATH (runs out of money before milestone)
Probability: [X%]
Timeline:
Impact:
Early warning:
Mitigation:

### 4. HIRING / TEAM BOTTLENECK
Probability: [X%]
Timeline:
Impact:
Early warning:
Mitigation:

### 5. TECHNOLOGY / INFRASTRUCTURE SCALING FAILURE
Probability: [X%]
Timeline:
Impact:
Early warning:
Mitigation:

### 6. PARTNERSHIP / VENDOR DEPENDENCY COLLAPSE
Probability: [X%]
Timeline:
Impact:
Early warning:
Mitigation:

### 7. FOUNDER BURNOUT / CO-FOUNDER CONFLICT
Probability: [X%]
Timeline:
Impact:
Early warning:
Mitigation:

## CRITICAL_PATH_ANALYSIS
### Month 1-3 Must-Dos (if these fail, company likely dies):
[List 3-5 critical early milestones]

### Month 4-9 Key Inflection Points:
[Where does execution either validate or invalidate the model?]

### Survival Probability Model:
- 6-month survival probability: [X%]
- 18-month survival probability: [X%]
- 36-month survival probability: [X%]

## SIMULATION_VERDICT
[2-3 paragraph summary: What is the most likely execution scenario? Where will this founder struggle most?]"""

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
