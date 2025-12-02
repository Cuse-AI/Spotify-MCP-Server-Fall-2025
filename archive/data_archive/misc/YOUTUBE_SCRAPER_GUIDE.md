# YOUTUBE SCRAPER BLITZ - QUICK REFERENCE

## 🎯 ALL 23 SCRAPERS READY TO RUN!

**Location:** `data/youtube/scrapers/`
**No rate limits!** Can run all simultaneously!

---

## 🚀 HOW TO RUN

### Single Scraper:
```bash
cd data/youtube/scrapers
python -u scrape_VIBENAME.py
```

### Multiple Scrapers (Parallel):
Open multiple terminals/command prompts:

**Terminal 1:**
```bash
cd data/youtube/scrapers
python -u scrape_happy.py
```

**Terminal 2:**
```bash
cd data/youtube/scrapers
python -u scrape_sad.py
```

**Terminal 3:**
```bash
cd data/youtube/scrapers
python -u scrape_energy.py
```

... and so on! Run as many as you want!

---

## 📋 ALL 23 VIBES

- [ ] scrape_angry.py
- [ ] scrape_anxious.py
- [ ] scrape_bitter.py
- [ ] scrape_bored.py
- [ ] scrape_chaotic.py
- [x] scrape_chill.py (DONE! 362 songs)
- [ ] scrape_confident.py
- [ ] scrape_dark.py
- [ ] scrape_drive.py
- [ ] scrape_energy.py
- [ ] scrape_excited.py
- [ ] scrape_grateful.py
- [ ] scrape_happy.py
- [ ] scrape_hopeful.py
- [ ] scrape_introspective.py
- [ ] scrape_jealous.py
- [ ] scrape_night.py
- [ ] scrape_nostalgic.py
- [ ] scrape_party.py
- [ ] scrape_peaceful.py
- [ ] scrape_playful.py
- [ ] scrape_romantic.py
- [ ] scrape_sad.py

---

## ⏱️ TIMING ESTIMATES

**Per scraper:** ~10-15 minutes for 300-500 songs
**All 23 scrapers (sequential):** ~4-6 hours
**All 23 scrapers (parallel, 5 at a time):** ~1-2 hours!

---

## 📊 EXPECTED OUTPUT

Each scraper produces:
- `test_results/VIBE_youtube_extraction.json`
- 300-500 songs with Spotify IDs
- YouTube comments with emotional context
- Ready for TRUE Ananki analysis

---

## 🔄 WORKFLOW AFTER SCRAPING

For each vibe:
```bash
# 1. Scrape (DONE)
python -u scrape_VIBE.py

# 2. Ananki (~20 min for 500 songs)
cd ../../reddit
python -u true_ananki_claude_api.py ../youtube/test_results/VIBE_youtube_extraction.json

# 3. Inject (~1 min)
python inject_to_tapestry.py ../youtube/test_results/VIBE_youtube_extraction_CLAUDE_MAPPED.json
```

---

## 💡 PRO TIPS

1. **Run scrapers in batches of 5-6** to manage terminals
2. **Prioritize vibes with empty sub-vibes** (check tapestry status)
3. **Let scrapers run overnight** if needed (checkpoints save progress!)
4. **Monitor with:** `cd data/youtube/test_results && ls -lt` to see latest files

---

## 🎯 PRIORITY ORDER (Suggested)

**High Priority** (empty/low coverage sub-vibes):
1. Drive
2. Dark  
3. Party
4. Energy
5. Anxious

**Medium Priority:**
6. Introspective
7. Nostalgic
8. Peaceful
9. Romantic
10. Happy

**Lower Priority** (already have some data):
11-23. Remaining vibes

---

**Ready to collect 8,000+ songs with NO rate limits!** 🚀
