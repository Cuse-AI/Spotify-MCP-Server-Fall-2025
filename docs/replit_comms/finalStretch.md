# finalStretch - Replit Comms
## December 2, 2025 - Pre-Demo Sprint

---

## OVERVIEW

We're in the final stretch before the demo! This session focused on major infrastructure improvements:

1. **Manifold Redesign** - Meta-vibes now positioned with proper emotional adjacency
2. **Ananki V2 System** - Modular analysis with Haiku (cheap) and Sonnet (expensive) stages
3. **Emotional Pins** - Color gradient badges replace album art, based on manifold coordinates
4. **Data Quality Check** - Running relevancy filter on all 4,976 songs

---

## CRITICAL: Manifold Changed!

The meta-vibe positions have been completely redesigned for emotional logic:

```
NEW POSITIONS:
  Happy:    (500, 200)  <- TOP CENTER (brightest)
  Party:    (300, 250)
  Chill:    (700, 250)
  Energy:   (250, 450)
  Romantic: (750, 450)
  Sad:      (500, 600)
  Drive:    (200, 650)
  Dark:     (350, 800)
  Night:    (550, 850)  <- BOTTOM (darkest)
```

This means:
- Y-axis: LOW = Light/Happy, HIGH = Dark/Heavy
- X-axis: LOW = Intense, HIGH = Calm/Relaxed

All 106 sub-vibes have been recalculated based on these new positions.

---

## NEW: Ananki V2 Modules

Located in `/ananki/`:

### helper_relevancy.py (Haiku - cheap)
Filters comments for relevance. Scores 1-5:
- 5 = Perfect emotional match
- 4 = Strong emotional content
- 3 = Generally meaningful
- 2 = Weak but acceptable
- 1 = FAIL (remove from tapestry)

### helper_coordinates.py (Haiku - cheap)
Assigns x,y coordinates based on emotional analysis of comment.
Uses weighted average of meta-vibe positions.

### analyzer.py (Sonnet - expensive)
Full sub-vibe mapping with "why it fits" reasoning.
Only runs on songs that pass relevancy.

---

## NEW: Emotional Pin Component

`/code/web/client/src/components/emotional-pin.tsx`

- Displays color gradient based on song's x,y coordinates
- Colors blend based on proximity to meta-vibes
- Click to open in Spotify (no more preview API needed!)
- Much more on-brand than generic album art

---

## CURRENTLY RUNNING

Relevancy check on all 4,976 songs (~82% pass rate so far)

After completion:
1. Remove failed songs
2. Run coordinate helper for AI-analyzed positions
3. Sync to webapp
4. Deploy!

---

## FILES TO KNOW

```
/ananki/                           <- New analysis modules
/data/manifold/emotional_manifold_COMPLETE.json  <- Redesigned!
/core/tapestry.json                <- Main data
/core/sync_to_webapp.py            <- Syncs to all 3 webapp locations
/code/web/client/src/components/emotional-pin.tsx  <- New component
```

---

## WEBAPP SYNC LOCATIONS

The tapestry must exist in THREE places:
1. `/core/tapestry.json` (source of truth)
2. `/code/web/core/tapestry.json` (server)
3. `/code/web/client/public/core/tapestry.json` (frontend static)

Run `python core/sync_to_webapp.py` after any tapestry changes!

---

## META-VIBE COLORS (for reference)

```
Happy:    #FFD93D (bright yellow)
Party:    #E91E8C (magenta)
Chill:    #6DD5C3 (teal)
Energy:   #FF6B35 (orange-red)
Romantic: #FF85A2 (pink)
Sad:      #4A90D9 (blue)
Drive:    #F97316 (electric orange)
Dark:     #8B5CF6 (purple)
Night:    #2D3047 (deep indigo)
```

---

## DEMO PREP CHECKLIST

- [ ] Relevancy check complete
- [ ] Failed songs removed
- [ ] Coordinate helper run
- [ ] Sync to webapp
- [ ] Git commit & push
- [ ] Vercel deployment verified
- [ ] Test emotional pins display
- [ ] Test Spotify links work

---

Good luck with the demo! The system is way cleaner now. 🚀
