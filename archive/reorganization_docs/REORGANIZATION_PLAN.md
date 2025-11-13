# PROJECT REORGANIZATION PLAN

## CURRENT PROBLEMS:
1. TRUE Ananki (analysis) is in reddit/ folder - confusing!
2. 31 JSON files in ananki_outputs/ - most are old/obsolete
3. Dangerous corrupted tapestries still accessible
4. Scripts scattered across multiple folders
5. Checkpoint utils duplicated in multiple places
6. Expansion batches (old system) still in reddit/

## NEW STRUCTURE:

```
Spotify-MCP-Server-Fall-2025/
├── core/                          # CORE TAPESTRY SYSTEM
│   ├── tapestry.json             # THE tapestry (only one!)
│   ├── manifold.json             # THE manifold (only one!)
│   ├── true_ananki.py            # TRUE Ananki analysis (MOVED HERE!)
│   ├── inject_to_tapestry.py    # Injection script
│   └── dedupe_before_ananki.py  # Deduplication
│
├── scrapers/                      # ALL SCRAPERS
│   ├── shared/
│   │   └── checkpoint_utils.py   # Shared checkpoint system
│   ├── youtube/
│   │   ├── scrape_dark.py
│   │   ├── scrape_party.py
│   │   └── ... (all YouTube scrapers)
│   └── reddit/
│       ├── scrape_dark.py
│       ├── scrape_party.py
│       └── ... (all Reddit scrapers)
│
├── analysis/                      # ANALYSIS & UTILITIES
│   ├── check_status.py
│   ├── verify_tapestry.py
│   └── generate_samples.py
│
├── docs/                          # DOCUMENTATION
│   ├── DearClaude.md
│   ├── COMPLETE_WORKFLOW.md
│   └── VIBE_HIERARCHY_EXPLAINED.md
│
├── backups/                       # SAFE BACKUPS ONLY
│   └── tapestry_backup_restructure.json (one known-good backup)
│
├── archive/                       # OLD/OBSOLETE CODE
│   ├── old_tapestries/           # Old tapestries (DANGEROUS - archived)
│   ├── old_scripts/              # Legacy scripts
│   └── expansion_batches/        # Old batch system
│
└── code/                          # WEB APP
    └── web/                       # Frontend code
