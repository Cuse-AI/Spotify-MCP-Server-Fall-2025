# Scraper Test Output - 2024-11-30

## PIPELINE REMINDER

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MIDDEN DATA PIPELINE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. RAW (this folder → then data/pipeline/1_raw/)                   │
│     └─ Scraper output: songs + YouTube emotional comments           │
│     └─ NOT yet analyzed, NOT yet deduplicated                       │
│                                                                     │
│  2. DEDUPED (data/pipeline/2_deduped/)                              │
│     └─ Remove duplicate songs                                       │
│     └─ Remove songs already in tapestry                             │
│                                                                     │
│  3. ANALYZED (data/pipeline/3_analyzed/)                            │
│     └─ Ananki (Claude API) analyzes each song                       │
│     └─ Determines: mapped_subvibe, ananki_reasoning                 │
│     └─ THIS IS WHERE VIBE PLACEMENT HAPPENS                         │
│                                                                     │
│  4. READY (data/pipeline/4_ready/)                                  │
│     └─ Ready for injection into tapestry.json                       │
│     └─ All fields complete                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## FILES IN THIS TEST

| File | Description |
|------|-------------|
| `RAW_hybrid_scraper_output_*.json` | Direct scraper output - needs full pipeline |
| `STATS_scraper_run_*.json` | Statistics from the scraper run |

## IF TEST LOOKS GOOD

1. Move RAW file to `data/pipeline/1_raw/`
2. Run deduplication script
3. Run Ananki analysis (expensive - uses Claude API!)
4. Move to ready, then inject to tapestry

## WHAT THE SCRAPER PROVIDES

- ✅ Artist + Song
- ✅ YouTube emotional comment (score >= 6)
- ✅ Comment quality score + reasons
- ✅ Spotify ID (if found)
- ✅ Source URL

## WHAT ANANKI ADDS

- ❌ mapped_subvibe (WHERE on manifold)
- ❌ ananki_reasoning (WHY this vibe)
- ❌ emotion_markers
- ❌ primary_emotion / secondary_emotions
