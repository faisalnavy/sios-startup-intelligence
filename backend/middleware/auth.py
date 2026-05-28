from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

bearer = HTTPBearer(auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials = Security(bearer)) -> dict:
    """Verify Supabase JWT token and return user payload."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "")
    if not jwt_secret:
        # Supabase not configured — return a mock user for local dev
        return {"sub": "local-dev-user", "email": "dev@localhost.com"}

    try:
        payload = jwt.decode(
            credentials.credentials,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
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
