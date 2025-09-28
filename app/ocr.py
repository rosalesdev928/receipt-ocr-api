import io
import re
from typing import Dict, Optional
from PIL import Image, ImageOps
import numpy as np
import easyocr
from .settings import settings

# Idiomas
_LANGS = [lang.strip() for lang in settings.ocr_langs.split(",")]
_reader = easyocr.Reader(_LANGS, gpu=False)

# --- Preprocesado suave para imágenes comprimidas (WhatsApp) ---
def _preprocess(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("L")  # gris
    # Upscale si es pequeño (mejora OCR)
    w, h = img.size
    if max(w, h) < 1200:
        scale = 1200 / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))
    # Binarización simple (umbral)
    img = ImageOps.autocontrast(img)
    arr = np.array(img)
    thr = arr.mean() * 0.95
    arr = (arr > thr).astype(np.uint8) * 255
    return arr

# --- Regex robustos para monto y fecha ---
_AMOUNT_PATTERNS = [
    # TOTAL   S/ 60.00  | TOTAL: S/. 60,00
    re.compile(r"(?i)\bT\s*O\s*T\s*A\s*L\b\s*[:\-]?\s*([sS]\s*\/\.?|S\/|S\.)?\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{1,2})|[0-9]+(?:[.,][0-9]{1,2}))"),
    # IMPORTE / MONTO
    re.compile(r"(?i)\b(importe|monto)\b\s*[:\-]?\s*([sS]\s*\/\.?|S\/|S\.)?\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{1,2})|[0-9]+(?:[.,][0-9]{1,2}))"),
]

_DATE_RE = re.compile(r"(?:(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})|(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}))")

def _to_float(num: str) -> Optional[float]:
    num = num.replace(" ", "")
    if "," in num and "." in num:
        if num.rfind(",") > num.rfind("."):
            num = num.replace(".", "").replace(",", ".")
        else:
            num = num.replace(",", "")
    else:
        if "," in num:
            num = num.replace(",", ".")
    try:
        return float(num)
    except ValueError:
        return None

def _extract_amount(text: str) -> Optional[float]:
    for pat in _AMOUNT_PATTERNS:
        m = pat.search(text)
        if m:
            # último grupo es el número en ambos patrones
            num_group = m.group(m.lastindex)  # 2 o 3 según patrón
            val = _to_float(num_group)
            if val is not None:
                return val
    return None

def extract_fields(image_bytes: bytes) -> Dict[str, Optional[str]]:
    np_img = _preprocess(image_bytes)
    # Usamos párrafo=True para unir líneas
    lines = _reader.readtext(np_img, detail=0, paragraph=True)
    text = "\n".join(lines)

    total_val = _extract_amount(text)

    date_val = None
    dm = _DATE_RE.search(text)
    if dm:
        date_val = dm.group(1) or dm.group(2)

    return {
        "raw_text": text[:8000],
        "total": total_val,
        "date": date_val,
    }
