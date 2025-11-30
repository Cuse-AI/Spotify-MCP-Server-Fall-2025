import json
import random
import sys

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\core\tapestry.json', 'r', encoding='utf-8') as f:
    tapestry = json.load(f)

all_songs = [s for v in tapestry['vibes'].values() for s in v.get('songs', [])]

print("="*80)
print("QUALITY REPORT: 15 RANDOM SONGS WITH HUMAN QUOTES")
print("="*80)

sample = random.sample(all_songs, 15)

good_quotes = 0
for i, s in enumerate(sample, 1):
    print(f"\n{'='*60}")
    print(f"#{i}: {s.get('artist')} - {s.get('song')}")
    print(f"Subvibe: {s.get('mapped_subvibe')} | Confidence: {s.get('mapping_confidence', 0)*100:.0f}%")
    print("-"*60)
    
    comment = s.get('comment_text', '')
    if comment:
        # Clean and truncate for display
        comment_clean = comment.encode('ascii', 'replace').decode('ascii')
        display = comment_clean[:250] + ('...' if len(comment) > 250 else '')
        print(f"REDDIT QUOTE:\n\"{display}\"")
        if len(comment) > 30 and not comment.startswith('http'):
            good_quotes += 1
    else:
        print("REDDIT QUOTE: [NONE]")
    
    reasoning = s.get('ananki_reasoning', '')
    if reasoning:
        reasoning_clean = reasoning.encode('ascii', 'replace').decode('ascii')
        display = reasoning_clean[:200] + ('...' if len(reasoning) > 200 else '')
        print(f"\nANANKI REASONING:\n{display}")

print("\n" + "="*80)
print(f"QUALITY SCORE: {good_quotes}/15 songs have good displayable quotes ({100*good_quotes/15:.0f}%)")
print("="*80)

# Overall stats
has_comment = sum(1 for s in all_songs if s.get('comment_text') and len(s.get('comment_text', '')) > 30)
has_reasoning = sum(1 for s in all_songs if s.get('ananki_reasoning'))

print(f"\nOVERALL DATABASE:")
print(f"  Songs with quality comments (>30 chars): {has_comment}/{len(all_songs)} ({100*has_comment/len(all_songs):.1f}%)")
print(f"  Songs with ananki_reasoning: {has_reasoning}/{len(all_songs)} ({100*has_reasoning/len(all_songs):.1f}%)")
