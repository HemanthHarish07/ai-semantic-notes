# NeuroNote AI — Semantic Knowledge Base

NeuroNote AI is an AI-powered semantic knowledge base and note retrieval platform. The platform leverages modern generative AI for summarization, computes dense vector embeddings, and delivers production-ready semantic vector search queries.

---

## 🌐 Live Demo

Frontend: https://ai-semantic-notes-jnnk.vercel.app  
Backend API Docs: https://ai-semantic-notes.onrender.com/docs

## 🚀 Key Features

* **Advanced Semantic Search**: Retrieve knowledge entries based on conceptual meaning rather than exact word matches. Supports production-ready **Neon PostgreSQL + pgvector** integration for high-performance vector similarity searches, and automatically falls back to an optimized **pure-Python Cosine Similarity** search utilizing serialized JSON float arrays when running on SQLite.
* **AI-Powered Summarization & Auto-Tagging**: Generates structured, concise summaries and semantic tags for every note using Google's `gemini-1.5-flash` model with fallback extraction logic.
* **Bulletproof Authentication & Session Management**: JWT-based authentication with PBKDF2 password hashing. Features automated **Axios response interceptors** on the frontend that catch `401 Unauthorized` states (e.g. from deleted/expired database sessions) to automatically clean up `localStorage` and redirect to login.
* **Rich Glassmorphism UI**: Beautiful, interactive, modern dark-mode user experience utilizing TailwindCSS.

---

## 🧰 Tech Stack

| Layer            | Technology                |
| ---------------- | ------------------------- |
| Frontend         | React + TypeScript + Vite |
| Backend          | FastAPI                   |
| Database         | Neon PostgreSQL           |
| Vector Search    | pgvector                  |
| ORM              | SQLAlchemy                |
| Authentication   | JWT                       |
| AI Summarization | Gemini 1.5 Flash          |
| Embeddings       | sentence-transformers     |
| Deployment       | Vercel + Render           |
| Styling          | TailwindCSS               |


## 🛠️ Architecture Overview
Frontend → FastAPI API → AI Processing → Embedding Generation → Neon PostgreSQL + pgvector → Semantic Retrieval

### Backend (FastAPI)
* **Web Framework**: FastAPI for high-performance, async API routing.
* **Database & ORM**: SQLAlchemy with Neon PostgreSQL / SQLite capability.
* **Embeddings Pipeline**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2` generating 384-dimensional vector representations.
* **AI Model Client**: Google Generative AI (`google-generativeai`) using `gemini-1.5-flash` (with robust standard fallback tagging if API limits are hit).

### Frontend (React + Vite + TypeScript)
* **Dev Server**: Vite for ultra-fast hot reloading.
* **Styling**: TailwindCSS with harmonized slate/indigo glassmorphism themes.
* **API Client**: Axios with unified request/response interceptors to prevent stale token errors.

---

## 📂 Project Structure

```
├── app/                   # Backend codebase
│   ├── main.py            # FastAPI application entrypoint & API routes
│   ├── ai.py              # Gemini summarizer & SentenceTransformers pipeline
│   ├── crud.py            # Database CRUD transactions
│   ├── models.py          # SQLAlchemy models (User, Note, NoteAI)
│   ├── schemas.py         # Pydantic schemas (validations)
│   ├── security.py        # JWT generation & password hashing
│   └── database.py        # Database connection & schema setup (Postgres + SQLite fallback)
├── frontend/              # Frontend codebase (React + Vite + TS)
│   ├── src/
│   │   ├── components/    # Reusable layouts (AuthLayout, NoteCard)
│   │   ├── lib/           # Axios API client & token utilities
│   │   ├── pages/         # View pages (Dashboard, Search, Login, Register)
│   │   └── ui/            # UI components (NoteCard)
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yaml    # Production orchestration definition
└── requirements.txt       # Frozen, verified Python dependencies
```

---

## ⚙️ Setup and Installation

### Prerequisites
* Python 3.10+
* Node.js 18+ (npm)

---

### 1. Backend Setup

1. **Navigate to backend and prepare virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate       # On Windows (cmd/powershell)
   source .venv/bin/activate    # On macOS/Linux
   ```

2. **Install exact frozen dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory (or copy `.env.example`):
   ```ini
   SECRET_KEY=your_secure_jwt_signing_key_here
   GEMINI_API_KEY=your_google_gemini_api_key_here
   # Optional: DATABASE_URL=postgresql://user:pass@host/db
   ```
   *Note: If `DATABASE_URL` is omitted, the app will automatically initialize and use `dev.db` (SQLite).*

4. **Start the Backend Server:**
   ```bash
   python -m uvicorn app.main:app --port 8000 --reload
   ```
   *The Swagger API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).*

---

### 2. Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node modules:**
   ```bash
   npm install
   ```

3. **Start the Frontend Development Server:**
   ```bash
   npm run dev
   ```
   *The app will launch on [http://localhost:5173](http://localhost:5173) (or `5174` if port `5173` is occupied).*

---

## 🌐 Production Deployment

### Frontend

Deployed on Vercel:

* React + Vite production build
* Automatic CI/CD from GitHub
* Environment-based API configuration

### Backend

Deployed on Render using Docker:

* Dockerized deployment with dependency-isolated runtime environment
* FastAPI + Uvicorn production server
* HuggingFace embedding pipeline
* Neon PostgreSQL integration
* pgvector semantic retrieval

### Database

Hosted on Neon PostgreSQL:

* Serverless PostgreSQL
* pgvector extension enabled
* Persistent cloud vector storage


## 🧪 Verification & Testing Flow

To test all core features end-to-end:
1. **Register** a new account (`http://localhost:5173/register`).
2. **Log In** (`http://localhost:5173/login`) to acquire a fresh JWT token.
3. **Create Notes** by clicking `+ New` (`http://localhost:5173/notes/new`):
   * *Entry 1:* Title: `"Federated Learning"`, Description: `"Privacy-preserving machine learning across edge devices."`
   * *Entry 2:* Title: `"Vector Similarity"`, Description: `"Dense embedding representations searched via nearest neighbors."`
4. **Dashboard**: Verify that summaries and tags generated by Gemini appear cleanly.
5. **Semantic Search** (`http://localhost:5173/semantic-search`): Type a natural language query like `"privacy model aggregation"` or `"dense coordinates"` and verify that the results are semantically ranked and similarity percentages are displayed!

## ✅ Current Status

* Production deployed
* Semantic vector search operational
* AI summarization pipeline active
* Neon PostgreSQL + pgvector integrated
* JWT authentication secured
* End-to-end frontend/backend deployment completed
