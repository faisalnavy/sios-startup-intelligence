from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class BusinessStage(str, Enum):
    idea = "idea"
    mvp = "mvp"
    early = "early_traction"
    growth = "growth"
    scaling = "scaling"


class StartupInput(BaseModel):
    # ── Core fields ───────────────────────────────────────────────────
    startup_name: str = Field(..., min_length=2, max_length=100)
    idea_description: str = Field(..., min_length=50, max_length=3000)
    geography: str = Field(..., description="Primary country or region to launch")
    business_stage: BusinessStage = BusinessStage.idea

    # ── Founder ───────────────────────────────────────────────────────
    founder_background: Optional[str] = Field(None, max_length=1000)
    founder_experience_years: Optional[int] = Field(None, ge=0, le=50)

    # ── Market ────────────────────────────────────────────────────────
    target_market: Optional[str] = Field(None, max_length=500)
    competitors_known: Optional[str] = Field(None, max_length=500)
    unique_advantage: Optional[str] = Field(None, max_length=1000)

    # ── Business model ────────────────────────────────────────────────
    revenue_model: Optional[str] = Field(None, max_length=500)
    pricing_strategy: Optional[str] = Field(None, max_length=300)
    funding_required: Optional[str] = Field(None, description="e.g. ₹50 Lakhs or $100K")
    current_revenue: Optional[str] = Field(None, description="e.g. ₹0 or ₹10L/month")
    gtm_strategy: Optional[str] = Field(None, max_length=1000)

    # ── NEW v2: Business plan PDF (text extracted server-side) ────────
    business_plan_text: Optional[str] = Field(
        None,
        max_length=60000,
        description="Full text extracted from uploaded business plan PDF",
    )

    # ── NEW v2: Custom founder questions (max 10) ─────────────────────
    custom_questions: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Up to 10 specific questions the founder wants answered",
    )

    # ── NEW v2: Founder / co-founder profile URLs ─────────────────────
    founder_profile_urls: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="LinkedIn, GitHub, or personal site URLs for founders",
    )

    # ── NEW v2: Fetched profile data (filled by backend, not user) ────
    founder_profiles_data: Optional[str] = Field(
        None,
        description="Structured profile data fetched from URLs (GitHub API + Tavily)",
    )
