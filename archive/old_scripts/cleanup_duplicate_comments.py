# -*- coding: utf-8 -*-
"""
TAPESTRY DUPLICATE COMMENT CLEANUP
==================================
Nov 30, 2025

This script removes songs with duplicate/bad comments from tapestry.json

Types of duplicates to remove:
1. Playlist descriptions (contain "playlist", "subscribe", etc.)
2. Multi-song list comments (same comment on 3+ songs)
3. Generic spam comments

Strategy:
- If same comment appears on 3+ songs → REMOVE ALL (it's probably a playlist description)
- If same comment appears on 2 songs → KEEP the one with higher comment_score
- Use UnifiedQualityFilter to identify bad comments
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Add scrapers/shared to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scrapers' / 'shared'))
from unified_quality_filter import UnifiedQualityFilter

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TAPESTRY_PATH = Path(__file__).parent.parent / 'core' / 'tapestry.json'
BACKUP_PATH = Path(__file__).parent.parent / 'backups' / f'tapestry_pre_cleanup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

def load_tapestry():
    """Load tapestry.json"""
    with open(TAPESTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tapestry(data, path):
    """Save tapestry.json"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def analyze_duplicates(tapestry):
    """Find all duplicate comments and categorize them."""
    # Collect all songs with their vibe keys
    all_songs = []
    for vibe_name, vibe_data in tapestry['vibes'].items():
        for song in vibe_data.get('songs', []):
            all_songs.append({
                'vibe': vibe_name,
                'song': song
            })
    
    # Group by comment text
    comment_to_songs = defaultdict(list)
    for item in all_songs:
        comment = item['song'].get('comment_text', '').strip()
        if comment and len(comment) > 20:
            comment_to_songs[comment].append(item)
    
    return comment_to_songs, all_songs

def main():
    print("="*70)
    print("TAPESTRY DUPLICATE COMMENT CLEANUP")
    print("="*70)
    
    # Load tapestry
    print("\nLoading tapestry...")
    tapestry = load_tapestry()
    
    # Create backup FIRST
    print(f"Creating backup at: {BACKUP_PATH}")
    BACKUP_PATH.parent.mkdir(exist_ok=True)
    save_tapestry(tapestry, BACKUP_PATH)
    
    # Initialize quality filter
    quality_filter = UnifiedQualityFilter()
    
    # Analyze duplicates
    print("\nAnalyzing comments...")
    comment_to_songs, all_songs = analyze_duplicates(tapestry)
    
    original_count = len(all_songs)
    print(f"Total songs: {original_count}")
    print(f"Unique comments: {len(comment_to_songs)}")
    
    # Find problematic comments
    duplicates = {k: v for k, v in comment_to_songs.items() if len(v) > 1}
    print(f"Duplicate comment groups: {len(duplicates)}")
    
    # Track songs to remove
    songs_to_remove = set()  # (vibe, spotify_id) tuples
    removal_reasons = defaultdict(list)
    
    print("\n" + "="*70)
    print("PHASE 1: Remove songs with duplicate comments (3+ copies)")
    print("="*70)
    
    for comment, song_items in duplicates.items():
        if len(song_items) >= 3:
            # 3+ songs with same comment = definitely a playlist description
            # Remove ALL of them
            for item in song_items:
                key = (item['vibe'], item['song']['spotify_id'])
                songs_to_remove.add(key)
                removal_reasons['multi_duplicate'].append({
                    'artist': item['song']['artist'],
                    'song': item['song']['song'],
                    'comment_preview': comment[:60]
                })
    
    print(f"Songs flagged for multi-duplicate removal: {len([r for r in removal_reasons['multi_duplicate']])}")
    
    print("\n" + "="*70)
    print("PHASE 2: Remove songs with 2 copies (keep higher score)")
    print("="*70)
    
    for comment, song_items in duplicates.items():
        if len(song_items) == 2:
            # Keep the one with higher comment_score
            sorted_items = sorted(song_items, key=lambda x: x['song'].get('comment_score', 0), reverse=True)
            # Remove the lower-scored one
            loser = sorted_items[1]
            key = (loser['vibe'], loser['song']['spotify_id'])
            songs_to_remove.add(key)
            removal_reasons['duplicate_pair'].append({
                'artist': loser['song']['artist'],
                'song': loser['song']['song'],
                'kept': f"{sorted_items[0]['song']['artist']} - {sorted_items[0]['song']['song']}"
            })
    
    print(f"Songs flagged for duplicate-pair removal: {len([r for r in removal_reasons['duplicate_pair']])}")
    
    print("\n" + "="*70)
    print("PHASE 3: Quality filter check on remaining songs")
    print("="*70)
    
    # Check all songs with quality filter
    for item in all_songs:
        key = (item['vibe'], item['song']['spotify_id'])
        if key in songs_to_remove:
            continue  # Already flagged
        
        comment = item['song'].get('comment_text', '')
        if not comment:
            songs_to_remove.add(key)
            removal_reasons['no_comment'].append({
                'artist': item['song']['artist'],
                'song': item['song']['song']
            })
            continue
        
        # Determine source
        source_url = item['song'].get('source_url', '')
        source = 'youtube' if 'youtube' in source_url or 'youtu.be' in source_url else 'reddit'
        
        # Check quality
        passed, reason = quality_filter.check(comment, source=source)
        if not passed:
            songs_to_remove.add(key)
            removal_reasons[f'quality_{reason}'].append({
                'artist': item['song']['artist'],
                'song': item['song']['song'],
                'comment_preview': comment[:50]
            })
    
    print(f"Songs flagged by quality filter: {len(songs_to_remove) - len(removal_reasons['multi_duplicate']) - len(removal_reasons['duplicate_pair'])}")
    
    print("\n" + "="*70)
    print("REMOVAL SUMMARY")
    print("="*70)
    
    total_to_remove = len(songs_to_remove)
    print(f"\nTotal songs to remove: {total_to_remove}")
    print(f"Will remain: {original_count - total_to_remove}")
    print(f"\nBreakdown by reason:")
    for reason, items in sorted(removal_reasons.items(), key=lambda x: -len(x[1])):
        print(f"  {reason}: {len(items)}")
    
    # Show some examples
    print("\n" + "="*70)
    print("SAMPLE REMOVALS (first 10)")
    print("="*70)
    
    shown = 0
    for reason, items in removal_reasons.items():
        for item in items[:3]:
            if shown >= 10:
                break
            print(f"  [{reason}] {item['artist']} - {item['song']}")
            if 'comment_preview' in item:
                print(f"           Comment: \"{item['comment_preview']}...\"")
            shown += 1
        if shown >= 10:
            break
    
    # Ask for confirmation
    print("\n" + "="*70)
    response = input("Proceed with cleanup? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\nAborted. No changes made.")
        print(f"Backup saved at: {BACKUP_PATH}")
        return
    
    print("\n" + "="*70)
    print("EXECUTING CLEANUP")
    print("="*70)
    
    # Remove songs from tapestry
    removed_count = 0
    for vibe_name, vibe_data in tapestry['vibes'].items():
        original_songs = vibe_data.get('songs', [])
        filtered_songs = []
        
        for song in original_songs:
            key = (vibe_name, song['spotify_id'])
            if key not in songs_to_remove:
                filtered_songs.append(song)
            else:
                removed_count += 1
        
        vibe_data['songs'] = filtered_songs
    
    print(f"Removed {removed_count} songs")
    
    # Save cleaned tapestry
    print(f"\nSaving cleaned tapestry to: {TAPESTRY_PATH}")
    save_tapestry(tapestry, TAPESTRY_PATH)
    
    # Final stats
    final_count = sum(len(v.get('songs', [])) for v in tapestry['vibes'].values())
    
    print("\n" + "="*70)
    print("CLEANUP COMPLETE!")
    print("="*70)
    print(f"Original songs: {original_count}")
    print(f"Removed:        {removed_count}")
    print(f"Final count:    {final_count}")
    print(f"\nBackup saved at: {BACKUP_PATH}")
    print("="*70)


if __name__ == '__main__':
    main()
