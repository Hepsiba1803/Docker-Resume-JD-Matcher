from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routes import match_report  # make sure this import works
import os

print("Starting the Resume-JD Matcher API...")

web_app = FastAPI(
     title="Resume-JD Matcher API",
     version="1.0.0"
)

# CORS for frontend dev server (e.g., React / Vite)
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include backend routes
web_app.include_router(match_report.router, prefix="/api", tags=["Match Report"])

# Serve frontend
web_app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")


@web_app.get("/health")
async def health():
    return {"status": "ok"}

@web_app.get("/")
async def serve_frontend():
    path = "frontend/simpleui.html"
    if os.path.exists(path):
        return FileResponse(path)
    else:
        return {"error": "simpleui.html not found."}


