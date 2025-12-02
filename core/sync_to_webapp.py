#!/usr/bin/env python3
"""
SYNC TO WEBAPP
==============
Copies core data files to the webapp folder so changes go live on deploy.

Files synced:
  - core/tapestry.json -> code/web/core/tapestry.json
  - core/tapestry.json -> code/web/client/public/core/tapestry.json (STATIC/FRONTEND)
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

# Destinations (webapp - multiple locations!)
WEBAPP_DIR = PROJECT_ROOT / "code" / "web"
TAPESTRY_DEST_SERVER = WEBAPP_DIR / "core" / "tapestry.json"
TAPESTRY_DEST_PUBLIC = WEBAPP_DIR / "client" / "public" / "core" / "tapestry.json"  # Frontend static!
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
    print("=" * 50)
    print("[SYNC] SYNCING DATA TO WEBAPP")
    print("=" * 50)
    
    synced = []
    src_songs = get_song_count(TAPESTRY_SRC) if TAPESTRY_SRC.exists() else 0
    src_vibes = get_vibe_count(TAPESTRY_SRC) if TAPESTRY_SRC.exists() else 0
    
    # Sync tapestry to SERVER location
    if sync_file(TAPESTRY_SRC, TAPESTRY_DEST_SERVER, "tapestry.json (server)"):
        synced.append("tapestry-server")
    
    # Sync tapestry to PUBLIC/STATIC location (for frontend stats bar!)
    if sync_file(TAPESTRY_SRC, TAPESTRY_DEST_PUBLIC, "tapestry.json (public/static)"):
        synced.append("tapestry-public")
    
    # Sync manifold
    if sync_file(MANIFOLD_SRC, MANIFOLD_DEST, "emotional_manifold_COMPLETE.json"):
        synced.append("manifold")
    
    print("=" * 50)
    
    if synced:
        print(f"Synced {len(synced)} file(s). Don't forget to commit & push!")
    else:
        print("Everything already in sync!")
    
    # Show current stats
    print(f"\n[STATS] Current: {src_songs} songs across {src_vibes} vibes")

if __name__ == "__main__":
    sync_files()
