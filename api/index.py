from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.api import router as api_router
from backend.routers.cron import router as cron_router

app = FastAPI(title="AI Job Scraper - Vercel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(cron_router)
