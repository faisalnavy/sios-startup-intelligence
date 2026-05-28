"""
Admin Panel Router — SIOS v2

Protected endpoints for platform administration.
All routes require admin role (is_admin=true in Supabase users table).

Endpoints:
  GET  /api/admin/stats           — Platform usage statistics
  GET  /api/admin/users           — List all users
  GET  /api/admin/users/{id}      — Single user detail
  POST /api/admin/users/{id}/credits — Adjust user credits
  GET  /api/admin/analyses        — List all analyses
  DELETE /api/admin/analyses/{id} — Delete an analysis
  GET  /api/admin/credit-packs    — List credit packs
  POST /api/admin/credit-packs    — Create credit pack
  PUT  /api/admin/credit-packs/{id} — Update credit pack
  DELETE /api/admin/credit-packs/{id} — Delete credit pack
  GET  /api/admin/discounts       — List discount codes
  POST /api/admin/discounts       — Create discount code
  PUT  /api/admin/discounts/{id}/toggle — Enable/disable code
  DELETE /api/admin/discounts/{id} — Delete discount code
  GET  /api/admin/credit-adjustments — Audit log
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from middleware.auth import verify_admin
from services.supabase_service import SupabaseService

router = APIRouter(prefix="/api/admin", tags=["admin"])
db = SupabaseService()


# ── Request / Response Models ─────────────────────────────────────────────────

class CreditAdjustRequest(BaseModel):
    delta: int                  # positive = add, negative = deduct
    reason: str

class CreditPackCreate(BaseModel):
    name: str
    credits: int
    price_usd: float
    description: Optional[str] = ""
    is_popular: bool = False
    is_active: bool = True

class CreditPackUpdate(BaseModel):
    name: Optional[str] = None
    credits: Optional[int] = None
    price_usd: Optional[float] = None
    description: Optional[str] = None
    is_popular: Optional[bool] = None
    is_active: Optional[bool] = None

class DiscountCreate(BaseModel):
    code: str
    discount_pct: int           # 1-100
    max_uses: Optional[int] = None
    expires_at: Optional[str] = None   # ISO datetime string
    description: Optional[str] = ""


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(admin=Depends(verify_admin)):
    """Platform-wide usage statistics."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        stats = db.get_admin_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    page: int = 1,
    per_page: int = 50,
    search: Optional[str] = None,
    admin=Depends(verify_admin),
):
    """List all users with pagination and optional search."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        return db.admin_list_users(page=page, per_page=per_page, search=search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user_detail(user_id: str, admin=Depends(verify_admin)):
    """Get full detail for a single user including analyses and payment history."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        return db.admin_get_user_detail(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/credits")
async def adjust_credits(
    user_id: str,
    body: CreditAdjustRequest,
    admin: dict = Depends(verify_admin),
):
    """Manually add or remove credits from a user account (with audit log)."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    if body.delta == 0:
        raise HTTPException(status_code=400, detail="Delta cannot be zero")
    try:
        db.admin_adjust_credits(
            user_id=user_id,
            delta=body.delta,
            reason=body.reason,
            admin_id=admin.get("sub", "unknown"),
        )
        return {"success": True, "message": f"Credits adjusted by {body.delta}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/suspend")
async def toggle_suspend_user(user_id: str, admin=Depends(verify_admin)):
    """Suspend or unsuspend a user."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        result = db.admin_toggle_suspend(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Analyses ─────────────────────────────────────────────────────────────────

@router.get("/analyses")
async def list_analyses(
    page: int = 1,
    per_page: int = 50,
    verdict: Optional[str] = None,
    admin=Depends(verify_admin),
):
    """List all analyses across all users."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        return db.admin_list_analyses(page=page, per_page=per_page, verdict=verdict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: str, admin=Depends(verify_admin)):
    """Delete an analysis and its report (moderation)."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        db.admin_delete_analysis(analysis_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Credit Packs ─────────────────────────────────────────────────────────────

@router.get("/credit-packs")
async def list_credit_packs(admin=Depends(verify_admin)):
    """List all credit packs including inactive ones."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        return db.admin_list_credit_packs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credit-packs")
async def create_credit_pack(body: CreditPackCreate, admin=Depends(verify_admin)):
    """Create a new credit pack."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        return db.admin_create_credit_pack(body.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/credit-packs/{pack_id}")
async def update_credit_pack(pack_id: str, body: CreditPackUpdate, admin=Depends(verify_admin)):
    """Update a credit pack (price, credits, name, etc.)."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    try:
        return db.admin_update_credit_pack(pack_id, updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/credit-packs/{pack_id}")
async def delete_credit_pack(pack_id: str, admin=Depends(verify_admin)):
    """Deactivate (soft-delete) a credit pack."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        db.admin_update_credit_pack(pack_id, {"is_active": False})
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Discount Codes ────────────────────────────────────────────────────────────

@router.get("/discounts")
async def list_discounts(admin=Depends(verify_admin)):
    """List all discount codes."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        return db.admin_list_discounts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discounts")
async def create_discount(body: DiscountCreate, admin=Depends(verify_admin)):
    """Create a new discount code."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    if not 1 <= body.discount_pct <= 100:
        raise HTTPException(status_code=400, detail="discount_pct must be 1-100")
    try:
        return db.admin_create_discount(body.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/discounts/{discount_id}/toggle")
async def toggle_discount(discount_id: str, admin=Depends(verify_admin)):
    """Enable or disable a discount code."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        return db.admin_toggle_discount(discount_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/discounts/{discount_id}")
async def delete_discount(discount_id: str, admin=Depends(verify_admin)):
    """Permanently delete a discount code."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        db.admin_delete_discount(discount_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Audit Log ─────────────────────────────────────────────────────────────────

@router.get("/credit-adjustments")
async def list_credit_adjustments(
    page: int = 1,
    per_page: int = 50,
    admin=Depends(verify_admin),
):
    """Full audit log of all manual credit adjustments."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        return db.admin_list_credit_adjustments(page=page, per_page=per_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Discount validation (public endpoint for checkout) ───────────────────────

@router.get("/discounts/validate/{code}")
async def validate_discount_code(code: str):
    """Public endpoint — validates a discount code during checkout."""
    if not db.is_available():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        result = db.validate_discount_code(code.upper())
        if not result:
            raise HTTPException(status_code=404, detail="Invalid or expired discount code")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
