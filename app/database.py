from sqlmodel import SQLModel, create_engine
from .settings import settings

# Configuración especial para SQLite
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

# Motor de base de datos
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)

# Inicializar base de datos y crear tablas
def init_db():
    SQLModel.metadata.create_all(engine)
