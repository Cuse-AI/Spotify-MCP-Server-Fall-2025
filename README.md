# TAPESTRY PROJECT - EMOTIONAL MUSIC MAPPING

**Last Updated:** November 12, 2025 - 

---

## PROJECT VISION

**The Tapestry** maps songs to 114 emotional sub-vibes using human-sourced data from Reddit. This goes beyond simple keyword playlists to capture how humans actually describe music emotionally.

**Goal:** Create a navigable 2D emotional manifold where each song has context explaining WHY it's associated with that emotion.

---

## CURRENT STATUS

### The Manifold
- **114 sub-vibes** across 23 emotional categories (COMPLETE)
- **2D coordinate system** for geometric emotion navigation (COMPLETE)

### The Database
- **5,00+ validated songs and growing** with Spotify IDs
- **Each song includes:**
  - Original Reddit context (post title + comment)
  - Ananki reasoning (AI analysis of emotional fit)
  - Confidence score
  - Sub-vibe placement

### What Just Happened (BREAKTHROUGH!)
We discovered the previous Ananki was using **keyword matching** instead of true AI reasoning. This caused false positives like motivational speaking tracks being mapped to "Happy - Euphoric."

**Solution:** Built TRUE Ananki using Claude API for real human-level analysis!

---

## THE WORKFLOW

### Phase 1: Smart Scraping
```bash
cd data/reddit/smart_scrapers
python scrape_happy.py  # Or any meta-vibe
```
- Searches Reddit for emotional music discussions
- Extracts song mentions
- Validates with Spotify API during extraction
- Dedupes the results, so no track/artist happens more than once
- **Result:** 100% validated songs with full context

### Phase 2: TRUE Ananki Analysis
```bash
cd data/reddit
python true_ananki_claude_api.py test_results/happy_smart_extraction_500.json
```
- Claude reads the Reddit context for each song
- Analyzes emotional intent like a human would
- Maps to specific sub-vibe (Happy - Feel Good vs Happy - Euphoric)
- Flags ambiguous cases for review
- **NO KEYWORD MATCHING - Real AI reasoning!**

### Phase 3: Injection
```bash
python inject_to_tapestry.py test_results/happy_smart_extraction_500_CLAUDE_MAPPED.json
```
- Adds songs to tapestry with all context preserved
- Each song includes Ananki's reasoning
- Result: Clean, high-confidence data

---

## ANANKI PRINCIPLES - ANANKI IS THE AGENT ACTING AS "HUMAN IN THE LOOP"

**What Ananki Does:**
1. Reads full Reddit context (post title + comment)
2. Analyzes emotional intent using Claude API
3. Maps to specific sub-vibe based on human language
4. Provides reasoning for the decision
5. Flags ambiguous/off-topic cases

**What Ananki Does NOT Do:**
- Keyword matching
- Artist/song name analysis
- Guessing when context is unclear

**Example:**
- Post: "What's your favorite feel good song?"
- Comment: "Goodbye Stranger by Supertramp"
- Claude Analysis: "The human explicitly requested 'feel good song' recommendations, and 'Goodbye Stranger' was offered as a direct response. This is a clear match to the 'Happy - Feel Good' sub-vibe category."
- Confidence: 1.0
- Result: Song → Happy - Feel Good


---

## FOR NEW CLAUDE INSTANCES

Read `docs/DearClaude.md` first! It has:
- Current exact status
- What was done in last session
- What to do next
- Where all the important files are

---

**The breakthrough:** We're not doing keyword matching anymore. TRUE Ananki uses real AI reasoning to understand emotional context!
