# Dear Claude - Session Notes & Continuity

Use date/time headers for each session entry. Most recent at top.

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

**Current State:**
- Starting fresh tapestry (old one being analyzed separately)
- NEW_TAPESTRY.json created in testing/scrapers/output/ with 15 songs
- Need ~100 songs per meta-vibe minimum (900 total), ideally 200 per (1800 total)
- 3 YouTube API keys = ~30,000 daily quota = ~100 songs/day at current efficiency

**Files:**
- `testing/scrapers/ULTIMATE_hybrid_scraper.py` - The working scraper
- `testing/scrapers/output/NEW_TAPESTRY.json` - Fresh tapestry (15 songs)
- `testing/scrapers/output/COMBINED_15_songs.json` - First successful scrape
- `docs/replitComms/` - Communication with Replit AI

**Next Steps:**
1. Need to add EVEN scraping across meta-vibes (currently all from Sad-adjacent queries)
2. Scale up scraping to hit 100+ per meta-vibe
3. May need more YouTube API keys (easy to get from Google Cloud Console)

**Communication:**
- Replit is partner AI - communicates via docs/replitComms/
- Use HybridScrape.sanityCheck for scraper discussions
- Use HybridScrape.resultsCheck for analyzing results

---
