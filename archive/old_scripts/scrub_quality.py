# -*- coding: utf-8 -*-
"""
TAPESTRY DATA QUALITY SCRUBBER
==============================
Removes low-quality entries that don't meet human emotional content standards.

Quality criteria - a song FAILS if ANY of these are true:
1. Has URL in comment (http, spotify.com, youtube.com, etc.)
2. Comment is very short (<30 chars) - not enough emotional context
3. No comment at all
4. List format - just song names without emotional context (3+ " - " patterns)
5. Generic phrases only ("great song", "love this", etc.)

Bad data is ARCHIVED (not deleted) to data/archive/quality_scrub/
"""

import json
import os
import sys
from datetime import datetime
from collections import defaultdict

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Paths
TAPESTRY_PATH = 'core/tapestry.json'
ARCHIVE_DIR = 'data/archive/quality_scrub'
BACKUP_PATH = f'backups/tapestry_pre_scrub_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

# Quality thresholds
MIN_COMMENT_LENGTH = 30
MAX_LIST_SEPARATORS = 2  # More than this = probably just a song list

# Generic phrases that don't provide emotional context
GENERIC_PHRASES = [
    'great song', 'love this', 'amazing song', 'good song', 'nice song',
    'this song', 'best song', 'my favorite', 'so good', 'hits hard',
    'this hits', 'banger', 'absolute banger', 'fire', 'slaps',
]

def has_url(text):
    """Check if text contains URLs"""
    if not text:
        return False
    text_lower = text.lower()
    url_indicators = ['http://', 'https://', 'www.', 'spotify.com', 'youtube.com', 
                      'youtu.be', 'open.spotify', 'soundcloud.com', '.com/watch',
                      '.com/track', '.com/playlist']
    return any(ind in text_lower for ind in url_indicators)

def is_too_short(text):
    """Check if comment is too short for meaningful emotional context"""
    if not text:
        return True
    return len(text.strip()) < MIN_COMMENT_LENGTH

def is_list_format(text):
    """Check if text is just a list of songs without emotional context"""
    if not text:
        return False
    # Count " - " patterns (Artist - Song format)
    separator_count = text.count(' - ')
    # Also check for numbered lists
    has_numbered_list = any(f'{i}.' in text or f'{i})' in text for i in range(1, 10))
    return separator_count > MAX_LIST_SEPARATORS or has_numbered_list

def is_generic_only(text):
    """Check if comment is only generic phrases without real emotional content"""
    if not text:
        return True
    text_lower = text.lower().strip()
    # If the entire comment is just a generic phrase
    for phrase in GENERIC_PHRASES:
        if text_lower == phrase or text_lower == phrase + '!' or text_lower == phrase + '.':
            return True
    # If very short and contains only generic content
    if len(text_lower) < 50:
        generic_count = sum(1 for phrase in GENERIC_PHRASES if phrase in text_lower)
        words = text_lower.split()
        if generic_count > 0 and len(words) < 8:
            return True
    return False

def check_quality(song):
    """
    Check if a song meets quality standards.
    Returns (is_good, issues_list)
    """
    comment = song.get('comment_text', '') or song.get('human_comment', '') or ''
    full_context = song.get('full_context', '') or ''
    
    # Use comment_text preferentially, fall back to full_context
    text_to_check = comment if comment else full_context
    
    issues = []
    
    if has_url(text_to_check):
        issues.append('has_url')
    
    if is_too_short(text_to_check):
        issues.append('too_short')
    
    if is_list_format(text_to_check):
        issues.append('list_format')
    
    if is_generic_only(text_to_check):
        issues.append('generic_only')
    
    # Also check if there's NO text at all
    if not text_to_check.strip():
        issues.append('no_comment')
    
    return (len(issues) == 0, issues)

def main():
    print("=" * 60)
    print("TAPESTRY DATA QUALITY SCRUBBER")
    print("=" * 60)
    print(f"\nLoading tapestry from: {TAPESTRY_PATH}")
    
    # Load tapestry
    with open(TAPESTRY_PATH, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Create backup
    os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        json.dump(tapestry, f, indent=2, ensure_ascii=False)
    print(f"✅ Backup saved to: {BACKUP_PATH}")
    
    # Create archive directory
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Process each vibe
    stats = {
        'total_before': 0,
        'total_after': 0,
        'removed': 0,
        'issues': defaultdict(int),
        'by_vibe': {}
    }
    
    archived_songs = defaultdict(list)
    cleaned_tapestry = {'vibes': {}}
    
    for vibe_name, vibe_data in tapestry['vibes'].items():
        songs = vibe_data.get('songs', [])
        stats['total_before'] += len(songs)
        
        good_songs = []
        bad_songs = []
        
        for song in songs:
            is_good, issues = check_quality(song)
            
            if is_good:
                good_songs.append(song)
            else:
                # Track issues
                for issue in issues:
                    stats['issues'][issue] += 1
                # Archive bad song with its issues
                song['_quality_issues'] = issues
                bad_songs.append(song)
        
        # Save good songs to cleaned tapestry
        cleaned_tapestry['vibes'][vibe_name] = {'songs': good_songs}
        
        # Track bad songs for archive
        if bad_songs:
            archived_songs[vibe_name] = bad_songs
        
        # Stats per vibe
        stats['by_vibe'][vibe_name] = {
            'before': len(songs),
            'after': len(good_songs),
            'removed': len(bad_songs)
        }
        
        stats['total_after'] += len(good_songs)
        stats['removed'] += len(bad_songs)
    
    # Save cleaned tapestry
    with open(TAPESTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(cleaned_tapestry, f, indent=2, ensure_ascii=False)
    print(f"✅ Cleaned tapestry saved to: {TAPESTRY_PATH}")
    
    # Save archived bad data
    archive_file = os.path.join(ARCHIVE_DIR, f'removed_songs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    archive_data = {
        'archived_at': datetime.now().isoformat(),
        'reason': 'quality_scrub',
        'songs_by_vibe': dict(archived_songs),
        'total_archived': stats['removed']
    }
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(archive_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Archived {stats['removed']} songs to: {archive_file}")
    
    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nTotal songs BEFORE: {stats['total_before']:,}")
    print(f"Total songs AFTER:  {stats['total_after']:,}")
    print(f"Songs REMOVED:      {stats['removed']:,} ({stats['removed']/stats['total_before']*100:.1f}%)")
    print(f"Songs KEPT:         {stats['total_after']:,} ({stats['total_after']/stats['total_before']*100:.1f}%)")
    
    print("\n--- Issues Breakdown ---")
    for issue, count in sorted(stats['issues'].items(), key=lambda x: -x[1]):
        print(f"  {issue}: {count:,}")
    
    print("\n--- Top 10 Most Affected Vibes ---")
    sorted_vibes = sorted(stats['by_vibe'].items(), key=lambda x: -x[1]['removed'])
    for vibe, data in sorted_vibes[:10]:
        if data['removed'] > 0:
            print(f"  {vibe}: {data['before']} → {data['after']} (-{data['removed']})")
    
    print("\n" + "=" * 60)
    print("DONE! Your tapestry now contains ONLY quality human emotional content.")
    print("=" * 60)
    
    return stats

if __name__ == '__main__':
    main()
