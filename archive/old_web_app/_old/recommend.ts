import util from 'util';
import { makeSpotifyClient } from '@/lib/spotify';
import artistCocktail from '@/data/artist-cocktail.json';

type ModelSeeds = {
  genres?: string[];
  artists?: string[];
  tracks?: string[];
  features?: Record<string, number>;
};

const mapTracks = (items: any[]) =>
  items.map((t: any) => ({
    id: t.id,
    uri: t.uri,
    name: t.name,
    artist: t.artists?.[0]?.name ?? 'Unknown',
    preview_url: t.preview_url ?? null,
    image: t.album?.images?.[1]?.url ?? t.album?.images?.[0]?.url ?? null,
    url: t.external_urls?.spotify ?? null,
  }));

const prioritizePreview = (tracks: any[]) => tracks.sort((a, b) => (b.preview_url ? 1 : 0) - (a.preview_url ? 1 : 0));

function shuffle<T>(arr: T[]) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function diversifyTracks(raw: any[], max: number, perArtist = 2) {
  const byArtist = new Map<string, any[]>();
  for (const t of raw) {
    const aid = (t.artists && t.artists[0] && t.artists[0].id) || t.artists?.[0]?.name || 'unknown';
    if (!byArtist.has(aid)) byArtist.set(aid, []);
    byArtist.get(aid)!.push(t);
  }
  const final: any[] = [];
  // round-robin pick up to perArtist from each artist to maximize diversity
  const artistQueues = Array.from(byArtist.values()).map(q => q.slice());
  let idx = 0;
  while (final.length < max && artistQueues.length) {
    const q = artistQueues[idx % artistQueues.length];
    if (q.length) {
      final.push(q.shift());
    } else {
      // remove empty queues
      artistQueues.splice(idx % artistQueues.length, 1);
      idx--; // compensate
    }
    idx++;
  }
  return shuffle(final).slice(0, max);
}

async function cocktailFallback(spotify: any, prompt?: string, max = 20) {
  try {
    const q = (prompt || '').toLowerCase();
    // decide mood key
    const mood = q.includes('gym') || q.includes('workout') || q.includes('hype') ? 'workout'
      : q.includes('chill') || q.includes('study') || q.includes('lofi') ? 'chill'
      : q.includes('sad') || q.includes('melancholy') ? 'sad'
      : q.includes('romance') || q.includes('date') || q.includes('love') ? 'romance'
      : q.includes('party') || q.includes('hype') ? 'hype'
      : 'default';

    const pool: any[] = [];
    const artistIds: string[] = (artistCocktail as any)[mood] || (artistCocktail as any)['default'] || [];
    const sample = artistIds.slice(0, Math.min(8, artistIds.length));
    for (const aid of sample) {
      try {
        const top = await spotify.getArtistTopTracks(aid, 'US');
        pool.push(...(top?.body?.tracks || []).slice(0, 6));
      } catch (e) {
        // ignore per-artist fetch errors
      }
    }
    if (pool.length === 0) return null;
    // dedupe by id
    const uniq = Array.from(new Map(pool.map((t: any) => [t.id, t])).values());
    const diversified = diversifyTracks(uniq, max, 2);
    return diversified.map((t: any) => ({
      id: t.id,
      uri: t.uri,
      name: t.name,
      artist: t.artists?.[0]?.name ?? 'Unknown',
      preview_url: t.preview_url ?? null,
      image: t.album?.images?.[1]?.url ?? t.album?.images?.[0]?.url ?? null,
      url: t.external_urls?.spotify ?? null,
    }));
  } catch (err) {
    return null;
  }
}

function featuresToParams(features?: Record<string, number>) {
  const params: Record<string, any> = {};
  if (!features) return params;
  // Map a few common feature names to recommendation params (target_)
  for (const k of Object.keys(features)) {
    const v = features[k];
    if (typeof v !== 'number') continue;
    // use target_ prefix
    params[`target_${k}`] = v;
  }
  return params;
}

export async function materializeModelOutput({ accessToken, modelSeeds, prompt, max = 20, forceCocktail = false }: { accessToken: string; modelSeeds?: ModelSeeds; prompt?: string; max?: number; forceCocktail?: boolean }) {
  const spotify = makeSpotifyClient(accessToken);
  const debugEvents: any[] = [];

  // If a user supplied a prompt, prefer the cocktail fallback first to ensure
  // prompt-driven, diverse results that change every request.
  if (forceCocktail || prompt) {
    try {
      const early = await cocktailFallback(spotify, prompt, max);
      if (early && early.length) {
        debugEvents.push({ phase: 'cocktail_early', count: early.length });
        return { tracks: prioritizePreview(early), used: { cocktail: true, prompt }, debug: { events: debugEvents } };
      }
    } catch (e) {
      // continue to other strategies
    }
  }

  // helper: attempt getRecommendations via client (no forced market)
  const tryRecommendations = async (opts: Record<string, any>) => {
    try {
      const rec = await spotify.getRecommendations(opts);
      debugEvents.push({ phase: 'spotify_recommendations', opts, status: 200, got: rec?.body?.tracks?.length ?? 0 });
      if (rec?.body?.tracks?.length) return mapTracks(rec.body.tracks);
    } catch (e: any) {
      debugEvents.push({ phase: 'spotify_recommendations_error', opts, statusCode: e?.statusCode ?? null, body: e?.body ?? null });
    }
    return null;
  };

  // 1) prefer explicit model seeds
  try {
    const featureParams = featuresToParams(modelSeeds?.features);

    if (modelSeeds?.genres?.length) {
      const opts = { seed_genres: modelSeeds.genres.slice(0, 5), limit: max, ...featureParams };
      const r = await tryRecommendations(opts);
      if (r && r.length) return { tracks: prioritizePreview(r), used: { seed_genres: opts.seed_genres }, debug: { events: debugEvents } };
      // try direct fetch as fallback
      try {
        const params = new URLSearchParams();
        params.set('limit', String(max));
        for (const [k, v] of Object.entries(featureParams)) params.set(k, String(v));
        params.set('seed_genres', modelSeeds.genres.join(','));
        const url = `https://api.spotify.com/v1/recommendations?${params.toString()}`;
        debugEvents.push({ phase: 'direct_fetch_attempt', url });
        const resp = await fetch(url, { headers: { Authorization: `Bearer ${accessToken}` } });
        const txt = await resp.text();
        let parsed: any = null; try { parsed = JSON.parse(txt); } catch (_) { parsed = txt; }
        debugEvents.push({ phase: 'direct_fetch_result', status: resp.status, statusText: resp.statusText, url: resp.url, body: parsed });
        if (resp.ok && parsed?.tracks?.length) return { tracks: prioritizePreview(mapTracks(parsed.tracks)), used: { seed_genres: modelSeeds.genres }, debug: { events: debugEvents } };
      } catch (dfErr) {
        debugEvents.push({ phase: 'direct_fetch_error', message: String(dfErr) });
      }
    }

    // 2) try artist seeds -> recommendations
    if (modelSeeds?.artists?.length) {
      const opts = { seed_artists: modelSeeds.artists.slice(0, 5), limit: max, ...featureParams };
      const r = await tryRecommendations(opts);
      if (r && r.length) return { tracks: prioritizePreview(r), used: { seed_artists: opts.seed_artists }, debug: { events: debugEvents } };
    }

    // 3) try track seeds -> recommendations
    if (modelSeeds?.tracks?.length) {
      const opts = { seed_tracks: modelSeeds.tracks.slice(0, 5), limit: max, ...featureParams };
      const r = await tryRecommendations(opts);
      if (r && r.length) return { tracks: prioritizePreview(r), used: { seed_tracks: opts.seed_tracks }, debug: { events: debugEvents } };
    }

    // 4) fallback: user personalization (top artists) => artist top-tracks + related artists
    try {
      const top = await spotify.getMyTopArtists({ limit: 5 });
      const topIds = (top?.body?.items || []).map((a: any) => a.id).filter(Boolean);
      const candidate: any[] = [];
      for (const id of topIds) {
        try {
          const t = await spotify.getArtistTopTracks(id, 'US');
          candidate.push(...(t?.body?.tracks || []).slice(0, 5));
        } catch (_) {}
        try {
          const rel = await spotify.getArtistRelatedArtists(id);
          for (const r of (rel?.body?.artists || []).slice(0, 3)) {
            try {
              const rt = await spotify.getArtistTopTracks(r.id, 'US');
              candidate.push(...(rt?.body?.tracks || []).slice(0, 3));
            } catch (_) {}
          }
        } catch (_) {}
      }
      if (candidate.length) {
        const final = Array.from(new Map(candidate.map((t: any) => [t.id, t])).values()).slice(0, max);
        return { tracks: prioritizePreview(mapTracks(final)), used: { synthesized_from_top_artists: true }, debug: { events: debugEvents } };
      }
    } catch (_) {}

    // 5) fallback: playlist search derived from prompt / genres
    try {
      const q = (prompt || '').toLowerCase();
      const queries = new Set<string>();
      if (q) {
        q.split(/\s+/).slice(0, 4).forEach(s => queries.add(s));
        queries.add(q);
      }
      (modelSeeds?.genres || []).slice(0,3).forEach(s => queries.add(s));
      const candidateTracks: any[] = [];
      for (const qq of Array.from(queries).slice(0,8)) {
        debugEvents.push({ phase: 'playlist_query', query: qq });
        try {
          const pls = await spotify.searchPlaylists(qq, { limit: 3 });
          const items = pls?.body?.playlists?.items || [];
          for (const p of items) {
            try {
              const tr = await spotify.getPlaylistTracks(p.id, { limit: 15 });
              candidateTracks.push(...(tr?.body?.items || []).map((it: any) => it.track).filter(Boolean));
            } catch (_) {}
            if (candidateTracks.length >= 40) break;
          }
        } catch (_) {}
        if (candidateTracks.length >= 40) break;
      }
      if (candidateTracks.length) {
        const final = Array.from(new Map(candidateTracks.map((t: any) => [t.id, t])).values()).slice(0, max);
        // diversify to avoid single-artist dominance
        const diversified = diversifyTracks(final, max, 2);
        return { tracks: prioritizePreview(mapTracks(diversified)), used: { synthesized_from_playlists: true }, debug: { events: debugEvents } };
      }
    } catch (_) {}

    // 6) cocktail fallback: curated popular-artist sampling — useful if recommendations endpoint fails
    try {
      const c = await cocktailFallback(spotify, prompt, max);
      if (c && c.length) {
        debugEvents.push({ phase: 'cocktail_fallback', count: c.length });
        return { tracks: prioritizePreview(c), used: { cocktail: true }, debug: { events: debugEvents } };
      }
    } catch (e) {
      // ignore
    }

  } catch (err) {
    debugEvents.push({ phase: 'materialize_error', error: String(err) });
  }

  return { tracks: [], used: { none: true }, debug: { events: debugEvents } };
}

export default { materializeModelOutput };
