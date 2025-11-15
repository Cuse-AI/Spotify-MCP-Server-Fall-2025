# Automated Scraping + Pipeline Workflow

## Quick Start

### Option 1: YouTube Only
```bash
# Scrape specific vibes (e.g., dark, drive, night, party)
python run_scrapers.py dark,drive,night,party

# Or scrape ALL YouTube vibes
python run_scrapers.py
```

### Option 2: Reddit Only
```bash
# Scrape specific vibes
python run_reddit_scrapers.py dark,drive,night

# Or scrape ALL Reddit vibes
python run_reddit_scrapers.py
```

### Option 3: BOTH (YouTube + Reddit)
```bash
# Scrape everything from both sources
python scrape_all.py

# Or specify which vibes for each source
python scrape_all.py --youtube dark,drive --reddit party,night
```

## What Happens Automatically

Each script will:
1. ✅ Run the scrapers you specify
2. ✅ Move results to `1_raw_scrapes/`
3. ✅ Automatically dedupe against tapestry
4. ✅ Automatically run Ananki analysis ($)
5. ✅ Automatically inject to tapestry
6. ✅ Show you the final count!

## Cost Estimates

- **YouTube scraping**: FREE (uses YouTube API quota, not money)
- **Reddit scraping**: FREE (uses Reddit API, no cost)
- **Ananki analysis**: ~$0.003 per song (~$0.90 per 300 songs)

## Examples

```bash
# Quick test - scrape 300 songs from 3 vibes
python run_scrapers.py dark,night,party

# Full workflow - scrape 9 vibes from both sources
python scrape_all.py

# Reddit only for emotional vibes
python run_reddit_scrapers.py sad,angry,grateful
```

## Pipeline Steps (Automatic)

1. **Dedupe** - Compares against existing tapestry (saves money!)
2. **Ananki** - Claude analyzes emotional context of each song
3. **Inject** - Adds songs to tapestry with proper vibe mapping
4. **Archive** - Moves processed files to archive

## Monitoring

The pipeline will show real-time progress:
- Status updates every 10 songs
- Checkpoints every 25 songs (safe to Ctrl+C)
- Final summary with song counts

## Notes

- Scrapers now skip playlists they've already processed (no YouTube quota waste!)
- All 23 YouTube scrapers have been fixed with the latest improvements
- Reddit scrapers find emotional context posts (not just song lists)
- Pipeline checks timestamps to avoid re-analyzing old data
