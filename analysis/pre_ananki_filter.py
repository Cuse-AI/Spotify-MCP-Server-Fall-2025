# -*- coding: utf-8 -*-
"""
PRE-ANANKI QUALITY FILTER
=========================
Run this BEFORE sending scraped data to Claude for TRUE Ananki analysis.
This saves API credits by filtering out low-quality entries that won't produce
good emotional content anyway.

Usage:
    python analysis/pre_ananki_filter.py <input_file> [output_file]
    
Example:
    python analysis/pre_ananki_filter.py data/2_deduped/happy_deduped.json
    # Creates: data/2_deduped/happy_deduped_filtered.json
"""

import json
import os
import sys
from datetime import datetime

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Quality thresholds - SAME as scrub_quality.py for consistency
MIN_COMMENT_LENGTH = 30
MAX_LIST_SEPARATORS = 2

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
    separator_count = text.count(' - ')
    has_numbered_list = any(f'{i}.' in text or f'{i})' in text for i in range(1, 10))
    return separator_count > MAX_LIST_SEPARATORS or has_numbered_list

def is_generic_only(text):
    """Check if comment is only generic phrases"""
    if not text:
        return True
    text_lower = text.lower().strip()
    generic_phrases = [
        'great song', 'love this', 'amazing song', 'good song', 'nice song',
        'this song', 'best song', 'my favorite', 'so good', 'hits hard',
        'this hits', 'banger', 'absolute banger', 'fire', 'slaps',
    ]
    for phrase in generic_phrases:
        if text_lower == phrase or text_lower == phrase + '!' or text_lower == phrase + '.':
            return True
    if len(text_lower) < 50:
        generic_count = sum(1 for phrase in generic_phrases if phrase in text_lower)
        words = text_lower.split()
        if generic_count > 0 and len(words) < 8:
            return True
    return False

def passes_quality_check(entry):
    """
    Check if a scraped entry passes quality standards.
    Returns (passes, reason) - reason is None if passes, else string explaining failure.
    """
    # Try different field names for comment text
    comment = (entry.get('comment_text') or entry.get('comment') or 
               entry.get('human_comment') or entry.get('text') or 
               entry.get('full_context') or '')
    
    if not comment.strip():
        return False, 'no_comment'
    if has_url(comment):
        return False, 'has_url'
    if is_too_short(comment):
        return False, 'too_short'
    if is_list_format(comment):
        return False, 'list_format'
    if is_generic_only(comment):
        return False, 'generic_only'
    
    return True, None

def filter_file(input_path, output_path=None):
    """Filter a scraped JSON file, keeping only quality entries."""
    
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_filtered{ext}"
    
    print(f"Loading: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if isinstance(data, list):
        entries = data
        is_list = True
    elif isinstance(data, dict) and 'songs' in data:
        entries = data['songs']
        is_list = False
    elif isinstance(data, dict) and 'entries' in data:
        entries = data['entries']
        is_list = False
    else:
        print(f"Unknown JSON structure. Keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
        return
    
    total = len(entries)
    passed = []
    failed_reasons = {}
    
    for entry in entries:
        passes, reason = passes_quality_check(entry)
        if passes:
            passed.append(entry)
        else:
            failed_reasons[reason] = failed_reasons.get(reason, 0) + 1
    
    # Save filtered data
    if is_list:
        output_data = passed
    else:
        output_data = dict(data)
        if 'songs' in data:
            output_data['songs'] = passed
        elif 'entries' in data:
            output_data['entries'] = passed
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Report
    print(f"\n{'='*50}")
    print(f"PRE-ANANKI FILTER RESULTS")
    print(f"{'='*50}")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"\nTotal entries:  {total:,}")
    print(f"Passed filter:  {len(passed):,} ({len(passed)/total*100:.1f}%)")
    print(f"Filtered out:   {total - len(passed):,} ({(total - len(passed))/total*100:.1f}%)")
    
    if failed_reasons:
        print(f"\nFiltered reasons:")
        for reason, count in sorted(failed_reasons.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")
    
    print(f"\n✅ Ready for TRUE Ananki analysis!")
    print(f"   API calls saved: ~{total - len(passed):,}")
    
    return len(passed), total

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    filter_file(input_path, output_path)

if __name__ == '__main__':
    main()
