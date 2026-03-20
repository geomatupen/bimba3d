from pathlib import Path
from typing import List
import os


def _load_env_file(env_file: Path) -> None:
    if not env_file.exists() or not env_file.is_file():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        os.environ.setdefault(key, value)

# Directories
BASE_DIR = Path(__file__).parent.parent
REPO_ROOT = Path(__file__).resolve().parents[2]

# Load local env files automatically so backend can be started with just uvicorn.
# Precedence: existing shell env vars > .env.server > .env > backend .env
_load_env_file(REPO_ROOT / ".env.server")
_load_env_file(REPO_ROOT / ".env")
_load_env_file(BASE_DIR / ".env")

_data_dir_override = os.environ.get("BIMBA3D_DATA_DIR")
if _data_dir_override:
    DATA_DIR = Path(_data_dir_override).expanduser().resolve()
else:
    DATA_DIR = BASE_DIR / "data" / "projects"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# API
API_PORT = 8005

# CORS - Update these for production
# Default allowed origins for local development and the Cloudflare domain.
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:5174",  # Alternate Vite dev port
    "http://localhost:3000",  # Alternative frontend port
    "http://localhost:8080",  # Another common port
    "http://app.bimba3d.com",
    "https://app.bimba3d.com",
]

# Allow overriding via environment variable (comma-separated)
_env_origins = os.environ.get("ALLOWED_ORIGINS")
if _env_origins:
    ALLOWED_ORIGINS = [o.strip() for o in _env_origins.split(",") if o.strip()]
else:
    ALLOWED_ORIGINS = DEFAULT_ALLOWED_ORIGINS

# File upload settings
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

# Runtime mode
APP_MODE = os.environ.get("APP_MODE", "desktop").strip().lower()

# Database / auth
DB_ENABLED = os.environ.get("DB_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/bimba3d")
DB_AUTO_CREATE_SCHEMA = os.environ.get("DB_AUTO_CREATE_SCHEMA", "true").strip().lower() in {"1", "true", "yes", "on"}

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "14"))

ADMIN_EMAILS = {
    e.strip().lower()
    for e in os.environ.get("ADMIN_EMAILS", "").split(",")
    if e.strip()
}

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "").strip()
