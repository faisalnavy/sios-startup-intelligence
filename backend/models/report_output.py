from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class Verdict(str, Enum):
    strong_buy = "STRONG BUY"
    buy_with_caution = "BUY WITH CAUTION"
    wait_and_watch = "WAIT & WATCH"
    pivot_required = "PIVOT REQUIRED"
    do_not_invest = "DO NOT INVEST"


class ScoreBreakdown(BaseModel):
    market_demand: float
    founder_capability: float
    unit_economics: float
    scalability: float
    competition_advantage: float
    timing: float
    financial_stability: float
    execution_capability: float
    total_score: float


class RiskItem(BaseModel):
    risk: str
    severity: str  # HIGH / MEDIUM / LOW
    mitigation: str


class CompetitorItem(BaseModel):
    name: str
    status: str  # active / failed / pivot
    strength: str
    weakness: str


class CountryRanking(BaseModel):
    country: str
    score: int
    reason: str
    challenges: str


class InvestorMatch(BaseModel):
    type: str  # VC / Angel / PE / Family Office
    name: Optional[str] = None
    thesis_match: str
    suggested_stage: str
    suggested_ticket_size: Optional[str] = None


class AgentResult(BaseModel):
    agent_name: str
    status: str  # completed / error
    summary: str
    details: dict


# ── NEW v2: Structured outputs from new agents ────────────────────────────────

class PivotPath(BaseModel):
    path_name: str          # e.g. "TempCard-only, India B2B"
    description: str
    effort: str             # LOW / MEDIUM / HIGH
    potential: str          # LOW / MEDIUM / HIGH


class BuildVsPartnerItem(BaseModel):
    capability: str         # e.g. "KYC Engine"
    decision: str           # BUILD / PARTNER / BUY
    reason: str
    suggested_partners: Optional[str] = None


class ExecutionRiskItem(BaseModel):
    risk: str
    probability_pct: int    # 0-100
    timeline: str           # e.g. "within 6 months"
    impact: str             # HIGH / MEDIUM / LOW


class InvestorArchetype(BaseModel):
    archetype: str          # e.g. "MENA Fintech VC"
    fit_score: int          # 0-100
    why_would_invest: str
    why_would_reject: str
    example_funds: Optional[str] = None


class CustomQA(BaseModel):
    question: str
    answer: str


class FullReport(BaseModel):
    analysis_id: str
    startup_name: str

    # ── Original 12 sections ─────────────────────────────────────────
    executive_summary: str
    startup_overview: str
    founder_analysis: str
    market_analysis: str
    competitor_analysis: List[CompetitorItem]
    financial_analysis: str
    country_feasibility: List[CountryRanking]
    risk_analysis: List[RiskItem]
    investment_recommendation: str
    growth_strategy: str
    scaling_roadmap: str
    final_verdict: Verdict

    # ── NEW v2: 5 new agent sections ─────────────────────────────────
    alternative_strategies: str = ""           # Alternative Strategy Agent
    pivot_paths: List[PivotPath] = []
    moat_analysis: str = ""                    # Moat Analysis Agent
    moat_score: int = 0                        # 0-100
    execution_simulation: str = ""             # Execution Simulation Agent
    execution_risks: List[ExecutionRiskItem] = []
    build_vs_partner: str = ""                 # Build vs Partner Agent
    build_vs_partner_matrix: List[BuildVsPartnerItem] = []
    investor_fit: str = ""                     # Investor Fit Agent
    investor_archetypes: List[InvestorArchetype] = []
    fundraising_difficulty: str = ""           # EASY / MODERATE / HARD / VERY HARD

    # ── NEW v2: Custom Q&A ────────────────────────────────────────────
    custom_qa: List[CustomQA] = []

    # ── Scores ───────────────────────────────────────────────────────
    score_breakdown: ScoreBreakdown
    success_probability: int  # 0-100

    # ── Structured data ──────────────────────────────────────────────
    top_risks: List[RiskItem]
    investor_matches: List[InvestorMatch]
    funding_recommendation: str

    # ── Meta ─────────────────────────────────────────────────────────
    agent_results: List[AgentResult]
    generated_at: str
