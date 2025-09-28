FROM python:3.11-slim

# Carpeta de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la app
COPY app ./app

# Variables de entorno
ENV API_KEY=devkey \
    DATABASE_URL=sqlite:///./receipts.db \
    OCR_LANGS=es,en \
    DEFAULT_CURRENCY=PEN

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
