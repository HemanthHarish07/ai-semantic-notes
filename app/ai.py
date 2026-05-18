import json
import traceback
import requests
import re
from sqlalchemy import inspect
from .database import SessionLocal
from . import crud
from .config import EMBEDDING_PROVIDER, GEMINI_API_KEY


# Lazy load HF model (sentence-transformers) globally.
_hf_model = None

def _load_hf_model():
    global _hf_model

    if _hf_model is None:
        try:
            print("[HF] Loading SentenceTransformer model")

            import os
            os.environ["TRANSFORMERS_CACHE"] = "/tmp/huggingface"
            os.environ["HF_HOME"] = "/tmp/huggingface"

            from sentence_transformers import SentenceTransformer

            _hf_model = SentenceTransformer(
                "all-MiniLM-L6-v2",
                cache_folder="/tmp/huggingface"
            )

            print("[HF] Embedding model loaded successfully")

        except Exception as e:
            print(f"[HF] Failed to load embedding model: {e}")
            traceback.print_exc()
            _hf_model = None

    return _hf_model

def _compute_embedding(text: str):
    """Returns embedding list[float] (384 dims) or None."""
    try:
        model = _load_hf_model()
        if model is None:
            print("[_compute_embedding] no HF model available")
            return None
        print("[_compute_embedding] encoding text", repr(text[:80]))
        vec = model.encode(text)
        vec_list = vec.tolist() if hasattr(vec, 'tolist') else list(vec)
        print("[_compute_embedding] embedding length", len(vec_list))
        return vec_list
    except Exception:
        print("[_compute_embedding] exception during embedding generation")
        traceback.print_exc()
        return None


def simple_summarize_and_tag(note: dict):

    text = (note.get("title", "") + "\n" + note.get("description", "")).strip()
    summary = text[:300]
    # naive tags: top 3 frequent words excluding short words
    words = re.findall(r"\w+", text.lower())
    freq = {}
    for w in words:
        if len(w) <= 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    tags = sorted(freq.keys(), key=lambda k: -freq[k])[:3]
    return summary, tags


def call_gemini_summarize(note: dict):
    """Call Gemini via the official google-generativeai SDK.


    Expected output: JSON {"summary": str, "tags": [str, ...]}

    If the SDK is not installed, raise to be handled by the caller as a graceful fallback.
    """

    prompt = (
        "Summarize the following note and return ONLY a JSON object with keys "
        "'summary' (string) and 'tags' (array of strings). "
        "No markdown.\n"
        f"Title: {note.get('title','')}\n"
        f"Description: {note.get('description','')}"
    )

    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt)
        text = getattr(resp, "text", None) or str(resp)

        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return text[:300], []

        parsed = json.loads(m.group(0))
        summary = parsed.get("summary")
        tags = parsed.get("tags") or []
        return summary or text[:300], tags
    except Exception:
        traceback.print_exc()
        raise


def generate_and_store_ai(note: dict, note_id: str):
    # note: run in background; create own DB session
    db = SessionLocal()
    try:
        try:
            print(f"[generate_and_store_ai] START note_id={note_id} title={repr(note.get('title','')[:50])}")
            
            summary = None
            tags = []
            if GEMINI_API_KEY:
                try:
                    print(f"[generate_and_store_ai] Attempting Gemini summarization")
                    summary, tags = call_gemini_summarize(note)
                    print(f"[generate_and_store_ai] Gemini success: summary_len={len(summary) if summary else 0}, tags={tags}")
                except Exception as e:
                    # Gemini failed; keep existing fallback behavior
                    print(f"[generate_and_store_ai] Gemini FAILED: {str(e)}")
                    traceback.print_exc()
                    summary, tags = simple_summarize_and_tag(note)
                    print(f"[generate_and_store_ai] Using fallback: summary_len={len(summary)}, tags={tags}")
            else:
                print(f"[generate_and_store_ai] No GEMINI_API_KEY; using fallback summarization")
                summary, tags = simple_summarize_and_tag(note)
                print(f"[generate_and_store_ai] Fallback done: summary_len={len(summary)}, tags={tags}")

            tags_str = ",".join(tags)

            # Generate embedding from combined title + description
            combined_text = (note.get("title", "") + " " + note.get("description", "")).strip()
            print(f"[generate_and_store_ai] Computing embedding for text: {repr(combined_text[:100])}")
            embedding_vector = _compute_embedding(combined_text)
            if embedding_vector is not None:
                import json as json_lib
                embedding_json = json_lib.dumps(embedding_vector)
                print(f"[Embedding Generation] SUCCESS: Computed dense embedding with dimension={len(embedding_vector)}")
                print(f"[generate_and_store_ai] Embedding computed: length={len(embedding_vector)}")
            else:
                embedding_json = None
                embedding_vector = None
                print("[generate_and_store_ai] Embedding computation failed; will save summary/tags anyway")

            # create or update NoteAI
            try:
                has_embedding_vector_column = False
                try:
                    inspector = inspect(db.bind)
                    columns = {col['name'] for col in inspector.get_columns('note_ai')}
                    has_embedding_vector_column = 'embedding_vector' in columns
                except Exception:
                    print('[generate_and_store_ai] failed to inspect note_ai table columns')
                    traceback.print_exc()

                print(f"[generate_and_store_ai] note_id={note_id} has_embedding_vector_column={has_embedding_vector_column}")

                # IMPORTANT: do NOT use load_only() here.
                # With SQLite + partial column loading, embedding persistence was observed to fail.
                existing = (
                    db.query(crud.models.NoteAI)
                    .filter(crud.models.NoteAI.note_id == note_id)
                    .first()
                )


                if existing:
                    existing.summary = summary
                    existing.tags = tags_str
                    if embedding_json:
                        existing.embedding = embedding_json

                    if embedding_vector is not None and has_embedding_vector_column:
                        try:
                            if db.bind.dialect.name == "postgresql":
                                existing.embedding_vector = embedding_vector
                            else:
                                existing.embedding_vector = embedding_json
                        except Exception:
                            print('[generate_and_store_ai] failed assigning embedding_vector to existing row')
                            traceback.print_exc()

                    try:
                        db.commit()
                        print(f"[generate_and_store_ai] commit succeeded existing note_id={note_id}")
                    except Exception:
                        print(f"[generate_and_store_ai] commit failed existing note_id={note_id}")
                        traceback.print_exc()
                        db.rollback()
                        raise
                else:
                    new = crud.models.NoteAI(note_id=note_id, summary=summary, tags=tags_str)
                    if embedding_json:
                        new.embedding = embedding_json

                    if embedding_vector is not None and has_embedding_vector_column:
                        try:
                            if db.bind.dialect.name == "postgresql":
                                new.embedding_vector = embedding_vector
                            else:
                                new.embedding_vector = embedding_json
                        except Exception:
                            print('[generate_and_store_ai] failed assigning embedding_vector to new row')
                            traceback.print_exc()

                    db.add(new)
                    try:
                        db.commit()
                        print(f"[generate_and_store_ai] commit succeeded new note_id={note_id}")
                    except Exception:
                        print(f"[generate_and_store_ai] commit failed new note_id={note_id}")
                        traceback.print_exc()
                        db.rollback()
                        raise

            except Exception:
                print(f"[generate_and_store_ai] DB upsert failed note_id={note_id}")
                traceback.print_exc()
                db.rollback()
                raise

        except Exception:
            # Ensure background-task exceptions are visible with full traceback
            print(f"[generate_and_store_ai] FAILED note_id={note_id}")
            traceback.print_exc()
            raise
    finally:
        db.close()

