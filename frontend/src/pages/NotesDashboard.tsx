import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../lib/api';
import { getToken } from '../lib/token';
import { Link } from 'react-router-dom';
import NoteCard from '../ui/NoteCard';

export default function NotesDashboard() {
  const token = getToken();
  const [notes, setNotes] = useState<Array<{ id: string; title: string; description: string }>>([]);
  const [loading, setLoading] = useState(true);

  const access_token = useMemo(() => token || '', [token]);

  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        console.log('[NotesDashboard] Fetching notes...');
        const resp = await api.get('/user/notes', {
          params: { access_token },
        });
        console.log('[NotesDashboard] Fetched notes:', resp.data);
        if (!cancelled) {
          setNotes(resp.data || []);
          console.log('[NotesDashboard] Setting notes state ids:', (resp.data || []).map((x: any) => x.id));
        }

      } catch (err) {
        console.error('[NotesDashboard] Fetch error:', err);
        // swallow; UI shows empty state
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [access_token, token]);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-sm text-slate-400">Your notes</div>
          <div className="text-xl font-semibold">Dashboard</div>
        </div>
        <Link
          to="/notes/new"
          className="rounded-xl bg-indigo-600/90 px-4 py-2 font-semibold hover:bg-indigo-500 transition"
        >
          + Create
        </Link>
      </div>

      {loading ? (
        <div className="rounded-2xl bg-slate-900/40 ring-1 ring-slate-800 p-4">Loading…</div>
      ) : notes.length === 0 ? (
        <div className="rounded-2xl bg-slate-900/40 ring-1 ring-slate-800 p-4 text-slate-300">
          No notes yet. Create one to see AI summaries.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {notes.map((n) => (
            <NoteCard key={n.id} note={n} access_token={access_token} />
          ))}
        </div>
      )}

      <div className="mt-6 text-xs text-slate-500">
        AI summaries are generated in the background. Refresh if you just created a note.
      </div>
    </div>
  );
}

