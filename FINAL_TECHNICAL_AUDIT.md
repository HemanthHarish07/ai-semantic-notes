# Final Technical Audit

Scope
- Purpose: minimal, high-ROI changes to make the project runnable and presentable as a junior-level portfolio piece.

Changes made (concrete)
- `app/database.py`: read `DATABASE_URL` from environment; use SQLite fallback `sqlite:///./dev.db` for local development; use appropriate `connect_args` for SQLite.
- `app/security.py`: read `SECRET_KEY` from environment with a dev default; keep existing PBKDF2 hashing logic.
- `app/main.py`, `app/crud.py`, `app/models.py`, `app/security.py`: changed intra-package imports to package-relative imports to avoid PYTHONPATH issues when running `uvicorn app.main:app`.

Why these changes
- The original code assumed environment variables and a particular runtime environment (PYTHONPATH or Docker). For portfolio use, it's essential that reviewers can run the app locally without extra setup.

Runtime verification
- Installed dependencies and started the server with the workspace Python.
- Verified endpoints: user creation, token issuance, note create/list.

Security considerations
- Custom JWT: functional but not production-ready. It uses HMAC SHA-256 but lacks robust claim validation and edge-case handling. Consider replacing with `PyJWT` and validating expiry as a UNIX timestamp or using standard claim checks.
- Secrets: `SECRET_KEY` must be set in production; the repo default is intentionally insecure for local dev.

Docker notes
- `docker-compose.yaml` references an external network `proxy_gateway_default`. If you want to run with Docker locally, either remove the `external: true` section or create that network beforehand.

Next steps (small, high ROI)
- Add `.env.example` and update `README.md` (I can do this).
- Replace custom JWT helpers with a standard library or add comprehensive unit tests around token handling.
- Add a GitHub Actions workflow to run linting and basic tests on PRs.
