from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analysis_routes import router

app = FastAPI(title="RIP Dependency Analysis API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])
app.include_router(router)

@app.get("/")
def root(): return {"name": "RIP Dependency Analysis API", "docs": "/docs"}
