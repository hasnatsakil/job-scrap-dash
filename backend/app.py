import logging, os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config import env_settings
from backend.services.database import db_client
from backend.scheduler import setup_scheduler
from backend.routers.api import router as api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    db_client.verify_connection()
    setup_scheduler()
    yield

app = FastAPI(title="AI Job Scraper", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api")

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    @app.api_route("/{path_name:path}", methods=["GET"])
    async def catch_all(path_name: str):
        if path_name.startswith("api/"): return {"error": "Not found"}
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file): return FileResponse(index_file)
        return {"error": "Frontend build not found"}
else: logger.warning("Frontend dist not found. API only mode.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=env_settings.port, reload=True)

# Phase 1: Authentication logic removed
