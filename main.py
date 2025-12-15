from fastapi import FastAPI, Request, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import shutil
from pathlib import Path
import os
import time

from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import make_asgi_app
import logging.config
from logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logger.info("Starting App")

app = FastAPI()

# directory degli upload
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ==========================
#  METRICHE CUSTOM
# ==========================

# Quante richieste di upload, per stato (success, invalid_format, error)
UPLOAD_REQUESTS = Counter(
    "upload_requests_total",
    "Numero totale di richieste POST /upload",
    ["status"],
)

# Byte totali caricati
UPLOAD_BYTES = Counter(
    "upload_bytes_total",
    "Numero totale di byte caricati con successo",
)

# Durata dell'handling della richiesta di upload
UPLOAD_DURATION = Histogram(
    "upload_duration_seconds",
    "Tempo impiegato per gestire una richiesta POST /upload",
    buckets=(0.1, 0.3, 1.0, 3.0, 10.0),
)

# Quante richieste GET /uploads
UPLOAD_LIST_REQUESTS = Counter(
    "upload_list_requests_total",
    "Numero totale di richieste GET /uploads",
)

UPLOAD_FILES_TOTAL = Gauge(
    "upload_files_total",
    "Numero di file presenti nella directory degli upload"
)

# Summary of upload file sizes
UPLOAD_SIZE_SUMMARY = Summary(
    "upload_file_size_bytes",
    "Riepilogo statistico delle dimensioni dei file caricati in byte",
)


def update_upload_files_total():
    count = len([f for f in UPLOAD_DIR.iterdir() if f.is_file()])
    UPLOAD_FILES_TOTAL.set(count)

# Add prometheus asgi middleware to route /metrics requests
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

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
    start_time = time.time()
    try:
        if not file.filename.endswith(".zip"):
            logger.warning(f"Rejected non-zip file upload attempt: {file.filename}")
            UPLOAD_REQUESTS.labels(status="invalid_format").inc()
            raise HTTPException(status_code=400, detail="Only .zip files are allowed")

        logger.info(f"Receiving upload request for file: {file.filename}")
        dest_path = UPLOAD_DIR / file.filename
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = dest_path.stat().st_size

        # Update metrics for successful upload
        UPLOAD_REQUESTS.labels(status="success").inc()
        UPLOAD_BYTES.inc(file_size)
        UPLOAD_SIZE_SUMMARY.observe(file_size)  # Add this line
        UPLOAD_DURATION.observe(time.time() - start_time)

        update_upload_files_total()

        logger.info(f"Successfully uploaded file {file.filename} ({file_size} bytes)")
        return {"filename": file.filename, "size": file_size}

    except HTTPException:
        raise
    except Exception as e:
        UPLOAD_REQUESTS.labels(status="error").inc()
        raise HTTPException(status_code=500, detail="Upload failed") from e
    finally:
        UPLOAD_DURATION.observe(time.time() - start_time)

@app.get("/uploads", dependencies=[Depends(require_bearer_token)])
def list_uploads():
    logger.info("Listing uploaded files")
    UPLOAD_LIST_REQUESTS.inc()
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
