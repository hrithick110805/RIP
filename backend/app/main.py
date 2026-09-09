import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analysis_routes import router


def allowed_origins():
    """Read deployed frontend URLs while keeping local development working."""
    production_origins = os.getenv("ALLOWED_ORIGINS", "")
    configured = [origin.strip().rstrip("/") for origin in production_origins.split(",") if origin.strip()]
    return ["http://localhost:5173", "http://127.0.0.1:5173", *configured]


app = FastAPI(title="RIP Dependency Analysis API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins(),
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])
app.include_router(router)

@app.get("/")
def root(): return {"name": "RIP Dependency Analysis API", "docs": "/docs"}
