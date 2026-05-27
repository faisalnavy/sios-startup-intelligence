from fastapi import FastAPI, HTTPException, Depends
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
from typing import Dict, Any

load_dotenv(Path(__file__).parent / ".env", override=True)

from models.startup_input import StartupInput
from models.report_output import FullReport
from agents.master_orchestrator import MasterOrchestrator
from services.supabase_service import SupabaseService
from services.email_service import EmailService
from middleware.auth import verify_token, optional_token
from routers import payments as payments_router
from routers import user as user_router


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
    description="AI-powered startup analysis with dual Claude + OpenAI cross-validation",
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

# In-memory store (also persisted to Supabase)
analyses: Dict[str, Any] = {}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "SIOS",
        "version": "2.0.0",
        "supabase": db.is_available(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/analyze")
async def start_analysis(startup: StartupInput, user: dict = Depends(optional_token)):
    analysis_id = str(uuid.uuid4())
    user_id = user["sub"] if user else "anonymous"

    # Check credits if authenticated
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

    # Persist to Supabase
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

        # Save to Supabase
        if user_id and db.is_available():
            db.update_analysis_complete(
                analysis_id,
                report.final_verdict.value if report.final_verdict else "WAIT & WATCH",
                report.score_breakdown.total_score if report.score_breakdown else 0,
                report.success_probability or 0,
            )
            db.save_report(analysis_id, report_dict)

            # Send email notification
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


@app.get("/api/analysis/{analysis_id}/stream")
async def stream_progress(analysis_id: str):
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")

    async def event_generator():
        last_sent = 0
        while True:
            data = analyses[analysis_id]
            progress = data["progress"]

            if len(progress) > last_sent:
                for event in progress[last_sent:]:
                    yield {"event": "progress", "data": json.dumps(event)}
                last_sent = len(progress)

            if data["status"] == "completed":
                yield {"event": "complete", "data": json.dumps({"status": "completed", "analysis_id": analysis_id})}
                break
            elif data["status"] == "error":
                yield {"event": "error", "data": json.dumps({"error": data["error"]})}
                break

            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())


@app.get("/api/analysis/{analysis_id}/report")
async def get_report(analysis_id: str):
    if analysis_id not in analyses:
        # Try Supabase for historical reports
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
        "created_at": data["created_at"],
    }


@app.get("/api/share/{share_token}")
async def get_shared_report(share_token: str):
    """Public endpoint — returns report for a share token."""
    if not db.is_available():
        raise HTTPException(status_code=404, detail="Not found")
    try:
        res = db.client.table("analyses").select("id").eq("share_token", share_token).eq("is_public", True).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Report not found or not public")
        analysis_id = res.data["id"]
        report_row = db.get_report_by_analysis(analysis_id)
        return report_row["report_data"] if report_row else HTTPException(status_code=404, detail="Report not generated yet")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=False)
