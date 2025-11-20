from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File
import shutil
from pathlib import Path

from auth import require_bearer_token

app = FastAPI()

# directory degli upload
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/stats", dependencies=[Depends(require_bearer_token)])
def list_uploads():
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    file_count = len(files)
    # TODO: .. aggiungere logica per gli altri campi (dimensione min, max, avg, etc.)

    return {"file_count": file_count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)