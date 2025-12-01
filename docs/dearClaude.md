# Dear Claude - Session Notes & Continuity

Use date/time headers for each session entry. Most recent at top.

---

## Claude - 11/30/2025 8:15 PM

### Project Cleanup & New Parallel Scraper Architecture

**Cleanup Done:**
- Moved scorched earth outputs to `testing/scorched_earth/`
- Archived old `DearClaude.md` from root to `archive/`
- Moved initial 15 test songs to `data/pipeline/1_raw/`
- Cleaned up test outputs to `testing/old_test_outputs/`

**Project Structure Now:**
```
/core/                     - Production tapestry (DON'T TOUCH for now)
/data/pipeline/            - NEW PIPELINE (this is where new scrapes go!)
  /1_raw/                  - Raw scraper output lands here
  /2_deduped/              - After deduplication
  /3_analyzed/             - After Ananki analysis
  /4_ready/                - Ready to inject to tapestry
/testing/                  - All our new work
  /scrapers/               - New scraper code
  /scorched_earth/         - Classifier outputs (GOLD/REVIEW/CUT)
/docs/                     - Documentation
  /dearClaude.md           - THIS FILE (session notes)
  /replitComms/            - Communication with Replit AI
```

**New Parallel Scraper System:**
- 9 YouTube API keys (1 per meta-vibe)
- `metavibe_scraper.py` - Scrapes single meta-vibe with dedicated key
- `launch_all_scrapers.py` - Launches all 9 in parallel
- `check_scrape_status.py` - Shows progress per meta-vibe
- Output goes directly to `data/pipeline/1_raw/`

**Pipeline Flow:**
```
1. Scrape → data/pipeline/1_raw/{Metavibe}_{timestamp}.json
2. Dedupe → data/pipeline/2_deduped/
3. Ananki → data/pipeline/3_analyzed/
4. Ready → data/pipeline/4_ready/
5. Inject → core/tapestry.json
```

**Current Status:**
- 15 test songs in pipeline (from first successful scrape)
- 9 API keys configured in .env
- Awaiting Replit sanity check before parallel launch

**Quota Math:**
- 9 keys × 10,000 units = 90,000 daily quota
- ~281 units per song average
- ~320 songs/day possible
- 100 per meta-vibe (900 total) = ~3 days

---

## Claude - 11/30/2025 7:20 PM

### MAJOR BREAKTHROUGH: Ultimate Hybrid Scraper v4 Working!

**What happened:**
- Fixed the broken scraper (old one was searching YouTube directly for "ambient music relaxing" - GARBAGE)
- New scraper does: Reddit → Spotify → YouTube (targeted "Artist Song official/lyrics")
- Added multi-version fallback (official → lyrics → slowed → acoustic → live)
- Added 3 YouTube API key rotation
- First diagnostic run: 15 quality songs collected!

**Key Stats from First Run:**
- 15 songs, all score 6+ (avg 8.5)
- 4 songs (27%) RESCUED by lyrics version fallback
- 281 units average quota per song
- Real artists: Garbage, AWOLNATION, Halsey, Billie Eilish, The Cure, Nine Inch Nails, etc.

**Lyrics Fallback Results:**
- Replit predicted >30% rescue rate = valuable
- We got **44% rescue rate!**
- Official worked: 5 songs (56%)
- Lyrics rescued: 4 songs (44%)
- Without lyrics fallback we'd have lost nearly half our data

---
