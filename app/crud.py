from sqlalchemy.orm import Session
import os
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, OrderedDict
from .jwt import *
import json
import uuid


from . import models, schemas
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256', # The hash digest algorithm for HMAC
        user.password.encode('utf-8'), # Convert the password to bytes
        salt, # Provide the salt
        100000 # It is recommended to use at least 100,000 iterations of SHA-256 
    )   
        #Bytes encoded to Base64 but still in byte format
    encodedSalt = base64.b64encode(salt)
    encodedKey = base64.b64encode(key)
    # fake_hashed_password = user.password + "notreallyhashed"
     
    db_user = models.User(email=user.email, hashed_password=encodedKey.decode('utf-8'),salt=encodedSalt.decode('utf-8'))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()



def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
def create_user_note(db: Session, note: str, user_id: int):
    """Create a note for a user.

    Additive fix: if incoming payload lacks `id`, generate a UUID string.
    """
    print(note)

    if not isinstance(note, dict):
        raise ValueError("note payload must be an object")

    note_data = dict(note)
    if not note_data.get("id"):
        note_data["id"] = uuid.uuid4().hex

    db_item = models.Note(**note_data, owner_id=user_id)
    db.add(db_item)
    # Flush to catch issues (e.g., PK problems) before commit.
    db.flush()
    db.commit()
    db.refresh(db_item)
    return db_item

def update_user_note(db:Session, note:str,user_id:int):
    # Runtime guard: update requires an id. The create-note flow intentionally
    # sends only {"title", "description"} and must not crash here.
    if not isinstance(note, dict):
        raise ValueError("note payload must be an object")

    note_id = note.get("id")
    if not note_id:
        # Controlled behavior instead of KeyError
        # Caller may treat this as a failed update.
        return None

    db_item = models.Note(**note, owner_id=user_id)
    updateObject = (
        db.query(models.Note)
        .filter_by(owner_id=user_id, id=note_id)
        .first()
    )
    if not updateObject:
        return None

    updateObject.description = db_item.description
    updateObject.title = db_item.title
    db.commit()
    db.refresh(updateObject)
    return note


def create_note_ai(db: Session, note_id: str, summary: str, tags: str):
    db_item = models.NoteAI(note_id=note_id, summary=summary, tags=tags)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_note_ai(db: Session, note_id: str):
    return db.query(models.NoteAI).filter(models.NoteAI.note_id == note_id).first()

def get_user_notes(db: Session, user: schemas.User,skip: int = 0, limit: int = 100):
    items = db.query(models.Note).filter_by(owner_id=user.id).offset(skip).limit(limit).all()
    notes = []
    for item in items:
        note = OrderedDict()
        note["id"]=item.id
        note["title"] =  item.title
        note["description"] = item.description
        notes.append(note)
    return notes

def delete_user_note(db: Session, note:str,user_id: int):
    # note = json.loads(note)
    item = db.query(models.Note).filter_by(owner_id=user_id,id=note["id"]).first()
    # db.add(db_item)
    db.delete(item)
    db.commit()
    return item