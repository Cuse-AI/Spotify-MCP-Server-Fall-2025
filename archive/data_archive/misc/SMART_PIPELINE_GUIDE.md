# SMART SCRAPING PIPELINE - COMPLETE GUIDE

**Revolutionary approach:** Let Spotify validate during scraping, let Ananki map to sub-vibes!

---

## 🎯 THE PIPELINE

### Step 1: Archive Unvalidated Data
```bash
cd data/reddit
python archive_unvalidated.py
```
- Removes 31K unvalidated songs from tapestry
- Keeps 2,285 validated songs
- Preserves all 114 sub-vibe structures
- Creates backup

### Step 2: Smart Scrape a Meta-Vibe
```bash
python scrape_happy_500.py
```
- Searches Reddit for Happy music discussions
- Extracts songs via Spotify search (pre-validated!)
- Preserves comment context
- Output: ~400-500 songs with 100% Spotify validation

### Step 3: Ananki Sub-Vibe Mapping
```bash
python ananki_subvibe_mapper.py test_results/happy_smart_extraction_500.json
```
- Analyzes comment context
- Maps to specific sub-vibe (Happy-Feel Good vs Happy-Sunshine, etc.)
- Uses keyword matching (same as original manifold analysis)
- Output: Songs with sub-vibe assignments

### Step 4: Inject to Tapestry
```bash
python inject_to_tapestry.py test_results/happy_smart_extraction_500_MAPPED.json
```
- Adds songs to correct sub-vibe nodes
- Checks for duplicates
- Updates tapestry_VALIDATED_ONLY.json

---

## 📊 EXPECTED RESULTS PER META-VIBE

| Meta-Vibe | Estimated Songs | Sub-Vibes |
|-----------|----------------|-----------|
| Sad | 2,000-3,000 | 7 sub-vibes |
| Happy | 1,500-2,000 | 5 sub-vibes |
| Anxious | 1,000-1,500 | 6 sub-vibes |
| Dark | 1,500-2,000 | 7 sub-vibes |
| Energy | 1,500-2,000 | 5 sub-vibes |
| Romantic | 2,000-2,500 | 7 sub-vibes |

**Total projected: 15K-20K songs, all 100% validated!**

---

## 🧠 HOW ANANKI WORKS

Ananki uses the SAME analysis that created the original 114 sub-vibe mappings:

### Keyword Matching (90% of songs)
- "crying" → Sad - Crying
- "heartbreak" → Sad - Heartbreak
- "lonely" → Sad - Lonely
- "feel good" → Happy - Feel Good

### Contextual Analysis (10% of songs)
- Analyzes full comment context
- Identifies emotional intent
- Maps hybrid/ambiguous emotions

---

## 🗂️ FILE OUTPUTS

### After Each Meta-Vibe Scrape
```
test_results/
├── [metavibe]_smart_extraction_500.json      # Raw scraped (Spotify validated)
├── [metavibe]_smart_extraction_500_MAPPED.json  # Ananki mapped
└── injection_stats_[metavibe].json           # What got added
```

---

## ✅ VERIFICATION

After running full pipeline, check tapestry:
```bash
python -c "import json; t=json.load(open('../ananki_outputs/tapestry_VALIDATED_ONLY.json')); print(f'Total: {sum(len(v[\"songs\"]) for v in t[\"vibes\"].values())}')"
```

Should show only validated songs with Spotify IDs!

---

*Next: Run this pipeline for all 23 meta-vibes to build complete validated tapestry!*
