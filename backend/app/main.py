from fastapi import FastAPI
from backend.app.routes import match_report
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