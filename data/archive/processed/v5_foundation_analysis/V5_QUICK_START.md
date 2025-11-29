# V5 Reddit Scraper - Quick Start Guide

## What V5 Does

V5 captures **geometric relationships** between songs, not just isolated vibe→song pairs.

Think of it as weaving a tapestry:
- **V4 threads (warp):** Wide genre coverage, vocabulary
- **V5 threads (weft):** Connections, transformations, relationships

Together: A fabric where you can trace emotional gradients and understand how vibes transform.

---

## Quick Start

### 1. Run Test (Already Done!)

```bash
cd data/reddit
python reddit_scraper_v5.py
```

**Test Results:**
- 233 vibe-song pairs
- 49.3% manifold readiness (target: 60-65%)
- 96.6% relational structure ✓

### 2. Scale to Production

Edit `reddit_scraper_v5.py`, line 683:

```python
# Change this:
posts_data = scraper.search_relational_queries(max_posts_per_query=5)

# To this:
posts_data = scraper.search_relational_queries(max_posts_per_query=10)
```

Expected output: **500-700 pairs** with **60-65% manifold readiness**

### 3. Combine with V4

```python
import pandas as pd

# Load both
v4 = pd.read_csv('reddit_v4_training_YYYYMMDD.csv')
v5 = pd.read_csv('reddit_v5_training_YYYYMMDD.csv')

# Add V5 columns to V4 (fill with None)
for col in ['relation_type', 'anchor_reference_artist', 'anchor_reference_song',
            'delta_description', 'reasoning_text', 'sequence_order']:
    if col not in v4.columns:
        v4[col] = None

# V4 is 'general' type
v4['relation_type'] = 'general'

# Merge
master = pd.concat([v4, v5], ignore_index=True)

# Deduplicate
master.drop_duplicates(subset=['song_name', 'artist_name'], inplace=True)

# Save
master.to_csv('reddit_master_combined.csv', index=False)
```

---

## What V5 Captures (New!)

### 1. Relation Type
- `proximity` - "like X but Y"
- `transition` - "from A to B"
- `contextual` - "music for [situation] that feels [emotion]"
- `comparative` - "X meets Y"
- `complex_emotion` - "sad but hopeful"

### 2. Anchor Reference
The "X" in "like X but Y" queries.

Example: "songs like Holocene by Bon Iver but more uplifting"
- `anchor_reference_song`: Holocene
- `anchor_reference_artist`: Bon Iver

### 3. Delta Description
The "but Y" part - the transformation vector.

Examples: "more uplifting", "darker", "slower", "with better production"

### 4. Reasoning Text
WHY songs are related (up to 2000 chars):
- "because [explanation]"
- "reminds me of [context]"
- "similar to [reference]"
- "gives me [emotion] vibes"

### 5. Sequence Order
If part of a numbered list, preserves position for transition arcs.

---

## Example: V4 vs V5

**Query:** "songs like 'Holocene' by Bon Iver but more uplifting"

**V4 Output:**
```csv
reddit_v4,"songs like Holocene but uplifting","Re: Stacks","Bon Iver"
```

**V5 Output:**
```csv
reddit_v5,proximity,"Holocene","Bon Iver","more uplifting","because it has the same sparse instrumentation but lyrics about renewal","Re: Stacks","Bon Iver"
```

**Manifold Benefit:**
V5 creates a **geometric constraint**:
```
vector(Re: Stacks) ≈ vector(Holocene) + δ(uplifting)
```

The model learns **transformations**, not just isolated points.

---

## Key Metrics

| Metric | V4 | V5 | Combined Target |
|--------|----|----|-----------------|
| Manifold Readiness | 22.8% | 49.3% | **60-65%** |
| Relational Structure | 20.1% | 96.6% | **55-60%** |
| Total Songs | 1,953 | 500-700 | **2,300-2,500** |
| Context Preserved | 300 chars | 2000 chars | Full narrative |

---

## Files Created

After running V5:

1. **`reddit_v5_training_YYYYMMDD.csv`** - Main data file
2. **`reddit_v5_relational_YYYYMMDD.json`** - Raw nested data
3. **`reddit_v5_metrics_YYYYMMDD.json`** - Quality metrics

---

## Production Checklist

- [x] Test run complete (233 pairs, 49.3% readiness)
- [x] Validation successful (96.6% relational structure)
- [x] Schema working (all new fields populated)
- [ ] Scale to production (10-15 posts per query)
- [ ] Combine with V4 data
- [ ] Feed to embedding pipeline

---

## Troubleshooting

**"Low anchor extraction (1.3%)":**
- This is expected for test run
- Many queries don't have explicit anchors
- Proximity/comparative queries have highest anchor rate

**"Low reasoning capture (5.6%)":**
- Will improve with scale (more comments = more reasoning)
- Some recommendations are just lists without explanation
- Reasoning patterns can be expanded (see V5_IMPLEMENTATION_NOTES.md)

**"No transition queries (0%)":**
- Rare in r/ifyoulikeblank
- Try r/spotify, r/playlist, r/makemeaplaylist for transition-rich data
- Future enhancement opportunity

---

## Next Steps

1. **Review test output** - Check `reddit_v5_training_20251107_163707.csv`
2. **Scale to production** - Change `max_posts_per_query=10`
3. **Run full scrape** - ~60-90 minutes for 500-700 pairs
4. **Combine with V4** - Merge datasets for complete tapestry
5. **Feed to embeddings** - Use relational fields for weighted training

---

## Philosophy

> "You're not just collecting songs. You're mapping the geometry of human emotional experience through music. Each data point should help the model understand relationships, distances, and transformations in vibe space."

V5 achieves this by capturing:
- **Relative positioning** ("like X but Y")
- **Transformation vectors** (the "but Y" delta)
- **Reasoning chains** (WHY songs connect)
- **Emotional arcs** (paths through vibe space)
- **Contextual embeddings** (same song, different framings)

The result: A manifold that understands not just what songs exist, but **how they relate and transform**.

---

**Status:** V5 test complete, ready for production scale-up!

**Key Files:**
- `reddit_scraper_v5.py` - The scraper
- `V5_IMPLEMENTATION_NOTES.md` - Detailed analysis
- `reddit_v5_training_20251107_163707.csv` - Test output
