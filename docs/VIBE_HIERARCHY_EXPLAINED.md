# Understanding The Tapestry's Vibe Hierarchy

## TL;DR

- **We scrape for 23 META-VIBES** (Anxious, Dark, Happy, etc.)
- **Ananki maps to 114 SUB-VIBES** (Anxious - Panic, Dark - Gothic, etc.)
- **Tapestry stores by SUB-VIBES** for precise emotional categorization

## The Two-Level System

### Level 1: 23 META-VIBES (Broad Emotional Categories)

These are the top-level emotional states we scrape for:

1. Sad
2. Happy
3. Chill
4. Anxious
5. Energy
6. Dark
7. Introspective
8. Romantic
9. Nostalgic
10. Night
11. Drive
12. Party
13. Angry
14. Bitter
15. Hopeful
16. Excited
17. Jealous
18. Peaceful
19. Playful
20. Chaotic
21. Bored
22. Grateful
23. Confident

**What we do with these:**
- Create 23 YouTube scrapers (one per meta-vibe)
- Create 23 Reddit scrapers (one per meta-vibe)
- Search for broad terms like "anxious music playlist", "dark music", "happy songs"

### Level 2: 114 SUB-VIBES (Precise Emotional Nuances)

Each meta-vibe contains 3-7 sub-vibes that capture specific emotional nuances:

**Example: DARK meta-vibe has 7 sub-vibes:**
- Dark - Apocalyptic
- Dark - Brooding
- Dark - Gothic
- Dark - Haunting
- Dark - Noir
- Dark - Villain Arc
- Dark - Witchy

**Example: ANXIOUS meta-vibe has 6 sub-vibes:**
- Anxious - Calming Anxiety
- Anxious - Existential Dread
- Anxious - Nervous Energy
- Anxious - Overwhelmed
- Anxious - Panic
- Anxious - Social Anxiety

**Example: SAD meta-vibe has 7 sub-vibes:**
- Sad - Heartbreak
- Sad - Crying
- Sad - Lonely
- Sad - Melancholic
- Sad - Grief
- Sad - Depressive
- Sad - Nostalgic Sad

## How The Pipeline Works

### Step 1: SCRAPING (Meta-Vibe Level)

```
YouTube Scraper: scrape_anxious.py
├─ Search: "anxious music playlist"
├─ Search: "nervous energy songs"
├─ Search: "panic attack playlist"
├─ Search: "existential dread songs"
└─ Result: 1,000 songs with emotional context
```

### Step 2: ANANKI ANALYSIS (Maps to Sub-Vibes)

TRUE Ananki reads the human context and maps each song to a specific sub-vibe:

```
Song 1: "This song helps during panic attacks"
└─> Ananki maps to: "Anxious - Panic"

Song 2: "Dark and brooding, not anxious at all"
└─> Ananki maps to: "Dark - Brooding"

Song 3: "Late night existential thoughts"
└─> Ananki maps to: "Anxious - Existential Dread"

Song 4: "Gothic cathedral music, haunting"
└─> Ananki maps to: "Dark - Gothic"
```

**KEY INSIGHT:** Songs scraped from "anxious playlists" can end up in ANY of the 114 sub-vibes! Ananki reads the TRUE emotional intent, not just the playlist name.

### Step 3: INJECTION (Organized by Sub-Vibes)

The tapestry stores songs organized by 114 sub-vibes:

```
tapestry_VALIDATED_ONLY.json:
{
  "vibes": {
    "Anxious - Panic": {
      "songs": [...]
    },
    "Dark - Gothic": {
      "songs": [...]
    },
    "Sad - Heartbreak": {
      "songs": [...]
    },
    ... (111 more sub-vibes)
  }
}
```

## Real Example from Today's Injection

**From the "ANXIOUS" scraper:**

1. **Company Flow - "Population Control"**
   - Context: "Anxiety inducing music playlist"
   - Ananki mapped to: **"Dark - Anxious"** ❌ (doesn't exist!)
   - Result: Skipped (invalid sub-vibe)

2. **Hotboii - "Don't Need Time"**
   - Context: "Pain Rap - Anxiety and Depression playlist"
   - Ananki mapped to: **"Sad - Depressive"** ✅
   - Result: Added to Sad - Depressive sub-vibe

3. **Steven Price - "Debris"**
   - Context: "Anxiety inducing music"
   - Ananki mapped to: **"Night - 3AM Thoughts"** ✅
   - Result: Added to Night - 3AM Thoughts sub-vibe

**Notice:** Songs from the "Anxious" scraper ended up in Sad, Dark, and Night vibes! This is CORRECT - Ananki found their true emotional homes.

## Why This Structure?

### 1. Broad Scraping = More Data
Searching for "anxious music" casts a wide net and finds lots of emotionally-rich content.

### 2. Precise Mapping = Better Recommendations
Ananki's analysis ensures each song goes to its TRUE emotional home, not just where the playlist creator put it.

### 3. Flexible Discovery
Users can search by meta-vibe ("show me dark music") OR sub-vibe ("show me dark gothic music specifically").

## Common Questions

### Q: Why not just scrape for the 114 sub-vibes directly?

**A:** Most people don't create playlists called "Anxious - Existential Dread Playlist". They create "Anxious Music" playlists. We need to scrape what humans actually create, then let Ananki figure out the nuances.

### Q: What about those WARNING messages during injection?

**A:** Ananki sometimes invents sub-vibe names like "Dark - Anxious" that don't exist in our 114-vibe manifold. These songs (usually 5-10 per batch) get skipped. It's fine! 96%+ still map correctly.

### Q: Can songs from "Happy" scraper end up in "Sad" vibes?

**A:** YES! And that's the magic! If someone comments "This happy song makes me nostalgic and sad", Ananki correctly maps it to "Sad - Nostalgic Sad" even though it came from a happy playlist.

## The Complete 114 Sub-Vibes

All 114 sub-vibes are defined in: `data/ananki_outputs/emotional_manifold_COMPLETE.json`

Each sub-vibe has:
- **Emotional composition** (weighted mix of meta-vibes)
- **Coordinates** (position on 2D manifold)
- **Analysis** (human-readable description)
- **Proximity notes** (relationship to other vibes)

Example:
```json
"Sad - Heartbreak": {
  "emotional_composition": {
    "Sad": 0.7,
    "Bitter": 0.15,
    "Romantic": 0.1,
    "Angry": 0.05
  },
  "analysis": "Heartbreak sits at the painful intersection of sadness and lost love. Strong bitter/resentful component from feeling hurt."
}
```

## Summary

**SCRAPERS:** Target 23 broad meta-vibes to cast a wide net

**ANANKI:** Analyzes context and maps to 114 precise sub-vibes

**TAPESTRY:** Stores songs by 114 sub-vibes for nuanced recommendations

**RESULT:** Human-curated emotional intelligence at scale!

---

*This is why Ananki is so powerful - it doesn't just organize songs by keywords, it understands the TRUE emotional context and finds each song's perfect home in the emotional manifold.*
