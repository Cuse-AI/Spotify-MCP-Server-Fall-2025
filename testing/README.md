# Testing Folder

This folder contains test scrapers and experimental code that is **separate from the main project**.

## Structure

```
testing/
└── scrapers/
    └── reddit/
        ├── test_scraper.py    # Clean test scraper with quality filtering
        └── output/            # Scraped data lands here
```

## Workflow

1. **Run scraper** with small target (30-50 songs)
2. **STOP** - Don't run Ananki yet!
3. **Verify quality** - Ask Claude to check output file
4. **If good** → Proceed to Ananki analysis
5. **If bad** → Adjust filters and re-run

## Usage

```bash
cd testing/scrapers/reddit
python test_scraper.py
```

Edit `test_scraper.py` to change:
- Target vibe (DRIVE_CONFIG, PARTY_CONFIG, NIGHT_CONFIG)
- Target count (default 30)
- Queries and subreddits

## Quality Rules

The scraper rejects comments that:
- Are too short (<30 chars) or too long (>500 chars)
- Contain URLs
- Are generic ("great song", "masterpiece", etc.)
- Are just song lists (3+ "Artist - Song" patterns)
- Have no emotional language

## Why This Exists

Previous scrapers had no quality filtering, resulting in 33% garbage data.
This scraper filters AT THE SOURCE to prevent bad data from ever entering.
