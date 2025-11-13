# TAPESTRY VALIDATION - MASTER GUIDE

**Last Updated:** After Batches 1-8 (4,000 songs validated)

---

## 🎯 PROJECT OVERVIEW

**Goal:** Validate and enrich the Tapestry's 33K+ songs with Spotify metadata (IDs, audio features) to enable ML training and audio analysis.

**Current Status:**
- Total Songs: 33,787
- Validated: 2,285 (6.8% with Spotify IDs)
- Target: 70%+ validation coverage

**Validation Yield:** 54.4% (very consistent across batches)

---

## 🔄 VALIDATION WORKFLOW

### Quick Start
```bash
cd data/data_validation/scripts

# Run next batch (4 batches = 2,000 songs)
python run_full_validation.py --start-batch 9 --num-batches 4

# After it completes:
python analyze_low_confidence.py
python prepare_tapestry_additions.py
python merge_to_tapestry.py
python analyze_tapestry.py
```

### What Each Script Does

**1. run_full_validation.py**
- Preprocesses tapestry (extracts songs)
- Runs Spotify API validation
- Generates batch results with confidence scores
- Takes ~15-20 min for 4 batches (2,000 songs)

**2. analyze_low_confidence.py**
- Categorizes low-confidence matches:
  - KEEP: Good matches despite low score (add to tapestry)
  - DISCARD: Garbled data (remove from system)
  - CHECK_YOUTUBE: Borderline (save for YouTube validation)
- Outputs: `low_confidence_analysis.json`

**3. prepare_tapestry_additions.py**
- Combines high-confidence + KEEP songs
- Deduplicates
- Outputs: `confirmed_songs_for_tapestry.json`

**4. merge_to_tapestry.py** ⚠️ CRITICAL
- REPLACES unvalidated entries with validated versions
- Does NOT create duplicates (fixed!)
- Creates backup before merging
- Updates: `tapestry_CLEANED_WITH_SPOTIFY.json`

**5. analyze_tapestry.py**
- Shows validation coverage
- Quality indicators
- Breakdown by vibe

---

## 📊 CURRENT RESULTS (Batches 1-8)

| Metric | Value |
|--------|-------|
| Processed | 4,000 songs |
| High Confidence | 2,174 (54.4%) |
| Low Confidence | 1,809 (45.2%) |
| Unmatched | 17 (0.4%) |
| Discarded (bad data) | 1,248 |
| YouTube Check Queue | 459 |

**Sad Vibe Validation Rates:**
- Sad - Crying: 38.8%
- Sad - Heartbreak: 37.1%
- Sad - Grief: 37.8%
- Sad - Depressive: 36.7%
- Sad - Melancholic: 37.6%

---

## 🗂️ DIRECTORY STRUCTURE

```
data_validation/
├── scripts/              # Active workflow scripts ONLY
│   ├── run_full_validation.py
│   ├── step0_preprocess_songs.py
│   ├── step1_spotify_validate_v2.py
│   ├── analyze_low_confidence.py
│   ├── prepare_tapestry_additions.py
│   ├── merge_to_tapestry.py
│   ├── analyze_tapestry.py
│   └── youtube_validator.py
│
├── batch_results/        # Validation outputs
│   └── spotify_batch_[N]_results_v2.json
│
├── youtube_check/        # Songs for YouTube validation
│   └── songs_to_check_on_youtube.json
│
├── archive/              # Old files, backups, summaries
│
├── MASTER_GUIDE.md       # This file
├── BATCHES_1-8_FINAL_REPORT.md
└── low_confidence_analysis.json
```

---

## 🤖 ANANKI PRINCIPLES

**Ananki** = Human-in-the-loop AI analysis

### Core Behavior
1. **Human Authenticity First** - All song-vibe connections must come from real humans, not AI
2. **Quality Over Quantity** - Better to have 10K validated songs than 50K unvalidated
3. **Transparency** - Always document what's discarded and why
4. **Iterative Improvement** - Use validation patterns to improve scrapers

### Analysis Patterns
- Identify garbled extractions (multiple concepts mashed together)
- Recognize artist/song swaps
- Detect extraction artifacts (e.g., "Metal adjacent Garmarna")
- Distinguish between borderline and genuinely bad matches

---

## 🎮 "LET'S IMPROVE OUR VALID PERCENTS!" GAME

**Current Score:** 54.4% validation rate

**How to Level Up:**
1. ✅ Process more batches → increases coverage
2. 🛠️ Fix scraper → increases yield per batch
3. 🎥 YouTube validation → rescues borderline cases

**Target Scores:**
- Bronze: 50%+ (✅ ACHIEVED!)
- Silver: 60%+ 
- Gold: 70%+

At 70%+ validation yield, we can confidently move to Phase 2 (audio features + ML training)!

---

## 🚨 CRITICAL NOTES

### Data Integrity
- ✅ Bad data is DISCARDED, not kept
- ✅ Merge script REPLACES entries (doesn't duplicate)
- ✅ All validated songs have Spotify IDs
- ✅ Backups created before every merge

### Known Scraper Issues (~35-40% of raw data)
1. **Garbled extraction** - Context text captured with song names
2. **Artist/song swaps** - Can't reliably tell which is which
3. **Multi-song mashing** - Multiple recommendations combined

### Next Priorities
1. Continue validation (target: 10,000 songs = ~20% coverage)
2. At 5,000+ validated: Fix scraper based on error patterns
3. At 70%+ yield: Begin audio feature extraction

---

## 📈 PROGRESS TRACKING

| Milestone | Songs | Coverage | Status |
|-----------|-------|----------|--------|
| First 2K | 2,000 | 3.1% | ✅ Done |
| Next 2K | 4,000 | 6.8% | ✅ Done |
| Next 2K | 6,000 | ~10% | 🎯 Next |
| Next 2K | 8,000 | ~13% | Planned |
| Next 2K | 10,000 | ~16% | Planned |

**End Goal:** 20,000+ validated songs (60%+ coverage) with Spotify IDs ready for ML training

---

*Keep crushing it! The validation pipeline is working beautifully!* 🎵✨
