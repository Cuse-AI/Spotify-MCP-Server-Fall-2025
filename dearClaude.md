# DearClaude.md - Midden Project Status & History

## PROJECT STATUS - NOV 29, 2025

**Last Update:** Nov 29, 2025 ~9:30 PM (Saturday)
**Current Version:** 1.0.0 (PRODUCTION DEPLOYED! 🎉)
**Demo Dates:** Dec 2 (demo day - 3 DAYS!), Dec 4 (industry summit)
**Live Site:** https://midden.vercel.app/ ← FULLY WORKING!

---

## 🎯 WHAT WE ACHIEVED TODAY (Nov 29)

### Vercel Serverless Deployment - FINALLY WORKING!
The big win today was fixing the serverless API deployment on Vercel. This was a multi-hour debugging session with several breakthroughs:

**Problems Solved:**
1. ✅ **404 on /api endpoints** - Created `api/index.ts` serverless handler
2. ✅ **Node version hell** - Vercel kept flip-flopping between requiring 18.x, 20.x, and 24.x. Final answer: `"engines": { "node": "24.x" }`
3. ✅ **Path alias crash** - `@shared/schema` doesn't work in Vercel serverless! Changed all imports to relative: `../shared/schema.js`
4. ✅ **ESM import extensions** - All local imports need `.js` extension for ESM modules
5. ✅ **TypeScript null checks** - Fixed `manifoldCache` possibly null errors
6. ✅ **File path resolution** - Added `__dirname` detection using `fileURLToPath(import.meta.url)` for serverless environment

**Key Files Modified:**
- `code/web/api/index.ts` - New serverless API handler with all routes
- `code/web/server/storage.ts` - Fixed imports + path resolution
- `code/web/server/claude-service.ts` - Fixed imports + path resolution  
- `code/web/server/routes.ts` - Fixed imports (still used for local dev)
- `code/web/vercel.json` - Serverless config with includeFiles
- `code/web/package.json` - Added `engines.node: "24.x"`

### Code Cleanup
- ✅ Deleted `attached_assets/claude-service.ts` (old duplicate causing VSCode errors)
- ✅ Moved old backups to archive (pre-scrub data, old restructure backups)
- ✅ Renamed good backup to `tapestry_GOOD_5786songs_20251128.json`
- ✅ Removed interactive map modal (will reimagine later)
- ✅ Auto-sync added to `core/inject_analyzed_songs.py` - copies tapestry to Vercel locations

### What's Working Now
- ✅ Full question flow (3 questions → loading → results)
- ✅ Claude API integration (walks the emotional manifold!)
- ✅ Spotify metadata enrichment (album art, previews)
- ✅ Health endpoint showing all systems green
- ✅ Stats banner showing 5,786 tracks

---

## 📊 CURRENT DATA STATUS

**Tapestry Database:**
```
Total songs: 5,786 (quality-verified)
Sub-vibes: 114
Meta-vibes: 9
Human-sourced: TRUE
Location: core/tapestry.json (8.01 MB)
```

**Health Check Response (LIVE):**
```json
{
  "status": "healthy",
  "environment": {
    "anthropic_key": "✅ set",
    "spotify_id": "✅ set", 
    "spotify_secret": "✅ set"
  },
  "data": {
    "total_tracks": 5786,
    "total_sub_vibes": 114,
    "total_meta_vibes": 9,
    "human_sourced": true
  }
}
```

---

## 🔥 NEXT TASKS (Priority Order for Dec 2 Demo)

### HIGH PRIORITY (Must have for demo)
1. **Playlist page text** - Update copy/messaging on results page
2. **Error handling** - "Failed to add songs to tapestry" needs fixing
3. **Clean up thumbs UI** - Remove up/down from non-extrapolated songs

### MEDIUM PRIORITY (Nice to have)
4. **Add human quotes** - Show scraped Reddit comments on playlist page
5. **Create Playlist button** - Make "Add to Spotify" actually work
6. **Cover art** - Decide how to handle playlist cover images

### LOW PRIORITY (Post-demo)
7. **General aesthetics** - Polish UI/UX
8. **Interactive map reimagined** - New approach to visualizing the manifold

---

## 📁 CURRENT FILE STRUCTURE

```
Spotify-MCP-Server-Fall-2025/
├── DearClaude.md          # THIS FILE
├── core/
│   ├── tapestry.json      # THE database (5,786 songs, 8MB)
│   └── inject_analyzed_songs.py  # Now auto-syncs to Vercel!
│
├── code/web/              # VERCEL ROOT DIRECTORY
│   ├── api/
│   │   └── index.ts       # Serverless API handler (all routes)
│   ├── server/
│   │   ├── storage.ts     # Data access + Claude orchestration
│   │   ├── claude-service.ts  # Claude API calls
│   │   ├── spotify-service.ts # Spotify API calls
│   │   └── routes.ts      # Express routes (local dev)
│   ├── shared/
│   │   └── schema.ts      # TypeScript types + Zod schemas
│   ├── client/            # React frontend
│   ├── core/              # Synced copy of tapestry.json
│   ├── data/              # Synced copy of manifold
│   ├── vercel.json        # Serverless config
│   └── package.json       # engines.node: "24.x"
│
├── data/
│   ├── emotional_manifold_COMPLETE.json
│   └── pipeline/          # Scraper data pipeline stages
│
├── scrapers/              # Reddit/YouTube scrapers
├── analysis/              # Quality scripts
├── backups/               # GOOD backups only now
│   ├── tapestry_GOOD_5786songs_20251128.json
│   └── manifold_safe_backup.json
└── archive/               # Old stuff we don't need
```

---

## 🔧 KEY TECHNICAL NOTES FOR FUTURE CLAUDE

### Vercel Serverless Gotchas
1. **Path aliases DON'T WORK** - Use relative imports: `../shared/schema.js`
2. **ESM needs .js extensions** - Even for .ts files, import as `.js`
3. **`process.cwd()` is unreliable** - Use `fileURLToPath(import.meta.url)` instead
4. **includeFiles in vercel.json** - Must explicitly include `core/**,data/**` for JSON files

### Data Sync Flow
When songs are injected via `core/inject_analyzed_songs.py`:
1. Updates `core/tapestry.json` (source of truth)
2. Auto-copies to `code/web/core/tapestry.json`
3. Auto-copies to `code/web/client/public/core/tapestry.json`
4. Still need `git push` to deploy to Vercel

### The API Handler Pattern
`code/web/api/index.ts` handles ALL API routes via a switch:
- `/api/health` - System status
- `/api/generate-playlist` - Main Claude workflow
- `/api/tapestry-stats` - Stats for banner
- `/api/validate-song` - Upvote/add to tapestry
- `/api/downvote-song` - Record bad matches
- `/api/create-spotify-playlist` - Export to Spotify
- `/api/debug` - Shows file paths (temporary)

---

## 💎 WHAT MAKES MIDDEN SPECIAL (Elevator Pitch)

**Midden** creates emotionally intelligent playlists by "walking" a 2D emotional manifold.

Unlike Spotify's genre-based recommendations:
- **Human-sourced data** - Every song mapped from real Reddit discussions
- **TRUE Ananki** - AI understands WHY songs match emotions, not just keywords
- **Emotional journeys** - Songs progress from where you ARE to where you're GOING
- **Manifold math** - Songs placed on 2D space with 9 emotional axes

The 3-question flow:
1. "What's your vibe?" (overall mood)
2. "Where are you now?" (current emotional state)
3. "Where are you going?" (desired destination)

Claude then walks the manifold, selecting songs that create a smooth emotional arc.

---

## 📅 HISTORY

### Nov 28, 2025 (Yesterday)
- Quality scrub: removed 2,940 bad songs (33.7%)
- Created quality filter scripts
- Down to 5,786 verified songs

### Nov 27, 2025
- Initial Vercel deployment
- Atomic writes for data safety
- API key validation

### Nov 16, 2025
- Data quality crisis discovered (70% garbage)
- Created quality_filters.py
- Major scraper overhaul

---

**Last updated by Claude:** Nov 29, 2025 ~9:30 PM
**Status:** PRODUCTION LIVE! Demo prep mode activated 🚀
