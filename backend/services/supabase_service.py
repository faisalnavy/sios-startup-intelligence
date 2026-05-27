from supabase import create_client, Client
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / ".env", override=True)


def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)


class SupabaseService:
    def __init__(self):
        self.client = get_supabase()
        self._available = self.client is not None

    def is_available(self) -> bool:
        return self._available

    # ── User ──────────────────────────────────────────────────────────

    def get_user(self, user_id: str) -> dict | None:
        if not self._available:
            return None
        try:
            res = self.client.table("users").select("*").eq("id", user_id).single().execute()
            return res.data
        except Exception:
            return None

    def get_user_credits(self, user_id: str) -> int:
        user = self.get_user(user_id)
        return user["credits"] if user else 0

    def deduct_credit(self, user_id: str, analysis_id: str) -> bool:
        if not self._available:
            return True  # skip check if Supabase not configured
        try:
            res = self.client.rpc("use_credit", {"p_user_id": user_id, "p_analysis_id": analysis_id}).execute()
            return res.data
        except Exception:
            return False

    def add_credits(self, user_id: str, amount: int, description: str, payment_id: str = None) -> None:
        if not self._available:
            return
        try:
            self.client.rpc("add_credits", {
                "p_user_id": user_id,
                "p_amount": amount,
                "p_description": description,
                "p_payment_id": payment_id,
            }).execute()
        except Exception as e:
            print(f"add_credits error: {e}")

    # ── Analysis ──────────────────────────────────────────────────────

    def save_analysis(self, analysis_id: str, user_id: str, startup_name: str, input_data: dict) -> None:
        if not self._available:
            return
        try:
            self.client.table("analyses").upsert({
                "id": analysis_id,
                "user_id": user_id,
                "startup_name": startup_name,
                "input_data": input_data,
                "status": "running",
            }).execute()
        except Exception as e:
            print(f"save_analysis error: {e}")

    def update_analysis_complete(self, analysis_id: str, verdict: str, score: float, success_prob: int) -> None:
        if not self._available:
            return
        try:
            from datetime import datetime
            self.client.table("analyses").update({
                "status": "completed",
                "verdict": verdict,
                "score": score,
                "success_prob": success_prob,
                "completed_at": datetime.utcnow().isoformat(),
            }).eq("id", analysis_id).execute()
        except Exception as e:
            print(f"update_analysis error: {e}")

    def save_report(self, analysis_id: str, report_data: dict) -> None:
        if not self._available:
            return
        try:
            self.client.table("reports").upsert({
                "analysis_id": analysis_id,
                "report_data": report_data,
            }).execute()
        except Exception as e:
            print(f"save_report error: {e}")

    def get_user_analyses(self, user_id: str, limit: int = 20) -> list:
        if not self._available:
            return []
        try:
            res = (
                self.client.table("analyses")
                .select("id, startup_name, status, verdict, score, success_prob, created_at, completed_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return res.data or []
        except Exception:
            return []

    def get_report_by_analysis(self, analysis_id: str) -> dict | None:
        if not self._available:
            return None
        try:
            res = self.client.table("reports").select("*").eq("analysis_id", analysis_id).single().execute()
            return res.data
        except Exception:
            return None

    # ── Payments ──────────────────────────────────────────────────────

    def save_payment(self, user_id: str, gateway: str, gateway_id: str, amount_usd: float, credits: int) -> str:
        if not self._available:
            return None
        try:
            res = self.client.table("payments").insert({
                "user_id": user_id,
                "gateway": gateway,
                "gateway_id": gateway_id,
                "amount_usd": amount_usd,
                "credits_added": credits,
                "status": "pending",
            }).execute()
            return res.data[0]["id"] if res.data else None
        except Exception as e:
            print(f"save_payment error: {e}")
            return None

    def complete_payment(self, gateway_id: str, receipt_url: str = None) -> dict | None:
        if not self._available:
            return None
        try:
            from datetime import datetime
            res = (
                self.client.table("payments")
                .update({"status": "completed", "receipt_url": receipt_url, "completed_at": datetime.utcnow().isoformat()})
                .eq("gateway_id", gateway_id)
                .execute()
            )
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"complete_payment error: {e}")
            return None

    def get_user_payments(self, user_id: str) -> list:
        if not self._available:
            return []
        try:
            res = (
                self.client.table("payments")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            return res.data or []
        except Exception:
            return []
