"""
Master Orchestrator — coordinates all 8 SIOS agents, collects results,
runs scoring engine, generates investment recommendation, and assembles
the final 12-section startup intelligence report.
"""
import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator, Callable

from models.startup_input import StartupInput
from models.report_output import (
    FullReport, Verdict, ScoreBreakdown, AgentResult,
    RiskItem, CompetitorItem, CountryRanking, InvestorMatch
)
from agents.market_agent import MarketResearchAgent
from agents.vc_investor_agent import VCInvestorAgent
from agents.competitor_agent import CompetitorAgent
from agents.failure_agent import FailureAnalysisAgent
from agents.financial_agent import FinancialCAAgent
from agents.country_agent import CountryFeasibilityAgent
from agents.trend_agent import TrendAnalysisAgent
from agents.scoring_engine import ScoringEngine
from agents.investment_recommendation import InvestmentRecommendationEngine
from services import ClaudeService


class MasterOrchestrator:
    def __init__(self):
        self.market_agent = MarketResearchAgent()
        self.vc_agent = VCInvestorAgent()
        self.competitor_agent = CompetitorAgent()
        self.failure_agent = FailureAnalysisAgent()
        self.financial_agent = FinancialCAAgent()
        self.country_agent = CountryFeasibilityAgent()
        self.trend_agent = TrendAnalysisAgent()
        self.scoring_engine = ScoringEngine()
        self.recommendation_engine = InvestmentRecommendationEngine()
        self.claude = ClaudeService()

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

        # Phase 1: Run 6 research agents in parallel
        emit("Research Phase", "starting")

        tasks = {
            "market": self.market_agent.run(startup),
            "vc": self.vc_agent.run(startup),
            "competitor": self.competitor_agent.run(startup),
            "failure": self.failure_agent.run(startup),
            "financial": self.financial_agent.run(startup),
            "country": self.country_agent.run(startup),
            "trend": self.trend_agent.run(startup),
        }

        emit("Market Research Agent", "running")
        emit("VC & Investor Agent", "running")
        emit("Competitor Analysis Agent", "running")
        emit("Failure Analysis Agent", "running")
        emit("Financial & CA Agent", "running")
        emit("Country Feasibility Agent", "running")
        emit("Trend Analysis Agent", "running")

        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )

        agent_data = dict(zip(tasks.keys(), results))

        def extract(key: str) -> str:
            r = agent_data.get(key)
            if isinstance(r, Exception):
                emit(key.upper(), f"error: {str(r)}")
                return f"Agent error: {str(r)}"
            emit(r.get("agent", key), "completed")
            agent_results.append(AgentResult(
                agent_name=r.get("agent", key),
                status="completed",
                summary=r.get("analysis", "")[:300],
                details={"openai_critique": r.get("openai_critique", "")[:200]},
            ))
            return r.get("analysis", "")

        market_text = extract("market")
        vc_text = extract("vc")
        competitor_text = extract("competitor")
        failure_text = extract("failure")
        financial_text = extract("financial")
        country_text = extract("country")
        trend_text = extract("trend")

        # Phase 2: Scoring
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

        # Phase 3: Investment Recommendation
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

        # Phase 4: Generate the 12 report sections via Claude
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
            score=score_breakdown,
            recommendation=recommendation,
        )
        emit("Report Assembly", "completed")

        # Map verdict string to enum
        verdict_map = {
            "STRONG BUY": Verdict.strong_buy,
            "BUY WITH CAUTION": Verdict.buy_with_caution,
            "WAIT & WATCH": Verdict.wait_and_watch,
            "PIVOT REQUIRED": Verdict.pivot_required,
            "DO NOT INVEST": Verdict.do_not_invest,
        }
        verdict_str = recommendation.get("verdict", "WAIT & WATCH")
        verdict = verdict_map.get(verdict_str, Verdict.wait_and_watch)

        emit("SIOS Analysis", "complete")

        return FullReport(
            analysis_id=analysis_id,
            startup_name=startup.startup_name,
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
            score_breakdown=score_breakdown,
            success_probability=success_probability,
            top_risks=[],
            investor_matches=[],
            funding_recommendation=recommendation.get("funding_recommendation", ""),
            agent_results=agent_results,
            generated_at=datetime.utcnow().isoformat(),
        )

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
        score: ScoreBreakdown,
        recommendation: dict,
    ) -> dict:
        system_prompt = """You are a world-class startup intelligence report writer.
You produce executive-grade reports comparable to McKinsey, Sequoia, and top-tier VC research.
Be specific, data-driven, and brutally honest. No fluff."""

        all_data = f"""STARTUP: {startup.startup_name}
IDEA: {startup.idea_description}
SCORE: {score.total_score}/100
VERDICT: {recommendation.get('verdict', 'N/A')}

MARKET: {market_text[:1200]}
COMPETITORS: {competitor_text[:800]}
FINANCIAL: {financial_text[:1000]}
RISKS: {failure_text[:800]}
COUNTRY: {country_text[:600]}
TRENDS: {trend_text[:600]}
INVESTORS: {vc_text[:600]}
RECOMMENDATION: {recommendation.get('verdict_reasoning', '')}"""

        sections_prompt = f"""Based on the complete startup intelligence data below, write these report sections:

{all_data}

Write each section clearly labeled:

## EXECUTIVE_SUMMARY
(3-4 paragraph overview: what this startup is, key findings, score, verdict, and why)

## STARTUP_OVERVIEW
(Business model, revenue model, value proposition, target market, go-to-market)

## FOUNDER_ANALYSIS
(Founder background assessment, founder-market fit score, key strengths, key gaps)

## GROWTH_STRATEGY
(Specific recommended growth actions: customer acquisition, partnerships, pricing, distribution)

## SCALING_ROADMAP
(12-month, 24-month, 36-month milestones and scaling plan)"""

        raw = await self.claude.analyze(
            system_prompt=system_prompt,
            user_message=sections_prompt,
            max_tokens=6000,
        )

        def extract_section(text: str, section_name: str) -> str:
            marker = f"## {section_name}"
            if marker not in text:
                return ""
            start = text.index(marker) + len(marker)
            next_markers = [f"## {s}" for s in ["STARTUP_OVERVIEW", "FOUNDER_ANALYSIS", "GROWTH_STRATEGY", "SCALING_ROADMAP", "EXECUTIVE_SUMMARY"] if f"## {s}" != marker]
            end = len(text)
            for nm in next_markers:
                if nm in text[start:]:
                    pos = text.index(nm, start)
                    if pos < end:
                        end = pos
            return text[start:end].strip()

        return {
            "executive_summary": extract_section(raw, "EXECUTIVE_SUMMARY"),
            "startup_overview": extract_section(raw, "STARTUP_OVERVIEW"),
            "founder_analysis": extract_section(raw, "FOUNDER_ANALYSIS"),
            "growth_strategy": extract_section(raw, "GROWTH_STRATEGY"),
            "scaling_roadmap": extract_section(raw, "SCALING_ROADMAP"),
        }
