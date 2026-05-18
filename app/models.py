from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import uuid

from .database import Base

# pgvector is optional at runtime; models must still import for SQLite.
try:
    from pgvector.sqlalchemy import Vector  # type: ignore
except Exception:  # pragma: no cover
    Vector = None  # type: ignore


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    salt = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")
    notes = relationship("Note", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")


class Note(Base):
    __tablename__ = "notes"

    id = Column(
        String, primary_key=True, index=True, default=lambda: uuid.uuid4().hex
    )
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="notes")


class NoteAI(Base):
    __tablename__ = "note_ai"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(String, ForeignKey("notes.id"), unique=True, index=True)

    summary = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # comma-separated tags

    # JSON-serialized embedding for SQLite fallback/debugging.
    embedding = Column(String, nullable=True)

    # pgvector column.
    # Additive + safe for SQLite: keep it as NULLable TEXT when running without pgvector.
    # Also, CRUD/API must NEVER expose this column.
    if Vector is not None:
        embedding_vector = Column(Vector(384), nullable=True)
    else:  # pgvector not installed; keep a TEXT column (but only for new DBs)
        embedding_vector = Column(String, nullable=True)



    note = relationship("Note", backref="ai")

