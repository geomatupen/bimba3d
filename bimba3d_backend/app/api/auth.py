import uuid
import json
import secrets
import urllib.parse
import urllib.request
import time
from collections import deque

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from sqlalchemy import select

from bimba3d_backend.app.config import (
    ADMIN_EMAILS,
    ALLOWED_ORIGINS,
    APP_MODE,
    DB_ENABLED,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from bimba3d_backend.app.models.auth import AuthTokens, AuthUser, LoginRequest, RefreshRequest, SignupRequest
from sqlalchemy.orm import Session

from bimba3d_backend.app.services.db import User, db_session
from bimba3d_backend.app.services.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_required,
    hash_password,
    normalize_email,
    revoke_refresh_token,
    save_refresh_token,
    validate_refresh_token,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = {}


def _assert_auth_enabled() -> None:
    if APP_MODE != "server" or not DB_ENABLED:
        raise HTTPException(status_code=503, detail="Auth is disabled (set APP_MODE=server and DB_ENABLED=true)")


def _user_payload(user: User) -> AuthUser:
    return AuthUser(id=user.id, name=user.name, email=user.email, role=user.role)


def _issue_tokens(user: User, session: Session | None = None) -> AuthTokens:
    access = create_access_token(user.id, user.role)
    refresh, refresh_hash, expires_at = create_refresh_token(user.id)
    save_refresh_token(user.id, refresh_hash, expires_at, session=session)
    return AuthTokens(access_token=access, refresh_token=refresh, user=_user_payload(user))


def _assert_google_enabled() -> None:
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _enforce_rate_limit(request: Request, route_key: str, limit: int, window_seconds: int) -> None:
    ip = _client_ip(request)
    key = f"{route_key}:{ip}"
    now = time.monotonic()
    bucket = _RATE_LIMIT_BUCKETS.setdefault(key, deque())

    cutoff = now - float(window_seconds)
    while bucket and bucket[0] < cutoff:
        bucket.popleft()

    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

    bucket.append(now)


def _origin_allowed(origin: str | None) -> bool:
    if not origin:
        return False
    return origin in ALLOWED_ORIGINS


def _create_google_state(origin: str) -> str:
    payload = {
        "nonce": secrets.token_urlsafe(24),
        "origin": origin,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _decode_google_state(state: str) -> dict:
    try:
        payload = jwt.decode(state, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=400, detail="Invalid OAuth state") from exc
    origin = payload.get("origin")
    if not _origin_allowed(origin):
        raise HTTPException(status_code=400, detail="Invalid OAuth origin")
    return payload


def _http_json_post(url: str, payload: dict) -> dict:
    body = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_json_get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _verify_google_id_token(id_token: str) -> dict:
    verify_url = "https://oauth2.googleapis.com/tokeninfo?id_token=" + urllib.parse.quote(id_token)
    payload = _http_json_get(verify_url)
    if payload.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Google token audience mismatch")
    if payload.get("email_verified") not in {"true", True}:
        raise HTTPException(status_code=401, detail="Google email is not verified")
    return payload


def _popup_html(origin: str, ok: bool, payload: dict) -> HTMLResponse:
    message_type = "bimba3d-google-auth-success" if ok else "bimba3d-google-auth-failure"
    encoded = json.dumps(payload)
    escaped_origin = origin.replace("'", "")
    html = f"""
<!doctype html>
<html>
  <body>
    <script>
      (function() {{
        const targetOrigin = '{escaped_origin}';
        const payload = {encoded};
        if (window.opener && targetOrigin) {{
          window.opener.postMessage({{ type: '{message_type}', payload }}, targetOrigin);
        }}
        window.close();
      }})();
    </script>
    <p>You can close this window.</p>
  </body>
</html>
"""
    return HTMLResponse(content=html)


@router.post("/providers")
def auth_providers():
    _assert_auth_enabled()
    return {
        "google_enabled": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REDIRECT_URI),
    }


@router.post("/signup", response_model=AuthTokens)
def signup(payload: SignupRequest, request: Request):
    _assert_auth_enabled()
    _enforce_rate_limit(request, "signup", limit=10, window_seconds=300)
    email = normalize_email(payload.email)
    with db_session() as session:
        existing = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        role = "admin" if email in ADMIN_EMAILS else "user"
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=payload.name.strip(),
            password_hash=hash_password(payload.password),
            role=role,
            is_active=True,
        )
        session.add(user)
        session.flush()
        session.refresh(user)
        return _issue_tokens(user, session=session)


@router.post("/login", response_model=AuthTokens)
def login(payload: LoginRequest, request: Request):
    _assert_auth_enabled()
    _enforce_rate_limit(request, "login", limit=20, window_seconds=300)
    email = normalize_email(payload.email)
    with db_session() as session:
        user = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User is disabled")
        return _issue_tokens(user)


@router.post("/refresh", response_model=AuthTokens)
def refresh(payload: RefreshRequest, request: Request):
    _assert_auth_enabled()
    _enforce_rate_limit(request, "refresh", limit=60, window_seconds=300)
    user = validate_refresh_token(payload.refresh_token)
    revoke_refresh_token(payload.refresh_token)
    return _issue_tokens(user)


@router.post("/logout")
def logout(payload: RefreshRequest):
    _assert_auth_enabled()
    revoke_refresh_token(payload.refresh_token)
    return {"status": "ok"}


@router.get("/me", response_model=AuthUser)
def me(current=Depends(get_current_user_required)):
    _assert_auth_enabled()
    user_id = current["user_id"]
    with db_session() as session:
        user = session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return _user_payload(user)


@router.get("/google/start")
def google_start(request: Request, origin: str = Query(...)):
    _assert_auth_enabled()
    _assert_google_enabled()
    _enforce_rate_limit(request, "google_start", limit=20, window_seconds=300)
    if not _origin_allowed(origin):
        raise HTTPException(status_code=400, detail="Origin not allowed")

    state = _create_google_state(origin)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return {"authorization_url": authorization_url}


@router.get("/google/callback")
def google_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
):
    _assert_auth_enabled()
    _assert_google_enabled()

    if not state:
        raise HTTPException(status_code=400, detail="Missing OAuth state")

    state_payload = _decode_google_state(state)
    origin = state_payload["origin"]

    if error:
        return _popup_html(origin, False, {"error": f"Google OAuth failed: {error}"})
    if not code:
        return _popup_html(origin, False, {"error": "Missing Google authorization code"})

    try:
        token_payload = _http_json_post(
            "https://oauth2.googleapis.com/token",
            {
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        id_token = token_payload.get("id_token")
        if not id_token:
            return _popup_html(origin, False, {"error": "Google token exchange failed"})

        profile = _verify_google_id_token(id_token)
        email = normalize_email(profile.get("email", ""))
        if not email:
            return _popup_html(origin, False, {"error": "Google account email is unavailable"})

        name = (profile.get("name") or email.split("@")[0]).strip()
        google_sub = profile.get("sub")
        avatar_url = profile.get("picture")

        with db_session() as session:
            user = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if not user and google_sub:
                user = session.execute(select(User).where(User.oauth_sub == google_sub)).scalar_one_or_none()

            if not user:
                role = "admin" if email in ADMIN_EMAILS else "user"
                user = User(
                    id=str(uuid.uuid4()),
                    email=email,
                    name=name,
                    password_hash=hash_password(secrets.token_urlsafe(24)),
                    oauth_provider="google",
                    oauth_sub=google_sub,
                    avatar_url=avatar_url,
                    role=role,
                    is_active=True,
                )
                session.add(user)
                session.flush()
                session.refresh(user)
            else:
                user.name = name or user.name
                user.oauth_provider = "google"
                user.oauth_sub = google_sub or user.oauth_sub
                user.avatar_url = avatar_url or user.avatar_url

            if not user.is_active:
                return _popup_html(origin, False, {"error": "User is disabled"})

            tokens = _issue_tokens(user, session=session)
            return _popup_html(origin, True, tokens.model_dump())
    except HTTPException as exc:
        return _popup_html(origin, False, {"error": exc.detail})
    except Exception:
        return _popup_html(origin, False, {"error": "Google sign-in failed"})
