import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';

export default function NoteCard({
  note,
  access_token,
}: {
  note: { id: string; title: string; description: string };
  access_token: string;
}) {
  const [summary, setSummary] = useState<string | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [embeddingPresent, setEmbeddingPresent] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function loadAi() {
      setLoading(true);
      console.log(`[NoteCard] Loading AI data for note_id=${note.id}`);
      try {
        console.log(`[NoteCard] Fetching AI for note_id=${note.id} with access_token present=${!!access_token}`);
        const resp = await api.get(`/user/notes/${note.id}/ai`, {
          params: { access_token },
        });
        console.log(`[NoteCard] AI data loaded for note_id=${note.id}:`, resp.data);

        if (cancelled) return;
        console.log(`[NoteCard] Applying AI state: summary=${String(resp.data?.summary)}, tags=${JSON.stringify(resp.data?.tags)}, embedding_present=${resp.data?.embedding_present}`);

        setSummary(resp.data?.summary ?? null);
        setTags(resp.data?.tags ?? []);
        setEmbeddingPresent(!!resp.data?.embedding_present);

      } catch (err) {
        console.error(`[NoteCard] Failed to load AI data for note_id=${note.id}:`, err);
        if (!cancelled) {
          setSummary(null);
          setTags([]);
          setEmbeddingPresent(false);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadAi();

    return () => {
      cancelled = true;
    };
  }, [access_token, note.id]);

  return (
    <div className="rounded-2xl bg-slate-900/40 ring-1 ring-slate-800 p-5 hover:ring-indigo-400/30 transition">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm text-indigo-200/80">{embeddingPresent ? 'Indexed' : 'Pending index'}</div>
          <div className="text-lg font-semibold mt-1">{note.title}</div>
        </div>
      </div>

      <div className="mt-3 text-sm text-slate-300 line-clamp-3">{note.description}</div>

      <div className="mt-4 rounded-xl bg-slate-950/30 ring-1 ring-slate-800 p-4">
        <div className="text-xs text-slate-400">AI Summary</div>

        {loading ? (
          <div className="mt-2 text-sm text-slate-300">Generating…</div>
        ) : summary ? (
          <div className="mt-2 text-sm text-slate-100">{summary}</div>
        ) : (
          <div className="mt-2 text-sm text-slate-500">No summary yet.</div>
        )}

        <div className="mt-3">
          <div className="text-xs text-slate-400">Tags</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {tags.length === 0 ? (
              <div className="text-xs text-slate-500">—</div>
            ) : (
              tags.map((t) => (
                <span
                  key={t}
                  className="rounded-full bg-indigo-600/20 ring-1 ring-indigo-400/30 px-3 py-1 text-xs text-indigo-100"
                >
                  {t}
                </span>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

