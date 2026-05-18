from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import crud, schemas, security

router = APIRouter(prefix="/user")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


import traceback


@router.get("/notes/{note_id}/ai", response_model=schemas.NoteAIResponse)
def get_note_ai(note_id: str, access_token: str, db: Session = Depends(get_db)):
    try:
        if not access_token:
            raise HTTPException(status_code=401, detail="Authentication required")

        email = security.get_current_user_email(access_token)
        user = crud.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found or session expired")

        note = (
            db.query(crud.models.Note)
            .filter(
                crud.models.Note.id == note_id,
                crud.models.Note.owner_id == user.id,
            )
            .first()
        )
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        ai_row = (
            db.query(
                crud.models.NoteAI.note_id,
                crud.models.NoteAI.summary,
                crud.models.NoteAI.tags,
                crud.models.NoteAI.embedding,
            )
            .filter(crud.models.NoteAI.note_id == note_id)
            .first()
        )
        if not ai_row:
            return schemas.NoteAIResponse(
                note_id=note_id,
                summary=None,
                tags=[],
                embedding_present=False,
            )

        summary = ai_row.summary
        tags = ai_row.tags
        embedding_present = bool(ai_row.embedding)

        print(
            f"[get_note_ai] note_id={note_id} user_email={email} "
            f"summary={repr(summary)} tags={repr(tags)} embedding_present={embedding_present}"
        )

        return schemas.NoteAIResponse(
            note_id=note_id,
            summary=summary,
            tags=(tags.split(",") if tags else []),
            embedding_present=embedding_present,
        )
    except Exception:
        print("[get_note_ai] FAILED")
        print("[get_note_ai] full_traceback=\n" + traceback.format_exc())
        raise



