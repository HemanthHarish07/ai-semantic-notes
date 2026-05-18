import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { clearToken, getToken } from '../lib/token';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const token = getToken();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) navigate('/login');
  }, [token, navigate]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl px-4 py-6">
        <header className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-indigo-600/20 ring-1 ring-indigo-400/30 grid place-items-center text-indigo-200">
              N
            </div>
            <div className="leading-tight">
              <div className="text-sm text-slate-300">NeuroNote AI</div>
              <div className="text-lg font-semibold">Semantic Knowledge Base</div>
            </div>
          </div>

          <nav className="flex items-center gap-3 text-sm">
            <Link className="text-slate-300 hover:text-slate-100" to="/">
              Notes
            </Link>
            <Link
              className="text-slate-300 hover:text-slate-100"
              to="/semantic-search"
            >
              Semantic search
            </Link>
            <Link
              className="rounded-lg bg-indigo-600 px-3 py-2 hover:bg-indigo-500 transition"
              to="/notes/new"
            >
              + New
            </Link>
            <button
              className="rounded-lg px-3 py-2 hover:bg-slate-800 transition"
              onClick={() => {
                clearToken();
                navigate('/login');
              }}
            >
              Sign out
            </button>
          </nav>
        </header>

        {children}
      </div>
    </div>
  );
}

