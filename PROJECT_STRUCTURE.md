# THE TAPESTRY - Project Structure (REORGANIZED Nov 12, 2025)

## CLEAN, ORGANIZED, SAFE!

```
Spotify-MCP-Server-Fall-2025/
│
├── core/                          ⭐ THE HEART - Start here!
│   ├── tapestry.json             # THE database (6,081 songs)
│   ├── manifold.json             # Structure definition (9 metas, 114 sub-vibes)
│   ├── true_ananki.py            # AI analyzer ($$ Claude API)
│   ├── inject_to_tapestry.py    # Add songs to tapestry
│   ├── dedupe_before_ananki.py  # Remove duplicates
│   └── README.md                 # How to use core files
│
├── code/                          💻 WEB APP
│   └── web/                      # Conversational music journey app
│       ├── client/               # React frontend
│       │   └── src/
│       │       ├── components/   # UI components
│       │       ├── pages/        # Page components
│       │       └── lib/          # Client utilities
│       ├── server/               # Express backend
│       │   ├── index.ts          # Server entry point
│       │   ├── routes.ts         # API routes
│       │   ├── claude-service.ts # Claude playlist generation
│       │   ├── spotify-service.ts # Spotify metadata
│       │   └── storage.ts        # Tapestry read/write
│       ├── shared/               # Shared types/schemas
│       ├── package.json          # Dependencies
│       └── .env                  # API keys (not in git)
│
├── scrapers/                      🔍 DATA COLLECTION (FREE!)
│   ├── shared/
│   │   └── checkpoint_utils.py   # Checkpoint system (resume scraping)
│   ├── youtube/
│   │   ├── scrape_dark.py       # Updated with consolidated keywords
│   │   ├── scrape_party.py
│   │   ├── scrape_night.py
│   │   └── ... (23 scrapers total)
│   └── reddit/
│       ├── scrape_dark.py       # Updated with consolidated keywords
│       ├── scrape_party.py
│       ├── scrape_night.py
│       └── ... (23 scrapers total)
│
├── analysis/                      📊 UTILITIES
│   ├── verify_tapestry.py       # Check data quality
│   ├── check_tapestry_status.py # Current stats
│   ├── show_random_samples.py   # See examples
│   ├── balance_tapestry.py      # Balance distribution tool
│   └── archive_overflow.py      # Archive utility
│
├── docs/                          📚 DOCUMENTATION
│   ├── DearClaude.md            # Current status & strategy
│   ├── COMPLETE_WORKFLOW.md     # Full workflow guide
│   └── VIBE_HIERARCHY_EXPLAINED.md
│
├── backups/                       💾 SAFE BACKUPS
│   ├── tapestry_safe_backup_20251112.json
│   └── manifold_safe_backup.json
│
├── archive/                       🗄️ OLD/OBSOLETE (Don't use!)
│   ├── old_tapestries/          # Dangerous corrupted files
│   ├── old_scripts/             # Legacy code
│   ├── expansion_batches/       # Old batch system
│   └── old_processing_files/    # Old CSVs and processing artifacts
│
└── data/                          📁 SCRAPED DATA & OUTPUT
    ├── youtube/                 # YouTube scraper outputs
    ├── reddit/                  # Reddit scraper outputs
    ├── emotional_manifold_COMPLETE.json  # Manifold for web app
    └── user_downvotes.json      # Downvoted songs from web app
```

## QUICK START:

### 1. Run Web App:
```bash
cd code/web
npm install  # First time only
npm run dev  # Start on http://localhost:5000
```

### 2. Check Status:
```bash
cd analysis
python check_tapestry_status.py
```

### 3. Scrape Data (FREE):
```bash
cd scrapers/reddit
python scrape_dark.py
```

### 4. Analyze ($$):
```bash
cd ../../core
python dedupe_before_ananki.py ../data/reddit/test_results/dark_smart_extraction.json
python true_ananki.py ../data/reddit/test_results/dark_smart_extraction_DEDUPED.json
```

### 5. Add to Tapestry (FREE):
```bash
python inject_to_tapestry.py ../data/reddit/test_results/dark_smart_extraction_DEDUPED_CLAUDE_MAPPED.json
```

## WEB APP DETAILS:

### How It Works:
1. **User Journey** - 3 questions about emotional state
2. **Claude Curates** - Walks the manifold using TRUE Ananki data
3. **Playlist Generated** - 60-70% from Tapestry + 30-40% extrapolated
4. **Feedback Loop** - Upvotes → tapestry.json, Downvotes → user_downvotes.json

### Key Files:
- `server/claude-service.ts` - Reads tapestry & manifold, calls Claude API
- `server/storage.ts` - Saves upvotes/downvotes
- `server/routes.ts` - API endpoints (/api/generate-playlist, /api/tapestry-stats)
- `.env` - API keys (ANTHROPIC_API_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

## IMPORTANT:

### SAFE FILES (in core/):
- ✅ tapestry.json - THE database (6,081 songs)
- ✅ manifold.json - THE structure (9 metas, 114 sub-vibes)

### DANGEROUS FILES (in archive/):
- ❌ old_tapestries/ - CORRUPTED! Don't use!
- ❌ old_scripts/ - Obsolete code

### YOUR $70 IS SAFE:
- All analyzed data is in core/tapestry.json
- 100% TRUE Ananki reasoning
- No corrupted data accessible
- Web app reads from core/, never modifies without user action

## WHAT'S NEW:

1. ✅ Working web app with conversational interface
2. ✅ Real-time stats banner (6,081 tracks shown)
3. ✅ Feedback loop feeding back into Tapestry
4. ✅ Windows-compatible server setup
5. ✅ All paths properly configured (../../core/tapestry.json)
6. ✅ Ready for UI customization!

**See docs/DearClaude.md for current status and next steps!**
