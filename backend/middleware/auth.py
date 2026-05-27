from fastapi import HTTPException, Security
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
