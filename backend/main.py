from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

load_dotenv(Path(__file__).parent / ".env", override=True)

from models.startup_input import StartupInput
from models.report_output import FullReport
from agents.master_orchestrator import MasterOrchestrator
from services.supabase_service import SupabaseService
from services.email_service import EmailService
from middleware.auth import verify_token, optional_token
from routers import payments as payments_router
from routers import user as user_router
from routers import admin as admin_router


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:3000"
    port: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
db = SupabaseService()
email_svc = EmailService()

app = FastAPI(
    title="SIOS — Startup Intelligence Operating System",
    description="AI-powered startup analysis: 12 agents, dual Claude + OpenAI cross-validation",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments_router.router)
app.include_router(user_router.router)
app.include_router(admin_router.router)

# In-memory analysis store (also persisted to Supabase)
analyses: Dict[str, Any] = {}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "SIOS",
        "version": "2.0.0",
        "agents": 12,
        "supabase": db.is_available(),
        "timestamp": datetime.utcnow().isoformat(),
    }


# ── Business Plan PDF Upload ──────────────────────────────────────────────────

@app.post("/api/upload/business-plan")
async def upload_business_plan(file: UploadFile = File(...)):
    """
    Accept a PDF file, extract its text content, and return it.
    The client includes the returned text in the analysis form submission.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Size check: 10MB max
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB.")

    try:
        import fitz  # PyMuPDF
        import io
        doc = fitz.open(stream=io.BytesIO(content), filetype="pdf")
        pages = doc.page_count

        text_parts = []
        for page_num in range(min(pages, 50)):  # Cap at 50 pages
            page = doc[page_num]
            text_parts.append(page.get_text())

        extracted_text = "\n\n".join(text_parts).strip()
        word_count = len(extracted_text.split())

        if word_count < 50:
            raise HTTPException(
                status_code=422,
                detail="PDF appears to be a scanned image or has very little text. Please use a text-based PDF."
            )

        return {
            "text": extracted_text[:60000],  # Cap to avoid token overflow
            "pages": pages,
            "word_count": word_count,
            "filename": file.filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract PDF text: {str(e)}")


# ── Analysis ──────────────────────────────────────────────────────────────────

@app.post("/api/analyze")
async def start_analysis(startup: StartupInput, user: dict = Depends(optional_token)):
    analysis_id = str(uuid.uuid4())
    user_id = user["sub"] if user else "anonymous"

    # Credit check for authenticated users
    if user and db.is_available():
        credits = db.get_user_credits(user_id)
        if credits < 1:
            raise HTTPException(status_code=402, detail="Insufficient credits. Please purchase more credits.")
        db.deduct_credit(user_id, analysis_id)

    analyses[analysis_id] = {
        "status": "queued",
        "startup_name": startup.startup_name,
        "user_id": user_id,
        "progress": [],
        "report": None,
        "error": None,
        "created_at": datetime.utcnow().isoformat(),
    }

    if user and db.is_available():
        db.save_analysis(analysis_id, user_id, startup.startup_name, startup.model_dump())

    asyncio.create_task(_run_analysis(analysis_id, startup, user_id if user else None))
    return {"analysis_id": analysis_id, "status": "queued"}


async def _run_analysis(analysis_id: str, startup: StartupInput, user_id: str | None):
    analyses[analysis_id]["status"] = "running"
    orchestrator = MasterOrchestrator()

    def on_progress(agent: str, status: str):
        analyses[analysis_id]["progress"].append({
            "agent": agent,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        })

    try:
        report = await orchestrator.analyze(startup, progress_callback=on_progress)
        report_dict = report.model_dump()
        analyses[analysis_id]["report"] = report_dict
        analyses[analysis_id]["status"] = "completed"

        if user_id and db.is_available():
            db.update_analysis_complete(
                analysis_id,
                report.final_verdict.value if report.final_verdict else "WAIT & WATCH",
                report.score_breakdown.total_score if report.score_breakdown else 0,
                report.success_probability or 0,
            )
            db.save_report(analysis_id, report_dict)

            user = db.get_user(user_id)
            if user:
                email_svc.send_report_ready(
                    user["email"],
                    startup.startup_name,
                    report.final_verdict.value if report.final_verdict else "WAIT & WATCH",
                    report.score_breakdown.total_score if report.score_breakdown else 0,
                    analysis_id,
                )

    except Exception as e:
        analyses[analysis_id]["status"] = "error"
        analyses[analysis_id]["error"] = str(e)


# ── Streaming Progress ────────────────────────────────────────────────────────

@app.get("/api/analysis/{analysis_id}/stream")
async def stream_progress(analysis_id: str):
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    async def event_generator():
        last_sent = 0
        idle_ticks = 0
        while True:
            data = analyses[analysis_id]
            progress = data["progress"]

            if len(progress) > last_sent:
                for event in progress[last_sent:]:
                    yield {"event": "progress", "data": json.dumps(event)}
                last_sent = len(progress)
                idle_ticks = 0
            else:
                idle_ticks += 1
                # Send a keepalive comment every 20s to prevent Railway proxy timeout
                if idle_ticks % 40 == 0:
                    yield {"event": "heartbeat", "data": json.dumps({"ts": datetime.utcnow().isoformat()})}

            if data["status"] == "completed":
                yield {"event": "complete", "data": json.dumps({"status": "completed", "analysis_id": analysis_id})}
                break
            elif data["status"] == "error":
                yield {"event": "error", "data": json.dumps({"error": data["error"]})}
                break

            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())


# ── Report & Status ───────────────────────────────────────────────────────────

@app.get("/api/analysis/{analysis_id}/report")
async def get_report(analysis_id: str):
    if analysis_id not in analyses:
        if db.is_available():
            report_row = db.get_report_by_analysis(analysis_id)
            if report_row:
                return report_row["report_data"]
        raise HTTPException(status_code=404, detail="Analysis not found")

    data = analyses[analysis_id]
    if data["status"] in ("running", "queued"):
        return {"status": data["status"], "message": "Analysis still in progress"}
    if data["status"] == "error":
        raise HTTPException(status_code=500, detail=data["error"])
    return data["report"]


@app.get("/api/analysis/{analysis_id}/status")
async def get_status(analysis_id: str):
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    data = analyses[analysis_id]
    return {
        "analysis_id": analysis_id,
        "status": data["status"],
        "startup_name": data["startup_name"],
        "progress": data["progress"],
        "error": data.get("error"),
        "created_at": data["created_at"],
    }


# ── Amended Business Plan ─────────────────────────────────────────────────────

@app.post("/api/analysis/{analysis_id}/generate-plan")
async def generate_amended_plan(
    analysis_id: str,
    user: dict = Depends(verify_token),
):
    """
    Generate an optimized, investor-ready amended business plan
    based on SIOS analysis findings. Costs 2 additional credits.
    """
    user_id = user["sub"]

    # Credit check (amended plan costs 2 credits)
    if db.is_available():
        credits = db.get_user_credits(user_id)
        if credits < 2:
            raise HTTPException(status_code=402, detail="Generating an amended plan requires 2 credits.")

    # Get the report
    report_data = None
    if analysis_id in analyses and analyses[analysis_id]["status"] == "completed":
        report_data = analyses[analysis_id]["report"]
    elif db.is_available():
        row = db.get_report_by_analysis(analysis_id)
        if row:
            report_data = row["report_data"]

    if not report_data:
        raise HTTPException(status_code=404, detail="Analysis report not found or not completed yet")

    # Reconstruct startup input from analysis input_data
    startup_data = None
    if db.is_available():
        try:
            res = db.client.table("analyses").select("input_data").eq("id", analysis_id).single().execute()
            startup_data = res.data.get("input_data") if res.data else None
        except Exception:
            pass

    if not startup_data:
        raise HTTPException(status_code=404, detail="Original startup input not found")

    try:
        from models.startup_input import StartupInput
        from models.report_output import FullReport
        startup = StartupInput(**startup_data)
        report = FullReport(**report_data)

        # Deduct 2 credits
        if db.is_available():
            db.add_credits(user_id, -2, "Amended business plan generation", analysis_id)

        orchestrator = MasterOrchestrator()
        plan_text = await orchestrator.generate_amended_plan(startup, report)

        return {
            "analysis_id": analysis_id,
            "startup_name": startup.startup_name,
            "amended_plan": plan_text,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


# ── Public Share ──────────────────────────────────────────────────────────────

@app.get("/api/share/{share_token}")
async def get_shared_report(share_token: str):
    if not db.is_available():
        raise HTTPException(status_code=404, detail="Not found")
    try:
        res = db.client.table("analyses").select("id").eq("share_token", share_token).eq("is_public", True).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Report not found or not public")
        analysis_id = res.data["id"]
        report_row = db.get_report_by_analysis(analysis_id)
        if report_row:
            return report_row["report_data"]
        raise HTTPException(status_code=404, detail="Report not generated yet")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Not found")


# ── Credit packs (dynamic from DB with fallback) ──────────────────────────────

@app.get("/api/payments/packs-dynamic")
async def get_dynamic_packs():
    """Return active credit packs from DB (admin-editable)."""
    if db.is_available():
        packs = db.get_active_credit_packs()
        if packs:
            return {"packs": packs}
    # Fallback to static packs
    return {
        "packs": [
            {"id": "starter", "name": "Starter", "credits": 5, "price_usd": 9.99, "description": "Perfect for exploring", "is_popular": False},
            {"id": "growth",  "name": "Growth",  "credits": 20, "price_usd": 29.99, "description": "For active founders", "is_popular": True},
            {"id": "scale",   "name": "Scale",   "credits": 50, "price_usd": 59.99, "description": "For teams and VCs", "is_popular": False},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=False)
