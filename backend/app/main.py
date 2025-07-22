from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routes import match_report  # make sure this import works

print("Starting the Resume-JD Matcher API...")

web_app = FastAPI(
     title="Resume-JD Matcher API",
     version="1.0.0"
)

# CORS for frontend dev server (e.g., React / Vite)
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include backend routes
web_app.include_router(match_report.router, prefix="/api", tags=["Match Report"])

# Serve frontend
web_app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Serve the main frontend page at root
@web_app.get("/")
async def serve_frontend():
    return FileResponse("frontend/simpleui.html")
