# DearClaude.md - Midden Project Status & History

## PROJECT STATUS - NOV 28, 2025

**Last Update:** Nov 28, 2025 11:15 PM (Friday)
**Current Version:** 0.9.3 (Post-Quality Scrub)
**Demo Dates:** Dec 2 (demo day), Dec 4 (industry summit)
**Live Site:** https://midden.vercel.app/

---

## 🎯 WHAT WE ACHIEVED TODAY (Nov 28)

### Data Quality Scrub
- ✅ **Removed 2,940 low-quality songs** (33.7% of dataset)
- ✅ **Tapestry now contains 5,786 verified quality songs**
- ✅ Created `analysis/scrub_quality.py` for future cleaning
- ✅ Created `analysis/pre_ananki_filter.py` to save API credits
- ✅ Archived bad data to `data/archive/quality_scrub/`
- ✅ Backup saved before scrub

### Quality Issues Removed
| Issue | Count Removed |
|-------|---------------|
| List format (just song names) | 1,794 |
| URLs in comments | 999 |
| Too short (<30 chars) | 598 |
| Generic only | 341 |
| No comment | 270 |

---

## 📊 CURRENT DATA STATUS

**Tapestry Database (Post-Scrub):**
```
Total songs: 5,786
Sub-vibes: 118
Meta-vibes: 9
Human-sourced: TRUE (verified quality)
```

**Meta-Vibe Distribution:**
| Status | Meta-Vibe | Songs | % |
|--------|-----------|-------|---|
| ✅ Strong | Sad | 1,401 | 24.2% |
| ✅ Strong | Energy | 1,014 | 17.5% |
| ✅ Strong | Dark | 667 | 11.5% |
| ✅ Strong | Happy | 623 | 10.8% |
| ✅ Strong | Chill | 597 | 10.3% |
| ⚠️ Needs work | Romantic | 459 | 7.9% |
| 🔴 Priority | Night | 394 | 6.8% |
| 🔴 Priority | Party | 335 | 5.8% |
| 🔴 Priority | Drive | 296 | 5.1% |

**Priority Scraper Targets:**
- Drive (296 songs) - Road Trip, Night Drive
- Party (335 songs) - Club, Festival, College  
- Night (394 songs) - Introspective sub-vibes
- 8 empty sub-vibes need content

---


## 🚀 DEPLOYMENT STATUS

### Completed (Nov 27)
- ✅ Deployed to Vercel at midden.vercel.app
- ✅ Atomic writes for data safety
- ✅ API key validation at startup
- ✅ Health check endpoint `/api/health`
- ✅ Error messages with context

### Next Steps
1. [ ] Test live site functionality
2. [ ] Fix stats → manifold map display issue
3. [ ] Set up scrapers as separate project
4. [ ] Build APK for demo distribution
5. [ ] Buff weak meta-vibes (Drive, Party, Night)

---

## 📁 PROJECT STRUCTURE

```
Spotify-MCP-Server-Fall-2025/
├── README.md              # Project overview
├── PROJECT_STRUCTURE.md   # Detailed structure docs
├── DearClaude.md          # This file - status & history
├── .gitignore
│
├── core/
│   └── tapestry.json      # THE database (5,786 songs)
│
├── code/web/              # Web application
│   ├── client/            # React frontend
│   ├── server/            # Express backend
│   └── .env               # API keys (not committed)
│
├── data/
│   ├── emotional_manifold_COMPLETE.json
│   ├── 1_raw_scrapes/     # Raw scraper output
│   ├── 2_deduped/         # Deduplicated data
│   ├── 3_analyzed/        # Ananki-processed
│   ├── 4_injected/        # Injected to tapestry
│   └── archive/           # Archived bad/old data
│
├── scrapers/
│   ├── reddit/            # Reddit scrapers
│   ├── youtube/           # YouTube scrapers
│   └── shared/            # Shared utilities
│
├── analysis/              # Analysis & utility scripts
│   ├── scrub_quality.py   # Clean existing tapestry
│   ├── pre_ananki_filter.py # Filter before API calls
│   └── distribution_check.py # Check vibe distribution
│
├── backups/               # Pre-operation backups
│
└── docs/
    ├── PIPELINE_ANALYSIS.md
    ├── COMPLETE_WORKFLOW.md
    └── design_guidelines.md
```

---

## 🔧 KEY SCRIPTS

### Data Quality
- `analysis/scrub_quality.py` - Remove low-quality songs from tapestry
- `analysis/pre_ananki_filter.py` - Filter BEFORE Ananki to save API credits
- `analysis/distribution_check.py` - Check meta-vibe/sub-vibe distribution

### Pipeline
- `data/run_full_pipeline.py` - Full scrape → analyze → inject pipeline
- `core/inject_analyzed_songs.py` - Inject analyzed songs to tapestry

---


## 💡 QUALITY STANDARDS

A song PASSES quality check if:
- ✅ Comment is 30+ characters
- ✅ No URLs in comment
- ✅ Not a list of song names (max 2 " - " patterns)
- ✅ Not generic only ("great song", "love this", etc.)
- ✅ Has actual emotional content

A song FAILS if ANY of:
- ❌ Has URL (spotify, youtube, etc.)
- ❌ Too short (<30 chars)
- ❌ Just a song list
- ❌ Generic praise only
- ❌ No comment at all

---

# HISTORY: DATA QUALITY CRISIS (Nov 16, 2025)

## What Happened

On Nov 16, we discovered that ~70% of scraped data was garbage:
- Comments like "Bold of you to assume I had friends"
- Generic spam like "Who's listening in 2024?"
- Off-topic jokes and memes
- No quality filters existed despite claims

### Root Causes
1. **NO QUALITY FILTERS** - Just checked if "song" appeared in text
2. **SILENT FAILURES** - Bare `except Exception` blocks hid errors
3. **NO VALIDATION** - Never sampled output to verify quality
4. **RELIED ON AI TO FIX BAD INPUT** - Expected Ananki to filter

### Fixes Implemented (Nov 16)
- ✅ Created `data/quality_filters.py` with proper validation
- ✅ Integrated into all 23 scrapers
- ✅ Added proper logging and error handling
- ✅ Fixed `all_results` NameError bug
- ✅ Added statistics tracking

---

## 💎 LESSONS LEARNED

1. **Quality > Quantity** - 5,786 good songs beats 8,726 mixed-quality
2. **Sample Your Data** - Look at output before scaling up
3. **Don't Hide Failures** - Bare except blocks hide bugs
4. **Filter at the Source** - Don't rely on AI to fix garbage input
5. **Implement What You Claim** - If you say filters exist, build them

---

## 🎯 WHAT MAKES MIDDEN SPECIAL

1. **TRUE Ananki Analysis** - Real AI emotional understanding, not keywords
2. **Human-Sourced Content** - Every song from real Reddit discussions
3. **Emotional Journey** - 3 questions: WHERE YOU ARE → WHERE YOU'RE GOING
4. **Rich Context** - Original human comment + emotional reasoning
5. **Quality Over Quantity** - 100% verified emotional content

---

**Last updated by Claude:** Nov 28, 2025 11:15 PM
**Status:** Quality scrub complete, ready for scraper improvements
