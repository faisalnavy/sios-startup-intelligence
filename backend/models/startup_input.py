from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class BusinessStage(str, Enum):
    idea = "idea"
    mvp = "mvp"
    early = "early_traction"
    growth = "growth"
    scaling = "scaling"


class StartupInput(BaseModel):
    startup_name: str = Field(..., min_length=2, max_length=100)
    idea_description: str = Field(..., min_length=50, max_length=3000)
    founder_background: Optional[str] = Field(None, max_length=1000)
    founder_experience_years: Optional[int] = Field(None, ge=0, le=50)
    target_market: Optional[str] = Field(None, max_length=500)
    geography: str = Field(..., description="Primary country or region to launch")
    revenue_model: Optional[str] = Field(None, max_length=500)
    pricing_strategy: Optional[str] = Field(None, max_length=300)
    funding_required: Optional[str] = Field(None, description="e.g. ₹50 Lakhs or $100K")
    business_stage: BusinessStage = BusinessStage.idea
    current_revenue: Optional[str] = Field(None, description="e.g. ₹0 or ₹10L/month")
    competitors_known: Optional[str] = Field(None, max_length=500)
    gtm_strategy: Optional[str] = Field(None, max_length=1000)
    unique_advantage: Optional[str] = Field(None, max_length=1000)
