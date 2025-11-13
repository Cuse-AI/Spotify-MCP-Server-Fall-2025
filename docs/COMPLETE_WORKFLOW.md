# THE TAPESTRY - COMPLETE WORKFLOW
## Updated Nov 12, 2025 - WITH REORGANIZATION!

---

## 🚨 CRITICAL: ALWAYS DEDUPE BEFORE ANANKI!

**Never run Ananki without deduping first - it wastes money!**

---

## THE 4-STEP WORKFLOW

### Step 1: SCRAPE (Collect Raw Data)

**YouTube (NO rate limits until quota):**
```bash
cd scrapers/youtube
python -u scrape_VIBE.py
# Output: data/youtube/test_results/VIBE_youtube_extraction.json
# Time: ~10-15 min for 500-1000 songs
```

**Reddit (21-hour cooldown after limit):**
```bash
cd scrapers/reddit
python -u scrape_VIBE.py
# Output: data/reddit/test_results/VIBE_smart_extraction.json
# Time: ~15-20 min for 500 songs
```

---

### Step 2: DEDUPE (Remove Existing Songs) ⭐ REQUIRED!

**ALWAYS run this before Ananki to save money!**

```bash
cd core
python dedupe_before_ananki.py ../data/reddit/test_results/VIBE_extraction.json
# Output: VIBE_extraction_DEDUPED.json
# Shows: How many NEW vs duplicate songs
# Time: ~5 seconds
```

**Example:**
```bash
cd core
python dedupe_before_ananki.py ../data/youtube/test_results/sad_youtube_extraction.json
python dedupe_before_ananki.py ../data/reddit/test_results/angry_checkpoint.json
```

**Savings:** $0.003 per duplicate song avoided!
- 100 duplicates = Save $0.30
- 500 duplicates = Save $1.50
- 1,000 duplicates = Save $3.00

---

### Step 3: ANANKI (Claude Analysis)

**Run on DEDUPED file only!**

```bash
cd core
python -u true_ananki.py ../data/reddit/test_results/VIBE_extraction_DEDUPED.json
# Output: VIBE_extraction_DEDUPED_CLAUDE_MAPPED.json
# Time: ~2 min per 100 songs
# Cost: ~$0.003 per song
```

**Can run multiple in parallel!** (3-5 processes works well)

---

### Step 4: INJECT (Add to Tapestry)

```bash
cd core
python inject_to_tapestry.py ../data/reddit/test_results/VIBE_extraction_DEDUPED_CLAUDE_MAPPED.json
# Updates: core/tapestry.json
# Time: ~30 seconds
# Shows: Distribution across sub-vibes
```

---

## 💰 COST MANAGEMENT

**Per 100 Songs:**
- Scraping: FREE (just API quotas)
- Deduping: FREE (instant)
- Ananki: ~$0.30 (if all new)
- Injection: FREE

**Per 1,000 Songs (all new):** ~$3.00
**Per 1,000 Songs (50% dupes):** ~$1.50

**Always dedupe first to minimize costs!**

---

## 🔄 AUTOMATION TIPS

**Run multiple scrapers:**
```bash
# Terminal 1
cd scrapers/reddit
python -u scrape_happy.py

# Terminal 2
python -u scrape_sad.py

# Terminal 3
python -u scrape_energy.py
```

**Batch dedupe:**
```bash
cd core
for file in ../data/reddit/test_results/*_extraction.json; do
    python dedupe_before_ananki.py "$file"
done
```

**Batch Ananki:**
```bash
cd core
# Start multiple Ananki on deduped files:
python -u true_ananki.py ../data/reddit/test_results/file1_DEDUPED.json &
python -u true_ananki.py ../data/reddit/test_results/file2_DEDUPED.json &
python -u true_ananki.py ../data/reddit/test_results/file3_DEDUPED.json &
```

---

## ⚠️ COMMON MISTAKES

❌ **DON'T:** Run Ananki on raw scraped data
✅ **DO:** Always dedupe first!

❌ **DON'T:** Re-analyze files you've already processed
✅ **DO:** Check for existing _CLAUDE_MAPPED.json files

❌ **DON'T:** Ignore duplicate warnings during injection
✅ **DO:** If you see lots of duplicates, you forgot to dedupe!

❌ **DON'T:** Run scripts from wrong directory
✅ **DO:** Always run core scripts from `core/` directory

---

## 📈 QUALITY METRICS

**Good Ananki Success Rates:**
- 85-98% songs mapped successfully
- 2-15% ambiguous/low confidence

**If success rate is low (<80%):**
- Check scraping quality
- Review search queries
- May be scraping non-music content

---

## 📊 CHECKING RESULTS

**View new Ananki results:**
```bash
cd analysis
python check_new_ananki.py
```

**Check Tapestry status:**
```bash
cd analysis
python check_tapestry_status.py
```

**View random samples:**
```bash
cd analysis
python show_random_samples.py
```

---

**Remember: Scrape → Dedupe → Ananki → Inject!** 💰🎯
