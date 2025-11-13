# REDDIT DATA PIPELINE

**Active workflow using TRUE Ananki with Claude API**

---

## WORKFLOW (3 Steps)

### Step 1: Smart Scraping
```bash
cd smart_scrapers
python scrape_happy.py    # Or any meta-vibe
python scrape_sad.py
python scrape_energy.py
# etc.
```

**What it does:**
- Searches Reddit for emotional music discussions
- Extracts song mentions from comments
- Validates with Spotify during extraction (100% validation rate!)
- Preserves full context (post title + comment text)

**Output:** `test_results/{metavibe}_smart_extraction_2000.json`

---

### Step 2: TRUE Ananki Analysis
```bash
cd ..  # Back to data/reddit/
python true_ananki_claude_api.py test_results/happy_smart_extraction_500.json
```

**What it does:**
- Uses Claude API to read each song's Reddit context
- Analyzes emotional intent like a human would
- Maps to specific sub-vibe (Happy - Feel Good vs Happy - Euphoric)
- Provides reasoning for each decision
- Flags ambiguous cases for review
- **NO KEYWORD MATCHING - Real AI analysis!**

**Output:**
- `test_results/happy_smart_extraction_500_CLAUDE_MAPPED.json` (high confidence songs)
- `test_results/happy_smart_extraction_500_CLAUDE_AMBIGUOUS.json` (needs review)

---

### Step 3: Inject to Tapestry
```bash
python inject_to_tapestry.py test_results/happy_smart_extraction_500_CLAUDE_MAPPED.json
```

**What it does:**
- Adds songs to tapestry with all context preserved
- Each song includes:
  - Original Reddit post title + comment
  - Ananki's reasoning
  - Confidence score
  - Sub-vibe placement

**Result:** Updated `data/ananki_outputs/tapestry_VALIDATED_ONLY.json`

---

## KEY FILES

### Active Scripts
- `smart_scrapers/scrape_*.py` - One scraper per meta-vibe
- `true_ananki_claude_api.py` - Claude API analysis (NO keyword matching!)
- `inject_to_tapestry.py` - Add songs to tapestry
- `.env` - API keys (Anthropic + Spotify)

### Test & Results
- `test_results/` - All scraping and mapping outputs
- `show_random_samples.py` - Verify tapestry has context

### Utilities
- `list_subvibes.py` - Show all 114 sub-vibes
- `reset_tapestry.py` - Clear tapestry (use with caution!)

---

## CURRENT STATUS

### Completed
- [x] TRUE Ananki built and tested
- [x] 10-song test: 90% mapped, 10% ambiguous
- [x] Claude API working with model `claude-sonnet-4-5`

### Ready To Do
- [ ] Fix scraper to prevent false positives (Task #1)
- [ ] Run TRUE Ananki on all existing scraped data (Task #2)
- [ ] Scrape remaining meta-vibes

---

## ANANKI RULES (CRITICAL!)

1. **NEVER use artist/song names** in context analysis
   - Ananki reads ONLY the human's emotional language
   - Song metadata is just for identification

2. **ALWAYS use full context**
   - Post title + comment text
   - Don't truncate or summarize

3. **NO keyword matching**
   - Use Claude API for real reasoning
   - Old keyword approach caused false positives

4. **Flag ambiguous cases**
   - If context is unclear, mark as AMBIGUOUS
   - Don't guess or force a mapping

---

## EXAMPLE: How TRUE Ananki Works

**Input:**
```json
{
  "artist": "Supertramp",
  "song": "Goodbye Stranger",
  "post_title": "What's your favorite feel good song?",
  "comment_text": "Goodbye stranger by Supertramp"
}
```

**Claude Analysis:**
> "The human explicitly requested 'feel good song' recommendations in the post title, and 'Goodbye Stranger' by Supertramp was offered as a response. This is a direct match to the 'Happy - Feel Good' sub-vibe category. The song itself has an upbeat, positive energy with its catchy melody and optimistic sound."

**Output:**
```json
{
  "ananki_subvibe": "Happy - Feel Good",
  "ananki_reasoning": "The human explicitly requested...",
  "ananki_confidence": 1.0
}
```

---

## BREAKTHROUGH MOMENT

We discovered the old Ananki was using **keyword matching** instead of true AI analysis. This caused false positives like motivational speaking tracks being mapped as music.

**Example of bad mapping:**
- Comment: Philosophical discussion about learning
- Old scraper extracted: "Learn from the Negative"
- Spotify found: Jim Rohn motivational speaking
- Old Ananki mapped: Happy - Euphoric (keyword "good" in comment)
- **WRONG!** This isn't music!

**TRUE Ananki catches this:**
- Claude reads context and sees it's not a music recommendation
- Marks as AMBIGUOUS with confidence 0.0
- Prevents false positive from entering tapestry

---

**Next step:** Fix scraper to only extract from actual music discussions!
