from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel

# Modelo principal de la tabla Receipts
class Receipt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant: Optional[str] = Field(default=None, index=True)
    total: Optional[float] = Field(default=None, index=True)
    currency: str = Field(default="PEN")
    purchase_date: Optional[date] = Field(default=None, index=True)
    raw_text: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Modelo para creación
class ReceiptCreate(SQLModel):
    merchant: Optional[str] = None
    currency: Optional[str] = "PEN"

# Modelo para lectura (respuesta API)
class ReceiptRead(SQLModel):
    id: int
    merchant: Optional[str]
    total: Optional[float]
    currency: str
    purchase_date: Optional[date]
    created_at: datetime
