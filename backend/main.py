from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import crud
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List 
import os
from dotenv import load_dotenv

load_dotenv()

class ScanTimesRequest(BaseModel):
    scan_times: List[str]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def index():
    return {"message":"Start page"}

# bot_settings を取得
@app.get("/bot_settings")
def read_bot_settings(db: Session = Depends(get_db)):
    return crud.get_bot_settings(db)

# scan_url を取得
@app.get("/scan_url")
def get_scan_url(db: Session = Depends(get_db)):
    return crud.get_scan_url(db)

# scan_url を追加
@app.post("/scan_url")
def add_scan_url(url: str, db: Session = Depends(get_db)):
    return crud.create_scan_url(db, url)

# scan_times を取得
@app.get("/scan_times")
def get_scan_time(db: Session = Depends(get_db)):
    return crud.get_scan_time(db)

# scan_times を追加
@app.post("/scan_times")
def update_scan_times(data: ScanTimesRequest, db: Session = Depends(get_db)):
    url_id = 1
    bot_id = 1
    return crud.update_scan_times(db, data.scan_times, url_id, bot_id)
