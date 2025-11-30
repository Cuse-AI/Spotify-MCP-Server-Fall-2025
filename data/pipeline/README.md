# Midden Data Pipeline

## Flow

```
1_raw/          → Scraper output (songs + YouTube comments)
    ↓
2_deduped/      → Duplicates removed, existing songs filtered
    ↓
3_analyzed/     → Ananki (Claude API) adds vibe mapping
    ↓
4_ready/        → Ready for injection to tapestry.json
```

## Stage Details

### 1. RAW
- Source: `testing/scraper_test_*/` after validation
- Contains: artist, song, comment_text, comment_score, spotify_id, youtube_url
- Missing: mapped_subvibe, ananki_reasoning

### 2. DEDUPED
- Script: `scripts/dedupe_raw.py` (TODO)
- Removes: duplicate songs, songs already in tapestry
- Saves API costs by not analyzing duplicates

### 3. ANALYZED
- Script: `scripts/run_ananki_analysis.py` (TODO)
- Uses: Claude API (EXPENSIVE - be careful!)
- Adds: mapped_subvibe, ananki_reasoning, emotion_markers
- This is where songs get placed on the emotional manifold

### 4. READY
- Final check before injection
- All required fields present
- Can be batch-injected to tapestry.json

## File Naming Convention

```
RAW_hybrid_scraper_YYYYMMDD_HHMMSS.json
DEDUPED_from_RAW_YYYYMMDD_HHMMSS.json
ANALYZED_from_DEDUPED_YYYYMMDD_HHMMSS.json
READY_from_ANALYZED_YYYYMMDD_HHMMSS.json
```

## Workflow

1. Run scraper test → `testing/scraper_test_*/`
2. Review output quality
3. If good: `mv testing/.../RAW_*.json data/pipeline/1_raw/`
4. Run dedupe script
5. Run Ananki analysis (watch costs!)
6. Inject ready songs to tapestry
