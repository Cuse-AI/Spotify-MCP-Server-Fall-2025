#!/usr/bin/env python3
"""
Remove the Mario Judah song by Rherherherh from tapestry_quality_final.json
The song has no actual speech content and should be deleted.
"""

import json

def remove_mario_judah():
    """Remove the problematic Mario Judah song."""
    input_file = "tapestry_quality_final.json"

    print(f"Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Track if we found and removed it
    found = False
    removed_count = 0

    # Search through all vibes
    for vibe_name, vibe_data in data["vibes"].items():
        songs = vibe_data.get("songs", [])
        original_count = len(songs)

        # Filter out the Mario Judah song
        vibe_data["songs"] = [
            song for song in songs
            if not (song.get("artist") == "Rherherherh" and song.get("song") == "Mario Judah")
        ]

        new_count = len(vibe_data["songs"])
        if new_count < original_count:
            found = True
            removed = original_count - new_count
            removed_count += removed
            print(f"[OK] Removed {removed} song(s) from {vibe_name}")

    if not found:
        print("[ERROR] Mario Judah song not found in the tapestry")
        return

    # Save the cleaned version
    print(f"\nRemoving {removed_count} problematic song(s)...")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[DONE] Saved cleaned tapestry to {input_file}")

    # Count total songs
    total_songs = sum(len(v.get("songs", [])) for v in data["vibes"].values())
    print(f"\nTotal songs remaining: {total_songs}")

if __name__ == "__main__":
    remove_mario_judah()
