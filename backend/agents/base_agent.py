from abc import ABC, abstractmethod
from services import DualAIService, TavilyService
from models.startup_input import StartupInput


class BaseAgent(ABC):
    def __init__(self):
        self.dual_ai = DualAIService()
        self.tavily = TavilyService()
        self.agent_name = "Base Agent"

    def _startup_context(self, startup: StartupInput) -> str:
        """Build the standard startup context string passed to every agent prompt."""
        ctx = f"""=== STARTUP PROFILE ===
Name: {startup.startup_name}
Idea: {startup.idea_description}
Geography: {startup.geography}
Stage: {startup.business_stage.value}
Revenue Model: {startup.revenue_model or 'Not specified'}
Pricing Strategy: {startup.pricing_strategy or 'Not specified'}
Funding Required: {startup.funding_required or 'Not specified'}
Current Revenue: {startup.current_revenue or 'Not specified'}
Target Market: {startup.target_market or 'Not specified'}
Founder Background: {startup.founder_background or 'Not specified'}
Founder Experience: {f'{startup.founder_experience_years} years' if startup.founder_experience_years else 'Not specified'}
Known Competitors: {startup.competitors_known or 'Not specified'}
Unique Advantage: {startup.unique_advantage or 'Not specified'}
GTM Strategy: {startup.gtm_strategy or 'Not specified'}"""

        # ── NEW v2 enrichment fields ──────────────────────────────────
        if startup.founder_profiles_data:
            ctx += f"\n\n=== FOUNDER PROFILE DATA (from LinkedIn/GitHub) ===\n{startup.founder_profiles_data[:2000]}"

        if startup.business_plan_text:
            # Truncate to avoid token overflow — take first 4000 chars
            plan_excerpt = startup.business_plan_text[:4000]
            ctx += f"\n\n=== BUSINESS PLAN (uploaded PDF excerpt) ===\n{plan_excerpt}"

        if startup.custom_questions:
            questions = "\n".join(f"  {i+1}. {q}" for i, q in enumerate(startup.custom_questions))
            ctx += f"\n\n=== FOUNDER'S SPECIFIC QUESTIONS ===\n{questions}"

        return ctx

    @abstractmethod
    async def run(self, startup: StartupInput) -> dict:
        """Execute this agent's analysis and return structured result dict."""
        pass
