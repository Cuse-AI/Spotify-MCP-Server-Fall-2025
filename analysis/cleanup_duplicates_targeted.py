# -*- coding: utf-8 -*-
"""
TAPESTRY DUPLICATE COMMENT CLEANUP - TARGETED VERSION
=====================================================
Nov 30, 2025

This script ONLY removes obvious duplicates, NOT quality filtering.
The songs already passed Ananki analysis - we just need to remove duplicates.

Targets:
1. Same comment on 3+ songs → REMOVE ALL (playlist descriptions)
2. Same comment on 2 songs → KEEP higher score
3. Obvious playlist description patterns (but only if clearly promotional)
"""

import json
import sys
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TAPESTRY_PATH = Path(__file__).parent.parent / 'core' / 'tapestry.json'
BACKUP_PATH = Path(__file__).parent.parent / 'backups' / f'tapestry_pre_cleanup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

# Obvious playlist description patterns
PLAYLIST_DESC_PATTERNS = [
    r'subscribe',
    r'new music every',
    r'best.*hits.*20\d\d',
    r'playlist.*20\d\d',
    r'turn on notifications',
    r'follow us',
    r'check out our',
    r'tracklist:',
    r'featuring:',
    r'all rights reserved',
    r'copyright',
]

def is_playlist_description(text):
    """Check if text is obviously a playlist description."""
    if not text:
        return False
    text_lower = text.lower()
    matches = sum(1 for p in PLAYLIST_DESC_PATTERNS if re.search(p, text_lower))
    return matches >= 2  # Need 2+ indicators

def load_tapestry():
    with open(TAPESTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tapestry(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("="*70)
    print("TAPESTRY DUPLICATE CLEANUP - TARGETED")
    print("="*70)
    print("This ONLY removes duplicates, not quality filtering.")
    print("="*70)
    
    # Load
    print("\nLoading tapestry...")
    tapestry = load_tapestry()
    
    # Backup
    print(f"Creating backup: {BACKUP_PATH.name}")
    BACKUP_PATH.parent.mkdir(exist_ok=True)
    save_tapestry(tapestry, BACKUP_PATH)
    
    # Collect all songs
    all_songs = []
    for vibe_name, vibe_data in tapestry['vibes'].items():
        for song in vibe_data.get('songs', []):
            all_songs.append({'vibe': vibe_name, 'song': song})
    
    original_count = len(all_songs)
    print(f"Total songs: {original_count}")
    
    # Group by comment
    comment_to_songs = defaultdict(list)
    for item in all_songs:
        comment = item['song'].get('comment_text', '').strip()
        if comment and len(comment) > 20:
            comment_to_songs[comment].append(item)
    
    duplicates = {k: v for k, v in comment_to_songs.items() if len(v) > 1}
    print(f"Duplicate comment groups: {len(duplicates)}")
    
    # Track removals
    songs_to_remove = set()
    removal_reasons = defaultdict(list)
    
    # PHASE 1: Multi-duplicates (3+ songs same comment)
    print("\n[Phase 1] Multi-duplicates (3+ songs)...")
    for comment, items in duplicates.items():
        if len(items) >= 3:
            for item in items:
                key = (item['vibe'], item['song']['spotify_id'])
                songs_to_remove.add(key)
                removal_reasons['multi_duplicate'].append(
                    f"{item['song']['artist']} - {item['song']['song']}"
                )
    print(f"  Flagged: {len(removal_reasons['multi_duplicate'])}")
    
    # PHASE 2: Duplicate pairs (keep higher score)
    print("\n[Phase 2] Duplicate pairs (keep higher score)...")
    for comment, items in duplicates.items():
        if len(items) == 2:
            sorted_items = sorted(items, key=lambda x: x['song'].get('comment_score', 0), reverse=True)
            loser = sorted_items[1]
            key = (loser['vibe'], loser['song']['spotify_id'])
            songs_to_remove.add(key)
            removal_reasons['duplicate_pair'].append(
                f"{loser['song']['artist']} - {loser['song']['song']}"
            )
    print(f"  Flagged: {len(removal_reasons['duplicate_pair'])}")
    
    # PHASE 3: Obvious playlist descriptions
    print("\n[Phase 3] Obvious playlist descriptions...")
    for item in all_songs:
        key = (item['vibe'], item['song']['spotify_id'])
        if key in songs_to_remove:
            continue
        comment = item['song'].get('comment_text', '')
        if is_playlist_description(comment):
            songs_to_remove.add(key)
            removal_reasons['playlist_desc'].append(
                f"{item['song']['artist']} - {item['song']['song']}"
            )
    print(f"  Flagged: {len(removal_reasons['playlist_desc'])}")
    
    # Summary
    total_to_remove = len(songs_to_remove)
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total to remove: {total_to_remove}")
    print(f"Will remain:     {original_count - total_to_remove}")
    print(f"\nBreakdown:")
    for reason, items in sorted(removal_reasons.items(), key=lambda x: -len(x[1])):
        print(f"  {reason}: {len(items)}")
    
    # Show worst offenders
    print("\n" + "="*70)
    print("WORST DUPLICATE OFFENDERS (by # of copies)")
    print("="*70)
    sorted_dups = sorted(duplicates.items(), key=lambda x: -len(x[1]))[:10]
    for comment, items in sorted_dups:
        print(f"\n{len(items)} copies: \"{comment[:80]}...\"")
        for item in items[:3]:
            print(f"  - {item['song']['artist']} - {item['song']['song']}")
        if len(items) > 3:
            print(f"  ... and {len(items)-3} more")
    
    # Confirmation
    print("\n" + "="*70)
    response = input("Proceed with cleanup? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\nAborted. No changes made.")
        return
    
    # Execute removal
    print("\nExecuting cleanup...")
    removed = 0
    for vibe_name, vibe_data in tapestry['vibes'].items():
        original_songs = vibe_data.get('songs', [])
        filtered = [s for s in original_songs if (vibe_name, s['spotify_id']) not in songs_to_remove]
        removed += len(original_songs) - len(filtered)
        vibe_data['songs'] = filtered
    
    # Save
    save_tapestry(tapestry, TAPESTRY_PATH)
    
    final_count = sum(len(v.get('songs', [])) for v in tapestry['vibes'].values())
    
    print("\n" + "="*70)
    print("CLEANUP COMPLETE!")
    print("="*70)
    print(f"Original: {original_count}")
    print(f"Removed:  {removed}")
    print(f"Final:    {final_count}")
    print(f"\nBackup at: {BACKUP_PATH}")

if __name__ == '__main__':
    main()
