from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.api import router as api_router
from backend.routers.cron import router as cron_router
from backend.services.google_sheet import google_sheets_service
from backend.config import env_settings

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

# Vercel Serverless functions can't rely on lifespan startup easily across invocations
# We initialize on first request or explicitly in endpoints if needed
# but we can try basic initialization at module load:
try:
    if env_settings.environment != "test":
        google_sheets_service.initialize_sheets()
except Exception as e:
    print(f"Init error: {e}")
