"""
Master Orchestrator — SIOS v2

Coordinates all 12 agents, collects results, runs scoring engine,
generates investment recommendation, and assembles the full report.

v2 additions:
  - 5 new Tier 1 agents (Alternative Strategy, Moat, Execution Simulation,
    Build vs Partner, Investor Fit)
  - Business plan PDF context passed to all agents
  - Founder profile data enrichment
  - Custom Q&A section generation
  - Amended Business Plan generation endpoint
"""
import asyncio
import uuid
from datetime import datetime
from typing import Callable

from models.startup_input import StartupInput
from models.report_output import (
    FullReport, Verdict, ScoreBreakdown, AgentResult,
    RiskItem, CompetitorItem, CountryRanking, InvestorMatch,
    CustomQA,
)

# Original 7 agents
from agents.market_agent import MarketResearchAgent
from agents.vc_investor_agent import VCInvestorAgent
from agents.competitor_agent import CompetitorAgent
from agents.failure_agent import FailureAnalysisAgent
from agents.financial_agent import FinancialCAAgent
from agents.country_agent import CountryFeasibilityAgent
from agents.trend_agent import TrendAnalysisAgent

# NEW v2 agents
from agents.alternative_strategy_agent import AlternativeStrategyAgent
from agents.moat_agent import MoatAnalysisAgent
from agents.execution_simulation_agent import ExecutionSimulationAgent
from agents.build_vs_partner_agent import BuildVsPartnerAgent
from agents.investor_fit_agent import InvestorFitAgent

# Engines
from agents.scoring_engine import ScoringEngine
from agents.investment_recommendation import InvestmentRecommendationEngine
from services import ClaudeService, ProfileService


class MasterOrchestrator:
    def __init__(self):
        # Original agents
        self.market_agent = MarketResearchAgent()
        self.vc_agent = VCInvestorAgent()
        self.competitor_agent = CompetitorAgent()
        self.failure_agent = FailureAnalysisAgent()
        self.financial_agent = FinancialCAAgent()
        self.country_agent = CountryFeasibilityAgent()
        self.trend_agent = TrendAnalysisAgent()

        # NEW v2 agents
        self.alt_strategy_agent = AlternativeStrategyAgent()
        self.moat_agent = MoatAnalysisAgent()
        self.execution_agent = ExecutionSimulationAgent()
        self.build_vs_partner_agent = BuildVsPartnerAgent()
        self.investor_fit_agent = InvestorFitAgent()

        # Engines
        self.scoring_engine = ScoringEngine()
        self.recommendation_engine = InvestmentRecommendationEngine()
        self.claude = ClaudeService()
        self.profile_service = ProfileService()

    async def analyze(
        self,
        startup: StartupInput,
        progress_callback: Callable[[str, str], None] = None,
    ) -> FullReport:
        analysis_id = str(uuid.uuid4())

        def emit(agent: str, status: str):
            if progress_callback:
                progress_callback(agent, status)

        agent_results = []

        # ── Pre-flight: Fetch founder profiles if URLs provided ────────
        if startup.founder_profile_urls and not startup.founder_profiles_data:
            emit("Founder Profile Fetch", "running")
            try:
                profile_data = await self.profile_service.fetch_all(startup.founder_profile_urls)
                startup = startup.model_copy(update={"founder_profiles_data": profile_data})
                emit("Founder Profile Fetch", "completed")
            except Exception:
                emit("Founder Profile Fetch", "completed")  # Non-fatal

        # ── Phase 1: Run all 12 research agents in parallel ───────────
        emit("Research Phase", "starting")

        tasks = {
            # Original 7
            "market":      self.market_agent.run(startup),
            "vc":          self.vc_agent.run(startup),
            "competitor":  self.competitor_agent.run(startup),
            "failure":     self.failure_agent.run(startup),
            "financial":   self.financial_agent.run(startup),
            "country":     self.country_agent.run(startup),
            "trend":       self.trend_agent.run(startup),
            # NEW v2
            "alt_strategy":    self.alt_strategy_agent.run(startup),
            "moat":            self.moat_agent.run(startup),
            "execution":       self.execution_agent.run(startup),
            "build_vs_partner":self.build_vs_partner_agent.run(startup),
            "investor_fit":    self.investor_fit_agent.run(startup),
        }

        # Emit running for all agents
        emit("Market Research Agent",        "running")
        emit("VC & Investor Agent",           "running")
        emit("Competitor Analysis Agent",     "running")
        emit("Failure Analysis Agent",        "running")
        emit("Financial & CA Agent",          "running")
        emit("Country Feasibility Agent",     "running")
        emit("Trend Analysis Agent",          "running")
        emit("Alternative Strategy Agent",    "running")
        emit("Moat Analysis Agent",           "running")
        emit("Execution Simulation Agent",    "running")
        emit("Build vs Partner Agent",        "running")
        emit("Investor Fit Agent",            "running")

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        agent_data = dict(zip(tasks.keys(), results))

        def extract(key: str) -> str:
            r = agent_data.get(key)
            if isinstance(r, Exception):
                emit(key.upper(), f"error: {str(r)}")
                return f"Agent error: {str(r)}"
            agent_name = r.get("agent", key)
            emit(agent_name, "completed")
            agent_results.append(AgentResult(
                agent_name=agent_name,
                status="completed",
                summary=r.get("analysis", "")[:300],
                details={"openai_critique": r.get("openai_critique", "")[:200]},
            ))
            return r.get("analysis", "")

        market_text       = extract("market")
        vc_text           = extract("vc")
        competitor_text   = extract("competitor")
        failure_text      = extract("failure")
        financial_text    = extract("financial")
        country_text      = extract("country")
        trend_text        = extract("trend")
        alt_strategy_text = extract("alt_strategy")
        moat_text         = extract("moat")
        execution_text    = extract("execution")
        build_partner_text= extract("build_vs_partner")
        investor_fit_text = extract("investor_fit")

        # ── Phase 2: Scoring ──────────────────────────────────────────
        emit("Scoring Engine", "running")
        score_breakdown, success_probability, scoring_rationale = await self.scoring_engine.calculate(
            startup=startup,
            market_analysis=market_text,
            financial_analysis=financial_text,
            competitor_analysis=competitor_text,
            failure_analysis=failure_text,
            trend_analysis=trend_text,
            vc_analysis=vc_text,
        )
        emit("Scoring Engine", "completed")

        # ── Phase 3: Investment Recommendation ────────────────────────
        emit("Investment Recommendation Engine", "running")
        recommendation = await self.recommendation_engine.generate(
            startup=startup,
            total_score=score_breakdown.total_score,
            market_analysis=market_text,
            financial_analysis=financial_text,
            failure_analysis=failure_text,
            vc_analysis=vc_text,
            scoring_rationale=scoring_rationale,
        )
        emit("Investment Recommendation Engine", "completed")

        # ── Phase 4: Report Assembly ──────────────────────────────────
        emit("Report Assembly", "running")
        report_sections = await self._generate_report_sections(
            startup=startup,
            market_text=market_text,
            vc_text=vc_text,
            competitor_text=competitor_text,
            failure_text=failure_text,
            financial_text=financial_text,
            country_text=country_text,
            trend_text=trend_text,
            alt_strategy_text=alt_strategy_text,
            moat_text=moat_text,
            execution_text=execution_text,
            build_partner_text=build_partner_text,
            investor_fit_text=investor_fit_text,
            score=score_breakdown,
            recommendation=recommendation,
        )
        emit("Report Assembly", "completed")

        # ── Phase 5: Custom Q&A (if founder submitted questions) ──────
        custom_qa_list: list[CustomQA] = []
        if startup.custom_questions:
            emit("Custom Q&A Engine", "running")
            custom_qa_list = await self._generate_custom_qa(startup, report_sections)
            emit("Custom Q&A Engine", "completed")

        # ── Map verdict string → enum ─────────────────────────────────
        verdict_map = {
            "STRONG BUY":       Verdict.strong_buy,
            "BUY WITH CAUTION": Verdict.buy_with_caution,
            "WAIT & WATCH":     Verdict.wait_and_watch,
            "PIVOT REQUIRED":   Verdict.pivot_required,
            "DO NOT INVEST":    Verdict.do_not_invest,
        }
        verdict_str = recommendation.get("verdict", "WAIT & WATCH")
        verdict = verdict_map.get(verdict_str, Verdict.wait_and_watch)

        emit("SIOS Analysis", "complete")

        return FullReport(
            analysis_id=analysis_id,
            startup_name=startup.startup_name,

            # Original sections
            executive_summary=report_sections.get("executive_summary", ""),
            startup_overview=report_sections.get("startup_overview", ""),
            founder_analysis=report_sections.get("founder_analysis", ""),
            market_analysis=market_text,
            competitor_analysis=[],
            financial_analysis=financial_text,
            country_feasibility=[],
            risk_analysis=[],
            investment_recommendation=recommendation.get("funding_recommendation", ""),
            growth_strategy=report_sections.get("growth_strategy", ""),
            scaling_roadmap=report_sections.get("scaling_roadmap", ""),
            final_verdict=verdict,

            # NEW v2 sections
            alternative_strategies=alt_strategy_text,
            pivot_paths=[],
            moat_analysis=moat_text,
            moat_score=0,
            execution_simulation=execution_text,
            execution_risks=[],
            build_vs_partner=build_partner_text,
            build_vs_partner_matrix=[],
            investor_fit=investor_fit_text,
            investor_archetypes=[],
            fundraising_difficulty=self._extract_fundraising_difficulty(investor_fit_text),

            # Custom Q&A
            custom_qa=custom_qa_list,

            # Scores
            score_breakdown=score_breakdown,
            success_probability=success_probability,

            # Structured data
            top_risks=[],
            investor_matches=[],
            funding_recommendation=recommendation.get("funding_recommendation", ""),

            # Meta
            agent_results=agent_results,
            generated_at=datetime.utcnow().isoformat(),
        )

    def _extract_fundraising_difficulty(self, investor_fit_text: str) -> str:
        """Quick extraction of fundraising difficulty from investor fit analysis."""
        for level in ["VERY HARD", "HARD", "MODERATE", "EASY"]:
            if level in investor_fit_text.upper():
                return level
        return "MODERATE"

    async def _generate_custom_qa(self, startup: StartupInput, report_sections: dict) -> list:
        """Generate specific answers to the founder's custom questions."""
        if not startup.custom_questions:
            return []

        questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(startup.custom_questions))
        context_summary = f"""
Startup: {startup.startup_name}
Idea: {startup.idea_description[:500]}
Geography: {startup.geography}
Report Sections Available:
- Executive Summary: {report_sections.get('executive_summary', '')[:400]}
- Growth Strategy: {report_sections.get('growth_strategy', '')[:300]}
"""

        prompt = f"""You are a startup intelligence system. Answer these specific questions about the startup
with maximum specificity and actionability. Use all context from the full analysis.

{context_summary}

QUESTIONS TO ANSWER:
{questions_text}

For each question, provide a detailed, specific answer. Format as:
Q1: [answer]
Q2: [answer]
... etc."""

        try:
            raw = await self.claude.analyze(
                system_prompt="You are a startup expert. Answer the founder's specific questions with precision.",
                user_message=prompt,
                max_tokens=2000,
            )

            qa_list = []
            for i, question in enumerate(startup.custom_questions):
                marker = f"Q{i+1}:"
                next_marker = f"Q{i+2}:" if i + 1 < len(startup.custom_questions) else None

                if marker in raw:
                    start = raw.index(marker) + len(marker)
                    end = raw.index(next_marker) if next_marker and next_marker in raw else len(raw)
                    answer = raw[start:end].strip()
                else:
                    answer = "Analysis complete — refer to the relevant report sections for details on this question."

                qa_list.append(CustomQA(question=question, answer=answer))

            return qa_list
        except Exception:
            return [CustomQA(question=q, answer="Answer generation encountered an error. Please review the full report sections.") for q in startup.custom_questions]

    async def _generate_report_sections(
        self,
        startup: StartupInput,
        market_text: str,
        vc_text: str,
        competitor_text: str,
        failure_text: str,
        financial_text: str,
        country_text: str,
        trend_text: str,
        alt_strategy_text: str,
        moat_text: str,
        execution_text: str,
        build_partner_text: str,
        investor_fit_text: str,
        score: ScoreBreakdown,
        recommendation: dict,
    ) -> dict:
        system_prompt = """You are a world-class startup intelligence report writer.
You produce executive-grade reports comparable to McKinsey, Sequoia, and top-tier VC research.
Be specific, data-driven, and brutally honest. No fluff. Every sentence must add value."""

        all_data = f"""STARTUP: {startup.startup_name}
IDEA: {startup.idea_description}
SCORE: {score.total_score}/100
VERDICT: {recommendation.get('verdict', 'N/A')}

MARKET: {market_text[:1000]}
COMPETITORS: {competitor_text[:700]}
FINANCIAL: {financial_text[:900]}
RISKS: {failure_text[:700]}
COUNTRY: {country_text[:500]}
TRENDS: {trend_text[:500]}
INVESTORS: {vc_text[:500]}
ALTERNATIVE STRATEGIES: {alt_strategy_text[:600]}
MOAT ANALYSIS: {moat_text[:500]}
EXECUTION SIMULATION: {execution_text[:500]}
BUILD VS PARTNER: {build_partner_text[:400]}
INVESTOR FIT: {investor_fit_text[:400]}
RECOMMENDATION: {recommendation.get('verdict_reasoning', '')}"""

        sections_prompt = f"""Based on the complete startup intelligence data below, write these report sections:

{all_data}

Write each section clearly labeled:

## EXECUTIVE_SUMMARY
(4-5 paragraph overview: startup description, key findings, score reasoning, verdict with specific logic, and the #1 strategic opportunity or gap. Mention the new v2 insights from alternative strategies and moat analysis.)

## STARTUP_OVERVIEW
(Business model, revenue model, value proposition, target customer, go-to-market, competitive positioning)

## FOUNDER_ANALYSIS
(Founder background assessment, founder-market fit score, key strengths, key gaps, and recommended team additions)

## GROWTH_STRATEGY
(Specific recommended growth actions: customer acquisition channels, partnerships, pricing strategy, distribution approach. Reference the build vs partner insights.)

## SCALING_ROADMAP
(12-month, 24-month, 36-month milestones and scaling plan. Reference the execution simulation insights on where bottlenecks will appear.)"""

        raw = await self.claude.analyze(
            system_prompt=system_prompt,
            user_message=sections_prompt,
            max_tokens=7000,
        )

        def extract_section(text: str, section_name: str) -> str:
            marker = f"## {section_name}"
            if marker not in text:
                return ""
            start = text.index(marker) + len(marker)
            all_markers = ["## STARTUP_OVERVIEW", "## FOUNDER_ANALYSIS", "## GROWTH_STRATEGY",
                           "## SCALING_ROADMAP", "## EXECUTIVE_SUMMARY"]
            next_markers = [m for m in all_markers if m != marker]
            end = len(text)
            for nm in next_markers:
                if nm in text[start:]:
                    pos = text.index(nm, start)
                    if pos < end:
                        end = pos
            return text[start:end].strip()

        return {
            "executive_summary": extract_section(raw, "EXECUTIVE_SUMMARY"),
            "startup_overview":  extract_section(raw, "STARTUP_OVERVIEW"),
            "founder_analysis":  extract_section(raw, "FOUNDER_ANALYSIS"),
            "growth_strategy":   extract_section(raw, "GROWTH_STRATEGY"),
            "scaling_roadmap":   extract_section(raw, "SCALING_ROADMAP"),
        }

    async def generate_amended_plan(self, startup: StartupInput, report: FullReport) -> str:
        """
        Generate a complete, improved, investor-ready business plan
        incorporating all SIOS recommendations.
        Returns HTML string for PDF rendering.
        """
        system_prompt = """You are a world-class business plan writer and startup strategist.
You write investor-ready business plans that incorporate rigorous strategic analysis.
Your plans are specific, data-driven, and actionable. No fluff. Every section addresses real investor questions."""

        prompt = f"""Based on the SIOS analysis of {startup.startup_name}, create a completely improved,
investor-ready business plan that incorporates all strategic recommendations.

ORIGINAL STARTUP:
{startup.idea_description[:1000]}

SIOS FINDINGS:
- Score: {report.score_breakdown.total_score}/100
- Verdict: {report.final_verdict.value}
- Success Probability: {report.success_probability}%
- Key recommendations from Alternative Strategy: {report.alternative_strategies[:600]}
- Moat opportunities: {report.moat_analysis[:400]}
- Execution risks to mitigate: {report.execution_simulation[:400]}
- Build vs Partner key decisions: {report.build_vs_partner[:400]}
- Investor fit: {report.investor_fit[:400]}
- Growth strategy: {report.growth_strategy[:400]}

Write a complete REVISED BUSINESS PLAN with these sections:
1. Executive Summary (incorporating verdict reasoning)
2. Problem & Solution (refined based on analysis)
3. Market Opportunity (TAM/SAM/SOM with data)
4. Revised Business Model (incorporating pivot recommendations)
5. Go-To-Market Strategy (channel-specific)
6. Technology & Build vs Partner Plan
7. Financial Projections (3-year, realistic)
8. Team Requirements (gaps to fill)
9. Funding Ask & Use of Funds (corrected amount)
10. Risk Mitigation Plan (from execution simulation)
11. Competitive Moat Strategy
12. 18-Month Milestone Roadmap

Make this the best possible version of this startup idea. Be specific, realistic, and data-driven."""

        return await self.claude.analyze(
            system_prompt=system_prompt,
            user_message=prompt,
            max_tokens=8000,
        )
