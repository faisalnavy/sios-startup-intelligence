from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials
from middleware.auth import verify_token
from services.stripe_service import StripeService, CREDIT_PACKS
from services.supabase_service import SupabaseService
from services.email_service import EmailService
import os

router = APIRouter(prefix="/api/payments", tags=["payments"])
stripe_svc = StripeService()
db = SupabaseService()
email_svc = EmailService()


@router.get("/packs")
def get_credit_packs():
    """Return available credit packs."""
    packs = []
    for pack_id, pack in CREDIT_PACKS.items():
        packs.append({
            "id": pack_id,
            "credits": pack["credits"],
            "amount_usd": pack["amount_usd"],
            "label": {
                "starter": "Starter",
                "popular": "Popular",
                "pro": "Pro",
            }.get(pack_id, pack_id),
            "popular": pack_id == "popular",
        })
    return {"packs": packs}


@router.post("/checkout")
def create_checkout(pack_id: str, user: dict = Depends(verify_token)):
    """Create Stripe checkout session and return redirect URL."""
    user_id = user["sub"]
    user_email = user.get("email", "")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    try:
        result = stripe_svc.create_checkout_session(pack_id, user_id, user_email, frontend_url)
        # Save pending payment
        pack = CREDIT_PACKS[pack_id]
        db.save_payment(user_id, "stripe", result["session_id"], pack["amount_usd"], pack["credits"])
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment error: {e}")


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Stripe webhook — called when payment completes."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe_svc.verify_webhook(payload, sig)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        credits = int(metadata.get("credits", 0))
        pack_id = metadata.get("pack_id", "")
        session_id = session["id"]
        receipt_url = session.get("receipt_url")

        if user_id and credits:
            payment = db.complete_payment(session_id, receipt_url)
            payment_id = payment["id"] if payment else None
            db.add_credits(user_id, credits, f"Purchased {credits} credits ({pack_id} pack)", payment_id)

            # Send email
            user = db.get_user(user_id)
            if user:
                pack = CREDIT_PACKS.get(pack_id, {})
                email_svc.send_payment_receipt(user["email"], credits, pack.get("amount_usd", 0), session_id)

    return {"received": True}


@router.get("/history")
def payment_history(user: dict = Depends(verify_token)):
    """Get user's payment history."""
    payments = db.get_user_payments(user["sub"])
    return {"payments": payments}
