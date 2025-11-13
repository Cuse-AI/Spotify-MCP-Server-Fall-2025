# Reddit V5 Scraper - Implementation Plan

Based on V4 validation findings, here are the specific code changes needed for V5.

---

## Critical Findings Requiring V5

### Parsing Issues Detected

**Multi-artist parsing errors:** Songs being split across multiple artist fields
```
Example: "Karma Archie Shepp - Mama Too Tight Anthony Br..." +
         "In the Tradition Don Cherry - Symphony for Imp..."
```

This happens when comments list multiple songs in rapid succession without clear delimiters.

**Solution:** Implement smarter list detection and individual song separation.

---

## V5 Code Changes

### 1. Enhanced Search Queries (CRITICAL)

```python
self.search_queries = {
    # NEW: Complex emotions (addresses 0.5% -> 15% goal)
    'complex_emotions': [
        'sad but hopeful music',
        'melancholic but beautiful songs',
        'aggressive but uplifting',
        'dark but comforting',
        'happy but bittersweet music',
        'angry but groovy',
        'calm but intense',
        'peaceful but unsettling'
    ],

    # NEW: Contextual vibes (addresses 4.6% -> 30% goal)
    'contextual_vibes': [
        'music for rainy days',
        'music for late night studying',
        'best road trip songs',
        'music for walking alone',
        'morning coffee music',
        'cooking dinner music',
        'workout music not mainstream',
        'empty highway driving music'
    ],

    # EXISTING: Free jazz (working well - keep)
    'free_jazz': [
        'free jazz recommendations',
        'spiritual jazz',
        'avant-garde jazz',
        'Albert Ayler type music'
    ],

    # ENHANCED: Metal variety (20 pairs -> 200+ goal)
    'metal_variety': [
        'doom metal recommendations',
        'post-metal',
        'atmospheric black metal',
        'sludge metal',
        'drone metal',
        'funeral doom'
    ],

    # ... rest of existing queries
}

# NEW: Weighted query system for balancing
self.query_weights = {
    'complex_emotions': 25,      # High priority
    'contextual_vibes': 20,      # High priority
    'metal_variety': 30,         # Underrepresented
    'world_music': 25,           # Underrepresented
    'ambient': 20,               # Underrepresented
    'free_jazz': 10,             # Already well-covered
    'default': 10
}
```

### 2. Full Comment Extraction (CRITICAL)

```python
def search_diverse_queries(self, max_posts_per_query=10):
    """Enhanced to extract full comments without truncation"""

    for comment in post.comments.list()[:30]:
        if comment.score >= 1 and len(comment.body) > 20:
            extracted_songs = self.extract_songs_with_reasoning(comment.body)

            if extracted_songs:
                post_data['comments'].append({
                    'comment_id': comment.id,
                    'body': comment.body,  # CHANGED: NO TRUNCATION
                    'score': comment.score,
                    'extracted_songs': extracted_songs
                })
```

### 3. Improved Song Extraction with Reasoning

```python
def extract_songs_with_reasoning(self, text):
    """
    Enhanced extraction that preserves reasoning context
    Returns songs with surrounding explanatory text
    """
    songs = []
    text = text.replace('\n\n', ' | ').replace('\n', ' ')

    # Split text into potential song blocks (numbered lists, bullet points)
    blocks = self._split_into_song_blocks(text)

    for block in blocks:
        # Extract song from block
        song_data = self._extract_single_song(block)

        if song_data:
            # Extract reasoning from same block
            reasoning = self._extract_reasoning(block, song_data)

            song_data['reasoning'] = reasoning
            song_data['full_context'] = block[:500]  # Preserve surrounding text
            songs.append(song_data)

    return songs

def _split_into_song_blocks(self, text):
    """
    Split comment into individual song recommendation blocks
    Handles: numbered lists, bullet points, multiple lines
    """
    blocks = []

    # Try numbered list first: "1. Song - Artist\n2. Song - Artist"
    numbered = re.split(r'\n\s*\d+[\.\)]\s*', text)
    if len(numbered) > 2:
        return numbered[1:]  # Skip first empty element

    # Try bullet points: "* Song - Artist\n* Song - Artist"
    bulleted = re.split(r'\n\s*[\*\-•]\s*', text)
    if len(bulleted) > 2:
        return bulleted[1:]

    # Try paragraph breaks for prose recommendations
    paragraphs = re.split(r'\n\s*\n', text)
    if len(paragraphs) > 1:
        return paragraphs

    # Fall back to single block
    return [text]

def _extract_reasoning(self, block, song_data):
    """
    Extract WHY the song was recommended
    """
    reasoning_patterns = [
        r'because\s+(.{10,100})',
        r'similar to .{3,50} in that (.{10,100})',
        r'reminds me of (.{10,100})',
        r'has that (.{10,100})',
        r'captures? (?:the |a )?(.{10,100})',
        r"it'?s got (.{10,100})",
        r'gives? (?:me |you )?(.{10,100})',
        r'feels? like (.{10,100})'
    ]

    for pattern in reasoning_patterns:
        match = re.search(pattern, block, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # If no explicit reasoning, return first sentence after song mention
    song_name = song_data['song']
    song_pos = block.lower().find(song_name.lower())
    if song_pos != -1:
        after_song = block[song_pos + len(song_name):]
        first_sentence = re.split(r'[.!?]', after_song)[0]
        if 10 < len(first_sentence) < 200:
            return first_sentence.strip()

    return ""
```

### 4. Emotional Axis Tagging (MEDIUM PRIORITY)

```python
def tag_emotional_axes(self, vibe_text):
    """
    Auto-tag vibes with emotional dimensions for manifold training
    """
    axes = {
        'valence': 0.0,      # sad (-1) to happy (+1)
        'energy': 0.0,       # calm (-1) to energetic (+1)
        'complexity': 0.0,   # simple (-1) to complex (+1)
        'has_contrast': False  # "sad but hopeful" type
    }

    text_lower = vibe_text.lower()

    # Valence (sad/happy axis)
    sad_words = ['sad', 'melanchol', 'depress', 'grief', 'sorrow', 'lonely', 'blue']
    happy_words = ['happy', 'joyful', 'uplifting', 'cheerful', 'bright', 'optimistic']

    sad_count = sum(1 for word in sad_words if word in text_lower)
    happy_count = sum(1 for word in happy_words if word in text_lower)

    if sad_count > happy_count:
        axes['valence'] = -0.5 - (min(sad_count, 3) * 0.15)
    elif happy_count > sad_count:
        axes['valence'] = 0.5 + (min(happy_count, 3) * 0.15)

    # Energy
    calm_words = ['calm', 'peaceful', 'gentle', 'soft', 'quiet', 'meditat']
    energetic_words = ['energy', 'intense', 'aggressive', 'loud', 'pump', 'adrenaline']

    calm_count = sum(1 for word in calm_words if word in text_lower)
    energetic_count = sum(1 for word in energetic_words if word in text_lower)

    if calm_count > energetic_count:
        axes['energy'] = -0.5 - (min(calm_count, 3) * 0.15)
    elif energetic_count > calm_count:
        axes['energy'] = 0.5 + (min(energetic_count, 3) * 0.15)

    # Complexity
    complex_words = ['complex', 'experimental', 'progressive', 'avant', 'weird', 'strange']
    simple_words = ['simple', 'straightforward', 'minimal', 'basic']

    complex_count = sum(1 for word in complex_words if word in text_lower)
    simple_count = sum(1 for word in simple_words if word in text_lower)

    axes['complexity'] = (complex_count - simple_count) * 0.3

    # Detect emotional contrasts
    contrast_patterns = [
        r'(sad|dark|melanchol\w*|depress\w*)\s+but\s+(\w+)',
        r'(happy|joyful|bright)\s+but\s+(\w+)',
        r'(\w+)\s+but\s+(hopeful|uplifting|beautiful|comforting)'
    ]

    for pattern in contrast_patterns:
        if re.search(pattern, text_lower):
            axes['has_contrast'] = True
            break

    return axes
```

### 5. Enhanced Training Format

```python
def create_training_format(self, posts_data):
    """Enhanced CSV output with reasoning and emotional axes"""
    rows = []

    for post in posts_data:
        vibe_request = post['title']
        if post['selftext']:
            vibe_request += f" | {post['selftext']}"  # FULL selftext, not truncated

        # Tag emotional axes
        emotional_axes = self.tag_emotional_axes(vibe_request)

        for comment in post['comments']:
            for song_data in comment['extracted_songs']:
                row = {
                    'source': 'reddit_v5',
                    'genre_category': post['genre_category'],
                    'subreddit': post['subreddit'],
                    'vibe_request': vibe_request,
                    'song_name': song_data['song'],
                    'artist_name': song_data['artist'],
                    'extraction_confidence': song_data['confidence'],
                    'extraction_method': song_data['method'],
                    'comment_context': comment['body'],  # FULL comment
                    'reasoning': song_data.get('reasoning', ''),  # NEW
                    'full_context': song_data.get('full_context', ''),  # NEW
                    'comment_score': comment['score'],
                    'post_score': post['score'],
                    'search_query': post['search_query'],
                    'permalink': post['permalink'],
                    # NEW: Emotional axes
                    'valence': emotional_axes['valence'],
                    'energy': emotional_axes['energy'],
                    'complexity': emotional_axes['complexity'],
                    'has_contrast': emotional_axes['has_contrast']
                }
                rows.append(row)

    return pd.DataFrame(rows)
```

### 6. Subreddit Priority Weighting

```python
def search_diverse_queries(self, max_posts_per_query=10):
    """
    Search with subreddit prioritization for narrative quality
    """

    # Prioritize narrative-rich subreddits
    priority_subs = ['ifyoulikeblank', 'LetsTalkMusic']
    standard_subs = ['musicsuggestions', 'ListenToThis']
    genre_subs = ['jazz', 'experimentalmusic', 'Metal', 'hiphopheads']

    for genre, queries in self.search_queries.items():
        weight = self.query_weights.get(genre, 10)

        for query in queries:
            # Search priority subs first
            self._search_subreddit_group(
                query, priority_subs,
                limit=int(weight * 0.5)  # 50% from priority subs
            )

            # Then standard subs
            self._search_subreddit_group(
                query, standard_subs,
                limit=int(weight * 0.3)  # 30% from standard
            )

            # Finally genre-specific
            self._search_subreddit_group(
                query, genre_subs,
                limit=int(weight * 0.2)  # 20% from genre
            )
```

---

## Expected V5 Outcomes

### Quantitative Goals

| Metric | V4 Actual | V5 Target | Change |
|--------|-----------|-----------|--------|
| Total pairs | 1,978 | 4,000+ | 2x |
| Complex emotions | 0.5% | 15% | 30x |
| Reasoning capture | 1.3% | 40% | 30x |
| Context/setting | 4.6% | 30% | 6.5x |
| Genre balance ratio | 16.8:1 | 5:1 | 3x improvement |
| Manifold alignment | 22.8% | 50%+ | 2.2x |

### Qualitative Improvements

**Better data:**
- Full comment context (not truncated)
- Explicit reasoning for why songs fit vibes
- Multi-dimensional emotional language
- Balanced genre representation
- Contextual understanding (activity, setting, mood)

**Manifold training benefits:**
- Learn complex emotional geometry ("sad but hopeful")
- Understand context-dependent vibe shifts
- Capture reasoning chains for interpretability
- Better edge case coverage

---

## Implementation Checklist

### Phase 1: Core Enhancements (Do First)
- [ ] Add complex_emotions query category
- [ ] Add contextual_vibes query category
- [ ] Remove comment truncation (store full text)
- [ ] Implement _split_into_song_blocks()
- [ ] Implement _extract_reasoning()
- [ ] Update create_training_format() with new fields

### Phase 2: Quality Improvements
- [ ] Add emotional axis tagging (tag_emotional_axes())
- [ ] Implement subreddit priority weighting
- [ ] Add query weight system
- [ ] Enhance metal/world/ambient queries

### Phase 3: Polish
- [ ] Add checkpoint system (save every 50 posts)
- [ ] Implement fuzzy deduplication
- [ ] Add Spotify API genre validation (optional)
- [ ] Multi-pass extraction fallback

---

## Testing Strategy

### Before Full Run

1. **Test extraction on sample comments:**
   ```python
   test_comment = '''
   1. Miles Davis - Kind of Blue
   This album captures that melancholic but hopeful vibe you're looking for.

   2. John Coltrane - A Love Supreme
   Similar spiritual energy, perfect for late night reflection.
   '''

   result = scraper.extract_songs_with_reasoning(test_comment)
   # Should extract 2 songs with reasoning preserved
   ```

2. **Test emotional axis tagging:**
   ```python
   test_vibe = "sad but hopeful music for rainy day studying"
   axes = scraper.tag_emotional_axes(test_vibe)
   # Should show: valence < 0, has_contrast = True
   ```

3. **Run mini-scrape (5 posts per query):**
   ```python
   scraper = RedditVibeScraperV5()
   posts = scraper.search_diverse_queries(max_posts_per_query=5)
   # Review quality before full run
   ```

### Success Criteria

Before declaring V5 complete:
- [ ] At least 10% of vibe requests contain complex emotions
- [ ] At least 30% of comments have reasoning text
- [ ] Metal_variety has 100+ pairs (vs 20 in V4)
- [ ] Average comment context > 200 chars (vs 119 in V4)
- [ ] Manifold alignment score > 45%

---

## File Structure

```
data/reddit/
├── reddit_scraper.py              # V4 (current)
├── reddit_scraper_v5.py           # V5 (new)
├── reddit_v4_diverse_*.json       # V4 output
├── reddit_v4_training_*.csv       # V4 output
├── reddit_v5_diverse_*.json       # V5 output (future)
├── reddit_v5_training_*.csv       # V5 output (future)
├── validate_reddit_v4.py          # Validation script
├── REDDIT_V4_VALIDATION_REPORT.md # This report
└── V5_IMPLEMENTATION_PLAN.md      # This file
```

---

## Next Steps

1. **Review this plan** with the team
2. **Decide: Supplement or Rebuild?**
   - Option A: Run targeted V5 scrape for 1,500 additional pairs (faster)
   - Option B: Full V5 rebuild for 4,000+ pairs (better quality)
3. **Implement Phase 1 changes** (core enhancements)
4. **Test on 50 posts** before full scrape
5. **Run validation** on V5 output
6. **Merge V4 + V5** if using Option A
7. **Proceed to canonical track building**

---

## Questions for Team

1. **Priority**: Do we need V5 immediately, or can we start manifold training with V4 + manual supplementation?
2. **Scope**: Target 2,000 additional pairs (supplement) or 4,000+ total (rebuild)?
3. **Spotify API**: Should we add genre validation against Spotify during scraping?
4. **Timeline**: When do we need manifold-ready data by?

---

**Status:** Ready for implementation
**Estimated effort:** 4-6 hours for Phase 1, 2-3 hours for Phase 2
**Estimated scrape time:** 3-4 hours for 4,000 pairs (with rate limiting)
