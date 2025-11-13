# V5 Extraction Issue Examples
**Concrete examples showing what SHOULD be extracted vs what IS being extracted**

---

## Example 1: Delta Description Failure

### Original Post (from dataset):
```
"[IIL] slow, despondent indie folk with only sparse guitar backing such as
'The Wolves (Act I and II)' by Bon Iver and 'Don't Wanna Go' by The Lumineers,
WEWIL?

Can include more instruments/increase in intensity LATER in the song like these
both do, but preferably not leave the realm of emotional rawness and low mood."
```

### What SHOULD Be Extracted:
```json
{
  "delta_description": "can include more instruments and intensity later, but maintains emotional rawness and low mood",
  "anchor_artist": "Bon Iver",
  "anchor_song": "The Wolves (Act I and II)",
  "reasoning_text": "slow, despondent indie folk with only sparse guitar backing, can increase in intensity later but preferably not leave emotional rawness"
}
```

### What WAS Extracted:
```json
{
  "delta_description": "preferably not | prefer",
  "anchor_artist": null,
  "anchor_song": null,
  "reasoning_text": null
}
```

**LOSS:** 95% of semantic content missing

---

## Example 2: Anchor Reference Failure

### Original Post:
```
"IIL Only in Dreams by Weezer, Forget Her by Jeff Buckley, Limousine by
Brand New, what else would i like?

Only in Dreams by Weezer: i love the slow buildup with the bassline..
To a perfect solo. The lyrics are also super fucking touching.

Forget Her by Jeff Buckley: His voice is one of the best i have ever heard,
the raw emotion is incredible, the lyrics are extremely relatable.

Limousine by Brand New: i love when bands move away from their respective
subgenres to create longer pieces of music that take you on a journey"
```

### What SHOULD Be Extracted:
```json
{
  "anchors": [
    {
      "artist": "Weezer",
      "song": "Only in Dreams",
      "description": "slow buildup with bassline to perfect solo, touching lyrics"
    },
    {
      "artist": "Jeff Buckley",
      "song": "Forget Her",
      "description": "incredible voice, raw emotion, extremely relatable lyrics"
    },
    {
      "artist": "Brand New",
      "song": "Limousine",
      "description": "moves away from subgenre, longer piece, takes you on journey"
    }
  ],
  "delta_description": "slow buildup, emotional journey, genre-transcending, raw emotion",
  "reasoning_text": "love the slow buildup with bassline to perfect solo, touching lyrics, incredible voice with raw emotion, bands that create longer pieces taking you on journey"
}
```

### What WAS Extracted:
```json
{
  "anchor_artist": null,
  "anchor_song": null,
  "delta_description": "it builds | what i | when it | at the",
  "reasoning_text": null
}
```

**LOSS:** 100% of anchor data, 90% of transformation data

---

## Example 3: Reasoning Text Failure

### Original Comment Context:
```
"Frightened Rabbit - Midnight Organ Fight

Scott sings, and there's some songs on it that still nearly 20 years later
make me feel things. It's quite silly in some ways but full of heart -
I've cried listening to it many times!"
```

### What SHOULD Be Extracted:
```json
{
  "reasoning_text": "Scott sings and songs still make me feel things nearly 20 years later, quite silly in some ways but full of heart, I've cried listening to it many times",
  "emotional_markers": ["make me feel things", "full of heart", "cried listening"],
  "temporal_context": "20 years later still emotional"
}
```

### What WAS Extracted:
```json
{
  "reasoning_text": "Scott sings, and there's some songs on it that still nearly 20 years later make me feel things..."
}
```

**LOSS:** Partial capture - truncated at arbitrary point, missing key context "full of heart" and "cried listening"

---

## Example 4: Complex Vibe Description (Gold Standard)

### Original Post:
```
"Great Ghosts by The Microphones - Down Colorful Hill ep

From Red House Painters album. This has sparse guitar, despondent vocals,
and slowly builds with additional instruments while maintaining the
emotional rawness. Perfect example of what I'm looking for - starts
minimal and sad, can become more complex sonically, but never loses
that feeling of being emotionally vulnerable and exposed."
```

### What SHOULD Be Extracted:
```json
{
  "song": "Great Ghosts",
  "artist": "The Microphones",
  "anchor_reference": {
    "artist": "Red House Painters",
    "album": "Down Colorful Hill"
  },
  "delta_description": "sparse guitar and despondent vocals that slowly build with additional instruments while maintaining emotional rawness, starts minimal and sad, becomes more complex sonically but never loses emotional vulnerability",
  "reasoning_text": "perfect example - starts minimal and sad, can become more complex sonically, but never loses that feeling of being emotionally vulnerable and exposed",
  "vibe_components": {
    "sonic": "sparse guitar, slowly builds, additional instruments, more complex",
    "emotional": "despondent, emotional rawness, vulnerable, exposed",
    "arc": "starts minimal, builds gradually, maintains core feeling"
  }
}
```

### What WAS Extracted:
```json
{
  "song": "Great Ghosts by The Microphones Down Colorful Hill ep",
  "artist": "Red House Painters",
  "delta_description": "preferably not | prefer",
  "reasoning_text": null,
  "anchor_reference_artist": null,
  "anchor_reference_song": null
}
```

**LOSS:** 90% of geometric relationship data, all vibe arc information

---

## Example 5: What Good Extraction Would Enable

### Properly Extracted V5 Record:
```json
{
  "track_id": "spotify:track:xyz123",
  "artist": "Frightened Rabbit",
  "title": "Midnight Organ Fight",
  "relation_type": "proximity",

  "anchor_track": {
    "track_id": "spotify:track:abc789",
    "artist": "Bon Iver",
    "title": "The Wolves (Act I and II)"
  },

  "delta_description": {
    "sonic": "more full band arrangement, faster tempo",
    "emotional": "maintains emotional rawness but adds urgency",
    "production": "less sparse, more layered instrumentation"
  },

  "reasoning_text": "Both have emotionally raw vocals and devastating lyrics, but Frightened Rabbit adds a full band dynamic that creates urgency while Bon Iver stays minimal and meditative",

  "vibe_vector_delta": [
    {"axis": "energy", "direction": "+0.3"},
    {"axis": "rawness", "direction": "0.0"},
    {"axis": "instrumentation", "direction": "+0.5"},
    {"axis": "tempo", "direction": "+0.2"}
  ],

  "confidence_score": 0.87,
  "extraction_method": "explicit",
  "source_vibe_text": "[full original post]"
}
```

### What This Enables for Manifold Training:
```python
# Geometric constraint loss
embedding(Frightened_Rabbit) ≈ embedding(Bon_Iver) + delta_vector

Where delta_vector represents:
- +energy
- +instrumentation
- +tempo
- =rawness (maintained)

This teaches the manifold:
"These tracks share emotional space but differ in sonic energy"
```

---

## The Core Problem Visualized

```
REDDIT POST (Rich Semantic Content)
        |
        | Current Extraction
        | (Rigid Regex Patterns)
        ↓
    FRAGMENTS ("preferably not | prefer")
        |
        | Manifold Training
        ↓
    GARBAGE (No geometric structure learned)


REDDIT POST (Rich Semantic Content)
        |
        | Fixed Extraction
        | (Semantic Understanding)
        ↓
    STRUCTURED DATA (Full transformations)
        |
        | Manifold Training
        ↓
    GEOMETRY (Learns vibe space structure)
```

---

## Summary: What Needs to Change

### Delta Description Extraction

**OLD (Broken):**
```python
patterns = [
    r'but\s+(more|less|very)?\s*([a-z]+)',  # Too narrow!
]
```

**NEW (Needed):**
```python
# Extract full clauses after transformation keywords
patterns = [
    r'but\s+([^.!?]{20,200})',  # Full clause after "but"
    r'(?:more|less|very|extremely|slightly)\s+([a-z\s]+)',  # Intensity modifiers
    r'(?:while|though|however)\s+(?:maintaining|keeping|staying|remaining)\s+([^.!?]{20,150})',  # Maintained qualities
    r'starts?\s+([^,]+),?\s+(?:becomes?|turns?|evolves?)\s+([^.!?]+)',  # Arcs
]
```

### Anchor Reference Extraction

**OLD (Broken):**
```python
# Looking for "Artist - Song" exactly
if " - " in text:
    parts = text.split(" - ")
```

**NEW (Needed):**
```python
# Flexible extraction from natural language
patterns = [
    r'"([^"]+)"\s+by\s+([A-Z][a-z\s]+)',  # "Song" by Artist
    r'([A-Z][a-z\s]+)\s+-\s+([^,\n]+)',  # Artist - Song
    r"'([^']+)'\s+by\s+([A-Z][a-z\s]+)",  # 'Song' by Artist
    r'\[([^\]]+)\]\s+by\s+([A-Z][a-z\s]+)',  # [Song] by Artist
    # + Spotify API validation for fuzzy matches
]
```

### Reasoning Text Extraction

**OLD (Limited):**
```python
patterns = [
    r'because\s+([^.!?]{10,200})',
    r'reminds me of\s+([^.!?]{10,200})',
]
```

**NEW (Needed):**
```python
# Capture full comment context, not just patterns
# Use comment_context field more aggressively
# Extract sentences containing emotional/musical descriptors
# Preserve paragraph structure instead of fragments

# Example approach:
full_context = comment.body
emotional_sentences = extract_sentences_with_markers(
    full_context,
    markers=['feel', 'emotion', 'touch', 'cry', 'love', 'vibe', 'mood', 'atmosphere']
)
```

---

**Key Insight:** We're not dealing with structured data - we're parsing human emotional expression. The extraction logic needs to be flexible and semantic, not rigid and syntactic.

---

Files referenced:
- c:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\reddit\reddit_v5_training_20251107_164412.csv
- c:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\reddit\reddit_scraper_v5.py
