"use client";
import { useState } from "react";

type Track = {
  id: string; uri: string; name: string; artist: string;
  preview_url: string | null; image: string | null; url: string | null;
};

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [tracks, setTracks] = useState<Track[]>([]);
  const [current, setCurrent] = useState<Track | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugJson, setDebugJson] = useState<string | null>(null);
  const [showDebug, setShowDebug] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState(false);
  const [usedSource, setUsedSource] = useState<string | null>(null);
  const [forceCocktail, setForceCocktail] = useState(false);

  async function getSongs() {
    setLoading(true);
    setError(null);
    try {
    const r = await fetch("/api/recommend", {
        method: "POST",
        // ensure browser includes cookies (access token) on same-origin requests
        credentials: "same-origin",
        headers: { "content-type": "application/json" },
      body: JSON.stringify({ prompt, forceCocktail }),
      });
  const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        // show full response in debug panel for easier diagnosis
        setDebugJson(JSON.stringify({ status: r.status, body: data }, null, 2));
        let msg = "Could not fetch recommendations.";
        if (data?.message) msg = data.message;
        if (data?.error) msg = data.error;
        throw new Error(msg);
      }
  const list: Track[] = data.tracks || [];
      // normalize the reported "used" source into a readable label and always record debug info
      const usedRaw = data?.used;
      let usedLabel: string | null = null;
      if (!usedRaw) usedLabel = null;
      else if (typeof usedRaw === 'string') usedLabel = usedRaw;
      else if (usedRaw?.source) usedLabel = usedRaw.source;
      else if (typeof usedRaw === 'object') {
        const keys = Object.keys(usedRaw || {});
        usedLabel = keys.length ? keys[0] : null;
      }
      setUsedSource(usedLabel);
      // always surface debug information so the UI can show what happened
      setDebugJson(JSON.stringify({ status: r.status, used: usedRaw ?? usedLabel, body: data, trackCount: list.length }, null, 2));
      setTracks(list);
      const first = list.find((t) => t.preview_url) ?? list[0] ?? null;
      setCurrent(first);
      if (!first) setError("No previews available. Try another vibe or open in Spotify.");
    } catch (e: any) {
      setError(e?.message || "Something went wrong.");
      setUsedSource(null);
      setTracks([]);
      setCurrent(null);
    } finally {
      setLoading(false);
    }
  }

  function shuffleLocal() {
    setTracks((prev) => {
      const arr = prev.slice();
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
      const first = arr.find((t) => t.preview_url) ?? arr[0] ?? null;
      setCurrent(first);
      return arr;
    });
  }

  // Dev / utility helpers
  function openLogin() {
    // redirect to the login flow which will set cookies via callback
    window.location.href = "/api/login";
  }

  async function doRefresh() {
    setRefreshing(true);
    setDebugJson(null);
    try {
      const r = await fetch("/api/refresh", { method: "GET", credentials: "same-origin" });
      const j = await r.json().catch(() => ({}));
      setDebugJson(JSON.stringify({ status: r.status, body: j }, null, 2));
    } catch (e: any) {
      setDebugJson(JSON.stringify({ error: e?.message ?? String(e) }, null, 2));
    } finally {
      setRefreshing(false);
    }
  }

  async function doTokenCheck() {
    setDebugJson(null);
    try {
      const r = await fetch("/api/token-check", { method: "GET", credentials: "same-origin" });
      const j = await r.json().catch(() => ({}));
      setDebugJson(JSON.stringify({ status: r.status, body: j }, null, 2));
    } catch (e: any) {
      setDebugJson(JSON.stringify({ error: e?.message ?? String(e) }, null, 2));
    }
  }

  async function doEchoCookies() {
    setDebugJson(null);
    try {
      const r = await fetch("/api/echo-cookies", { method: "GET", credentials: "same-origin" });
      const j = await r.json().catch(() => ({}));
      setDebugJson(JSON.stringify({ status: r.status, body: j }, null, 2));
    } catch (e: any) {
      setDebugJson(JSON.stringify({ error: e?.message ?? String(e) }, null, 2));
    }
  }

  return (
    <main className="center-wrap">
      <div className="card">
        <h1 className="title">CuseAI · Spotify MSP</h1>
        <p className="subtitle">Type your vibe. We’ll fetch a track and play a 30-sec preview.</p>

        <div className="inputRow">
          <input
            className="input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={'e.g., "hype gym", "chill study", "melancholy", "romantic"'}
          />
          <button className="primaryBtn" onClick={getSongs} disabled={loading}>
            {loading ? "Finding..." : "▶ Get songs"}
          </button>
        </div>
        {usedSource && (
          <div style={{ marginTop: 8, color: '#6b7280', fontSize: 13 }}>Strategy: {usedSource}</div>
        )}

        <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button className="ghostBtn" onClick={openLogin}>Login (Spotify)</button>
          <button className="ghostBtn" onClick={doRefresh} disabled={refreshing}>{refreshing ? 'Refreshing...' : 'Refresh token'}</button>
          <button className="ghostBtn" onClick={doTokenCheck}>Token check</button>
          <button className="ghostBtn" onClick={doEchoCookies}>Echo cookies</button>
          <button className="ghostBtn" onClick={() => setForceCocktail(!forceCocktail)} style={{ borderStyle: 'dashed' }}>{forceCocktail ? 'Cocktail: ON' : 'Cocktail: OFF'}</button>
          <button className="ghostBtn" onClick={shuffleLocal}>Shuffle list</button>
        </div>
        <div style={{ marginTop: 8, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button className="ghostBtn" onClick={() => window.open('https://github.com/Cuse-AI/Spotify-MCP-Server-Fall-2025', '_blank')}>Open repo</button>
          <button className="ghostBtn" onClick={() => window.open('https://developer.spotify.com/dashboard', '_blank')}>Spotify Dev</button>
          <button className="ghostBtn" onClick={() => window.open('https://developer.spotify.com', '_blank')}>Spotify Docs</button>
          <button className="ghostBtn" onClick={() => window.open('https://open.spotify.com', '_blank')}>Open Spotify</button>
        </div>

        {error && <div className="error">{error}</div>}

        {tracks.length === 0 && <div className="hint">Enter a vibe and click “Get songs”.</div>}

        {tracks.length > 0 && (
          <>
            <h2 className="listTitle">Playlist</h2>
            <ul className="listColumn">
              {tracks.slice(0, 10).map((t, i) => {
                const colors = ['#f97316', '#06b6d4', '#a78bfa', '#fb7185', '#34d399', '#f973b3', '#60a5fa', '#facc15', '#fb923c', '#7c3aed'];
                const color = colors[i % colors.length];
                return (
                  <li key={t.id} className="tile" onClick={() => setCurrent(t)}>
                    <div className="accent" style={{ background: color }} />
                    {t.image ? (
                      <img src={t.image} width={56} height={56} className="thumb" alt="" />
                    ) : (
                      <div className="thumb placeholder" />
                    )}
                    <div className="tileText">
                      <div className="tileName" title={t.name}>{t.name}</div>
                      <div className="tileArtist" title={t.artist}>{t.artist}</div>
                    </div>

                    <div className="hoverCard">
                      <div style={{ display: 'flex', gap: 12 }}>
                        {t.image ? <img src={t.image} className="hoverCover" alt=""/> : <div className="hoverCover placeholder" />}
                        <div className="hoverMeta">
                          <div className="hoverTitle">{t.name}</div>
                          <div className="hoverArtist">{t.artist}</div>
                          <div className="hoverActions">
                            {t.preview_url ? (
                              <audio controls src={t.preview_url} style={{ width: '100%' }} />
                            ) : null}
                          </div>
                          <div style={{ marginTop: 8 }}>
                            {t.url ? <a className="ghostBtn" href={t.url} target="_blank" rel="noreferrer">Open in Spotify</a> : null}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>

            {current?.preview_url ? (
              <audio controls src={current.preview_url} className="player" style={{ marginTop: 12 }} />
            ) : current ? (
              <div className="noPreview">No preview available. Use “Open in Spotify”.</div>
            ) : null}
          </>
        )}

        {debugJson && (
          <div style={{ marginTop: 16 }}>
            <h3 className="listTitle">Debug</h3>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
              <div style={{ color: '#6b7280' }}>Tracks: {tracks.length}</div>
              <div style={{ color: '#6b7280' }}>Used: {usedSource ?? 'unknown'}</div>
              <button className="ghostBtn" onClick={() => setShowDebug((s) => !s)}>{showDebug ? 'Hide full debug' : 'Show full debug'}</button>
            </div>
            {showDebug ? (
              <pre style={{ background: '#0b0b0b', color: '#e6e6e6', padding: 12, borderRadius: 6, overflowX: 'auto' }}>{debugJson}</pre>
            ) : null}
          </div>
        )}
      </div>
    </main>
  );
}
