from fastapi import FastAPI
from .routes import match_report
from fastapi.middleware.cors import CORSMiddleware

print("Starting the Resume-JD Matcher API...")
web_app = FastAPI(
    title="Resume-JD Matcher API",
    version="1.0.0"
)
@web_app.get("/")
async def root():
    return {"message":"Welcome to Resume Parser API"}
web_app.include_router(match_report.router,prefix="/api",tags=["Match Report"])

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount frontend's built files
web_app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Optional: serve index.html at root if you want frontend as default landing page
@web_app.get("/")
async def serve_frontend():
    return FileResponse("frontend/simpleui.html")
