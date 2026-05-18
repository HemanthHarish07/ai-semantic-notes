import React, { useMemo, useState } from 'react';
import { api } from '../lib/api';
import { getToken } from '../lib/token';

export default function SemanticSearchPage() {
  const token = getToken();
  const access_token = useMemo(() => token || '', [token]);

  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [results, setResults] = useState<
    Array<{ note_id: string; title: string; description: string; similarity: number }>
  >([]);

  async function onSearch() {
    setError(null);
    setLoading(true);
    console.log(`[SemanticSearchPage] Starting search: query="${query}" top_k=${topK}`);
    try {
      const resp = await api.post(
        '/user/notes/semantic-search',
        { query, top_k: topK },
        { params: { access_token } }
      );
      console.log(`[SemanticSearchPage] Search returned ${resp.data?.results?.length || 0} results`);
      setResults(resp.data?.results ?? []);
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || 'Semantic search failed';
      console.error(`[SemanticSearchPage] Search error: ${errorMsg}`, err);
      setError(errorMsg);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  const emptyState = !loading && results.length === 0;

  return (
    <div>
      <div className="mb-2">
        <div className="text-sm text-slate-400">Phase 2</div>
        <div className="text-xl font-semibold">Semantic search</div>
      </div>

      <div className="rounded-2xl bg-slate-900/40 ring-1 ring-slate-800 p-6 text-slate-300">
        Type a natural language query. Results are ranked semantically.


        <div className="mt-6 rounded-xl bg-slate-950/40 ring-1 ring-slate-800 p-4">
          <div className="text-sm font-medium">Search</div>

          <div className="mt-2 flex gap-2">
            <input
              className="flex-1 rounded-xl bg-slate-950/30 px-3 py-2 ring-1 ring-slate-800 outline-none focus:ring-indigo-500"
              placeholder="Try: vector retrieval systems"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />

            <button
              className="rounded-xl bg-indigo-600 px-4 py-2 font-semibold hover:bg-indigo-500 transition disabled:opacity-60"
              disabled={loading || !query.trim()}
              onClick={onSearch}
              type="button"
            >
              {loading ? 'Searching…' : 'Search'}
            </button>
          </div>

          <div className="mt-3 flex items-center gap-3">
            <label className="text-xs text-slate-500">Top K</label>
            <input
              type="number"
              min={1}
              max={20}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-24 rounded-xl bg-slate-950/30 px-3 py-2 ring-1 ring-slate-800 outline-none"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="mt-4 rounded-xl bg-red-500/10 ring-1 ring-red-500/30 px-3 py-2 text-sm text-red-200">
              {error}
            </div>
          )}
        </div>

        <div className="mt-6">
          {loading ? (
            <div className="rounded-2xl bg-slate-950/30 ring-1 ring-slate-800 p-4 text-slate-300">
              Searching embeddings…
            </div>
          ) : emptyState ? (
            <div className="rounded-2xl bg-slate-950/30 ring-1 ring-slate-800 p-4 text-slate-300">
              No matches found.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {results.map((r) => {
                const scorePct = Math.round((r.similarity ?? 0) * 100);
                return (
                  <div
                    key={r.note_id}
                    className="rounded-2xl bg-slate-900/40 ring-1 ring-slate-800 p-5 hover:ring-indigo-400/30 transition"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="text-xs text-indigo-200/80">Similarity: {scorePct}%</div>
                        <div className="text-lg font-semibold mt-1">{r.title}</div>
                      </div>
                    </div>
                    <div className="mt-3 text-sm text-slate-300 line-clamp-3">
                      {r.description}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

