import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';
import { setToken } from '../lib/token';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);

    try {
      const resp = await api.post('/token', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      setToken(resp.data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Login failed');
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 grid place-items-center px-4">
      <div className="w-full max-w-md rounded-2xl bg-slate-900/60 ring-1 ring-slate-800 p-6">
        <div className="mb-6">
          <div className="text-sm text-slate-300">Welcome back</div>
          <div className="text-2xl font-semibold mt-1">Login to NeuroNote AI</div>
          <div className="mt-2 text-sm text-slate-400">AI summaries, tags, and semantic retrieval.</div>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-slate-300">Email</label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-xl bg-slate-950/40 ring-1 ring-slate-800 px-3 py-2 outline-none focus:ring-indigo-500"
              type="email"
              required
            />
          </div>
          <div>
            <label className="text-sm text-slate-300">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-xl bg-slate-950/40 ring-1 ring-slate-800 px-3 py-2 outline-none focus:ring-indigo-500"
              type="password"
              required
            />
          </div>

          {error && (
            <div className="rounded-xl bg-red-500/10 ring-1 ring-red-500/30 px-3 py-2 text-sm text-red-200">
              {error}
            </div>
          )}

          <button
            className="w-full rounded-xl bg-indigo-600 px-4 py-2 font-semibold hover:bg-indigo-500 transition"
            type="submit"
          >
            Login
          </button>
        </form>

        <div className="mt-5 text-sm text-slate-400">
          No account?{' '}
          <Link to="/register" className="text-indigo-300 hover:underline">
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}

