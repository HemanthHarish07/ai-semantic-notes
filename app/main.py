from typing import List
from fastapi import Depends, FastAPI, HTTPException,Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import crud, models, schemas, security
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from .jwt import decodeJWT
from .routers import files
from .ai import generate_and_store_ai
from .routes_ai import router as ai_router
import re
from .semantic_search import semantic_search
from . import schemas
from pydantic import BaseModel




ACCESS_TOKEN_EXPIRE_MINUTES = 30



models.Base.metadata.create_all(bind=engine)
from .database import ensure_sqlite_schema, DATABASE_URL_EFFECTIVE
ensure_sqlite_schema()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

app.include_router(files.router)
app.include_router(ai_router)


# Local dev CORS (allow localhost frontend only)
origins = [
    "https://ai-semantic-notes-jnnk.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"[POST /users/] Creating user with email={user.email}")
    db_user = crud.create_user(db, user=user)
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(
        db,
        email=form_data.username
    )

    # USER NOT FOUND
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # INVALID PASSWORD
    if not (
        security.verify_hash(
            form_data.password,
            db_user.salt
        ).decode("utf-8")
        == db_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = security.create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token}

@app.get("/user",response_model=schemas.User)
async def get_user_profile(token: schemas.Token,db: Session = Depends(get_db)):    
    email=security.get_current_user_email(token.access_token)
    db_user = crud.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found or session expired")
    return db_user

@app.get("/user/notes")
async def get_notes(access_token: str,db: Session = Depends(get_db)):
    email=security.get_current_user_email(access_token)
    db_user = crud.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found or session expired")
    return crud.get_user_notes(db,db_user)

@app.post("/user/notes")
async def post_user_items(request:Request,access_token:str,db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    # print(request.json())
    json = await request.json()
    print(f"[POST /user/notes] START: title={repr(json.get('note', {}).get('title', '')[:50])}")
    # access_token = json["token"]["access_token"]
    email=security.get_current_user_email(access_token)
    db_user = crud.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found or session expired")
    note = json["note"]
    
    try:
        print(f"[POST /user/notes] Creating note for user_id={db_user.id}")
        new_note = crud.create_user_note(db, note, db_user.id)
        print(f"[POST /user/notes] Note created: note_id={new_note.id}")
        
        # schedule AI summarization/tagging (SYNCHRONOUS for debugging)
        print(f"[POST /user/notes] Running AI generation synchronously")
        generate_and_store_ai(note, new_note.id)
        print(f"[POST /user/notes] AI generation complete")
        
    except IntegrityError:
        # Fallback: attempt update if the note id conflicts (idempotency)
        print(f"[POST /user/notes] IntegrityError - rolling back and attempting update")
        db.rollback()
        crud.update_user_note(db, note, db_user.id)
        new_note = db.query(models.Note).filter(models.Note.owner_id == db_user.id).order_by(models.Note.id.desc()).first()

    created = None
    if getattr(new_note, "id", None):
        created = {
            "id": new_note.id,
            "title": new_note.title,
            "description": new_note.description,
        }

    # Backward-compatible response: keep original payload shape, add created_note.
    print(f"[POST /user/notes] SUCCESS: created_note_id={created.get('id') if created else 'None'}")
    return {"message": json, "created_note": created}


@app.put("/user/notes")
async def update_user_note(request:Request,access_token:str,db: Session = Depends(get_db)):
    json = await request.json()
    # access_token = json["token"]["access_token"]
    email=security.get_current_user_email(access_token)
    db_user = crud.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found or session expired")
    note = json["note"]
    crud.update_user_note(db,note,db_user.id)
    return {"message":json}

@app.delete("/user/notes")
async def post_user_items(request:Request,access_token:str,db: Session = Depends(get_db)):
    json = await request.json()
    # access_token = json["token"]["access_token"]
    email=security.get_current_user_email(access_token)
    db_user = crud.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found or session expired")
    note = json["note"]
    crud.delete_user_note(db,note,db_user.id)
    # email=security.get_current_user_email(access_token)
    # db_user = crud.get_user_by_email(db, email=email)
    return {"message":json}
    
    # return test
# @app.post("/test")
# async def playground(request:Request):
#     json = await request.json()
#     print(json)
#     return {"message":json}

# # Replace with JWT Access token response
# @app.post("/login/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = security.get_user_by_email(db, email=user.email)
#     if (security.verify_hash(user.password,db_user.salt).decode('utf-8') == db_user.hashed_password):
#         return db_user
#     else:
#         raise HTTPException(status_code=400, detail="Invalid Login")

@app.post("/user/notes/semantic-search", response_model=schemas.SemanticSearchResponse)
async def semantic_search_endpoint(request: Request, access_token: str, db: Session = Depends(get_db)):
    body = await request.json()

    # Basic shape validation (keeps changes additive + avoids broad refactors)
    query = body.get("query")
    top_k = body.get("top_k", 5)
    try:
        top_k = int(top_k)
    except Exception:
        top_k = 5
    if not isinstance(query, str) or not query.strip():
        raise HTTPException(status_code=400, detail="query must be a non-empty string")
    top_k = max(1, min(top_k, 20))

    email = security.get_current_user_email(access_token)
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found or session expired")

    # Embed + search (pgvector when available; otherwise JSON+cosine fallback)
    resp = semantic_search(db, user.id, query, top_k)

    return resp




