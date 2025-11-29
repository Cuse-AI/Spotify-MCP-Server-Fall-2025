# Midden Data Flow - Simple & Clear

## THE SIMPLE RULE

```
┌─────────────────────────────────────────────────────────────────┐
│                        WHERE THINGS GO                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SCRAPER CODE      →  scrapers/                                │
│   SCRAPER OUTPUT    →  data/pipeline/1_raw/                     │
│   DEDUPED DATA      →  data/pipeline/2_deduped/                 │
│   ANALYZED DATA     →  data/pipeline/3_analyzed/                │
│   READY TO INJECT   →  data/pipeline/4_ready/                   │
│   THE DATABASE      →  core/tapestry.json                       │
│   OLD/BAD STUFF     →  data/archive/                            │
│   ANALYSIS SCRIPTS  →  analysis/                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## THE PIPELINE (Left to Right)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  SCRAPE  │───▶│  DEDUPE  │───▶│  VERIFY  │───▶│  ANANKI  │───▶│  INJECT  │
│          │    │          │    │  (HUMAN) │    │          │    │          │
│ 1_raw/   │    │ 2_deduped│    │   ✋     │    │3_analyzed│    │ 4_ready/ │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │                              │                               │
     │                              │                               │
     ▼                              ▼                               ▼
  Scraper                      Ask Claude                    core/tapestry.json
  runs here                    "Is this                      (THE database)
                               quality?"                     
                                   │
                                   │ If bad
                                   ▼
                              data/archive/
                              (graveyard)
```

## FILE NAMING

```
Good: happy_reddit_20251128.json
      └─vibe─┘ └source┘ └─date──┘

Pipeline stages add suffix:
  1_raw:      happy_reddit_20251128.json
  2_deduped:  happy_reddit_20251128_DEDUPED.json  
  3_analyzed: happy_reddit_20251128_ANALYZED.json
  4_ready:    happy_reddit_20251128_READY.json
```

## WHAT WAS WRONG BEFORE

```
❌ Scripts in data/ folder (confusing!)
❌ 3 different archive folders
❌ Empty pipeline folders while data lived elsewhere
❌ Files named "DEDUPED.json" in the "analyzed" folder
❌ No clear "this is ready to inject" stage
❌ No human checkpoint before expensive Ananki
```

## WHAT'S CLEAR NOW

```
✅ Code and data are SEPARATE
✅ ONE archive folder
✅ Pipeline folders match the actual steps
✅ Human checkpoint BEFORE spending API credits
✅ Clear naming shows what stage a file is in
✅ "4_ready" = human approved, safe to inject
```
