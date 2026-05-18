# NeuroNote AI — Frontend (React + Vite)

Lightweight demo UI for the existing FastAPI backend.

## Quickstart

1) Install dependencies

```powershell
cd frontend
npm install
```

2) Run dev server

```powershell
npm run dev
```

3) Configure backend URL (optional)

Create `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## JWT persistence
- Access token is stored in `localStorage` under `neuronote_access_token`.
- The backend expects `access_token` as a query parameter, so all note/AI calls pass it via `params: { access_token }`.

