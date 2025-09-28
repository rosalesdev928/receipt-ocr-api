from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import Optional, List

from .database import engine, init_db
from .models import Receipt, ReceiptRead
from .ocr import extract_fields
from .settings import settings

app = FastAPI(title="Receipt OCR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

def api_key_guard(x_api_key: Optional[str] = Header(None)):
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/receipts/upload", response_model=ReceiptRead, dependencies=[Depends(api_key_guard)])
async def upload_receipt(
    file: UploadFile = File(...),
    merchant: Optional[str] = None,
    currency: Optional[str] = None
):
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Solo se aceptan JPG o PNG")

    data = await file.read()
    fields = extract_fields(data)

    r = Receipt(
        merchant=merchant,
        total=fields.get("total"),
        currency=currency or settings.default_currency,
        purchase_date=fields.get("date"),
        raw_text=fields.get("raw_text"),
    )

    with Session(engine) as session:
        session.add(r)
        session.commit()
        session.refresh(r)
        return r

@app.post("/receipts/dry-run", dependencies=[Depends(api_key_guard)])
async def ocr_dry_run(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Solo JPG o PNG")
    data = await file.read()
    fields = extract_fields(data)
    return {
        "total_raw": fields.get("total"),
        "date_raw": fields.get("date"),
        "raw_text_preview": (fields.get("raw_text") or "")[:1500]
    }




@app.get("/receipts", response_model=List[ReceiptRead], dependencies=[Depends(api_key_guard)])
def list_receipts(limit: int = 50):
    with Session(engine) as session:
        results = session.exec(
            select(Receipt).order_by(Receipt.created_at.desc()).limit(limit)
        ).all()
        return results
