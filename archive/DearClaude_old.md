# DearClaude.md - Midden Project Status & History

## PROJECT STATUS

**Current Version:** 1.0.1 (Data Quality Update)
**Demo Dates:** Dec 2 (demo day - 2 DAYS!), Dec 4 (industry summit)
**Live Site:** https://midden.vercel.app/

**Tapestry Database:**
```
Total songs: 5,076 (after duplicate cleanup)
Sub-vibes: 114
Meta-vibes: 9
Human-sourced: TRUE (but quality issues remain - see below)
Location: core/tapestry.json
```

---

# 🚨 CRITICAL: DATA QUALITY PROBLEMS

## The Core Issue
**Our comment quality is still bad.** We fixed scrapers and removed duplicates, but the EXISTING data in tapestry still has garbage comments that don't explain WHY a song fits an emotion.

## Examples of Bad Comments (from real playlist generation)

| Song | Comment | Problem |
|------|---------|---------|
| Baby One More Time — Britney Spears | "I still remember when Britney was the most famous person ever" | **NOSTALGIA ABOUT ARTIST, NOT SONG'S EMOTIONAL IMPACT** |
| 1/1 — Brian Eno | "Ambient 1: Music for Airports - Brian Eno" | **JUST THE ALBUM NAME - NO EMOTIONAL CONTEXT** |
| Parasympathetic Nervous System... | "I love how your cat joins you in your videos too 😊🐾🫶🏽" | **COMPLETELY IRRELEVANT - ABOUT THE VIDEO, NOT MUSIC** |
| Deep Connections — Dan Kraus | "The full moon helped me to find you beautiful soul ❤" | **VAGUE SPIRITUAL NONSENSE - NO EMOTIONAL SPECIFICITY** |

## What GOOD Comments Look Like
```
"Went thru a bad break up this song actually allows me to feel every emotion part of the healing process"
"This line destroyed me: 'I had all and then most of you, some, and now none of you'"
"this is the kind of song that will give you nostalgia even if you've never heard it before"
```

Good comments explain:
- **Personal emotional connection** ("went thru a bad break up")
- **Specific lyric/moment impact** ("this line destroyed me")
- **Emotional effect description** ("will give you nostalgia")

## Problems to Fix

### Problem 1: Artist/Album Comments (Not Song-Specific)
Comments like "Brian Eno is a genius" or "I love Britney" don't tell us anything about the SONG's emotional impact. They're just fan comments.

**Fix needed:** Filter requires song-specific language OR specific emotional description.

### Problem 2: Video Comments (Not Music-Related)
YouTube comments about the video itself: "love your cat", "great video quality", "first!", timestamps, etc.

**Fix needed:** Better YouTube spam detection - reject comments that reference video elements without music content.

### Problem 3: Vague Spiritual/Generic Praise
"Beautiful soul", "this heals me", "pure vibes" - these don't explain WHY or HOW the music affects emotions.

**Fix needed:** Require concrete emotional language, not just positive adjectives.

### Problem 4: The Ananki Paradox
Our Ananki analysis creates GREAT reasoning for why songs fit emotions - but it's based on BAD input comments. The AI is doing heavy lifting that should come from humans.

**The whole point of Midden:** Human-sourced emotional connections. If humans just say "nice song" and AI explains why it's emotional, we've defeated our purpose.

## What We Need

### Short-term (for demo)
- Identify what % of tapestry has quality vs garbage comments
- Consider filtering display to only show songs with quality comments
- OR: Don't show comment for songs with bad comments (just show AI reasoning)

### Long-term (post-demo)
- Create quality scoring system for existing comments
- Re-scrape with stricter filters
- Possibly re-run Ananki on songs with good comments only
- Build feedback loop: thumbs down → flag comment for review

---

# 🔧 KNOWN ISSUES

## Local Dev Server Broken
**Problem:** `npm install` completes but vite package doesn't appear in node_modules. Likely Windows permissions issue with corrupted node_modules folder.

**Workaround:** Test on Vercel production only.

**To fix later:**
1. Close all programs using the folder
2. Manually delete node_modules in Windows Explorer
3. Run `npm install` fresh

**Impact:** Can't test thumbs up/down persistence locally. Not critical for demo since Vercel can't persist files anyway.

---

# SESSION LOGS

## 📅 SESSION: Nov 29, 2025 ~11:30 PM - DATA QUALITY OVERHAUL

### 🎯 Session Goals
Fix the duplicate comment crisis discovered earlier today. 232 duplicate comment groups were affecting ~710 songs (~12% of tapestry).

### ✅ What We Accomplished

#### 1. Created UnifiedQualityFilter (`scrapers/shared/unified_quality_filter.py`)
Comprehensive quality filter for BOTH Reddit and YouTube scrapers:
- Rejects playlist descriptions
- Rejects multi-song lists
- YouTube-specific spam filters
- Reddit-specific filters
- Requires emotional depth

#### 2. Fixed ALL 46 Scrapers
- 23 YouTube scrapers: Added quality filter, removed playlist description fallback
- 23 Reddit scrapers: Added quality filter before extraction

#### 3. Cleaned Up Tapestry
- **Original:** 5,786 songs
- **Removed:** 710 songs (duplicates)
- **Final:** 5,076 songs

#### 4. Synced to Vercel
All three tapestry locations now have 5,076 songs:
- `core/tapestry.json`
- `code/web/core/tapestry.json`
- `code/web/client/public/core/tapestry.json`

### ⚠️ Discovered But Not Fixed
- Existing tapestry still has low-quality comments
- Scrapers are fixed for FUTURE data, but EXISTING data needs cleanup
- Local dev server broken (vite install issue)

---

## 📅 SESSION: Nov 29, 2025 ~10:00 PM - VERCEL DEPLOYMENT

### ✅ What We Accomplished
- Fixed serverless API deployment (404 errors)
- Fixed ESM imports and path resolution
- Cleaned up codebase
- Added human quotes display
- Simplified playlist header with journey visual

---

# REFERENCE SECTIONS

## 📁 Current File Structure

```
Spotify-MCP-Server-Fall-2025/
├── DearClaude.md              # THIS FILE
├── core/
│   ├── tapestry.json          # THE database (5,076 songs)
│   └── inject_analyzed_songs.py
│
├── scrapers/
│   ├── shared/
│   │   └── unified_quality_filter.py  # Quality filter for all scrapers
│   ├── reddit/                # 23 scrapers (all use unified filter)
│   └── youtube/               # 23 scrapers (all use unified filter)
│
├── code/web/                  # VERCEL ROOT
│   ├── api/index.ts           # Serverless API
│   ├── server/                # Backend services
│   └── client/                # React frontend
│
├── analysis/                  # Quality & cleanup scripts
│   ├── find_duplicate_comments.py
│   ├── cleanup_duplicates_targeted.py
│   ├── fix_youtube_scrapers.py
│   └── fix_reddit_scrapers.py
│
└── backups/
    └── tapestry_pre_cleanup_20251129_233135.json
```

## 💎 What Makes Midden Special

**Midden** creates emotionally intelligent playlists by "walking" a 2D emotional manifold.

The value prop: **Human-sourced emotional connections** - real people explaining WHY songs match feelings, not AI guessing.

**Current problem:** Our human comments aren't living up to this promise. Many are shallow, irrelevant, or not about the song's emotional impact.

---

**Last updated:** Nov 30, 2025 ~12:00 AM
**Priority:** DATA QUALITY - the scrapers are fixed, but existing data needs analysis and cleanup
