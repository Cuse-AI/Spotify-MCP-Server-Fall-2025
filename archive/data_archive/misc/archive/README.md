# DATA VALIDATION WORKFLOW

This directory contains the complete pipeline for validating songs from the Tapestry against Spotify's database.

## 📁 DIRECTORY STRUCTURE

```
data_validation/
├── scripts/              # Active workflow scripts
├── batch_results/        # Validation results by batch
├── archive/              # Old/deprecated files
├── README.md            # This file
├── VALIDATION_ASSESSMENT.md  # Quality analysis report
└── VALIDATION_WORKFLOW.md    # Original workflow docs
```

---

## 🚀 VALIDATION WORKFLOW (Step-by-Step)

### **STEP 1: Run Validation on New Batch**

To validate the next 2,000 songs (batches 5-8):

```bash
cd data_validation/scripts
python run_full_validation.py --start-batch 5 --num-batches 4
```

This will:
- Process songs 2000-4000 from the tapestry
- Match against Spotify API
- Generate confidence scores
- Output to `batch_results/`

### **STEP 2: Analyze Low-Confidence Matches**

```bash
python analyze_low_confidence.py
```

This categorizes low-confidence matches into:
- **KEEP**: Actually good matches despite low confidence
- **DISCARD**: Garbled data or terrible matches  
- **CHECK_YOUTUBE**: Borderline cases worth YouTube verification

Output: `low_confidence_analysis.json`

### **STEP 3: Prepare Songs for Tapestry**

```bash
python prepare_tapestry_additions.py
```

Combines:
- High-confidence Spotify matches
- KEEP songs from low-confidence analysis

Output: `confirmed_songs_for_tapestry.json`

### **STEP 4: Merge into Tapestry**

```bash
python merge_to_tapestry.py
```

Integrates validated songs into `tapestry_CLEANED_WITH_SPOTIFY.json`

Creates automatic backup before merging.

### **STEP 5: Analyze Results**

```bash
python analyze_tapestry.py
```

Shows:
- Total validation coverage
- Quality indicators
- Breakdown by vibe

---

## 📊 CURRENT STATUS (After Batches 1-4)

**Processed**: 2,000 songs (batches 1-4)  
**Validated**: 1,147 songs (57.4% yield)  
**Added to Tapestry**: 721 new songs  
**Current Tapestry Size**: 32,686 songs (3.1% validated)

**By Vibe:**
- Sad - Heartbreak: 34.9% validated
- Sad - Crying: 32.7% validated  
- Sad - Lonely: 32.2% validated

---

## 🔧 SCRIPT REFERENCE

### Core Workflow Scripts (in `scripts/`)

| Script | Purpose | Output |
|--------|---------|--------|
| `step0_preprocess_songs.py` | Extract songs from tapestry | Preprocessed JSON |
| `step1_spotify_validate_v2.py` | Match against Spotify API | Batch results |
| `run_full_validation.py` | Run complete validation pipeline | Multiple batches |
| `run_batches_2_to_4.py` | Convenience script for batches 2-4 | Batch 2-4 results |
| `analyze_low_confidence.py` | Categorize low-conf matches | Analysis JSON |
| `prepare_tapestry_additions.py` | Prep validated songs | Confirmed songs JSON |
| `merge_to_tapestry.py` | Add songs to tapestry | Updated tapestry |
| `analyze_tapestry.py` | Quality & coverage stats | Terminal output |
| `youtube_validator.py` | Fallback YouTube validation | YT validation results |

---

## 📋 BATCH RESULTS FORMAT

Each batch generates 2 files in `batch_results/`:

1. **`spotify_batch_N_results_v2.json`**: All matches
   - `good_matches`: High confidence (≥0.6)
   - `questionable_matches`: Low confidence (<0.6)
   - `unmatched_songs`: No match found

2. **`spotify_batch_N_results_v2_NEEDS_AI_REVIEW.json`**: Low-confidence only
   - Used by `analyze_low_confidence.py`

---

## 🎯 VALIDATION METRICS

### Confidence Score Calculation
```
confidence = (artist_similarity + song_similarity) / 2
```

Where similarity uses Levenshtein distance (fuzzy string matching)

### Quality Tiers
- **EXCELLENT**: confidence ≥ 0.8
- **GOOD**: 0.6 ≤ confidence < 0.8
- **QUESTIONABLE**: 0.45 ≤ confidence < 0.6
- **POOR**: confidence < 0.45

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue: "YouTube API key not set"
**Solution**: YouTube validation is optional. Skip for now or set API key in `youtube_validator.py`

### Issue: "Spotify rate limit hit"
**Solution**: Wait 60 seconds, or reduce batch size in validation script

### Issue: Lots of duplicates in results  
**Solution**: Normal! Pre-validation dedup catches ~20-30% duplicates

---

## 📈 NEXT STEPS

1. ✅ **Validate Batches 5-8** (songs 2000-4000)
2. 📊 **Analyze patterns** at 5,000 validated songs
3. 🛠️ **Improve scraper** based on error patterns
4. 🔄 **Re-validate** with improved extraction
5. 🚀 **Scale** to full dataset

Target: 70%+ validation yield with improved scraper

---

*Last updated: After batch 1-4 integration (721 songs added)*
