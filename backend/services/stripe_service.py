import stripe
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

CREDIT_PACKS = {
    "starter":  {"credits": 5,  "amount_usd": 5.00,  "price_id": os.getenv("STRIPE_PRICE_5", "")},
    "popular":  {"credits": 25, "amount_usd": 20.00, "price_id": os.getenv("STRIPE_PRICE_20", "")},
    "pro":      {"credits": 70, "amount_usd": 50.00, "price_id": os.getenv("STRIPE_PRICE_50", "")},
}


class StripeService:
    def __init__(self):
        self.enabled = bool(os.getenv("STRIPE_SECRET_KEY"))

    def create_checkout_session(self, pack_id: str, user_id: str, user_email: str, frontend_url: str) -> dict:
        if not self.enabled:
            raise ValueError("Stripe not configured")

        pack = CREDIT_PACKS.get(pack_id)
        if not pack:
            raise ValueError(f"Unknown pack: {pack_id}")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            customer_email=user_email,
            line_items=[{"price": pack["price_id"], "quantity": 1}],
            metadata={"user_id": user_id, "pack_id": pack_id, "credits": pack["credits"]},
            success_url=f"{frontend_url}/dashboard/credits?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/dashboard/credits?cancelled=true",
        )
        return {"checkout_url": session.url, "session_id": session.id}

    def create_payment_intent(self, pack_id: str, user_id: str) -> dict:
        """For inline card payments (alternative to checkout)."""
        if not self.enabled:
            raise ValueError("Stripe not configured")

        pack = CREDIT_PACKS.get(pack_id)
        if not pack:
            raise ValueError(f"Unknown pack: {pack_id}")

        intent = stripe.PaymentIntent.create(
            amount=int(pack["amount_usd"] * 100),
            currency="usd",
            metadata={"user_id": user_id, "pack_id": pack_id, "credits": pack["credits"]},
        )
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount_usd": pack["amount_usd"],
            "credits": pack["credits"],
        }

    def verify_webhook(self, payload: bytes, sig_header: str) -> stripe.Event:
        secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        return stripe.Webhook.construct_event(payload, sig_header, secret)

    def get_packs(self) -> dict:
        return CREDIT_PACKS
