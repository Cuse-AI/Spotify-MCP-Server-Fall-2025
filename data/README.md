# Data Folder

## Structure

```
data/
├── pipeline/           ← NEW DATA GOES HERE
│   ├── 1_raw/         ← Fresh scraper output
│   ├── 2_deduped/     ← After deduplication  
│   ├── 3_analyzed/    ← After Ananki analysis
│   └── 4_ready/       ← Human-verified, ready to inject
│
├── manifold/          ← Emotional mapping (don't touch)
│   └── emotional_manifold_COMPLETE.json
│
└── archive/           ← Old stuff (don't touch)
    ├── legacy/
    ├── misc/
    ├── processed/
    ├── quality_scrub/
    └── scripts/
```

## Pipeline Flow

```
1_raw → 2_deduped → STOP ✋ → 3_analyzed → 4_ready → core/tapestry.json
                      │
                  Ask Claude to verify!
```

## The Simple Rule

New scraper data follows the pipeline. Old stuff stays in archive.
