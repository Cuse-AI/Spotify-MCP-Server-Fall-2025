"""
Quick Lyrics Detector
=====================
Scans tapestry for comments that look like song lyrics.
Uses heuristics + optional Haiku verification.
"""

import json
import re
from pathlib import Path

def looks_like_lyrics(comment):
    """
    Heuristic detection of lyrics-only comments.
    Returns (is_lyrics, reason)
    """
    if not comment:
        return False, "empty"
    
    text = comment.strip()
    
    # Very long comments with repetitive patterns are often lyrics
    if len(text) > 400:
        # Check for repetitive phrases (chorus patterns)
        words = text.lower().split()
        if len(words) > 50:
            # Count repeated 3-word phrases
            phrases = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
            phrase_counts = {}
            for p in phrases:
                phrase_counts[p] = phrase_counts.get(p, 0) + 1
            repeated = sum(1 for c in phrase_counts.values() if c > 2)
            if repeated > 3:
                return True, f"repetitive phrases ({repeated} repeated 3+ times)"
    
    # Check for "ey oh" "la la" "na na" type patterns
    filler_patterns = [
        r'ey oh ey oh',
        r'la la la',
        r'na na na', 
        r'oh oh oh',
        r'yeah yeah',
        r'da da da',
        r'hey hey hey',
    ]
    for pattern in filler_patterns:
        if re.search(pattern, text.lower()):
            return True, f"song filler pattern: {pattern}"
    
    # Check for verse/chorus structure indicators
    structure_indicators = [
        r'\[verse\]',
        r'\[chorus\]',
        r'\[bridge\]',
        r'\[outro\]',
        r'\[intro\]',
    ]
    for pattern in structure_indicators:
        if re.search(pattern, text.lower()):
            return True, f"structure indicator: {pattern}"
    
    # Very short "emotional" content is fine, but long blocks without personal pronouns
    # talking about the commenter's experience are suspicious
    if len(text) > 300:
        personal_refs = len(re.findall(r'\b(i|me|my|we|our|myself)\b', text.lower()))
        # If long text but almost no first-person, might be lyrics
        if personal_refs < 2:
            # Check if it looks like prose vs song lyrics
            lines = text.split('\n')
            if len(lines) < 3:  # All on one line = probably pasted lyrics
                sentences = re.split(r'[.!?]', text)
                if len(sentences) > 8:  # Many comma-separated phrases
                    return True, "long text, no personal pronouns, run-on structure"
    
    # Check for quotation-heavy content (quoting entire lyrics)
    quote_chars = text.count('"') + text.count("'") + text.count('"') + text.count('"')
    if quote_chars > 10 and len(text) > 200:
        return True, "excessive quotation marks (likely quoting lyrics)"
    
    return False, "passed"


def scan_tapestry():
    """Scan current tapestry for lyrics-like comments."""
    
    project_root = Path(__file__).parent
    tapestry_path = project_root / "core" / "tapestry.json"
    
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    suspects = []
    total = 0
    
    for vibe_name, vibe_data in tapestry['vibes'].items():
        for song in vibe_data.get('songs', []):
            total += 1
            comment = song.get('comment_text', '')
            is_lyrics, reason = looks_like_lyrics(comment)
            
            if is_lyrics:
                suspects.append({
                    'vibe': vibe_name,
                    'artist': song.get('artist'),
                    'song': song.get('song'),
                    'reason': reason,
                    'comment_preview': comment[:150] + '...' if len(comment) > 150 else comment
                })
    
    print(f"\n{'='*60}")
    print(f"LYRICS SCAN RESULTS")
    print(f"{'='*60}")
    print(f"Total songs: {total}")
    print(f"Suspected lyrics: {len(suspects)}")
    print(f"{'='*60}\n")
    
    for i, s in enumerate(suspects, 1):
        print(f"{i}. {s['artist']} — {s['song']}")
        print(f"   Vibe: {s['vibe']}")
        print(f"   Reason: {s['reason']}")
        print(f"   Preview: {s['comment_preview'][:100]}...")
        print()
    
    return suspects


if __name__ == "__main__":
    suspects = scan_tapestry()
    
    if suspects:
        print(f"\nFound {len(suspects)} potential lyrics-only comments.")
        print("Review and remove manually if confirmed.")
    else:
        print("\nNo obvious lyrics-only comments found!")
