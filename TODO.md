# TODO.md (Phase 2 - Semantic Search with pgvector)

- [x] Add additive pgvector + embedding_vector column to NoteAI (384 dims) without breaking SQLite

- [x] Add safe runtime detection of Postgres+pgvector availability

- [x] Persist embeddings to BOTH NoteAI.embedding (JSON string) and NoteAI.embedding_vector (pgvector vector)

- [ ] Implement POST /user/notes/semantic-search endpoint
  - [ ] embed query (sentence-transformers all-MiniLM-L6-v2)
  - [ ] cosine similarity search with pgvector when available
  - [ ] Python cosine similarity fallback using NoteAI.embedding when pgvector not available
  - [ ] user-scoped retrieval only
- [ ] Update SemanticSearchPage.tsx to be functional
  - [ ] loading + error handling
  - [ ] no matches state
  - [ ] render ranked results with similarity score
- [ ] Runtime validation checklist
  - [ ] embeddings generated after note creation
  - [ ] summaries/tags still work
  - [ ] dashboard unchanged
  - [ ] semantic search returns relevant matches
  - [ ] frontend search works
  - [ ] no auth/CORS regressions
- [ ] Run backend + frontend smoke tests

