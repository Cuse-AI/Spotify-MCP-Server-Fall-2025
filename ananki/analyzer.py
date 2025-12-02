"""
ANANKI CORE ANALYZER
====================
Full sub-vibe mapping + "why it fits" reasoning using Sonnet.

This is the EXPENSIVE step - only run on songs that passed relevancy check!

Outputs:
- mapped_subvibe: The sub-vibe this song belongs to
- ananki_reasoning: The "why it fits" explanation shown to users
- mapping_confidence: How confident we are (0.0-1.0)
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

class AnankiAnalyzer:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found!")
        self.client = Anthropic(api_key=api_key)
        
        # Load available sub-vibes
        project_root = Path(__file__).parent.parent
        tapestry_path = project_root / "core" / "tapestry.json"
        
        with open(tapestry_path, 'r', encoding='utf-8') as f:
            tapestry = json.load(f)
        
        self.available_subvibes = sorted(tapestry['vibes'].keys())
        print(f"[ANALYZER] Loaded {len(self.available_subvibes)} sub-vibes")
    
    def analyze(self, song_data):
        """
        Full Ananki analysis - map to sub-vibe and generate "why it fits".
        
        Returns: {
            'mapped_subvibe': str,
            'ananki_reasoning': str,  # The "why it fits" text
            'mapping_confidence': float
        }
        """
        
        comment = song_data.get('comment_text', '')
        artist = song_data.get('artist', 'Unknown')
        song_name = song_data.get('song', 'Unknown')
        post_title = song_data.get('post_title', '')
        
        subvibes_list = "\n".join([f"  - {sv}" for sv in self.available_subvibes])
        
        prompt = f"""You are Ananki, the emotional music analyst for Midden.

SONG: {artist} - {song_name}
POST CONTEXT: {post_title}
HUMAN COMMENT: "{comment[:600]}"

AVAILABLE SUB-VIBES:
{subvibes_list}

YOUR TASK:

1. Choose the ONE sub-vibe that best fits this song based on the human's emotional context.

2. Write a "Why it fits" explanation (1-2 sentences) that:
   - Connects the comment's emotional content to the vibe
   - Sounds natural and insightful, not robotic
   - Could be shown to users in the app
   
   GOOD examples:
   - "The haunting atmosphere described captures that 2am feeling of beautiful melancholy"
   - "This raw expression of heartbreak resonates with anyone who's loved and lost"
   
   BAD examples:
   - "The comment mentions sadness so this fits Sad vibe"
   - "User expressed emotional content relating to the Dark-Gothic category"

3. Rate your confidence (0.0-1.0)

Respond in JSON:
{{
  "sub_vibe": "Exact - Sub Vibe Name",
  "why_it_fits": "Natural 1-2 sentence explanation",
  "confidence": 0.85
}}

RULES:
- Sub-vibe MUST exactly match one from the list
- "why_it_fits" should feel human-written, not analytical
- Confidence: 0.9+ (perfect match), 0.7-0.8 (good), 0.5-0.6 (reasonable guess)"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250514",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                return {
                    'mapped_subvibe': result.get('sub_vibe', 'Unknown'),
                    'ananki_reasoning': result.get('why_it_fits', ''),
                    'mapping_confidence': result.get('confidence', 0.5)
                }
            else:
                return {
                    'mapped_subvibe': 'Unknown',
                    'ananki_reasoning': 'Could not analyze',
                    'mapping_confidence': 0.0
                }
                
        except Exception as e:
            return {
                'mapped_subvibe': 'Unknown',
                'ananki_reasoning': f'Analysis error: {str(e)[:50]}',
                'mapping_confidence': 0.0
            }


def run_analysis(input_file, output_file=None, checkpoint_file=None):
    """
    Run full Ananki analysis on songs.
    
    Args:
        input_file: JSON file with songs (should have passed relevancy check)
        output_file: Where to save results
        checkpoint_file: Resume from checkpoint
    """
    
    analyzer = AnankiAnalyzer()
    project_root = Path(__file__).parent.parent
    
    # Load songs
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_songs = data.get('songs', [])
    print(f"\n[ANALYZER] Processing {len(all_songs)} songs with Sonnet")
    print("[WARNING] This uses Sonnet - more expensive! ~$0.01/song")
    
    # Output setup
    output_dir = project_root / "ananki" / "output"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not output_file:
        output_file = output_dir / f"ANALYZED_{timestamp}.json"
    
    checkpoint_path = output_dir / f"ANALYSIS_CHECKPOINT_{timestamp}.json"
    
    analyzed = []
    failed = []
    start_index = 0
    
    # Resume from checkpoint
    if checkpoint_file and Path(checkpoint_file).exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        analyzed = checkpoint.get('analyzed', [])
        failed = checkpoint.get('failed', [])
        start_index = checkpoint.get('index', 0)
        print(f"[RESUME] Starting from song {start_index}")
    
    # Process
    for i in range(start_index, len(all_songs)):
        song = all_songs[i]
        
        result = analyzer.analyze(song)
        
        if result['mapping_confidence'] > 0:
            song.update(result)
            analyzed.append(song)
            print(f"[{i+1}] {song.get('artist', '?')[:15]} -> {result['mapped_subvibe']}")
        else:
            failed.append({'song': song, 'error': result['ananki_reasoning']})
            print(f"[{i+1}] FAILED: {song.get('artist', '?')[:15]}")
        
        # Checkpoint every 25 (Sonnet is expensive, save often)
        if (i + 1) % 25 == 0:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'analyzed': analyzed, 'failed': failed,
                    'index': i + 1, 'total': len(all_songs)
                }, f, ensure_ascii=False)
            print(f"  [CHECKPOINT] {i+1}/{len(all_songs)}")
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'songs': analyzed,
            'count': len(analyzed),
            'failed_count': len(failed)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n[COMPLETE] Analyzed: {len(analyzed)} | Failed: {len(failed)}")
    print(f"[SAVED] {output_file}")
    
    return analyzed, failed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input JSON file with songs")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--resume", "-r", help="Resume from checkpoint")
    args = parser.parse_args()
    
    run_analysis(args.input, args.output, args.resume)
