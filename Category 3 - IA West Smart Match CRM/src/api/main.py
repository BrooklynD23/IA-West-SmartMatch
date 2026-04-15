"""FastAPI application entrypoint for the IA West Smart Match CRM backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import calendar, crawler, data, feedback, matching, outreach, portals, qr

app = FastAPI(title="IA West SmartMatch API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(qr.router, prefix="/api/qr", tags=["qr"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(matching.router, prefix="/api/matching", tags=["matching"])
app.include_router(outreach.router, prefix="/api/outreach", tags=["outreach"])
app.include_router(crawler.router, prefix="/api/crawler", tags=["crawler"])
app.include_router(portals.router, prefix="/api/portals", tags=["portals"])


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Return a minimal health payload for local dev and smoke tests."""
    return {"status": "ok"}
