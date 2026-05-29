from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

bearer = HTTPBearer(auto_error=False)


def _verify_via_supabase_api(token: str) -> dict:
    """Verify a Supabase JWT using the Admin API (service role key).
    Slower than local decode but works regardless of JWT secret config."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    service_key  = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not service_key:
        return {}
    try:
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
    except Exception:
        return {}


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
