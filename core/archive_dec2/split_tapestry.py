#!/usr/bin/env python3
"""
Split tapestry.json into ~500 song chunks for Claude Desktop cleaning.
Creates chunk files in core/tapestry_chunks/ directory.
"""

import json
import os
from pathlib import Path

SONGS_PER_CHUNK = 500
INPUT_FILE = "tapestry.json"
OUTPUT_DIR = "tapestry_chunks"

def count_total_songs(data):
    """Count total songs across all vibes."""
    total = 0
    for vibe_name, vibe_data in data["vibes"].items():
        total += len(vibe_data.get("songs", []))
    return total

def split_tapestry():
    """Split tapestry into chunks."""
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_songs = count_total_songs(data)
    print(f"Total songs: {total_songs}")

    num_chunks = (total_songs + SONGS_PER_CHUNK - 1) // SONGS_PER_CHUNK
    print(f"Will create {num_chunks} chunks of ~{SONGS_PER_CHUNK} songs each\n")

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    # Collect all songs with their vibe labels
    all_songs = []
    for vibe_name, vibe_data in data["vibes"].items():
        for song in vibe_data.get("songs", []):
            all_songs.append({
                "vibe": vibe_name,
                "song": song
            })

    # Split into chunks
    chunk_num = 1
    for i in range(0, len(all_songs), SONGS_PER_CHUNK):
        chunk_songs = all_songs[i:i + SONGS_PER_CHUNK]

        # Reconstruct the vibes structure for this chunk
        chunk_data = {"vibes": {}}
        for item in chunk_songs:
            vibe_name = item["vibe"]
            if vibe_name not in chunk_data["vibes"]:
                chunk_data["vibes"][vibe_name] = {"songs": []}
            chunk_data["vibes"][vibe_name]["songs"].append(item["song"])

        # Write chunk file
        chunk_filename = output_path / f"tapestry_chunk_{chunk_num:02d}_of_{num_chunks:02d}.json"
        with open(chunk_filename, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Created {chunk_filename.name} ({len(chunk_songs)} songs)")
        chunk_num += 1

    print(f"\n[DONE] Split complete! {num_chunks} chunk files created in {OUTPUT_DIR}/")
    print(f"\nNext steps:")
    print(f"1. Feed each chunk to Claude Desktop for cleaning")
    print(f"2. Claude Desktop will remove bad comments and return cleaned JSON")
    print(f"3. Save each cleaned chunk back to the same filename")
    print(f"4. Run merge script to combine all cleaned chunks")

if __name__ == "__main__":
    split_tapestry()
