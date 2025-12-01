#!/usr/bin/env python3
"""
Merge cleaned tapestry chunks back into a single tapestry_cleaned.json file.
Run this after Claude Desktop has cleaned all chunks.
"""

import json
from pathlib import Path

INPUT_DIR = "tapestry_chunks"
OUTPUT_FILE = "tapestry_cleaned.json"

def merge_chunks():
    """Merge all cleaned chunks into one file."""
    chunk_dir = Path(INPUT_DIR)

    # Find all chunk files
    chunk_files = sorted(chunk_dir.glob("tapestry_chunk_*.json"))

    if not chunk_files:
        print(f"ERROR: No chunk files found in {INPUT_DIR}/")
        return

    print(f"Found {len(chunk_files)} chunk files to merge\n")

    # Initialize merged data structure
    merged_data = {"vibes": {}}
    total_songs = 0

    # Process each chunk
    for chunk_file in chunk_files:
        print(f"Processing {chunk_file.name}...")

        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)

        chunk_songs = 0
        # Merge each vibe's songs
        for vibe_name, vibe_data in chunk_data["vibes"].items():
            if vibe_name not in merged_data["vibes"]:
                merged_data["vibes"][vibe_name] = {"songs": []}

            songs = vibe_data.get("songs", [])
            merged_data["vibes"][vibe_name]["songs"].extend(songs)
            chunk_songs += len(songs)

        total_songs += chunk_songs
        print(f"  -> Added {chunk_songs} songs")

    # Write merged file
    print(f"\nWriting merged data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print(f"\n[DONE] Merge complete!")
    print(f"Total songs in cleaned tapestry: {total_songs}")
    print(f"Output file: {OUTPUT_FILE}")

    # Show vibe breakdown
    print(f"\nVibe breakdown:")
    for vibe_name, vibe_data in sorted(merged_data["vibes"].items()):
        song_count = len(vibe_data["songs"])
        print(f"  {vibe_name}: {song_count} songs")

if __name__ == "__main__":
    merge_chunks()
