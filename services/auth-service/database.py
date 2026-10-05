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
    """Migración automática de columnas para SQLite y Postgres sin romper bases existentes"""
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("users")]
            new_cols = [
                ("logo_url", "TEXT"),
                ("banner_url", "TEXT"),
                ("bio", "TEXT"),
                ("social_instagram", "TEXT"),
                ("social_facebook", "TEXT"),
                ("social_twitter", "TEXT"),
                ("social_whatsapp", "TEXT"),
                ("website", "TEXT"),
            ]
            with engine.begin() as conn:
                for col_name, col_type in new_cols:
                    if col_name not in columns:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
    except Exception as e:
        print(f"[Warning] Error en migración de base de datos: {e}")

