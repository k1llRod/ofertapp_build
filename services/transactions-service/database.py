from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def migrate_db():
    """Migración automática de columnas y tablas para SQLite y Postgres sin romper bases existentes"""
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if "promotions" in tables:
            columns = [c["name"] for c in inspector.get_columns("promotions")]
            if "gallery" not in columns:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE promotions ADD COLUMN gallery TEXT DEFAULT ''"))
                    print("[MIGRATION] Columna 'gallery' agregada exitosamente a 'promotions'.")
    except Exception as e:
        print(f"[Warning] Error en migración de base de datos: {e}")
