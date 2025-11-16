# backend/app/main.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from services.retriever import Retriever

app = FastAPI(title="RealEstateGPT - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.getenv("DATA_DIR", "./data/uploads")
os.makedirs(DATA_DIR, exist_ok=True)

CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
retriever = Retriever(persist_directory=CHROMA_DIR)


class ChatReq(BaseModel):
    query: str
    session_id: Optional[str] = None


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = os.path.join(DATA_DIR, file.filename)
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        retriever.ingest_file(filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok", "filename": file.filename}


@app.post("/chat")
async def chat(req: ChatReq):
    if not req.query:
        raise HTTPException(status_code=400, detail="Query required")
    resp = retriever.answer(req.query)
    return resp


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
