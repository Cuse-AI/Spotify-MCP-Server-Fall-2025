# Dear Claude - Midden Project Session Notes

## Session: 11/30/2025

### Current Status: Parallel Scraping Working!

**Data collected so far:** 130 songs across all 9 meta-vibes

| Meta-Vibe | Songs | Quota Used | Quota Remaining |
|-----------|-------|------------|-----------------|
| Energy | 22 | 8,157 | 1,843 |
| Happy | 21 | 9,849 | 151 |
| Drive | 20 | 8,053 | 1,947 |
| Sad | 18 | 4,224 | 5,776 |
| Chill | 10 | 5,332 | 4,668 |
| Night | 7 | 2,514 | 7,486 |
| Uplifting | 7 | 3,514 | 6,486 |
| Party | 5 | 3,120 | 6,880 |
| Dark | 5 | 9,852 | 148 |

### Project Structure (Clean)
```
/data/pipeline/          <- NEW DATA GOES HERE
  /1_raw/                <- Scraper output (130 songs)
  /2_deduped/            <- After deduplication
  /3_analyzed/           <- After Ananki analysis
  /4_ready/              <- Ready for tapestry injection

/testing/scrapers/       <- Scraper code
  metavibe_scraper.py    <- Per-vibe scraper (works!)
  launch_all_scrapers.py <- Parallel launcher (has issues)
  check_scrape_status.py <- Progress monitor

/core/tapestry.json      <- Production (don't touch yet)
```

### What Works
- Individual metavibe scrapers work perfectly
- Reddit → Spotify → YouTube pipeline validated
- Lyrics fallback rescuing ~30-50% of songs
- Cover/tribute filter catching bad matches
- Dedupe against pipeline preventing duplicates

### Known Issue
The parallel launcher (`launch_all_scrapers.py`) has stdout redirect issues - some processes don't capture output. Running scrapers individually works fine.

### Demo Timeline
- Dec 2: Demo day
- Dec 4: Industry summit
- Target: 900+ songs minimum, 1800+ ideal

### Next Steps
1. Run remaining quota on 6 keys (Night, Party, Uplifting, Sad, Chill, Drive)
2. Add 9 more API keys for parallel capacity
3. Continue scraping through Dec 2
4. Dedupe and Ananki analysis once we hit targets
