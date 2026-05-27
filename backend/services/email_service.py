import resend
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

resend.api_key = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@sios.ai")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class EmailService:
    def __init__(self):
        self.enabled = bool(os.getenv("RESEND_API_KEY"))

    def send_report_ready(self, to_email: str, startup_name: str, verdict: str, score: float, analysis_id: str) -> None:
        if not self.enabled:
            return

        verdict_color = {
            "STRONG BUY": "#22c55e",
            "BUY WITH CAUTION": "#84cc16",
            "WAIT & WATCH": "#f59e0b",
            "PIVOT REQUIRED": "#f97316",
            "DO NOT INVEST": "#ef4444",
        }.get(verdict, "#6b7280")

        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0f172a;color:#f1f5f9;padding:40px;border-radius:12px;">
          <div style="text-align:center;margin-bottom:32px;">
            <span style="background:#7c3aed;color:white;padding:8px 20px;border-radius:20px;font-weight:700;font-size:18px;">SIOS</span>
            <p style="color:#94a3b8;margin-top:8px;">Startup Intelligence Operating System</p>
          </div>
          <h1 style="color:#f1f5f9;text-align:center;">Your Report is Ready!</h1>
          <p style="color:#cbd5e1;text-align:center;">AI analysis of <strong style="color:#a78bfa;">{startup_name}</strong> is complete.</p>
          <div style="background:#1e293b;border-radius:12px;padding:24px;margin:24px 0;text-align:center;">
            <div style="font-size:48px;font-weight:900;color:{verdict_color};">{score}/100</div>
            <div style="font-size:18px;font-weight:700;color:{verdict_color};margin-top:8px;">{verdict}</div>
          </div>
          <div style="text-align:center;margin-top:32px;">
            <a href="{FRONTEND_URL}/dashboard/analysis/{analysis_id}"
               style="background:#7c3aed;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:700;font-size:16px;">
              View Full Report →
            </a>
          </div>
          <p style="color:#475569;font-size:12px;text-align:center;margin-top:32px;">
            SIOS — Powered by Claude + GPT-4 + Tavily
          </p>
        </div>
        """

        try:
            resend.Emails.send({
                "from": FROM_EMAIL,
                "to": [to_email],
                "subject": f"SIOS Report Ready: {startup_name} — {verdict}",
                "html": html,
            })
        except Exception as e:
            print(f"Email send error: {e}")

    def send_payment_receipt(self, to_email: str, credits: int, amount_usd: float, payment_id: str) -> None:
        if not self.enabled:
            return

        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0f172a;color:#f1f5f9;padding:40px;border-radius:12px;">
          <h1 style="text-align:center;color:#22c55e;">Payment Confirmed!</h1>
          <div style="background:#1e293b;border-radius:12px;padding:24px;margin:24px 0;">
            <table style="width:100%;color:#cbd5e1;">
              <tr><td>Credits Added</td><td style="text-align:right;color:#a78bfa;font-weight:700;">{credits} credits</td></tr>
              <tr><td>Amount Paid</td><td style="text-align:right;">${amount_usd:.2f} USD</td></tr>
              <tr><td>Payment ID</td><td style="text-align:right;font-size:12px;color:#64748b;">{payment_id}</td></tr>
            </table>
          </div>
          <div style="text-align:center;">
            <a href="{FRONTEND_URL}/dashboard/new"
               style="background:#7c3aed;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:700;">
              Run Your Analysis →
            </a>
          </div>
        </div>
        """

        try:
            resend.Emails.send({
                "from": FROM_EMAIL,
                "to": [to_email],
                "subject": f"SIOS: {credits} credits added to your account",
                "html": html,
            })
        except Exception as e:
            print(f"Email send error: {e}")
