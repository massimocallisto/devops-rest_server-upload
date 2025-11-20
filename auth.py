from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os


# --- Sicurezza: Bearer token semplice ---
security = HTTPBearer(auto_error=True)

def get_expected_token() -> str:
    # imposta il token via env var; fallback a valore di default per demo
    return os.getenv("API_BEARER_TOKEN", "mysecrettoken")

def require_bearer_token(
    creds: HTTPAuthorizationCredentials = Depends(security),
    expected: str = Depends(get_expected_token),
):
    if creds.scheme.lower() != "bearer" or creds.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
