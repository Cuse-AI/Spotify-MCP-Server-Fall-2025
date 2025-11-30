# DearClaude.md - Midden Project Status & History

## PROJECT STATUS

**Current Version:** 1.0.1 (Data Quality Update)
**Demo Dates:** Dec 2 (demo day - 2 DAYS!), Dec 4 (industry summit)
**Live Site:** https://midden.vercel.app/

**Tapestry Database (UPDATED):**
```
Total songs: 5,076 (after duplicate cleanup)
Sub-vibes: 114
Meta-vibes: 9
Human-sourced: TRUE
Location: core/tapestry.json
```

---

# SESSION LOGS

## 📅 SESSION: Nov 29, 2025 ~11:30 PM - DATA QUALITY OVERHAUL

### 🎯 Session Goals
Fix the duplicate comment crisis discovered earlier today. 232 duplicate comment groups were affecting ~710 songs (~12% of tapestry), showing the same comment for multiple different songs.

### ✅ What We Accomplished

#### 1. Created UnifiedQualityFilter (`scrapers/shared/unified_quality_filter.py`)
A comprehensive quality filter for BOTH Reddit and YouTube scrapers that:
- **Rejects playlist descriptions** (catches "Best Deep House 2025..." spam)
- **Rejects multi-song lists** (comments listing 5+ songs)
- **Has YouTube-specific spam filters** (timestamps, "who's here 2024", etc.)
- **Has Reddit-specific filters** (generic praise, shallow comments)
- **Requires emotional depth** (comments must explain WHY a song fits)

Key patterns it catches:
```python
# Playlist description indicators (2+ = reject)
'subscribe', 'new music every', 'playlist.*20\\d\\d', 'tracklist:', 'featuring:'

# Multi-song list patterns
numbered/bulleted lists, 3+ "Artist - Song" patterns

# YouTube spam
timestamps, "who's listening 202X", "algorithm brought me"
```

#### 2. Fixed ALL 46 Scrapers
**YouTube scrapers (23 files in `scrapers/youtube/`):**
- Added `from unified_quality_filter import UnifiedQualityFilter`
- Added `self.quality_filter = UnifiedQualityFilter()` in `__init__`
- Changed comment selection to use quality filter
- **CRITICAL FIX:** Removed fallback to playlist description! Old code:
  ```python
  'comment_text': best_comment if best_comment else playlist['description'][:500]
  ```
  New code skips the song entirely if no quality comment found.

**Reddit scrapers (23 files in `scrapers/reddit/`):**
- Added quality filter import and initialization
- Added quality check BEFORE extracting songs from comments
- Rejects low-quality comments before they enter the pipeline

**Test scrapers (`testing/scrapers/`):**
- Updated both YouTube and Reddit test scrapers to use UnifiedQualityFilter
- These are used for testing new scraping approaches

#### 3. Cleaned Up Tapestry (710 songs removed)
Ran `analysis/cleanup_duplicates_targeted.py`:
- **Original:** 5,786 songs
- **Removed:** 710 songs
- **Final:** 5,076 songs

**Removal breakdown:**
- `multi_duplicate`: 571 songs (same comment on 3+ songs → remove ALL)
- `duplicate_pair`: 139 songs (same comment on 2 songs → keep higher score)

**Worst offenders removed:**
```
23 copies: "Best Deep House Music Hits 2025 | Deep House Playlist..."
17 copies: "Night Drive Playlist | Car Music playlist 2024, chill vibes."
16 copies: "The full OST soundtrack for the 2003 film 2 Fast 2 Furious..."
16 copies: "The really popular songs at my brother's wedding..."
```

**Backup saved:** `backups/tapestry_pre_cleanup_20251129_233135.json`

### 📁 Files Created/Modified This Session

**Created:**
- `scrapers/shared/unified_quality_filter.py` - The new unified filter
- `analysis/fix_youtube_scrapers.py` - Script that fixed all 23 YT scrapers
- `analysis/fix_reddit_scrapers.py` - Script that fixed all 23 Reddit scrapers
- `analysis/cleanup_duplicates_targeted.py` - Tapestry cleanup script

**Modified:**
- All 23 files in `scrapers/youtube/scrape_*.py`
- All 23 files in `scrapers/reddit/scrape_*.py`
- `testing/scrapers/youtube/test_scraper_yt.py`
- `testing/scrapers/reddit/test_scraper.py`
- `core/tapestry.json` (now 5,076 songs)

### 🔧 Technical Notes

**Why the duplicate problem happened:**
YouTube scrapers had a fallback that used playlist descriptions when no good comment was found. So if a playlist had 23 songs and none had good comments, all 23 got the playlist description as their "comment".

**Why we didn't quality-filter existing tapestry songs:**
The UnifiedQualityFilter is designed for NEW incoming data. Existing songs already passed Ananki analysis and have good `ananki_reasoning` fields. Retroactively applying the filter would have removed 4,000+ songs that are actually fine - the filter was being too strict for curated data.

**The targeted approach:**
Only remove obvious duplicates (same comment on multiple songs), not re-filter everything.

### ⚠️ Still TODO
- [ ] Sync updated tapestry to Vercel (`git push`)
- [ ] Update stats banner (will show 5,076 instead of 5,786)
- [ ] Test the live site after deploy

---

## 📅 SESSION: Nov 29, 2025 ~10:00 PM - VERCEL DEPLOYMENT

### 🎯 Session Goals
Get the Vercel serverless deployment working. The site was deployed but API endpoints returned 404.

### ✅ What We Accomplished

#### Vercel Serverless Deployment - FINALLY WORKING!
Multi-hour debugging session with several breakthroughs:

**Problems Solved:**
1. ✅ **404 on /api endpoints** - Created `api/index.ts` serverless handler
2. ✅ **Node version hell** - Final answer: `"engines": { "node": "24.x" }`
3. ✅ **Path alias crash** - `@shared/schema` doesn't work in serverless! Use relative imports
4. ✅ **ESM import extensions** - All local imports need `.js` extension
5. ✅ **TypeScript null checks** - Fixed `manifoldCache` possibly null errors
6. ✅ **File path resolution** - Added `__dirname` detection using `fileURLToPath`

**Key Files Modified:**
- `code/web/api/index.ts` - New serverless API handler
- `code/web/server/storage.ts` - Fixed imports + path resolution
- `code/web/server/claude-service.ts` - Fixed imports + path resolution
- `code/web/vercel.json` - Serverless config with includeFiles
- `code/web/package.json` - Added `engines.node: "24.x"`

#### Code Cleanup
- Deleted old duplicate files
- Moved old backups to archive
- Added auto-sync to injection script

#### UI Improvements
- Simplified playlist header with journey path visual `[Sad] → [Chill] → [Happy]`
- Human quotes now display for songs (with source: YouTube/Reddit)
- Only extrapolated songs show thumbs up/down

---

# REFERENCE SECTIONS

## 📁 Current File Structure

```
Spotify-MCP-Server-Fall-2025/
├── DearClaude.md              # THIS FILE
├── core/
│   ├── tapestry.json          # THE database (5,076 songs after cleanup)
│   └── inject_analyzed_songs.py
│
├── scrapers/
│   ├── shared/
│   │   └── unified_quality_filter.py  # NEW - unified filter for all scrapers
│   ├── reddit/                # 23 scrapers (all now use unified filter)
│   └── youtube/               # 23 scrapers (all now use unified filter)
│
├── testing/scrapers/          # Test versions of scrapers
│
├── code/web/                  # VERCEL ROOT DIRECTORY
│   ├── api/index.ts           # Serverless API handler
│   ├── server/                # Backend services
│   ├── client/                # React frontend
│   └── vercel.json            # Serverless config
│
├── analysis/                  # Quality & cleanup scripts
│   ├── find_duplicate_comments.py
│   ├── cleanup_duplicates_targeted.py
│   ├── fix_youtube_scrapers.py
│   └── fix_reddit_scrapers.py
│
├── backups/
│   ├── tapestry_pre_cleanup_20251129_233135.json  # Before duplicate removal
│   └── tapestry_GOOD_5786songs_20251128.json      # Before this session
│
└── data/
    └── emotional_manifold_COMPLETE.json
```

## 🔧 Key Technical Notes

### Vercel Serverless Gotchas
1. **Path aliases DON'T WORK** - Use relative imports: `../shared/schema.js`
2. **ESM needs .js extensions** - Even for .ts files, import as `.js`
3. **`process.cwd()` is unreliable** - Use `fileURLToPath(import.meta.url)`
4. **includeFiles in vercel.json** - Must explicitly include `core/**,data/**`
5. **CAN'T WRITE TO FILESYSTEM** - Serverless is ephemeral

### Data Pipeline
```
Scrape (Reddit/YouTube) 
    → Quality Filter (UnifiedQualityFilter) 
    → Spotify Validation 
    → TRUE Ananki Analysis (Claude API) 
    → Inject to Tapestry
    → Git push to deploy
```

### The API Handler Pattern
`code/web/api/index.ts` handles ALL API routes:
- `/api/health` - System status
- `/api/generate-playlist` - Main Claude workflow
- `/api/tapestry-stats` - Stats for banner
- `/api/validate-song` - Upvote (⚠️ won't persist on Vercel)
- `/api/downvote-song` - Downvote (⚠️ won't persist on Vercel)

## 💎 What Makes Midden Special

**Midden** creates emotionally intelligent playlists by "walking" a 2D emotional manifold.

Unlike Spotify's genre-based recommendations:
- **Human-sourced data** - Every song mapped from real Reddit/YouTube discussions
- **TRUE Ananki** - AI understands WHY songs match emotions, not just keywords
- **Emotional journeys** - Songs progress from where you ARE to where you're GOING

The 3-question flow:
1. "What's your vibe?" (overall mood)
2. "Where are you now?" (current emotional state)
3. "Where are you going?" (desired destination)

Claude then walks the manifold, selecting songs that create a smooth emotional arc.

---

## 📅 Older History (Condensed)

- **Nov 28**: Quality scrub removed 2,940 bad songs (33.7%), down to 5,786
- **Nov 27**: Initial Vercel deployment, atomic writes, API key validation
- **Nov 16**: Data quality crisis discovered (70% garbage), major scraper overhaul

---

**Last updated:** Nov 29, 2025 ~11:45 PM
**Next session:** Deploy changes, test live site, prep for Dec 2 demo!
