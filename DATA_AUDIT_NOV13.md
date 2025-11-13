# COMPLETE DATA AUDIT - November 13, 2025

## CURRENT STATE

**Tapestry:** 6,542 songs (up from stated 6,081 in DearClaude)
**Discrepancy:** +461 songs not accounted for

## FILE INVENTORY

Total JSON files in test_results: **109 files**

### Breakdown by Stage:

1. **RAW SCRAPES (29 files)**
   - Reddit: 12 files (angry, chill, dark, drive, excited, grateful, hopeful, jealous, night, party, romantic, sad)
   - YouTube: 17 files (anxious, bitter, bored, chaotic, chill, confident, dark, drive, energy, happy, introspective, night, nostalgic, party, peaceful, playful, romantic)

2. **DEDUPED (14 files)**
   - Reddit: 9 files (angry, dark, drive, excited, grateful, jealous, party, romantic, sad)
   - YouTube: 5 files (bitter, bored, chaotic, confident, playful)

3. **CLAUDE_MAPPED (31 files)** - ANALYZED & READY TO INJECT
   - Reddit: 14 files
   - YouTube: 17 files

4. **CLAUDE_AMBIGUOUS (31 files)** - Low confidence songs
   - Matching the 31 CLAUDE_MAPPED files (these are companion files)

5. **ANANKI_CHECKPOINTS (2 files)** - Partial analysis
   - dark_youtube_extraction_DEDUPED_ANANKI_CHECKPOINT.json
   - night_youtube_extraction_DEDUPED_ANANKI_CHECKPOINT.json

6. **UNKNOWN (2 files)** - Mystery files
   - happy_SAMPLE_10.json (8.9KB)
   - happy_feel_good_IMPROVED.json (672.4KB)

## TODAY'S SCRAPING (Nov 13, 2025)

**Raw scrapes:** 7 YouTube files
- chill, dark, drive, energy, happy, night, romantic

**After deduplication:** Only 113 NEW songs (not 1,132!)
- 1,350 duplicates already in tapestry
- Saved $4.06 in API costs

**Current status:** 7 DEDUPED files in `data/pending_analysis/`

## CRITICAL ISSUES IDENTIFIED

### Issue 1: Unclear Workflow
- Files scattered between `test_results` folders
- No clear indication of what's been injected vs pending
- Multiple duplicate analyses (some files analyzed twice with different DEDUPED versions)

### Issue 2: Missing Documentation
- 461 songs added to tapestry but no record of which files were injected
- DearClaude states 6,081 but actual is 6,542

### Issue 3: Orphaned/Duplicate Files
- 31 CLAUDE_MAPPED files exist but unclear which have been injected
- Some raw files have corresponding DEDUPED but no CLAUDE_MAPPED
- Some have CLAUDE_MAPPED but original raw file still exists

### Issue 4: Inconsistent Naming
- Some files: `checkpoint` (Reddit)
- Some files: `extraction` (YouTube)
- Some files: `smart_extraction` (Reddit)
- Makes it hard to track workflow stages

## PROPOSED REORGANIZATION

### New Folder Structure:
```
data/
├── 1_raw_scrapes/           # Fresh from scrapers
├── 2_deduped/               # After dedupe_before_ananki.py
├── 3_analyzed/              # After true_ananki_claude_api.py
│   ├── mapped/              # High confidence (CLAUDE_MAPPED)
│   └── ambiguous/           # Low confidence (CLAUDE_AMBIGUOUS)
├── 4_injected/              # After inject_to_tapestry.py
└── archive/                 # Old/completed batches
```

### Workflow:
1. **Scrape** → save to `1_raw_scrapes/`
2. **Dedupe** → move to `2_deduped/`
3. **Analyze** → move to `3_analyzed/mapped/` and `3_analyzed/ambiguous/`
4. **Inject** → move to `4_injected/`
5. **Archive** → periodically clean up to `archive/`

## IMMEDIATE ACTIONS NEEDED

1. ✅ Move today's 7 deduped files to pending_analysis (DONE)
2. ⏳ Determine which of 31 CLAUDE_MAPPED files are already injected
3. ⏳ Run Ananki ONLY on truly new files (today's 113 songs)
4. ⏳ Inject remaining CLAUDE_MAPPED files
5. ⏳ Reorganize all files into new structure
6. ⏳ Archive old/completed work
7. ⏳ Update documentation

## QUESTIONS FOR DIO

1. Do you want to inject the 31 existing CLAUDE_MAPPED files? (Could be hundreds more songs)
2. Should I delete the ANANKI_CHECKPOINT files (partial/incomplete analyses)?
3. What should I do with the 2 UNKNOWN files?
4. Should I archive all completed work to clean up test_results folders?
