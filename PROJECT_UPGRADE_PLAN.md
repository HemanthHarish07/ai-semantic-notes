# Project Upgrade Plan — AI-powered Semantic Notes (upgrade plan)

Goal
- Add AI summarization/tagging and semantic search to the existing JWT-authenticated FastAPI notes backend, with a minimal React frontend, preserving existing behavior and keeping changes additive and low-risk.

Verified current features (runtime-validated)
- FastAPI backend with user management and JWT flows (`POST /users/`, `POST /token`).
- Notes CRUD endpoints (`GET/POST /user/notes`) working with a developer SQLite fallback (verified).
- Static example endpoint `/api/files` working.

Proposed additive upgrades (minimal-risk order)
1. Add configuration and secrets management
   - Add `dotenv` support and a `.env.example` file for keys: `SECRET_KEY`, `DATABASE_URL`, `EMBEDDING_PROVIDER`, `EMBEDDING_API_KEY`, `GENIE_API_KEY` (or similar).
   - Rationale: centralizes runtime secrets and avoids hardcoding.

2. AI Summarization + Tagging (safe hook)
   - On `POST /user/notes` (server-side), call an AI summarization/tagging function asynchronously (background task) to generate a short summary and tags for the note.
   - Store `summary` and `tags` fields on the `notes` table (add nullable columns) so existing behavior persists even if AI calls fail.
   - Make the AI call pluggable via a provider interface (so we can swap Gemini/OpenAI).
   - Validation: if no API key provided, skip AI call and keep existing behavior.

3. Embeddings + `pgvector` integration (optional for prod, fallback locally)
   - Add an embeddings table or extend `notes` with a vector column when using Postgres+pgvector.
   - For local dev (SQLite), keep a fallback storing raw embeddings as JSON or skip vector storage — semantic search will be limited locally.
   - Required: confirm whether you will provide a Postgres instance with `pgvector` extension (or whether we should attempt to create it in Docker). Ask user before proceeding.

4. Semantic Search API
   - New endpoint `POST /search` (or `GET`) that accepts query, generates embeddings via chosen provider, retrieves nearest neighbors via `pgvector` index (or fallback approximate search), and returns ranked notes.
   - Keep original note listing endpoints unchanged.

5. Lightweight React frontend (minimal)
   - Create `frontend/` with a small React app (Vite) that supports register/login, notes dashboard, semantic search box, and note creation form (uses existing APIs).
   - Keep separate from backend; simple `npm` scripts to build/run; optional `docker-compose` service.

6. Docker + Compose adjustments
   - Optionally enhance `docker-compose.yaml` to include a Postgres service with `pgvector` and remove or make optional the external `proxy_gateway_default` network.
   - Document how to enable Postgres+pgvector for full semantic search.

7. Docs, tests, CI
   - Add `.env.example`, update `README.md`, `demo_script.md`, and `FINAL_TECHNICAL_AUDIT.md` with new features and limitations.
   - Add basic unit tests for the AI hook and semantic search logic (mocking external API calls).
   - Add GitHub Actions workflow to run lint and tests.

Potential breaking points and mitigations
- Schema changes: adding `summary`, `tags`, and optional vector columns to `notes` is a DB migration. Mitigation: add nullable columns with defaults and ensure code handles missing columns gracefully.
- External APIs: AI provider rate limits/keys. Mitigation: make AI calls optional and run in background; fall back to no-AI behavior when no key or on error.
- pgvector dependency: Docker/Postgres setup complexity. Mitigation: keep local SQLite fallback; document that semantic search requires Postgres+pgvector in production/demo.

Runtime validation plan (after each change)
1. Implement config + `.env.example`; run app and validate existing endpoints still work.
2. Implement AI hook: add nullable DB fields, add background task that no-ops when no key; validate creating notes still works with and without API key.
3. Implement embeddings and semantic search with Postgres+pgvector behind a feature flag; validate with real Postgres or mock tests.
4. Add frontend scaffold and validate login, create note, and search flows against the backend.

Questions I need you to answer before I implement AI/pgvector features
- Which embedding / LLM provider should I integrate for embeddings and summarization? (options: Gemini via Vertex AI, OpenAI, HuggingFace embeddings, or other)
- Do you have API keys available for the chosen provider? If yes, will you provide them or should I implement using environment variables for you to fill in? (I WILL NOT add keys to the repo.)
- Do you want me to enable Postgres+pgvector in `docker-compose.yaml` or keep Postgres optional and document steps to enable it? (If enable, do you permit me to modify `docker-compose.yaml` to remove the external network requirement?)
- For local dev, do you prefer the SQLite fallback to remain the default? (recommended for reviewer convenience)
- Frontend: confirm lightweight React (Vite + React) is acceptable.

If you confirm the above, I will proceed with step 1 (config + `.env.example`) and then implement step 2 (AI summarization hook) with safe fallbacks.
