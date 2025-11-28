from fastapi import FastAPI, Request, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import shutil
from pathlib import Path
import os
import logging.config
from logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logger.info("Starting App")

app = FastAPI()

# directory degli upload
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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
        logger.warning(f"Invalid authentication attempt with scheme {creds.scheme}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("Successful authentication")
    return True


@app.post("/upload", dependencies=[Depends(require_bearer_token)])
async def upload_package(file: UploadFile = File(...)):
    logger.info(f"Receiving upload request for file: {file.filename}")
    if not file.filename.endswith(".zip"):
        logger.warning(f"Rejected non-zip file upload attempt: {file.filename}")
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")
    dest_path = UPLOAD_DIR / file.filename
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_size = dest_path.stat().st_size
    logger.info(f"Successfully uploaded file {file.filename} ({file_size} bytes)")
    return {"filename": file.filename, "size": file_size}


@app.get("/uploads", dependencies=[Depends(require_bearer_token)])
def list_uploads():
    logger.info("Listing uploaded files")
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    logger.debug(f"Found {len(files)} files")
    return {"uploaded_files": files}


@app.get("/debug")
def debug(request: Request):
    logger.info("Debug endpoint accessed")
    logger.debug(f"Request headers: {dict(request.headers)}")
    return {"headers": dict(request.headers)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
