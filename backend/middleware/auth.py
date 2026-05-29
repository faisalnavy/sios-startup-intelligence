from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
import time
import concurrent.futures

bearer = HTTPBearer(auto_error=False)

# ── Token verification cache ──────────────────────────────────────────────────
# Avoids a slow Supabase network call on every authenticated request.
# key: token → (payload dict, unix expiry timestamp)
_token_cache: dict[str, tuple[dict, float]] = {}
_CACHE_TTL = 300      # 5 min — Supabase tokens last 1hr by default, so this is safe
_SUPABASE_TIMEOUT = 8.0  # Hard timeout so a slow Supabase never hangs a request


def _verify_via_supabase_api(token: str) -> dict:
    """Verify a Supabase JWT using the Admin API (service role key).
    Results are cached for 5 minutes so repeated requests are instant."""

    # ── Cache fast path ───────────────────────────────────────────────────────
    now = time.time()
    cached = _token_cache.get(token)
    if cached:
        payload, expires_at = cached
        if now < expires_at:
            return payload
        del _token_cache[token]  # Expired — evict

    supabase_url = os.getenv("SUPABASE_URL", "")
    service_key  = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not service_key:
        return {}

    def _call_supabase():
        from supabase import create_client
        admin = create_client(supabase_url, service_key)
        resp  = admin.auth.get_user(token)
        if not resp or not resp.user:
            return {}
        u = resp.user
        return {
            "sub":           str(u.id),
            "email":         u.email or "",
            "app_metadata":  u.app_metadata  or {},
            "user_metadata": u.user_metadata or {},
        }

    try:
        # Run the synchronous supabase call in a thread with a hard timeout.
        # Without this, a slow Supabase response blocks the entire FastAPI worker.
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_call_supabase)
            result = future.result(timeout=_SUPABASE_TIMEOUT)
    except concurrent.futures.TimeoutError:
        return {}
    except Exception:
        return {}

    # Cache successful verifications
    if result:
        _token_cache[token] = (result, now + _CACHE_TTL)

    return result


def verify_token(credentials: HTTPAuthorizationCredentials = Security(bearer)) -> dict:
    """Verify Supabase JWT token and return user payload."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token      = credentials.credentials
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "")

    # ── Fast path: local JWT decode ───────────────────────────────────────────
    if jwt_secret:
        try:
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            pass  # fall through to Supabase Admin API

    # ── Slow path: Supabase Admin API (handles any valid Supabase token) ──────
    payload = _verify_via_supabase_api(token)
    if payload:
        return payload

    # ── Local-dev fallback (no Supabase configured at all) ───────────────────
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url:
        return {"sub": "local-dev-user", "email": "dev@localhost.com"}

    raise HTTPException(status_code=401, detail="Invalid token")


def optional_token(credentials: HTTPAuthorizationCredentials = Security(bearer)) -> dict | None:
    """Return user payload if authenticated, None otherwise."""
    if not credentials:
        return None
    try:
        return verify_token(credentials)
    except HTTPException:
        return None


def verify_admin(credentials: HTTPAuthorizationCredentials = Security(bearer)) -> dict:
    """
    Verify the caller is a logged-in admin user.
    Checks is_admin flag stored in the JWT app_metadata or via Supabase lookup.
    """
    user = verify_token(credentials)

    # Check app_metadata.is_admin (set via Supabase service role)
    app_meta = user.get("app_metadata", {})
    if app_meta.get("is_admin"):
        return user

    # Fallback: check user_metadata.is_admin
    user_meta = user.get("user_metadata", {})
    if user_meta.get("is_admin"):
        return user

    # Fallback: check DB
    from services.supabase_service import SupabaseService
    db = SupabaseService()
    if db.is_available():
        db_user = db.get_user(user.get("sub", ""))
        if db_user and db_user.get("is_admin"):
            return user

    raise HTTPException(status_code=403, detail="Admin access required")
