import json
import traceback
from typing import List, Tuple

from .database import SessionLocal, DATABASE_URL_EFFECTIVE
from .config import EMBEDDING_PROVIDER
from . import models, schemas, crud
from .ai import _compute_embedding
from .pgvector_utils import pgvector_capabilities
from sqlalchemy import text


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    # Safe cosine similarity for Python fallback
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return -1.0
    return dot / ((na ** 0.5) * (nb ** 0.5))


def _load_embedding_from_json(embedding_json: str) -> List[float] | None:
    try:
        vec = json.loads(embedding_json)
        if isinstance(vec, list) and vec:
            return [float(x) for x in vec]
    except Exception:
        return None
    return None


def semantic_search_python(db, user_id: int, query_vec: List[float], top_k: int) -> List[Tuple[models.Note, float]]:
    # Python fallback: iterate user's notes with embeddings stored in NoteAI.embedding JSON.
    print(f"[semantic_search_python] START user_id={user_id} top_k={top_k}")
    
    rows = (
        db.query(models.Note)
        .join(models.NoteAI, models.NoteAI.note_id == models.Note.id)
        .filter(models.Note.owner_id == user_id)
        .filter(models.NoteAI.embedding != None)  # noqa: E711
        .all()
    )
    
    print(f"[semantic_search_python] Loaded {len(rows)} rows with embeddings from DB")

    scored: List[Tuple[models.Note, float]] = []
    for idx, note in enumerate(rows):
        ai = getattr(note, "ai", None)
        # Handle list/collection backref or single object gracefully
        if isinstance(ai, list) or hasattr(ai, "__iter__"):
            ai = ai[0] if ai else None

        if not ai or not ai.embedding:
            print(f"[semantic_search_python] Row {idx}: SKIP (no ai or embedding)")
            continue
        vec = _load_embedding_from_json(ai.embedding)
        if vec is None:
            print(f"[semantic_search_python] Row {idx}: SKIP (embedding parse failed)")
            continue
        sim = _cosine_similarity(query_vec, vec)
        print(f"[semantic_search_python] Row {idx}: note_id={note.id} similarity={sim:.4f} title={repr(note.title[:30])}")
        scored.append((note, sim))

    scored.sort(key=lambda t: t[1], reverse=True)
    result = scored[: max(0, top_k)]
    print(f"[semantic_search_python] Returning {len(result)} results after filtering")
    return result


def semantic_search(db, user_id: int, query: str, top_k: int) -> schemas.SemanticSearchResponse:
    # Ensure embedding provider is configured; if not, still attempt _compute_embedding (which is best-effort).
    print(f"[semantic_search] START query={repr(query[:50])} user_id={user_id} top_k={top_k}")
    
    query_vec = _compute_embedding(query.strip())
    if query_vec is None:
        print(f"[semantic_search] Query embedding generation FAILED")
        return schemas.SemanticSearchResponse(results=[], pgvector_used=False)
    
    print(f"[Embedding Generation] SUCCESS: Computed dense embedding with dimension={len(query_vec)}")
    print(f"[semantic_search] Query embedding generated: length={len(query_vec)}")

    caps = pgvector_capabilities(DATABASE_URL_EFFECTIVE)
    pgvector_used = bool(caps.get("using_pgvector"))
    print(f"[semantic_search] Using pgvector={pgvector_used}")

    # pgvector runtime query: best-effort. If it fails, fallback to python.
    if pgvector_used:
        try:
            print(f"[semantic_search] Attempting pgvector SQL query")
            # We use raw SQL to avoid ORM/varying pgvector type behavior.
            # cosine similarity: use <=> operator on pgvector (inner product distance).
            # If embeddings are not normalized, it's still a reasonable retrieval.
            # For cosine specifically, we use pgvector's cosine distance: embedding_vector <=> query_vec
            # and convert to similarity = 1 - distance.
            # Note: exact operator depends on pgvector version; use pgvector's cosine distance function if available.

            # Build Postgres vector literal
            vec_literal = "[" + ",".join(str(float(x)) for x in query_vec) + "]"

            sql = (
                "SELECT n.id, n.title, n.description, "
                "       (1 - (ai.embedding_vector <=> :qvec)) AS similarity "
                "FROM notes n "
                "JOIN note_ai ai ON ai.note_id = n.id "
                "WHERE n.owner_id = :user_id "
                "  AND ai.embedding_vector IS NOT NULL "
                "ORDER BY ai.embedding_vector <=> :qvec "
                "LIMIT :top_k"
            )

            result = db.execute(
                text(sql),
                {
                    "qvec": vec_literal,
                    "user_id": user_id,
                    "top_k": top_k,
                },
            )

            out: List[schemas.SemanticSearchResult] = []
            for row in result.fetchall():
                out.append(
                    schemas.SemanticSearchResult(
                        note_id=row.id,
                        title=row.title,
                        description=row.description,
                        similarity=float(row.similarity),
                    )
                )
            print(f"[Semantic Search] Path used: pgvector")
            print(f"[Semantic Search] SUCCESS: Search returned {len(out)} results")
            print(f"[semantic_search] pgvector query returned {len(out)} results")
            return schemas.SemanticSearchResponse(results=out, pgvector_used=True)
        except Exception as e:
            print(f"[semantic_search] pgvector query FAILED: {str(e)}")
            traceback.print_exc()
            print(f"[semantic_search] Falling back to Python implementation")
            # fall back

    # Python fallback
    print(f"[semantic_search] Using Python fallback search")
    scored = semantic_search_python(db, user_id, query_vec, top_k)
    out: List[schemas.SemanticSearchResult] = []
    for note, sim in scored:
        out.append(
            schemas.SemanticSearchResult(
                note_id=note.id,
                title=note.title,
                description=note.description,
                similarity=float(sim),
            )
        )
    
    print(f"[Semantic Search] Path used: python fallback")
    print(f"[Semantic Search] SUCCESS: Search returned {len(out)} results")
    print(f"[semantic_search] Returning {len(out)} final results")
    return schemas.SemanticSearchResponse(results=out, pgvector_used=False)

