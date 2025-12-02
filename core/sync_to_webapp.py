#!/usr/bin/env python3
"""
SYNC TO WEBAPP
==============
Copies core data files to the webapp folder so changes go live on deploy.

Files synced:
  - core/tapestry.json -> code/web/core/tapestry.json
  - data/manifold/emotional_manifold_COMPLETE.json -> code/web/data/emotional_manifold_COMPLETE.json

Run this after ANY changes to tapestry or manifold data!
"""

import shutil
import json
from pathlib import Path

# Get project root (where this script lives)
PROJECT_ROOT = Path(__file__).parent.parent

# Source files
TAPESTRY_SRC = PROJECT_ROOT / "core" / "tapestry.json"
MANIFOLD_SRC = PROJECT_ROOT / "data" / "manifold" / "emotional_manifold_COMPLETE.json"

# Destination (webapp)
WEBAPP_DIR = PROJECT_ROOT / "code" / "web"
TAPESTRY_DEST = WEBAPP_DIR / "core" / "tapestry.json"
MANIFOLD_DEST = WEBAPP_DIR / "data" / "emotional_manifold_COMPLETE.json"

def get_song_count(tapestry_path):
    """Get total songs from tapestry file"""
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return sum(len(v.get('songs', [])) for v in data.get('vibes', {}).values())

def get_vibe_count(tapestry_path):
    """Get total vibes from tapestry file"""
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return len(data.get('vibes', {}))

def sync_files():
    print("=" * 50)
    print("[SYNC] SYNCING DATA TO WEBAPP")
    print("=" * 50)
    
    synced = []
    
    # Sync tapestry
    if TAPESTRY_SRC.exists():
        src_songs = get_song_count(TAPESTRY_SRC)
        src_vibes = get_vibe_count(TAPESTRY_SRC)
        
        # Check if dest exists and compare
        if TAPESTRY_DEST.exists():
            dest_songs = get_song_count(TAPESTRY_DEST)
            if src_songs == dest_songs:
                print(f"[OK] tapestry.json already synced ({src_songs} songs)")
            else:
                shutil.copy2(TAPESTRY_SRC, TAPESTRY_DEST)
                print(f"[SYNCED] tapestry.json: {dest_songs} -> {src_songs} songs")
                synced.append("tapestry.json")
        else:
            TAPESTRY_DEST.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(TAPESTRY_SRC, TAPESTRY_DEST)
            print(f"[COPIED] tapestry.json ({src_songs} songs, {src_vibes} vibes)")
            synced.append("tapestry.json")
    else:
        print(f"[ERROR] Source not found: {TAPESTRY_SRC}")
    
    # Sync manifold
    if MANIFOLD_SRC.exists():
        if MANIFOLD_DEST.exists():
            # Compare file sizes as quick check
            if MANIFOLD_SRC.stat().st_size == MANIFOLD_DEST.stat().st_size:
                print(f"[OK] emotional_manifold_COMPLETE.json already synced")
            else:
                shutil.copy2(MANIFOLD_SRC, MANIFOLD_DEST)
                print(f"[SYNCED] emotional_manifold_COMPLETE.json")
                synced.append("manifold")
        else:
            MANIFOLD_DEST.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(MANIFOLD_SRC, MANIFOLD_DEST)
            print(f"[COPIED] emotional_manifold_COMPLETE.json")
            synced.append("manifold")
    else:
        print(f"[ERROR] Source not found: {MANIFOLD_SRC}")
    
    print("=" * 50)
    
    if synced:
        print(f"Synced {len(synced)} file(s). Don't forget to commit & push!")
    else:
        print("Everything already in sync!")
    
    # Show current stats
    if TAPESTRY_SRC.exists():
        songs = get_song_count(TAPESTRY_SRC)
        vibes = get_vibe_count(TAPESTRY_SRC)
        print(f"\n[STATS] Current: {songs} songs across {vibes} vibes")

if __name__ == "__main__":
    sync_files()
