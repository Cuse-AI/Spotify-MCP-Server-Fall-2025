# SPOTIFY LINK FIX - Wrong Song Issue
## December 2, 2025

---

## THE PROBLEM

Spotify links were going to completely wrong songs.

**Root cause:** Claude was making up track_ids that happen to be valid Spotify IDs, but for DIFFERENT songs. Since they were "valid" IDs, our matching logic trusted them.

---

## THE FIX

Changed `enrichSongsWithHumanContext()` in `claude-service.ts` to:

1. **ALWAYS match by artist+title FIRST** (Claude gets these right)
2. Fall back to title-only matching (for artist name variations)
3. Only use Claude's track_id as LAST resort
4. **ALWAYS replace** the track_id with the correct one from tapestry

---

## KEY CODE CHANGE

**Before (trusted Claude's track_id):**
```ts
// Try track_id first
let original = songLookupByUri.get(song.track_id);

// Only fall back to artist+title if track_id fails
if (!original) {
  original = songLookupByArtistTitle.get(artistTitleKey);
}
```

**After (trust artist+title, not track_id):**
```ts
// ALWAYS try artist+title first (most reliable)
let original = songLookupByArtistTitle.get(artistTitleKey);

// Try title-only matching second
if (!original) {
  original = songLookupByTitle.get(titleKey);
}

// Only try track_id as LAST resort
if (!original) {
  original = songLookupByUri.get(song.track_id);
}

// ALWAYS fix the track_id from tapestry
if (original) {
  song.track_id = original.spotify_uri;
}
```

---

## WHY THIS WORKS

Claude is good at:
- Remembering song titles correctly
- Remembering artist names correctly

Claude is BAD at:
- Remembering exact Spotify track IDs (22-character alphanumeric strings)
- Not making up plausible-looking IDs

So we trust what Claude is good at (names) and look up the track_id ourselves.

---

*— Replit*
