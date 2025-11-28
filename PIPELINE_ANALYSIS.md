# Data Pipeline Analysis & Injection Plan

## Current Status (Nov 27, 2025)

### ✅ What's IN the Tapestry
- **File:** `core/tapestry.json` (12.5 MB)
- **Last modified:** Nov 18, 2025
- **Contains:** High-quality songs with full TRUE Ananki reasoning

### ⏳ What's WAITING (Ready to Inject!)
- **Location:** `data/3_analyzed/mapped/` (16 files)
- **Content:** Fully analyzed, deduplicated songs with Claude reasoning
- **Status:** Ready to add to tapestry BUT NEVER INJECTED

Example files:
- `bitter_smart_extraction_DEDUPED_CLAUDE_MAPPED.json` (28/31 good songs)
- `bored_smart_extraction_DEDUPED_CLAUDE_MAPPED.json`
- `chaotic_smart_extraction_DEDUPED_CLAUDE_MAPPED.json`
- ... (13 more)

---

## Why the Automated Pipeline Failed (Analysis)

### Root Causes:

#### 1. **No Error Logging/Feedback Loop**
- Scripts run in background
- Errors silently fail or hang
- No real-time visibility into what's breaking
- You don't know if it's: stuck, crashed, out of credits, invalid JSON, etc.

#### 2. **API Credit Management**
- Anthropic credits ran out mid-pipeline
- Some files got analyzed → others hit "credit balance too low" error
- Example: `grateful_smart_extraction_DEDUPED_CLAUDE_MAPPED.json` shows:
  ```
  "ananki_reasoning": "API error: ... Your credit balance is too low"
  ```
- No graceful fallback or retry mechanism
- Pipeline just marks files as "ambiguous" and continues blindly

#### 3. **Missing Injection Trigger**
- Analyzed files sit in `data/3_analyzed/mapped/` forever
- No automatic trigger to inject into tapestry
- No monitoring to check if injection completed
- Pipeline assumes "analyzed = done" but never actually moves data

#### 4. **Asynchronous Complexity**
- Scrapers run (async)
- Deduplication runs (async)
- Ananki analysis runs (async, hits credits mid-batch)
- Injection supposed to run (but... doesn't?)
- Each stage has no dependency checking
- No checkpoints between stages

#### 5. **Process Visibility Issues**
- Long-running scripts with no progress indicators
- Can't tell if process is:
  - Still running (slow batch processing)
  - Hung (deadlock/infinite loop)
  - Failed (caught exception)
  - Out of resources (credits/memory/API quota)
- Timeout handling is non-existent

---

## What Should Have Happened vs What Did

### Ideal Flow:
```
Scrape → Dedupe → Analyze (Claude) → Inject → Verify
  ✓        ✓         ✓                ✗        ✗
```

### What Actually Happened:
```
Scrape → Dedupe → Analyze (Claude, hits credit error)
  ✓        ✓         ⚠️ PARTIAL SUCCESS (some files analyzed)
                   
Inject:  [NEVER RUNS - PIPELINE STALLS]
  ✗

Result: 16 analyzed files sit unused in `data/3_analyzed/mapped/`
        for weeks waiting to be added to tapestry
```

---

## Why It's "Tortuous"

1. **Silent Failures:** Scripts don't fail loudly, they just... don't complete
2. **No Checkpoints:** Can't resume mid-pipeline, have to restart from beginning
3. **Manual Inspection Required:** Only way to know what happened is manually checking directories
4. **Credit Surprises:** API limits hit without warning mid-process
5. **No Dependency Chain:** Each stage assumes previous stage worked (spoiler: it might not have)

---

## How to Fix Automation (For Future)

### Add These to Pipeline:

1. **Progress Logging** (Real-time feedback)
   ```python
   logger.info(f"Starting: {stage_name}")
   logger.info(f"Progress: {current}/{total}")
   logger.error(f"Failed: {reason}")
   ```

2. **API Credit Monitoring** (Before each expensive call)
   ```python
   if not check_credits():
       raise OutOfCreditsError("Cannot proceed - buy credits first")
   ```

3. **Dependency Checking** (Between stages)
   ```python
   if not files_exist(dedupe_output):
       raise MissingInputError("Deduplication didn't produce output")
   ```

4. **Health Checks** (Every stage)
   ```python
   assert len(output_files) > 0, "No output files produced"
   assert all(is_valid_json(f) for f in output_files)
   ```

5. **Injection Trigger** (Final stage)
   ```python
   for analyzed_file in data/3_analyzed/mapped/:
       inject_into_tapestry(analyzed_file)
       verify_injection()
   ```

6. **Checkpoint System** (Resume capability)
   ```python
   if checkpoint_exists(stage):
       resume_from_checkpoint(stage)
   else:
       run_stage(stage)
       save_checkpoint(stage)
   ```

---

## Current Blockers

### Blocker #1: No Injection Script
- Files are analyzed but never added to tapestry
- Solution: Create simple Python script to merge analyzed files into tapestry.json

### Blocker #2: API Credits Exhausted
- Can't analyze remaining deduplicated files
- Solution: User buys Anthropic credits (you mentioned you're out)

### Blocker #3: No Injection Verification
- We don't know if injection worked
- Solution: Add verification step (count songs before/after)

---

## Recommendation for Tapestry Update

**Next Steps (In Order):**

1. ✅ Create injection script for the 16 ready files
2. ✅ Verify data quality before injection
3. ✅ Run injection & verify counts
4. ⏭️ Buy Anthropic credits to analyze remaining deduplicated files
5. ⏭️ Then run NEXT pipeline cycle with better logging/monitoring

---

