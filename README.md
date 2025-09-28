# Receipt OCR API (FastAPI)

FastAPI microservice that extracts **total** and **date** from receipt images (JPG/PNG) using **EasyOCR** and stores results in **SQLite** via SQLModel.

## Stack
FastAPI · Uvicorn · EasyOCR · SQLModel/SQLite · Python 3.11 · Docker

## Quickstart
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/docs
