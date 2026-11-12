from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import advisor, db, dictionary
from .config import COUNTRY, GEMINI_API_KEY, GEMINI_MODEL, SARVAM_API_KEY, STATIC_DIR


@asynccontextmanager
async def lifespan(_app):
    db.init_db()
    yield


app = FastAPI(title="Vyapar Mitra - AI Business Advisory", lifespan=lifespan)


class Profile(BaseModel):
    name: str = Field(min_length=1)
    segment: str
    business: str = ""
    location: str = ""
    state: str = ""
    language: str = "English"
    stage: str = ""
    turnover: str = ""
    details: str = ""


class Ask(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    profile_id: Optional[int] = None
    mode: str = "quick"
    lat: Optional[float] = None
    lng: Optional[float] = None


class Knowledge(BaseModel):
    segment: str
    category: str
    title: str = Field(min_length=2)
    summary: str = Field(min_length=2)
    eligibility: str = ""
    benefits: str = ""
    how_to_apply: str = ""
    url: str = ""
    tags: str = ""


@app.get("/api/status")
def status():
    return {
        "ai_enabled": advisor.ai_enabled(),
        "model": " + ".join(
            [m for m in (GEMINI_MODEL if GEMINI_API_KEY else "", "Sarvam fallback" if SARVAM_API_KEY else "") if m]
        ) or "offline-knowledge-base",
        "country": COUNTRY,
        "segments": advisor.SEGMENTS,
        "modes": list(advisor.MODES),
    }


@app.get("/api/profiles")
def list_profiles():
    return db.list_profiles()


@app.post("/api/profiles")
def create_profile(p: Profile):
    if p.segment not in advisor.SEGMENTS:
        raise HTTPException(400, "Unknown segment")
    return db.save_profile(p.model_dump())


@app.put("/api/profiles/{pid}")
def update_profile(pid: int, p: Profile):
    if not db.get_profile(pid):
        raise HTTPException(404, "Profile not found")
    return db.save_profile(p.model_dump(), pid)


@app.delete("/api/profiles/{pid}")
def delete_profile(pid: int):
    db.delete_profile(pid)
    return {"ok": True}


@app.post("/api/ask")
def ask(body: Ask):
    profile = db.get_profile(body.profile_id) if body.profile_id else None
    mode = body.mode if body.mode in advisor.MODES else "quick"
    try:
        result = advisor.ask(body.question, profile, mode, body.lat, body.lng)
    except Exception as e:  # surface API problems (bad key, quota) to the UI
        if isinstance(e, httpx.TransportError):
            raise HTTPException(502, "Cannot reach Google right now. Check your internet connection and try again.")
        code = getattr(e, "code", None)
        msg = {
            400: "Google rejected the request. Check that GEMINI_API_KEY in .env is correct.",
            429: "The Gemini API key has run out of free quota for now. Wait a minute and try again, or enable billing in Google AI Studio.",
            503: "Google's Gemini servers are busy right now. Please try again in a minute.",
        }.get(code, f"AI service error: {e}")
        raise HTTPException(502, msg)
    cid = db.add_conversation(
        body.profile_id, mode, body.question, result["answer"],
        result["sources"], result["search_queries"], result["model"],
    )
    return {"id": cid, "mode": mode, "question": body.question, **result}


@app.get("/api/history")
def history(profile_id: Optional[int] = None, limit: int = 50):
    return db.history(profile_id, limit)


@app.delete("/api/history/{cid}")
def delete_history(cid: int):
    db.delete_conversation(cid)
    return {"ok": True}


@app.get("/api/knowledge")
def knowledge(q: str = "", segment: Optional[str] = None):
    return db.search_knowledge(q, segment or None, limit=50)


@app.post("/api/knowledge")
def add_knowledge(k: Knowledge):
    try:
        return db.add_knowledge(k.model_dump())
    except Exception as e:
        raise HTTPException(400, str(e))


@app.delete("/api/knowledge/{kid}")
def delete_knowledge(kid: int):
    db.delete_knowledge(kid)
    return {"ok": True}


@app.get("/api/dictionary")
def get_dictionary(q: str = "", category: str = ""):
    return dictionary.search(q, category or "", limit=100)


@app.get("/api/startup-toolkit")
def startup_toolkit():
    return dictionary.playbooks()


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
