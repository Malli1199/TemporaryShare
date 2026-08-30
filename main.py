import os
import random
import json
from pathlib import Path
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import redis

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "index.html"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# --- REDIS CLOUD CONNECTION ---
# Using IP address directly (3.109.60.254) to bypass local Windows DNS / getaddrinfo lookup failures.
# Added socket timeouts (5 seconds) to prevent infinite pending state on network failure.
r = redis.Redis(
    host="3.109.60.254",
    port=11249,
    password="B3ZTKOkWeiajjD6NGFbNXjGMCTwid1iA",
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5
)

@app.get("/", response_class=HTMLResponse)
def get_home():
    if not HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="index.html not found!")
    return HTML_PATH.read_text(encoding="utf-8")

# Helper to generate a unique 6-digit code
def generate_unique_code():
    for _ in range(10):
        code = str(random.randint(100000, 999999))
        if not r.exists(code):
            return code
    raise HTTPException(status_code=500, detail="Could not generate a unique share code.")

@app.post("/share")
async def share_data(
    data_type: str = Form(...), # 'text', 'pdf', or 'file'
    text_content: str = Form(None),
    file: UploadFile = File(None)
):
    try:
        code = generate_unique_code()
        
        if data_type == "text":
            if not text_content:
                raise HTTPException(status_code=400, detail="Text content is required.")
            payload = {"type": "text", "content": text_content}
            
        elif data_type in ["pdf", "file"]:
            if not file:
                raise HTTPException(status_code=400, detail="File is required.")
            
            # Save uploaded file locally inside uploads directory
            file_filename = f"{code}_{file.filename}"
            file_path = UPLOAD_DIR / file_filename
            
            with open(file_path, "wb") as f:
                f.write(await file.read())
                
            payload = {
                "type": "file",
                "filename": file.filename,
                "local_path": str(file_path)
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid data type.")

        # Store stringified JSON in Redis with 10-minute expiration (600s)
        r.setex(name=code, time=600, value=json.dumps(payload))
        return JSONResponse(status_code=200, content={"code": code})

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@app.post("/receive")
def receive_data(code: str = Form(...)):
    try:
        raw_data = r.get(code)
        if raw_data is None:
            raise HTTPException(status_code=404, detail="Invalid or expired code!")
        
        payload = json.loads(raw_data)
        ttl = r.ttl(code)
        payload["expires_in"] = ttl
        
        return JSONResponse(status_code=200, content=payload)
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{code}")
def download_file(code: str):
    raw_data = r.get(code)
    if not raw_data:
        raise HTTPException(status_code=404, detail="File expired or code invalid.")
    
    payload = json.loads(raw_data)
    if payload.get("type") != "file":
        raise HTTPException(status_code=400, detail="Not a downloadable file.")
    
    file_path = Path(payload["local_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File missing on server.")
        
    return FileResponse(path=file_path, filename=payload["filename"])