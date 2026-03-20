import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException
from bimba3d_backend.app.api.projects import router as projects_router
from bimba3d_backend.app.api.auth import router as auth_router
from bimba3d_backend.app.api.admin import router as admin_router
from bimba3d_backend.app.config import (
    ALLOWED_ORIGINS,
    APP_MODE,
    DB_AUTO_CREATE_SCHEMA,
    DB_ENABLED,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    JWT_SECRET_KEY,
)
from bimba3d_backend.app.config import DATA_DIR
import json
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Gaussian Splat Backend")


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router, prefix="/projects")
app.include_router(auth_router)
app.include_router(admin_router)


def _validate_server_env() -> None:
    if APP_MODE != "server" or not DB_ENABLED:
        return

    if JWT_SECRET_KEY == "change-me-in-production" or len(JWT_SECRET_KEY) < 32:
        raise RuntimeError(
            "In server mode, JWT_SECRET_KEY must be set to a strong value (min 32 chars, non-default)."
        )

    google_values = [GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]
    if any(google_values) and not all(google_values):
        raise RuntimeError(
            "Google OAuth env is partially configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI together."
        )


def _log_db_startup_state() -> None:
    if APP_MODE != "server" or not DB_ENABLED:
        logging.info(
            "db_startup state=disabled app_mode=%s db_enabled=%s",
            APP_MODE,
            DB_ENABLED,
        )
        return

    try:
        from bimba3d_backend.app.services.db import db_session, init_db

        if DB_AUTO_CREATE_SCHEMA:
            init_db()

        with db_session() as session:
            session.execute(text("SELECT 1"))

        logging.info(
            "db_startup state=healthy app_mode=%s db_enabled=%s schema_auto_create=%s",
            APP_MODE,
            DB_ENABLED,
            DB_AUTO_CREATE_SCHEMA,
        )
    except Exception as exc:
        logging.exception(
            "db_startup state=unhealthy app_mode=%s db_enabled=%s error=%s",
            APP_MODE,
            DB_ENABLED,
            exc,
        )


@app.on_event("startup")
def mark_interrupted_projects():
    """On backend start, mark any projects that were 'processing' as stopped/resumable.

    This ensures the frontend doesn't continue to show 'processing' for jobs
    that were interrupted by a backend restart or crash.
    """
    _validate_server_env()
    _log_db_startup_state()

    note = "Backend restarted — processing interrupted. Please resume when ready."
    from bimba3d_backend.app.services.colmap import stop_project_worker_containers
    for proj_dir in DATA_DIR.iterdir():
        try:
            if not proj_dir.is_dir():
                continue
            stopped = stop_project_worker_containers(proj_dir.name)
            if stopped:
                logging.info("Stopped %d stale worker container(s) for %s", stopped, proj_dir.name)
            status_file = proj_dir / "status.json"
            if not status_file.exists():
                continue
            try:
                with open(status_file, 'r') as f:
                    data = json.load(f)
            except Exception:
                data = {}
            if data.get("status") == "processing":
                data["status"] = "stopped"
                data["progress"] = data.get("progress", 0)
                data["error"] = note
                data["stop_requested"] = True
                data["stopped_stage"] = data.get("stage", "unknown")
                data["resumable"] = True
                data["percentage"] = data.get("percentage", 0.0)
                # write atomically
                tmp = status_file.with_suffix('.tmp')
                with open(tmp, 'w') as f:
                    json.dump(data, f)
                tmp.replace(status_file)
        except Exception:
            logging.exception(f"Failed to mark interrupted project: {proj_dir}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/health/db")
def db_health_check():
    """Database health check endpoint."""
    if APP_MODE != "server" or not DB_ENABLED:
        return {
            "status": "disabled",
            "app_mode": APP_MODE,
            "db_enabled": DB_ENABLED,
        }

    try:
        from bimba3d_backend.app.services.db import db_session

        with db_session() as session:
            session.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "app_mode": APP_MODE,
            "db_enabled": DB_ENABLED,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "app_mode": APP_MODE,
            "db_enabled": DB_ENABLED,
            "error": str(exc),
        }


@app.get("/health/gpu")
def gpu_health():
    """Report GPU availability and basic CUDA/device info."""
    try:
        import torch
        available = torch.cuda.is_available()
        count = torch.cuda.device_count() if available else 0
        devices = []
        for i in range(count):
            try:
                devices.append(torch.cuda.get_device_name(i))
            except Exception:
                devices.append(f"cuda:{i}")
        return {
            "gpu_available": available,
            "device_count": count,
            "devices": devices,
            "cuda_version": getattr(torch.version, "cuda", None),
        }
    except Exception:
        return {
            "gpu_available": False,
            "device_count": 0,
            "devices": [],
            "cuda_version": None,
        }


DEFAULT_FRONTEND_DIST = Path(__file__).resolve().parents[2] / "bimba3d_frontend" / "dist"
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", str(DEFAULT_FRONTEND_DIST))).resolve()
if FRONTEND_DIST.exists():
    app.mount("/", SPAStaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
    logging.info("Serving frontend build from %s", FRONTEND_DIST)
else:
    logging.info("Frontend dist not found at %s; API-only mode", FRONTEND_DIST)
