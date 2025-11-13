# Legacy Code (Pre-Vibe System)

This folder contains code from the original keyword-based recommendation approach, before we pivoted to the vibe understanding system.

## What's Here

- **`artist-cocktail.json`** - Hardcoded mood → artist ID mappings (chill, workout, sad, etc.)
- **`recommend.ts`** - Old recommendation logic using simple keyword matching
- **`page.tsx`** - Original simple UI with single text input

## Why It's Outdated

The old approach used simple keyword matching:
- "chill" → play from specific artist list
- "workout" → play from workout artist list
- "sad" → play from sad artist list

This is exactly what we're moving AWAY from with the new vibe system.

## New Approach

The new vibe system:
1. Uses a fine-tuned Claude model to understand complex emotional descriptions
2. Asks 3 questions to capture the full emotional journey
3. Understands metaphors, contradictions, and cultural context
4. Finds deep cuts, not just popular tracks
5. Learns from real human vibe descriptions (Reddit, YouTube, Spotify data)

---

**Keep this folder as reference only. All new development happens in the main codebase.**
