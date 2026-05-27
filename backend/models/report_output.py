from pydantic import BaseModel
from typing import Optional, List
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
    name: Optional[str]
    thesis_match: str
    suggested_stage: str
    suggested_ticket_size: Optional[str]


class AgentResult(BaseModel):
    agent_name: str
    status: str  # completed / error
    summary: str
    details: dict


class FullReport(BaseModel):
    analysis_id: str
    startup_name: str

    # 12 sections
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

    # Scores
    score_breakdown: ScoreBreakdown
    success_probability: int  # 0-100

    # Structured data
    top_risks: List[RiskItem]
    investor_matches: List[InvestorMatch]
    funding_recommendation: str

    # Meta
    agent_results: List[AgentResult]
    generated_at: str
