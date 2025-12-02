"""
HAIKU QUALITY PASS
==================
Run Haiku sanity check over existing tapestry to find bad comments.
This is CHEAP and will flag songs that need removal.

Output:
- FLAGGED_FOR_REMOVAL.json - songs with bad comments
- QUALITY_VERIFIED.json - songs that passed
"""

import json
import os
import sys
import re
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

class HaikuQualityChecker:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found!")
        self.client = Anthropic(api_key=api_key)
        
    def check_comment(self, song_data):
        """
        Quick Haiku check:
        - Is comment about the song's emotional experience?
        - Does it have substance?
        """
        
        comment = song_data.get('comment_text', '')
        
        # Skip empty comments
        if not comment or len(comment.strip()) < 10:
            return {'pass': False, 'reason': 'Comment too short or empty'}
        
        prompt = f"""You are a quality filter for a music emotion app.

SONG: {song_data.get('artist', 'Unknown')} - {song_data.get('song', 'Unknown')}
COMMENT: "{comment[:500]}"

Does this comment show genuine EMOTIONAL CONNECTION to the song?

GOOD comments (PASS):
- Describe feelings or emotional reactions
- Share memories or experiences connected to the song  
- Explain when/why/how they listen to it emotionally
- Paint an emotional scene or mood

BAD comments (FAIL):
- Just state facts ("released in 2003", "went viral on TikTok")
- Generic praise ("great song!", "love this", "classic")
- Too short to convey emotion ("yes", "same", "mood")
- About popularity/fame not emotional impact
- Memes or jokes without emotional substance
- About the artist personally, not the music's emotional effect
- Just timestamps or technical comments

Respond ONLY with JSON:
{{"pass": true/false, "reason": "brief 5-10 word explanation"}}

Be STRICT - we only want emotionally meaningful comments."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=128,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                return {
                    'pass': result.get('pass', False),
                    'reason': result.get('reason', 'No reason')
                }
            else:
                return {'pass': True, 'reason': 'Could not parse, keeping by default'}
                
        except Exception as e:
            return {'pass': True, 'reason': f'API error, keeping: {str(e)[:50]}'}


def run_quality_pass(checkpoint_file=None):
    """
    Run Haiku quality check over entire tapestry
    """
    
    checker = HaikuQualityChecker()
    
    # Load tapestry
    project_root = Path(__file__).parent.parent.parent
    tapestry_path = project_root / "core" / "tapestry.json"
    
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        tapestry = json.load(f)
    
    # Flatten all songs
    all_songs = []
    for vibe_name, vibe_data in tapestry['vibes'].items():
        for song in vibe_data.get('songs', []):
            all_songs.append({
                **song,
                'current_vibe': vibe_name
            })
    
    print(f"[QUALITY PASS] Checking {len(all_songs)} songs with Haiku")
    
    # Setup output
    output_dir = project_root / "data" / "pipeline"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    flagged_file = output_dir / f"FLAGGED_FOR_REMOVAL_{timestamp}.json"
    verified_file = output_dir / f"QUALITY_VERIFIED_{timestamp}.json"
    checkpoint_path = output_dir / f"QUALITY_CHECKPOINT_{timestamp}.json"
    
    flagged = []
    verified = []
    start_index = 0
    
    # Resume from checkpoint if provided
    if checkpoint_file and Path(checkpoint_file).exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        flagged = checkpoint.get('flagged', [])
        verified = checkpoint.get('verified', [])
        start_index = checkpoint.get('processed', 0)
        print(f"[RESUME] Starting from song {start_index}")
    
    # Process songs
    for i in range(start_index, len(all_songs)):
        song = all_songs[i]
        
        # Progress
        if (i + 1) % 50 == 0:
            print(f"\n[PROGRESS] {i+1}/{len(all_songs)} ({len(flagged)} flagged so far)")
        
        result = checker.check_comment(song)
        
        if result['pass']:
            verified.append(song)
            # Minimal output for passes
            if (i + 1) % 100 == 0:
                print(f"  [{i+1}] PASS: {song.get('artist', '?')[:20]} - {song.get('song', '?')[:20]}")
        else:
            flagged.append({
                'song': song,
                'reason': result['reason']
            })
            # Always show flagged
            print(f"  [{i+1}] FLAG: {song.get('artist', '?')[:20]} - {song.get('song', '?')[:25]}")
            print(f"         Reason: {result['reason']}")
            print(f"         Comment: {song.get('comment_text', '')[:80]}...")
        
        # Checkpoint every 100 songs
        if (i + 1) % 100 == 0:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'flagged': flagged,
                    'verified': verified,
                    'processed': i + 1,
                    'total': len(all_songs)
                }, f, indent=2, ensure_ascii=False)
            print(f"  [CHECKPOINT] Saved at {i+1}/{len(all_songs)}")
    
    # Final save
    with open(flagged_file, 'w', encoding='utf-8') as f:
        json.dump({
            'songs': flagged,
            'count': len(flagged),
            'total_checked': len(all_songs)
        }, f, indent=2, ensure_ascii=False)
    
    with open(verified_file, 'w', encoding='utf-8') as f:
        json.dump({
            'songs': verified,
            'count': len(verified)
        }, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"[COMPLETE] Quality Pass Results")
    print(f"{'='*60}")
    print(f"Total checked: {len(all_songs)}")
    print(f"Verified (good): {len(verified)} ({100*len(verified)/len(all_songs):.1f}%)")
    print(f"Flagged (bad): {len(flagged)} ({100*len(flagged)/len(all_songs):.1f}%)")
    print(f"\nOutput files:")
    print(f"  Flagged: {flagged_file}")
    print(f"  Verified: {verified_file}")
    
    return flagged, verified


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Haiku quality check on tapestry")
    parser.add_argument("--resume", "-r", help="Resume from checkpoint file")
    
    args = parser.parse_args()
    
    run_quality_pass(args.resume)
