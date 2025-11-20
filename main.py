from fastapi import FastAPI, Request, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import shutil
from pathlib import Path
import os

from auth import require_bearer_token

app = FastAPI()

# directory degli upload
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload", dependencies=[Depends(require_bearer_token)])
async def upload_package(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")
    dest_path = UPLOAD_DIR / file.filename
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "size": dest_path.stat().st_size}

@app.get("/uploads", dependencies=[Depends(require_bearer_token)])
def list_uploads():
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return {"uploaded_files": files}

@app.get("/debug")
def debug(request: Request):
    return {"headers": dict(request.headers)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)