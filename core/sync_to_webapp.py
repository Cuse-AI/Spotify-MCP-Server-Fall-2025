#!/usr/bin/env python3
"""
SYNC TO WEBAPP
==============
Copies core data files to ALL webapp locations so changes go live on deploy.

Files synced:
  - core/tapestry.json -> code/web/core/tapestry.json
  - core/tapestry.json -> code/web/server/tapestry.json
  - core/tapestry.json -> code/web/client/public/core/tapestry.json (FRONTEND STATS BAR)
  - core/tapestry.json -> code/web/public/static/tapestry.json
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

# Destinations (webapp - ALL locations that need tapestry!)
WEBAPP_DIR = PROJECT_ROOT / "code" / "web"
TAPESTRY_DESTINATIONS = [
    (WEBAPP_DIR / "core" / "tapestry.json", "tapestry.json (web/core)"),
    (WEBAPP_DIR / "server" / "tapestry.json", "tapestry.json (web/server)"),
    (WEBAPP_DIR / "client" / "public" / "core" / "tapestry.json", "tapestry.json (client/public/core - STATS BAR)"),
    (WEBAPP_DIR / "public" / "static" / "tapestry.json", "tapestry.json (public/static)"),
]
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

def sync_file(src, dest, name):
    """Sync a single file, return True if synced"""
    if not src.exists():
        print(f"[ERROR] Source not found: {src}")
        return False
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    if dest.exists():
        # Compare sizes as quick check
        if src.stat().st_size == dest.stat().st_size:
            print(f"[OK] {name} already synced")
            return False
    
    shutil.copy2(src, dest)
    print(f"[SYNCED] {name}")
    return True

def sync_files():
    print("=" * 60)
    print("[SYNC] SYNCING DATA TO WEBAPP (ALL LOCATIONS)")
    print("=" * 60)
    
    synced = []
    src_songs = get_song_count(TAPESTRY_SRC) if TAPESTRY_SRC.exists() else 0
    src_vibes = get_vibe_count(TAPESTRY_SRC) if TAPESTRY_SRC.exists() else 0
    
    # Sync tapestry to ALL destinations
    for dest_path, dest_name in TAPESTRY_DESTINATIONS:
        if sync_file(TAPESTRY_SRC, dest_path, dest_name):
            synced.append(dest_name)
    
    # Sync manifold
    if sync_file(MANIFOLD_SRC, MANIFOLD_DEST, "emotional_manifold_COMPLETE.json"):
        synced.append("manifold")
    
    print("=" * 60)
    
    if synced:
        print(f"Synced {len(synced)} file(s). Don't forget to commit & push!")
    else:
        print("Everything already in sync!")
    
    # Show current stats
    print(f"\n[STATS] Current: {src_songs} songs across {src_vibes} vibes")

if __name__ == "__main__":
    sync_files()
