"""
HELPER: RELEVANCY CHECK
=======================
Uses Haiku to check if a comment is relevant to the song's vibe/subvibe.

Questions answered:
1. Is this comment about THIS song's emotional experience?
2. Does it relate to the sub-vibe (e.g., Dark-Gothic, Sad-Heartbreak)?
3. If not vibe-specific, is it still emotionally meaningful/funny/insightful?

Cost: ~$0.001 per song (Haiku is cheap!)
"""

import json
import os
import sys
import re
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

class RelevancyChecker:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found!")
        self.client = Anthropic(api_key=api_key)
    
    def check_relevancy(self, song_data):
        """
        Check if comment is relevant to the song and its vibe.
        
        Returns: {
            'pass': bool,
            'score': 1-5,
            'reason': str,
            'relevancy_type': 'vibe_specific' | 'generally_emotional' | 'funny_insightful' | 'irrelevant'
        }
        """
        
        comment = song_data.get('comment_text', '')
        artist = song_data.get('artist', 'Unknown')
        song = song_data.get('song', 'Unknown')
        subvibe = song_data.get('mapped_subvibe', song_data.get('current_vibe', 'Unknown'))
        
        # Extract meta-vibe (e.g., "Dark" from "Dark - Gothic")
        meta_vibe = subvibe.split(' - ')[0] if ' - ' in subvibe else subvibe
        
        if not comment or len(comment.strip()) < 5:
            return {
                'pass': False,
                'score': 0,
                'reason': 'Comment too short',
                'relevancy_type': 'irrelevant'
            }
        
        prompt = f"""You are evaluating comments for a music emotion app called Midden.

SONG: {artist} - {song}
SUB-VIBE: {subvibe}
META-VIBE: {meta_vibe}

COMMENT: "{comment[:600]}"

TASK: Rate this comment's relevancy for our emotional music database.

SCORING (1-5):
5 - PERFECT: Directly describes emotional experience matching the {subvibe} vibe
   Example for Dark-Gothic: "This song makes me feel like I'm in a haunted cathedral at midnight"
   
4 - STRONG: Emotional content that fits the {meta_vibe} mood, even if not specific to sub-vibe
   Example: "The darkness in this track speaks to my soul"
   
3 - GOOD: Generally emotional/meaningful comment about the song's impact
   Example: "I cry every time I hear this" (works for sad songs)
   
2 - WEAK: Mildly relevant OR funny/insightful but not emotional
   Example: Clever observation, memorable quote, or witty take
   
1 - FAIL: Not about emotional experience - facts, popularity, timestamps, generic praise
   Examples: "went viral on TikTok", "classic!", "2024 anyone?", "great song"

Respond ONLY with JSON:
{{
  "score": 1-5,
  "relevancy_type": "vibe_specific" | "generally_emotional" | "funny_insightful" | "irrelevant",
  "reason": "10-15 word explanation"
}}

Be STRICT but fair. We want quality emotional content, but a genuinely funny or insightful comment can pass with score 2."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                score = result.get('score', 1)
                return {
                    'pass': score >= 2,  # Score 2+ passes
                    'score': score,
                    'reason': result.get('reason', 'No reason'),
                    'relevancy_type': result.get('relevancy_type', 'unknown')
                }
            else:
                return {
                    'pass': True,
                    'score': 3,
                    'reason': 'Could not parse, keeping by default',
                    'relevancy_type': 'unknown'
                }
                
        except Exception as e:
            return {
                'pass': True,
                'score': 3,
                'reason': f'API error: {str(e)[:30]}',
                'relevancy_type': 'unknown'
            }


def run_relevancy_check(input_source='tapestry', checkpoint_file=None):
    """
    Run relevancy check on songs.
    
    Args:
        input_source: 'tapestry' to check existing tapestry, or path to JSON file
        checkpoint_file: Resume from checkpoint if provided
    """
    
    checker = RelevancyChecker()
    project_root = Path(__file__).parent.parent
    
    # Load songs
    if input_source == 'tapestry':
        tapestry_path = project_root / "core" / "tapestry.json"
        with open(tapestry_path, 'r', encoding='utf-8') as f:
            tapestry = json.load(f)
        
        all_songs = []
        for vibe_name, vibe_data in tapestry['vibes'].items():
            for song in vibe_data.get('songs', []):
                all_songs.append({**song, 'current_vibe': vibe_name})
    else:
        with open(input_source, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_songs = data.get('songs', data.get('mapped_songs', []))
    
    print(f"[RELEVANCY] Checking {len(all_songs)} songs")
    
    # Setup output
    output_dir = project_root / "ananki" / "output"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    passed_file = output_dir / f"RELEVANCY_PASSED_{timestamp}.json"
    failed_file = output_dir / f"RELEVANCY_FAILED_{timestamp}.json"
    checkpoint_path = output_dir / f"RELEVANCY_CHECKPOINT_{timestamp}.json"
    
    passed = []
    failed = []
    score_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    start_index = 0
    
    # Resume from checkpoint
    if checkpoint_file and Path(checkpoint_file).exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        passed = checkpoint.get('passed', [])
        failed = checkpoint.get('failed', [])
        start_index = checkpoint.get('processed', 0)
        print(f"[RESUME] Starting from song {start_index}")
    
    # Process
    for i in range(start_index, len(all_songs)):
        song = all_songs[i]
        
        result = checker.check_relevancy(song)
        score = result.get('score', 0)
        score_counts[score] = score_counts.get(score, 0) + 1
        
        if result['pass']:
            song['relevancy_score'] = score
            song['relevancy_type'] = result['relevancy_type']
            passed.append(song)
            
            if score >= 4:
                print(f"[{i+1}] GREAT ({score}): {song.get('artist', '?')[:15]} - {song.get('song', '?')[:20]}")
        else:
            failed.append({
                'song': song,
                'score': score,
                'reason': result['reason'],
                'relevancy_type': result['relevancy_type']
            })
            print(f"[{i+1}] FAIL ({score}): {song.get('artist', '?')[:15]} - {song.get('song', '?')[:20]}")
            print(f"        {result['reason']}")
        
        # Progress & checkpoint
        if (i + 1) % 50 == 0:
            print(f"\n[PROGRESS] {i+1}/{len(all_songs)} | Passed: {len(passed)} | Failed: {len(failed)}")
            print(f"  Scores: 5={score_counts[5]} 4={score_counts[4]} 3={score_counts[3]} 2={score_counts[2]} 1={score_counts[1]}")
            
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'passed': passed, 'failed': failed,
                    'processed': i + 1, 'total': len(all_songs),
                    'score_counts': score_counts
                }, f, ensure_ascii=False)
            print(f"  [CHECKPOINT SAVED]")
    
    # Final save
    with open(passed_file, 'w', encoding='utf-8') as f:
        json.dump({'songs': passed, 'count': len(passed), 'score_counts': score_counts}, f, indent=2, ensure_ascii=False)
    
    with open(failed_file, 'w', encoding='utf-8') as f:
        json.dump({'songs': failed, 'count': len(failed)}, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"[COMPLETE] Relevancy Check Results")
    print(f"{'='*60}")
    print(f"Total: {len(all_songs)} | Passed: {len(passed)} | Failed: {len(failed)}")
    print(f"\nScore Distribution:")
    print(f"  5 (Perfect):  {score_counts[5]}")
    print(f"  4 (Strong):   {score_counts[4]}")
    print(f"  3 (Good):     {score_counts[3]}")
    print(f"  2 (Weak):     {score_counts[2]}")
    print(f"  1 (Fail):     {score_counts[1]}")
    print(f"\nOutput: {passed_file.name}")
    
    return passed, failed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", default="tapestry", help="'tapestry' or path to JSON")
    parser.add_argument("--resume", "-r", help="Resume from checkpoint file")
    args = parser.parse_args()
    
    run_relevancy_check(args.input, args.resume)
