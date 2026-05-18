import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read database URL from environment for production; fall back to SQLite for dev
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./dev.db"

# Used for runtime capability checks (pgvector, etc.)
DATABASE_URL_EFFECTIVE = SQLALCHEMY_DATABASE_URL


# SQLite needs a special connect arg
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_sqlite_schema():
    """Add missing SQLite columns for existing dev DBs (additive + safe).

    Note: SQLAlchemy create_all() does not alter existing tables.
    """
    try:
        if not SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
            return

        import sqlite3
        db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
        # Fallback: if URL parsing fails, keep previous behavior.
        if not db_path:
            db_path = "dev.db"

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # If note_ai table does not exist yet, don't fail startup.
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='note_ai'")
        if cur.fetchone() is None:
            conn.close()
            return

        cur.execute("PRAGMA table_info(note_ai)")
        cols = {row[1] for row in cur.fetchall()}
        if "embedding" not in cols:
            cur.execute("ALTER TABLE note_ai ADD COLUMN embedding TEXT")
            conn.commit()
        if "embedding_vector" not in cols:
            cur.execute("ALTER TABLE note_ai ADD COLUMN embedding_vector TEXT")
            conn.commit()

        conn.close()
    except Exception:
        # Never block app startup in dev.
        pass

