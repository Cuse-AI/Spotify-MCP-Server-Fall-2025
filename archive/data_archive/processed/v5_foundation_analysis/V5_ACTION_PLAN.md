# V5 Scraper - Critical Action Plan
**Status:** DO NOT SCALE - EXTRACTION FIXES REQUIRED
**Priority:** HIGH - Blocks manifold training pipeline
**Timeline:** 2-3 days to production-ready data

---

## EXECUTIVE SUMMARY

The V5 test run validated the architectural approach but revealed **critical extraction failures** preventing capture of geometric relationship data. The scraper is finding excellent source material (79.8% proximity queries from high-quality posts) but only extracting 1-5% of the valuable semantic content due to overly rigid regex patterns.

**Bottom Line:** Fix extraction logic before ANY scaling. The data exists in Reddit posts - we're just not capturing it.

---

## CRITICAL ISSUES (Block Scaling)

### Issue 1: Delta Description Extraction - 95% Data Loss
**Current Performance:** 58.8% coverage, but captured data is meaningless fragments
**Example Output:** "preferably not | prefer", "you feel | even now | I feel"
**Should Capture:** "maintains emotional rawness but adds instrumental complexity"
**Root Cause:** Regex patterns too narrow - only match "but [adjective]" format
**Impact:** Cannot learn geometric transformations in vibe space

### Issue 2: Anchor Reference Extraction - 98.7% Miss Rate
**Current Performance:** 1.3% of records have anchor tracks (need >70%)
**Example Output:** "Fleetwood Mac is probably also fine..." (sentence fragment)
**Should Capture:** artist="Bon Iver", song="The Wolves (Act I and II)"
**Root Cause:** Looking for rigid "Artist - Song" format, missing natural language mentions
**Impact:** Cannot create "like X but Y" geometric constraints - core V5 mission fails

### Issue 3: Reasoning Text Extraction - 94.4% Miss Rate
**Current Performance:** 5.6% of records have reasoning (need >40%)
**Example Output:** Short fragments from narrow pattern matches
**Should Capture:** Full explanatory context from comments
**Root Cause:** Limited pattern matching instead of context extraction
**Impact:** Missing rich human explanation of vibe relationships

---

## IMMEDIATE FIX PLAN

### Step 1: Rewrite Extraction Functions (TODAY - 6-10 hours)

#### Fix Delta Description Extraction
**File:** `reddit_scraper_v5.py`, function `extract_delta_description()`

**Current (Broken):**
```python
patterns = [
    r'but\s+(more|less|very)?\s*([a-z]+)',  # Too rigid
]
```

**Required Changes:**
```python
# Extract full transformation clauses
patterns = [
    # Full clause after "but"
    r'but\s+([^.!?]{20,200})',

    # Intensity modifiers with context
    r'(?:more|less|very|extremely|slightly)\s+([a-z\s]{3,50})',

    # Maintained qualities
    r'(?:while|though|however)\s+(?:maintaining|keeping|staying)\s+([^.!?]{20,150})',

    # Transformation arcs
    r'starts?\s+([^,]{10,80}),?\s+(?:becomes?|turns?|evolves?)\s+([^.!?]{10,100})',

    # Comparative forms (existing pattern is OK, expand it)
    r'(?:darker|lighter|heavier|faster|slower|calmer|more intense|less aggressive)',
]

# Return semantic summary, not fragments
return extract_semantic_delta(all_matches)
```

#### Fix Anchor Reference Extraction
**File:** `reddit_scraper_v5.py`, function `extract_anchor_reference()`

**Current (Broken):**
```python
if " - " in text:
    parts = text.split(" - ")  # Misses 99% of references
```

**Required Changes:**
```python
# Multiple extraction strategies
patterns = [
    r'"([^"]+)"\s+by\s+([A-Z][a-z\s&]+)',    # "Song" by Artist
    r"'([^']+)'\s+by\s+([A-Z][a-z\s&]+)",    # 'Song' by Artist
    r'\[([^\]]+)\]\s+by\s+([A-Z][a-z\s&]+)', # [Song] by Artist
    r'([A-Z][a-z\s&]+)\s+-\s+([A-Z][^,\n.!?]{3,80})',  # Artist - Song
    r'([A-Z][a-z\s&]+)(?:\'s)?\s+([A-Z][^,\n.!?]{3,80})',  # Artist's Song
]

# Extract from post title AND body first paragraph
title_anchors = extract_anchors_from_text(post.title)
body_anchors = extract_anchors_from_text(post.selftext[:500])

# Validate against Spotify API (fuzzy match)
validated_anchors = validate_with_spotify(title_anchors + body_anchors)

return validated_anchors[0] if validated_anchors else (None, None)
```

#### Fix Reasoning Text Extraction
**File:** `reddit_scraper_v5.py`, function `extract_reasoning_text()`

**Current (Limited):**
```python
patterns = [
    r'because\s+([^.!?]{10,200})',  # Only catches explicit "because"
]
```

**Required Changes:**
```python
# Strategy: Extract full comment context, not just pattern matches

# 1. Get the full comment body
full_context = comment.body

# 2. Extract sentences with emotional/musical markers
emotional_markers = [
    'feel', 'emotion', 'touch', 'cry', 'love', 'vibe', 'mood',
    'atmosphere', 'energy', 'raw', 'beautiful', 'perfect', 'reminds'
]

reasoning_sentences = []
for sentence in split_sentences(full_context):
    if any(marker in sentence.lower() for marker in emotional_markers):
        reasoning_sentences.append(sentence)

# 3. Also capture explicit reasoning patterns
explicit_patterns = [
    r'because\s+([^.!?]{10,300})',
    r'(?:it|this|that)(?:\'s|\s+is)\s+([^.!?]{10,300})',
    r'(?:the way|how)\s+([^.!?]{10,300})',
    r'reminds me of\s+([^.!?]{10,300})',
    r'similar to\s+([^.!?]{10,300})',
    r'gives me\s+([^.!?]{10,300})',
]

# 4. Combine and return up to 2000 chars
all_reasoning = reasoning_sentences + explicit_pattern_matches
return ' | '.join(all_reasoning)[:2000]
```

### Step 2: Test Fixes on Current Data (2 hours)

**Run extraction fixes on existing 233 records:**
```bash
cd "c:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\reddit"
python reddit_scraper_v5.py --reprocess reddit_v5_training_20251107_164412.csv
```

**Validation Targets:**
- has_delta: >70% (from 58.8%)
- has_anchor: >70% (from 1.3%)
- has_reasoning: >40% (from 5.6%)
- manifold_readiness_score: >65 (from 49.3)

**Manual Review:**
- Sample 20 random records
- Verify delta_description contains semantic transformations
- Verify anchor_reference contains actual artist/song
- Verify reasoning_text contains explanatory context

**If validation fails:** Iterate on extraction patterns until targets met

### Step 3: Re-Run Test Scrape (1 hour)

**Same configuration as original test:**
```python
test_config = {
    'subreddits': ['ifyoulikeblank', 'musicsuggestions'],
    'posts_per_query': 20,
    'query_types': ['proximity', 'contextual', 'general'],
    'expected_records': ~250
}
```

**Success Criteria:**
- Manifold readiness: >65/100
- Sample manual review: 20 records show proper extraction
- No regression in relation_type classification (maintain 79.8% proximity)

### Step 4: Production V5 Run (4-6 hours)

**Once validation passes, scale vertically:**
```python
production_config = {
    'subreddits': [
        'ifyoulikeblank',       # Primary source
        'musicsuggestions',     # Secondary source
    ],

    'query_distribution': {
        'proximity': 60,        # Core geometric signal
        'contextual': 30,       # Situational embeddings
        'general': 5,           # Baseline comparisons
        'complex_emotion': 5,   # Experimental multi-axis
    },

    'posts_per_query': 50,      # 2x current
    'time_filter': 'year',      # Expand time window
    'min_comment_score': 2,     # Quality filter

    'expected_output': '2,500-3,000 records',
    'target_manifold_readiness': '65-70/100',
}
```

**Add Bridge Queries for V4 Overlap:**
```python
# Extract top 50 tracks from V4
v4_popular = get_top_tracks('reddit_v4_training_20251107_150221.csv', n=50)

# Create proximity queries using V4 anchors
bridge_queries = [
    f'songs like {track} but [transformation]'
    for track in v4_popular
]

# Target: 25-30% overlap between V4 and V5
```

---

## VALIDATION CHECKLIST

Before declaring V5 production-ready:

### Data Quality
- [ ] Manifold readiness score >65/100
- [ ] Delta descriptions: >70% coverage, semantic content
- [ ] Anchor references: >70% coverage, validated tracks
- [ ] Reasoning text: >40% coverage, explanatory context
- [ ] Relation types: >75% proximity/contextual

### Manual Review (20 sample records)
- [ ] Delta descriptions describe actual transformations
- [ ] Anchor references are real artist/song pairs
- [ ] Reasoning text explains vibe relationships
- [ ] No random word fragments or sentence pieces
- [ ] Extraction confidence scores are reasonable

### V4/V5 Integration
- [ ] 25-30% track overlap for manifold continuity
- [ ] Bridge queries tested and working
- [ ] Canonical track IDs validated against Spotify
- [ ] No duplicate records in merge

### Downstream Readiness
- [ ] Schema compliance: 100%
- [ ] All required fields populated: >95%
- [ ] Confidence scores calculated: 100%
- [ ] Source attribution preserved: 100%
- [ ] Ready for embedding training: YES

---

## TIMELINE & RESOURCES

### Day 1 (TODAY)
**Focus:** Fix extraction logic
- Morning: Rewrite extraction functions (4 hours)
- Afternoon: Test on current 233 records (2 hours)
- Evening: Manual validation review (2 hours)
- **Deliverable:** Working extraction functions

### Day 2 (TOMORROW)
**Focus:** Validate fixes and re-test
- Morning: Re-run V5 test scrape (1 hour)
- Afternoon: Analyze new results (2 hours)
- Evening: Decide: scale or iterate (1 hour)
- **Deliverable:** Go/No-Go decision for production run

### Day 3 (IF VALIDATION PASSES)
**Focus:** Production scaling
- Full day: Run production V5 scrape (4-6 hours)
- Evening: Quality analysis and reporting (2 hours)
- **Deliverable:** 2,500-3,000 production V5 records

### Day 4 (V4/V5 Merge)
**Focus:** Dataset unification
- Morning: Validate tracks against Spotify API (3 hours)
- Afternoon: Create canonical track objects (3 hours)
- Evening: Generate manifold readiness report (2 hours)
- **Deliverable:** MASTER_CLEAN_VIBES dataset

---

## SUCCESS METRICS

### Phase 1: Extraction Fixes (Day 1)
- ✅ has_delta: >70% (from 58.8%)
- ✅ has_anchor: >70% (from 1.3%)
- ✅ has_reasoning: >40% (from 5.6%)
- ✅ Manual review: 18/20 records pass quality check

### Phase 2: Re-Test Validation (Day 2)
- ✅ Manifold readiness: >65/100 (from 49.3)
- ✅ No regression in relation type classification
- ✅ Extraction patterns robust across different post styles

### Phase 3: Production Scaling (Day 3)
- ✅ 2,500-3,000 high-quality records
- ✅ Manifold readiness: 65-70/100
- ✅ 25-30% overlap with V4 for continuity
- ✅ Diverse anchor tracks (>500 unique)

### Phase 4: Dataset Merge (Day 4)
- ✅ All tracks validated against Spotify
- ✅ Canonical track objects created
- ✅ Confidence scores calculated
- ✅ MASTER_CLEAN_VIBES ready for embedding training

---

## RISK MITIGATION

### Risk 1: Extraction Fixes Don't Improve Metrics
**Probability:** Low (patterns are clearly broken, fixes are straightforward)
**Mitigation:** Iterative testing on small samples before full re-run
**Fallback:** Consider NLP/LLM-based extraction (GPT-4 or Claude for semantic understanding)

### Risk 2: Reddit API Rate Limiting During Production Run
**Probability:** Medium (scraping 2,500-3,000 records)
**Mitigation:** Implement exponential backoff, checkpoint progress
**Fallback:** Split production run across multiple days

### Risk 3: Low V4/V5 Overlap Creates Disconnected Manifold
**Probability:** Medium (current overlap only 8.6%)
**Mitigation:** Add bridge queries using V4 popular tracks as anchors
**Fallback:** Create synthetic "transition tracks" connecting regions

### Risk 4: Spotify API Validation Fails for Many Tracks
**Probability:** Medium (Reddit users may misspell or use alternate names)
**Mitigation:** Use fuzzy matching with configurable threshold
**Fallback:** Manual curation of high-value tracks, flag low-confidence matches

---

## COMMUNICATION PLAN

### Daily Standup Updates
**Report:**
- Extraction fixes completed
- Validation results
- Blockers encountered
- Next 24-hour plan

### Milestone Notifications
**Notify when:**
- Extraction fixes pass validation
- Production V5 run starts
- Production V5 run completes
- MASTER_CLEAN_VIBES dataset ready

### Issue Escalation
**Escalate if:**
- Extraction fixes don't improve metrics after 2 iterations
- Validation fails on re-test
- Production run hits critical errors
- Manifold readiness <60 after production run

---

## FILES & ARTIFACTS

### Input Files
- `reddit_scraper_v5.py` - Scraper needing extraction fixes
- `reddit_v5_training_20251107_164412.csv` - Test data for validation
- `reddit_v4_training_20251107_150221.csv` - V4 data for overlap analysis

### Output Files (After Fixes)
- `reddit_scraper_v5_FIXED.py` - Scraper with improved extraction
- `reddit_v5_test_reprocessed.csv` - Test data re-extracted with fixes
- `reddit_v5_production_YYYYMMDD.csv` - Production V5 dataset (2,500-3,000 records)
- `reddit_v5_production_metrics.json` - Quality metrics for production run

### Analysis Reports
- ✅ `V5_FOUNDATION_ANALYSIS.md` - Comprehensive foundation report
- ✅ `V5_EXTRACTION_EXAMPLES.md` - Concrete examples of extraction issues
- ✅ `V5_ACTION_PLAN.md` - This document

### Final Deliverable
- `MASTER_CLEAN_VIBES.csv` - Merged V4+V5 with canonical tracks
- `MANIFOLD_READINESS_REPORT.md` - Final assessment before embedding training

---

## KEY INSIGHTS

### What We Learned
1. **Architectural validation:** V5 concept is sound - proximity queries DO generate geometric data
2. **Source quality:** Reddit posts contain rich relational vibe descriptions
3. **Extraction challenge:** Human language requires semantic understanding, not rigid patterns
4. **Subreddit selection:** r/ifyoulikeblank and r/musicsuggestions are optimal sources
5. **Testing importance:** Should have validated extraction on 10 posts before running 233

### What Changes for Production
1. **Extraction logic:** Semantic/flexible patterns instead of rigid regex
2. **Validation rigor:** Test extraction on samples before full runs
3. **Overlap strategy:** Explicit bridge queries to connect V4 and V5
4. **Quality thresholds:** Stricter filtering based on extraction confidence

### What Stays the Same
1. **Query types:** Proximity and contextual are proven winners
2. **Subreddits:** Current selection is optimal
3. **Scraping approach:** PRAW-based scraping works well
4. **Data schema:** V5 schema is correct, just needs better population

---

## FINAL RECOMMENDATION

**DO NOT SCALE CURRENT V5 SCRAPER**

Fix extraction logic first. The foundation is excellent (79.8% proximity queries, high-quality posts, good subreddit selection), but extraction failures prevent capture of the geometric relationship data that makes V5 valuable.

**Estimated Timeline:** 2-3 days to production-ready V5 dataset
**Confidence:** HIGH - Issues are clear, fixes are straightforward
**Risk:** LOW - Testing plan ensures validation before scaling

**The data exists. We just need to extract it properly.**

---

**Ready to begin extraction fixes on your command.**

Generated: 2025-11-07
Agent: Tapestry Data Scraper
Status: AWAITING INSTRUCTIONS
