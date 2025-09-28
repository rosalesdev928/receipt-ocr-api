from pydantic import BaseModel
import os

class Settings(BaseModel):
    api_key: str = os.getenv("API_KEY", "devkey")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./receipts.db")
    ocr_langs: str = os.getenv("OCR_LANGS", "es,en")
    default_currency: str = os.getenv("DEFAULT_CURRENCY", "PEN")

settings = Settings()
