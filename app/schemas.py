from typing import List, Optional
from pydantic import BaseModel

# Ensure consistent tags typing across pydantic v1/v2
# (some dev runs were hitting tags=None situations)



class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str

class Note(BaseModel):
    id: str
    title:str
    description:str

class NoteRequest(BaseModel):
    title: str
    description: str


class NoteAIResponse(BaseModel):
    note_id: str
    summary: str | None = None
    tags: list[str] = []
    embedding_present: bool = False


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SemanticSearchResult(BaseModel):
    note_id: str
    title: str
    description: str
    similarity: float


class SemanticSearchResponse(BaseModel):
    results: list[SemanticSearchResult]
    pgvector_used: bool = False

