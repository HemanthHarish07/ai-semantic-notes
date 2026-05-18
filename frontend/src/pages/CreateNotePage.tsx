import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { getToken } from '../lib/token';

export default function CreateNotePage() {
  const token = getToken();
  const navigate = useNavigate();

  const access_token = token || '';
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const resp = await api.post(
        '/user/notes',
        { note: { title, description } },
        { params: { access_token } }
      );
      navigate('/');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create note');
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-4">
        <div className="text-sm text-slate-400">Add note</div>
        <div className="text-xl font-semibold">Create a new knowledge entry</div>
      </div>

      <form onSubmit={onSubmit} className="rounded-2xl bg-slate-900/40 ring-1 ring-slate-800 p-5 space-y-4">
        <div>
          <label className="text-sm text-slate-300">Title</label>
          <input
            className="mt-1 w-full rounded-xl bg-slate-950/40 ring-1 ring-slate-800 px-3 py-2 outline-none focus:ring-indigo-500"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="text-sm text-slate-300">Description</label>
          <textarea
            className="mt-1 w-full min-h-[140px] rounded-xl bg-slate-950/40 ring-1 ring-slate-800 px-3 py-2 outline-none focus:ring-indigo-500"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>

        {error && (
          <div className="rounded-xl bg-red-500/10 ring-1 ring-red-500/30 px-3 py-2 text-sm text-red-200">
            {error}
          </div>
        )}

        <button
          disabled={submitting}
          className="w-full rounded-xl bg-indigo-600 px-4 py-2 font-semibold hover:bg-indigo-500 transition disabled:opacity-60"
          type="submit"
        >
          {submitting ? 'Creating…' : 'Create note'}
        </button>
      </form>
    </div>
  );
}

