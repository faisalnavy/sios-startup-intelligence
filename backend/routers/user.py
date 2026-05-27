from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import verify_token
from services.supabase_service import SupabaseService

router = APIRouter(prefix="/api/user", tags=["user"])
db = SupabaseService()


@router.get("/profile")
def get_profile(user: dict = Depends(verify_token)):
    profile = db.get_user(user["sub"])
    if not profile:
        return {"id": user["sub"], "email": user.get("email", ""), "credits": 0, "total_reports": 0}
    return profile


@router.get("/analyses")
def get_analyses(user: dict = Depends(verify_token)):
    analyses = db.get_user_analyses(user["sub"])
    return {"analyses": analyses}


@router.get("/credits")
def get_credits(user: dict = Depends(verify_token)):
    credits = db.get_user_credits(user["sub"])
    return {"credits": credits}


@router.get("/usage")
def get_usage(user: dict = Depends(verify_token)):
    analyses = db.get_user_analyses(user["sub"], limit=100)
    payments = db.get_user_payments(user["sub"])

    by_month: dict = {}
    for a in analyses:
        month = a["created_at"][:7] if a.get("created_at") else "unknown"
        by_month.setdefault(month, 0)
        by_month[month] += 1

    total_spent = sum(p["amount_usd"] for p in payments if p["status"] == "completed")
    total_credits_bought = sum(p["credits_added"] for p in payments if p["status"] == "completed")

    return {
        "total_analyses": len(analyses),
        "total_spent_usd": round(total_spent, 2),
        "total_credits_purchased": total_credits_bought,
        "analyses_by_month": by_month,
        "verdicts": {
            v: sum(1 for a in analyses if a.get("verdict") == v)
            for v in ["STRONG BUY", "BUY WITH CAUTION", "WAIT & WATCH", "PIVOT REQUIRED", "DO NOT INVEST"]
        },
    }
