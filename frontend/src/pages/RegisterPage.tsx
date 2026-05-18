import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    try {
      await api.post('/users/', { email, password });
      navigate('/login');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Registration failed');
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 grid place-items-center px-4">
      <div className="w-full max-w-md rounded-2xl bg-slate-900/60 ring-1 ring-slate-800 p-6">
        <div className="mb-6">
          <div className="text-sm text-slate-300">Create account</div>
          <div className="text-2xl font-semibold mt-1">Register NeuroNote AI</div>
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
            Create account
          </button>
        </form>

        <div className="mt-5 text-sm text-slate-400">
          Already have an account?{' '}
          <Link to="/login" className="text-indigo-300 hover:underline">
            Login
          </Link>
        </div>
      </div>
    </div>
  );
}

