# SCRAPER IMPROVEMENTS NEEDED

**Problem:** Current scrapers have 45-50% validation failure rate due to parsing errors.

**Analysis:** Examined 970 low-confidence matches from strategic sampling across Happy, Energy, Party, and Anxious vibes.

---

## 🐛 BUGS IDENTIFIED IN CURRENT SCRAPERS

### Bug 1: ARTIST/SONG ORDER REVERSED (CRITICAL)
**Location:** All `batch_XX_*.py` files, line ~45

**Current Code:**
```python
p2 = r'([A-Z][A-Za-z\s&]{2,40}?)\s*-\s*([A-Z][^-\n]{3,50}?)(?:\s|,|\.|\n|$)'
for m in re.finditer(p2, text):
    if len(m.group(2)) < 50:
        songs.append((m.group(2).strip(), m.group(1).strip(), 'dash'))  # WRONG ORDER!
```

**Problem:** Pattern extracts "Artist - Song" but code saves it as "(Song, Artist)" - completely backwards!

**Examples of failures:**
- Scraped: "Bridge Otis Redding" - "Sitting"
- Should be: "Otis Redding" - "(Sittin' On) The Dock of the Bay"

**Fix:**
```python
songs.append((m.group(1).strip(), m.group(2).strip(), 'dash'))  # CORRECT: (Artist, Song)
```

---

### Bug 2: REGEX TOO GREEDY
**Current Pattern:**
```python
p2 = r'([A-Z][A-Za-z\s&]{2,40}?)\s*-\s*([A-Z][^-\n]{3,50}?)'
```

**Problems:**
- `[A-Za-z\s&]{2,40}?` captures TOO many words
- `[^-\n]{3,50}?` allows everything except dash - way too permissive
- Captures entire sentences instead of just artist/song names

**Examples:**
- "Transatlanticism" - "I smile back at her Death Cab For Cutie"
- "No Difference Gregory Alan Isakov" - "Where"

**Fix:** More conservative word limits:
```python
p2 = r'([A-Z][A-Za-z\s\-&\'\.]{1,35}?)\s*[-–—]\s*([A-Z][A-Za-z\s\-&\'\.!?]{2,50}?)'
```

---

### Bug 3: NO TEXT CLEANING
**Problem:** Newlines and extra spaces aren't removed during scraping

**Examples:**
- Artist: "Face  \nSaint Bernard"
- Artist: "Meola\n\nA Drop"

**Fix:** Add cleaning function:
```python
def clean_text(self, text):
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

---

### Bug 4: NO VALIDATION
**Problem:** No checks if extracted data looks reasonable

**Fix:** Add validation:
```python
def validate_song(self, song, artist):
    if not song or not artist:
        return False
    if len(song) < 2 or len(artist) < 2:
        return False
    if len(song) > 100 or len(artist) > 60:
        return False
    if artist.lower().split()[0] in ['the', 'a', 'an', 'my']:
        return False
    return True
```

---

### Bug 5: FIELD NAMES INCONSISTENT
**Current:** Sometimes `song_name`/`artist_name`, sometimes `song`/`artist`

**Fix:** Standardize to `song` and `artist` everywhere

---

## 📊 EXPECTED IMPROVEMENTS

**Current Validation Rates:**
- Happy: 48.6%
- Energy: 55.6%
- Party: 50.6%
- Anxious: 49.4%
- **Average: ~51%**

**Expected After Fixes:**
- Bug 1 fix alone: +15-20% (fixes reversed songs)
- Bug 2 fix: +5-10% (less garbage)
- Bug 3 fix: +5-8% (clean newlines)
- Bug 4 fix: +3-5% (filter bad matches)
- **Target: 70-80% validation rate**

---

## 🔧 HOW TO FIX

### Option A: Update Template (Recommended)
1. Use `IMPROVED_SCRAPER_TEMPLATE.py` as base
2. Create new batch files for problem vibes (Happy, Anxious, Party)
3. Re-scrape those categories
4. Validate new data - should see 70%+ success

### Option B: Fix Existing Files
1. Find/replace in all `batch_XX_*.py` files:
   - Line 45: Fix reversed append
   - Lines 39-45: Update regex patterns
   - Add `clean_text()` and `validate_song()` methods
2. Re-run affected batches

---

## 🎯 ACTION PLAN

1. **Test improved scraper** on 1 vibe category (e.g., Happy - Feel Good)
2. **Validate results** - should get 70%+ high confidence
3. **If successful:** Re-scrape all problem categories (Happy, Anxious, Party)
4. **Validate full tapestry** - should reach 70%+ overall
5. **Complete validation** of remaining 26K songs
6. **Move to Phase 2B:** Audio features enrichment

---

## 📝 NOTES

- The improved template includes confidence scoring for each extraction method
- Quotes + "by" = highest confidence (0.9)
- Artist - Song with validation = medium (0.7)
- Unquoted "by" = lower confidence (0.5)
- This helps identify which songs need extra validation later

**We can save the 50% data loss with these fixes!** 🎉
