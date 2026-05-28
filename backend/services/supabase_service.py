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

    # ── Discount codes ────────────────────────────────────────────────

    def validate_discount_code(self, code: str) -> dict | None:
        """Validate a discount code and return its details if active."""
        if not self._available:
            return None
        try:
            from datetime import datetime
            res = (
                self.client.table("discount_codes")
                .select("*")
                .eq("code", code.upper())
                .eq("is_active", True)
                .execute()
            )
            if not res.data:
                return None
            discount = res.data[0]

            # Check expiry
            if discount.get("expires_at"):
                expires = datetime.fromisoformat(discount["expires_at"].replace("Z", "+00:00"))
                if expires < datetime.now(expires.tzinfo):
                    return None

            # Check max uses
            if discount.get("max_uses") and discount.get("uses_count", 0) >= discount["max_uses"]:
                return None

            return {
                "code": discount["code"],
                "discount_pct": discount["discount_pct"],
                "description": discount.get("description", ""),
            }
        except Exception:
            return None

    def apply_discount_code(self, code: str) -> bool:
        """Increment the uses_count for a discount code."""
        if not self._available:
            return False
        try:
            self.client.rpc("increment_discount_uses", {"p_code": code.upper()}).execute()
            return True
        except Exception:
            return False

    # ── ADMIN METHODS ─────────────────────────────────────────────────

    def get_admin_stats(self) -> dict:
        """Platform-wide statistics for admin dashboard."""
        if not self._available:
            return {}
        try:
            from datetime import datetime, timedelta
            today = datetime.utcnow().date().isoformat()
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()

            total_users = self.client.table("users").select("id", count="exact").execute()
            total_analyses = self.client.table("analyses").select("id", count="exact").execute()
            analyses_today = self.client.table("analyses").select("id", count="exact").gte("created_at", today).execute()
            analyses_week = self.client.table("analyses").select("id", count="exact").gte("created_at", week_ago).execute()
            analyses_month = self.client.table("analyses").select("id", count="exact").gte("created_at", month_ago).execute()
            total_payments = self.client.table("payments").select("amount_usd").eq("status", "completed").execute()

            total_revenue = sum(p.get("amount_usd", 0) for p in (total_payments.data or []))

            # Verdict breakdown
            verdicts_res = self.client.table("analyses").select("verdict").execute()
            verdict_counts: dict = {}
            for row in (verdicts_res.data or []):
                v = row.get("verdict", "unknown")
                verdict_counts[v] = verdict_counts.get(v, 0) + 1

            return {
                "users": {"total": total_users.count or 0},
                "analyses": {
                    "total": total_analyses.count or 0,
                    "today": analyses_today.count or 0,
                    "this_week": analyses_week.count or 0,
                    "this_month": analyses_month.count or 0,
                    "by_verdict": verdict_counts,
                },
                "revenue": {
                    "total_usd": round(total_revenue, 2),
                },
            }
        except Exception as e:
            print(f"get_admin_stats error: {e}")
            return {}

    def admin_list_users(self, page: int = 1, per_page: int = 50, search: str = None) -> dict:
        if not self._available:
            return {"users": [], "total": 0}
        try:
            query = self.client.table("users").select("*", count="exact")
            if search:
                query = query.ilike("email", f"%{search}%")
            offset = (page - 1) * per_page
            res = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
            return {"users": res.data or [], "total": res.count or 0, "page": page, "per_page": per_page}
        except Exception as e:
            print(f"admin_list_users error: {e}")
            return {"users": [], "total": 0}

    def admin_get_user_detail(self, user_id: str) -> dict:
        if not self._available:
            return {}
        try:
            user = self.get_user(user_id)
            analyses = self.get_user_analyses(user_id, limit=50)
            payments = self.get_user_payments(user_id)
            return {"user": user, "analyses": analyses, "payments": payments}
        except Exception as e:
            print(f"admin_get_user_detail error: {e}")
            return {}

    def admin_adjust_credits(self, user_id: str, delta: int, reason: str, admin_id: str) -> None:
        if not self._available:
            return
        try:
            # Adjust credits directly
            self.client.rpc("admin_adjust_credits", {
                "p_user_id": user_id,
                "p_delta": delta,
            }).execute()

            # Log the adjustment
            self.client.table("credit_adjustments").insert({
                "user_id": user_id,
                "admin_id": admin_id,
                "delta": delta,
                "reason": reason,
            }).execute()
        except Exception as e:
            print(f"admin_adjust_credits error: {e}")
            raise

    def admin_toggle_suspend(self, user_id: str) -> dict:
        if not self._available:
            return {}
        try:
            user = self.get_user(user_id)
            new_status = not user.get("is_suspended", False)
            self.client.table("users").update({"is_suspended": new_status}).eq("id", user_id).execute()
            return {"user_id": user_id, "is_suspended": new_status}
        except Exception as e:
            print(f"admin_toggle_suspend error: {e}")
            raise

    def admin_list_analyses(self, page: int = 1, per_page: int = 50, verdict: str = None) -> dict:
        if not self._available:
            return {"analyses": [], "total": 0}
        try:
            query = self.client.table("analyses").select(
                "id, startup_name, user_id, status, verdict, score, success_prob, created_at, completed_at",
                count="exact"
            )
            if verdict:
                query = query.eq("verdict", verdict)
            offset = (page - 1) * per_page
            res = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
            return {"analyses": res.data or [], "total": res.count or 0}
        except Exception as e:
            print(f"admin_list_analyses error: {e}")
            return {"analyses": [], "total": 0}

    def admin_delete_analysis(self, analysis_id: str) -> None:
        if not self._available:
            return
        try:
            self.client.table("reports").delete().eq("analysis_id", analysis_id).execute()
            self.client.table("analyses").delete().eq("id", analysis_id).execute()
        except Exception as e:
            print(f"admin_delete_analysis error: {e}")
            raise

    # ── Credit packs (dynamic, stored in DB) ─────────────────────────

    def admin_list_credit_packs(self) -> list:
        if not self._available:
            return []
        try:
            res = self.client.table("credit_packs").select("*").order("price_usd").execute()
            return res.data or []
        except Exception:
            return []

    def get_active_credit_packs(self) -> list:
        if not self._available:
            return []
        try:
            res = self.client.table("credit_packs").select("*").eq("is_active", True).order("price_usd").execute()
            return res.data or []
        except Exception:
            return []

    def admin_create_credit_pack(self, data: dict) -> dict:
        if not self._available:
            return {}
        try:
            res = self.client.table("credit_packs").insert(data).execute()
            return res.data[0] if res.data else {}
        except Exception as e:
            print(f"admin_create_credit_pack error: {e}")
            raise

    def admin_update_credit_pack(self, pack_id: str, updates: dict) -> dict:
        if not self._available:
            return {}
        try:
            res = self.client.table("credit_packs").update(updates).eq("id", pack_id).execute()
            return res.data[0] if res.data else {}
        except Exception as e:
            print(f"admin_update_credit_pack error: {e}")
            raise

    # ── Discount codes admin ──────────────────────────────────────────

    def admin_list_discounts(self) -> list:
        if not self._available:
            return []
        try:
            res = self.client.table("discount_codes").select("*").order("created_at", desc=True).execute()
            return res.data or []
        except Exception:
            return []

    def admin_create_discount(self, data: dict) -> dict:
        if not self._available:
            return {}
        try:
            data["code"] = data["code"].upper()
            data["uses_count"] = 0
            res = self.client.table("discount_codes").insert(data).execute()
            return res.data[0] if res.data else {}
        except Exception as e:
            print(f"admin_create_discount error: {e}")
            raise

    def admin_toggle_discount(self, discount_id: str) -> dict:
        if not self._available:
            return {}
        try:
            res = self.client.table("discount_codes").select("is_active").eq("id", discount_id).single().execute()
            new_state = not res.data.get("is_active", True)
            update_res = self.client.table("discount_codes").update({"is_active": new_state}).eq("id", discount_id).execute()
            return update_res.data[0] if update_res.data else {}
        except Exception as e:
            print(f"admin_toggle_discount error: {e}")
            raise

    def admin_delete_discount(self, discount_id: str) -> None:
        if not self._available:
            return
        try:
            self.client.table("discount_codes").delete().eq("id", discount_id).execute()
        except Exception as e:
            print(f"admin_delete_discount error: {e}")
            raise

    def admin_list_credit_adjustments(self, page: int = 1, per_page: int = 50) -> dict:
        if not self._available:
            return {"adjustments": [], "total": 0}
        try:
            offset = (page - 1) * per_page
            res = (
                self.client.table("credit_adjustments")
                .select("*", count="exact")
                .order("created_at", desc=True)
                .range(offset, offset + per_page - 1)
                .execute()
            )
            return {"adjustments": res.data or [], "total": res.count or 0}
        except Exception:
            return {"adjustments": [], "total": 0}
