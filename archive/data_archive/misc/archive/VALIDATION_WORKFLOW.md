# Tapestry Validation Workflow

## Complete Automated Pipeline

This document describes the full workflow from Reddit scraping to validated songs in the tapestry.

---

## Workflow Steps

### 1. Reddit Scraping
**Script:** `reddit/expansion_batches/batch_XX_*.py`

- Scrapes Reddit music recommendation threads
- Extracts songs from human emotional expressions
- Saves raw data as CSV files

**Output:** Raw song data with vibe descriptions from Reddit

---

### 2. Ananki Analysis
**Manual step** - Ananki (AI) analyzes the scraped data to:
- Categorize emotional vibes
- Add genre categorization
- Create vibe sub-categories
- Integrate into tapestry structure

**Output:** `tapestry_CLEANED.json` with categorized songs

---

### 3. Pre-Processing (NEW!)
**Script:** `step0_preprocess_songs.py`

Fixes common parsing errors from Reddit extraction:
- Cleans whitespace and newlines
- Detects artist/song swaps
- Fixes multiple artists in one field
- Removes bracketed info [remaster], (live), etc.
- Standardizes featuring notation

**Results:** 31.8% of songs fixed (10,067 out of 31,685)

**Fixes Applied:**
- Whitespace cleaned: 7,272 songs
- Artist/song swapped: 2,358 songs
- Multiple artists separator: 1,080 songs
- Bracketed info removed: 38 songs
- Featuring standardized: 35 songs

**Output:** `tapestry_PREPROCESSED.json`

---

### 4. Spotify Validation with Confidence Scoring
**Script:** `step1_spotify_validate_v2.py`

Validates songs against Spotify API with quality checks:
- Uses string similarity matching (SequenceMatcher)
- Detects artist/song swaps automatically
- Calculates confidence score (0.0-1.0)
- Rate limiting: ~170 requests/minute

**Confidence Thresholds:**
- ≥0.8: EXCELLENT match
- ≥0.6: GOOD match (auto-accept)
- ≥0.4: QUESTIONABLE match (needs review)
- <0.4: POOR match (needs review)

**Output:** `spotify_batch_X_results_v2.json` with:
- `good_matches`: High confidence (≥0.6)
- `questionable_matches`: Low confidence (<0.6)
- `unmatched_songs`: No Spotify match found

---

### 5. Auto-Add to Tapestry
**Script:** `step2_add_validated_to_tapestry.py`

Automatically adds high-confidence matches:
- Groups validated songs by vibe
- Checks for duplicates (by Spotify ID)
- Adds non-duplicate songs to tapestry
- Updates stats (total songs, validated count)

**Output:**
- `tapestry_PREPROCESSED_WITH_SPOTIFY.json` - Updated tapestry
- `spotify_batch_X_results_v2_NEEDS_AI_REVIEW.json` - Flagged songs

---

### 6. AI Review of Flagged Songs
**Manual step** - AI (Claude) analyzes questionable matches to:
- Determine if matches are actually correct (just swapped)
- Identify parsing errors that can be rescued
- Flag truly bad matches for rejection
- Provide recommendations for improvement

---

## Validation Results Comparison

### BEFORE Pre-Processing:
```
Batch 1 (500 songs from original CLEANED tapestry):
- High Confidence: 280 (56%)
- Low Confidence: 220 (44%)
- Unmatched: 0 (0%)
```

### AFTER Pre-Processing:
```
TBD - Currently running validation on PREPROCESSED tapestry
Expected improvement: 30-50% of previously flagged songs should now pass
```

---

## Key Insights

### Why Songs Were Flagged (Root Cause Analysis):

1. **Bad Parsing (Most Common)**:
   - Newlines in artist/song fields: `"Dragon \nNicest thing"`
   - Multiple artists mashed together: `"Artist1 Artist2 - Song"`

2. **Artist/Song Swaps**:
   - Common with Reddit extraction
   - Now detected automatically

3. **Formatting Issues**:
   - Extra whitespace, brackets, parentheses
   - Inconsistent featuring notation (feat vs ft. vs featuring)

### Pre-Processing Impact:
- Fixed 31.8% of all songs before validation
- Should significantly reduce low-confidence matches
- Rescues data that would otherwise be flagged

---

## Files in this Workflow

```
data/data_validation/
├── step0_preprocess_songs.py          # Pre-process before validation
├── step1_spotify_validate_v2.py       # Validate with confidence scoring
├── step2_add_validated_to_tapestry.py # Auto-add high confidence songs
├── spotify_batch_X_results_v2.json    # Validation results
└── spotify_batch_X_NEEDS_AI_REVIEW.json # Flagged songs for review

data/ananki_outputs/
├── tapestry_CLEANED.json              # Raw tapestry from Ananki
├── tapestry_PREPROCESSED.json         # After pre-processing
└── tapestry_PREPROCESSED_WITH_SPOTIFY.json # Final validated tapestry
```

---

## Next Steps

1. Complete validation of all 31,685 songs in batches of 500
2. AI review after each batch (manual quality check)
3. Implement feedback loop to improve preprocessing
4. Document final statistics after complete validation

---

## Success Metrics

**Target Goals:**
- 70%+ high confidence matches (auto-accepted)
- 20% questionable matches (AI review)
- 10% unmatched (need YouTube/manual search)

**With Pre-Processing:**
- Expected to improve high confidence rate by 10-15%
- Reduce questionable matches significantly
- Better data quality overall
