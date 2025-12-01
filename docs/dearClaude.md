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

---

## Session: Claude Code - 11/30/2025 10:30 PM

### Task: Old Tapestry Data Cleanup Preparation

**Context:** The original `core/tapestry.json` has 5,076 songs with data quality issues (36% grief in wrong vibes, 14% medical trauma, 24% context mismatches). Need to salvage the good data before demo.

**What I Did:**

1. **Cleaned up duplicates**
   - Confirmed `tapestry.json` and `tapestry_OLD_SCRAPERS_5076_songs_pre_scorched_earth.json` were identical (same hash)
   - Removed the duplicate file via git

2. **Split tapestry into manageable chunks**
   - Created `core/split_tapestry.py` to split 5,076 songs into 11 chunks of ~500 songs each
   - Generated chunks in `core/tapestry_chunks/` (chunks 01-10 have 500 songs, chunk 11 has 76)
   - Each chunk is ~680KB, well within Claude Desktop's context window

3. **Created merge script for after cleaning**
   - Created `core/merge_tapestry.py` to combine cleaned chunks back into `tapestry_cleaned.json`

4. **Wrote comprehensive cleaning instructions**
   - See "Claude Desktop Data Cleaning Instructions" section below
   - Detailed rules for what to REMOVE vs KEEP
   - Examples for each vibe type
   - Step-by-step workflow

---

# Claude Desktop Data Cleaning Instructions

## Mission: Clean the Tapestry Data

You're helping clean 5,076 songs from the old tapestry data. The data has been split into **11 chunks** of ~500 songs each (located in `core/tapestry_chunks/`).

Your job is to **remove bad data** and keep only "gold" comments - those with genuine, vibe-appropriate emotional context.

---

## What to REMOVE (Bad Data)

### 1. Grief/Death Stories in Wrong Vibes
**REMOVE** if the comment mentions death, funerals, or loss in these vibes:
- Party
- Energy
- Happy
- Uplifting
- Chill
- Drive

**Examples to REMOVE:**
- "My dad passed away and this was played at his funeral" (in Party/Energy/Happy)
- "This helped me through my mom's cancer" (in Energy)
- "RIP to my friend, this was his favorite" (in Party)

**KEEP** grief stories ONLY in:
- Sad (where grief belongs!)
- Dark (if it's about embracing darkness/villain arc, not just loss)

### 2. Medical/Trauma Stories in Wrong Vibes
**REMOVE** comments about:
- Cancer treatment/chemo
- Accidents/injuries
- Hospital stays
- Mental health crises (unless it's the RIGHT vibe, like Dark or Sad)

**Examples to REMOVE:**
- "This got me through chemo" (in Energy)
- "I broke my neck and this helped recovery" (in Energy)
- "Fighting depression for 4 years" (in Party)

### 3. Generic/Empty Comments
**REMOVE** comments that are:
- Just lyrics copy-pasted with no personal context
- Generic praise: "great song", "masterpiece", "fire"
- Music criticism: "the production is breathtaking"
- Just "this is a vibe" with no story

**Examples to REMOVE:**
- "[full song lyrics with no commentary]"
- "This is fire"
- "The atmosphere and ambience are breathtaking"

### 4. Context Mismatch
**REMOVE** if the emotional context doesn't match the vibe:
- Nostalgic childhood memories in Party (unless it's PARTY nostalgia)
- Regret/sadness in Happy
- Anxiety in Chill
- Dark themes in Happy/Uplifting

**Examples to REMOVE:**
- "Reminds me of when I was 9" (in Energy - just nostalgia, not energy)
- "Makes me think about dreams I never pursued" (in Energy - that's regret)
- "Like being in a nightmare" (in Party)

---

## What to KEEP (Gold Data)

### Gold Comments Have:
1. **Personal emotional story** (not just lyrics or generic praise)
2. **Vibe-appropriate context** (the emotion matches the vibe label)
3. **Specific details** (not just "this is good")

### Examples of GOLD Comments by Vibe:

**Party - KEEP:**
- "This was playing at my friend's 21st birthday, we danced all night"
- "Takes me back to college parties, best nights of my life"
- "Festival vibes! Heard this at Coachella 2023"

**Energy - KEEP:**
- "Crushed my PR at the gym to this song"
- "My go-to for the last mile of a run"
- "Pregame hype song before every game"

**Happy - KEEP:**
- "Played at my wedding reception, everyone got up to dance!"
- "This makes me smile every single time"
- "Song that feels like sunshine on a perfect day"

**Sad - KEEP (grief IS appropriate here!):**
- "My dad passed away and this was played at his funeral"
- "Helped me through my breakup"
- "This song makes me cry every time, reminds me of loss"

**Dark - KEEP:**
- "This is my villain era anthem"
- "Witchy vibes playlist essential"
- "Makes me feel powerful in a dark way"

**Chill - KEEP:**
- "Perfect rainy Sunday morning coffee song"
- "My go-to for winding down after work"
- "Study session essential"

**Drive - KEEP:**
- "Best road trip song with windows down"
- "Late night driving alone vibes"
- "Highway cruising perfection"

**Night - KEEP:**
- "3am thoughts soundtrack"
- "Can't sleep, this is perfect"
- "Walking city streets at midnight vibes"

**Uplifting - KEEP:**
- "This got me through a tough time and reminded me things get better"
- "Helped me believe in myself again"
- "New beginnings anthem"

---

## The Cleaning Process

### For Each Chunk File:

1. **Read the chunk** (it's a JSON file with vibes and songs)
2. **Go through each song's `comment_text` and `ananki_reasoning`**
3. **Decide: KEEP or REMOVE** based on the rules above
4. **Remove the entire song entry** if it's bad data
5. **Keep the entire song entry** if it's gold data
6. **Return the cleaned JSON** in the exact same format

### Important:
- Maintain the JSON structure exactly
- Don't modify song metadata (artist, song, spotify_id, etc.)
- Only remove entire song entries
- Don't add new fields or change field names

---

## Example Workflow

**Input chunk:** `tapestry_chunk_01_of_11.json`

**You see:**
```json
{
  "vibes": {
    "Party - House Party": {
      "songs": [
        {
          "artist": "David Guetta",
          "song": "Sexy Bitch",
          "comment_text": "Makes me think of my sister who died",
          ...
        },
        {
          "artist": "Tower of Power",
          "song": "What Is Hip",
          "comment_text": "Concert memories at Toad's Place with friends",
          ...
        }
      ]
    }
  }
}
```

**You output:**
```json
{
  "vibes": {
    "Party - House Party": {
      "songs": [
        {
          "artist": "Tower of Power",
          "song": "What Is Hip",
          "comment_text": "Concert memories at Toad's Place with friends",
          ...
        }
      ]
    }
  }
}
```

**Reasoning:** Removed David Guetta song (grief story in Party vibe). Kept Tower of Power (concert memory is party-appropriate).

---

## After You Clean All 11 Chunks

Save each cleaned chunk with the **same filename** in the same directory:
- `tapestry_chunk_01_of_11.json` → (cleaned version)
- `tapestry_chunk_02_of_11.json` → (cleaned version)
- etc.

Then we'll run `python core/merge_tapestry.py` to combine all cleaned chunks into `tapestry_cleaned.json`.

---

## Quick Reference: What Belongs Where

| Vibe | GOOD Context | BAD Context |
|------|-------------|-------------|
| **Party** | Dancing, clubs, festivals, friends, celebration | Death, grief, medical, anxiety |
| **Energy** | Gym, workout, running, sports, adrenaline | Cancer recovery, medical trauma |
| **Happy** | Joy, sunshine, weddings, good news, smiles | Grief, breakups, loss |
| **Sad** | Heartbreak, grief, crying, loss, loneliness | (Keep grief here!) |
| **Dark** | Villain arc, witchy, existential, powerful darkness | Just generic sadness |
| **Chill** | Coffee, rainy days, study, wind-down, cozy | Anxiety, stress, urgency |
| **Drive** | Road trips, night drives, cruising, windows down | Medical recovery, grief |
| **Night** | 3am thoughts, insomnia, midnight vibes, nocturnal | Daytime activities |
| **Uplifting** | Overcoming, hope, new beginnings, empowerment | Just nostalgia, no growth |

---

## Questions?

If you're unsure about a song:
- **Ask yourself:** "Does this comment's emotion match the vibe label?"
- **When in doubt, be strict** - better to remove borderline data than keep bad data
- **Prioritize quality over quantity** - we want GOLD comments only!

Ready? Start with chunk 01 and work through to chunk 11. Good luck!
