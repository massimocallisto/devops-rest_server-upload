from fastapi import FastAPI, Request, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import shutil
from pathlib import Path
import os
import time

from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import make_asgi_app

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

# Add prometheus asgi middleware to route /metrics requests
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# --- Sicurezza: Bearer token semplice ---
security = HTTPBearer(auto_error=True)

def get_expected_token() -> str:
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

@app.post("/upload", dependencies=[Depends(require_bearer_token)])
async def upload_package(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        if not file.filename.endswith(".zip"):
            UPLOAD_REQUESTS.labels(status="invalid_format").inc()
            raise HTTPException(status_code=400, detail="Only .zip files are allowed")
        
        dest_path = UPLOAD_DIR / file.filename
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = dest_path.stat().st_size
        
        # Update metrics for successful upload
        UPLOAD_REQUESTS.labels(status="success").inc()
        UPLOAD_BYTES.inc(file_size)
        UPLOAD_DURATION.observe(time.time() - start_time)
        
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
    UPLOAD_LIST_REQUESTS.inc()
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return {"uploaded_files": files}

@app.get("/debug")
def debug(request: Request):
    return {"headers": dict(request.headers)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)