"""
TRUE ANANKI - Claude API Analysis
Uses actual Claude reasoning to map songs to sub-vibes
NO KEYWORD MATCHING - Real human-level understanding
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load .env from the reddit directory (where API keys are stored)
env_path = Path(__file__).parent.parent / 'reddit' / '.env'
load_dotenv(dotenv_path=env_path)

class TrueAnankiClaudeAPI:
    def __init__(self):
        # Initialize Claude API
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment!")

        self.client = Anthropic(api_key=api_key)

        # Load tapestry to get all available sub-vibes
        tapestry_path = Path(__file__).parent.parent.parent / 'core' / 'tapestry.json'
        with open(tapestry_path, 'r', encoding='utf-8') as f:
            tapestry = json.load(f)

        self.available_subvibes = list(tapestry['vibes'].keys())
        print(f"Loaded {len(self.available_subvibes)} sub-vibes from tapestry")

    def analyze_song_placement(self, song_data):
        """
        Use Claude to analyze WHERE this song belongs
        Like a real human would!
        """

        # Build complete list of available sub-vibes
        subvibes_formatted = "\n".join([f"  - {sv}" for sv in sorted(self.available_subvibes)])

        # Build the prompt for Claude
        prompt = f"""You are Ananki, a human-in-the-loop AI that reads human emotional expressions about music and maps songs to specific emotional sub-vibes.

A human on Reddit/YouTube recommended this song with the following context:

POST TITLE: {song_data.get('post_title', 'N/A')}

COMMENT TEXT: {song_data.get('comment_text', 'N/A')[:500]}

SONG VALIDATED BY SPOTIFY:
- Artist: {song_data['artist']}
- Song: {song_data['song']}
- Spotify ID: {song_data['spotify_id']}

AVAILABLE SUB-VIBES (you MUST choose from this exact list):
{subvibes_formatted}

CRITICAL RULES:
1. You MUST select EXACTLY one sub-vibe from the list above
2. DO NOT create new sub-vibe names or variations
3. Copy the sub-vibe name EXACTLY as shown (including capitalization and hyphens)
4. If the context is NOT about music or is ambiguous/off-topic, use "AMBIGUOUS"

YOUR TASK:
1. Read the human's emotional context carefully
2. Determine which ONE sub-vibe from the list best fits this song's emotional intent
3. Provide clear reasoning for your choice

Respond in JSON format:
{{"sub_vibe": "Exact - Sub Vibe Name", "reasoning": "Clear explanation", "confidence": 0.9}}

Confidence scale:
- 0.9-1.0: Very clear emotional context
- 0.7-0.8: Clear but some interpretation needed
- 0.5-0.6: Ambiguous, best guess
- 0.0-0.4: Not enough context or off-topic (use "AMBIGUOUS")
"""

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-5",  # Claude Sonnet 4.5 (latest)
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse Claude's response
            response_text = message.content[0].text

            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Fallback if JSON not found
                return {
                    "sub_vibe": "AMBIGUOUS",
                    "reasoning": f"Could not parse response: {response_text[:200]}",
                    "confidence": 0.0
                }

        except Exception as e:
            return {
                "sub_vibe": "AMBIGUOUS",
                "reasoning": f"API error: {str(e)}",
                "confidence": 0.0
            }

    def map_songs(self, songs_file, output_file=None):
        """
        Process all songs with TRUE Claude analysis
        WITH CHECKPOINTING & STATUS UPDATES
        """
        import time
        from datetime import datetime

        # Load songs
        with open(songs_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        songs = data.get('mapped_songs', data.get('songs', []))

        # Setup checkpoint file
        checkpoint_file = Path(songs_file).parent / f"{Path(songs_file).stem}_ANANKI_CHECKPOINT.json"
        
        # Try to resume from checkpoint
        start_index = 0
        mapped_songs = []
        ambiguous_songs = []
        
        if checkpoint_file.exists():
            print("[CHECKPOINT FOUND] Resuming from previous run...")
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                mapped_songs = checkpoint.get('mapped_songs', [])
                ambiguous_songs = checkpoint.get('ambiguous_songs', [])
                start_index = checkpoint.get('processed_count', 0)
            print(f"   Resuming from song {start_index}/{len(songs)}")

        print("="*70)
        print("TRUE ANANKI - CLAUDE API ANALYSIS")
        print("="*70)
        print(f"Total songs: {len(songs)}")
        print(f"Already processed: {start_index}")
        print(f"Remaining: {len(songs) - start_index}")
        print("This will take time - Claude reads each context carefully!")
        print("="*70)
        print("STATUS UPDATES EVERY 10 SONGS")
        print("AUTO-CHECKPOINT EVERY 25 SONGS")
        print("="*70)

        last_status_time = time.time()
        start_time = time.time()

        for i in range(start_index, len(songs)):
            song = songs[i]
            current = i + 1
            
            # Get Claude's analysis
            analysis = self.analyze_song_placement(song)

            # Add analysis to song data (with safe defaults)
            song['ananki_subvibe'] = analysis.get('sub_vibe', 'AMBIGUOUS')
            song['ananki_reasoning'] = analysis.get('reasoning', 'No reasoning provided')
            song['ananki_confidence'] = analysis.get('confidence', 0.0)

            # Categorize
            if analysis['sub_vibe'] == 'AMBIGUOUS' or analysis['confidence'] < 0.5:
                ambiguous_songs.append(song)
            else:
                mapped_songs.append(song)
            
            # STATUS UPDATE every 10 songs OR every 30 seconds
            current_time = time.time()
            if current % 10 == 0 or (current_time - last_status_time) >= 30:
                elapsed = current_time - start_time
                rate = current / elapsed if elapsed > 0 else 0
                remaining = (len(songs) - current) / rate if rate > 0 else 0
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Progress: {current}/{len(songs)} ({current/len(songs)*100:.1f}%) | "
                      f"Mapped: {len(mapped_songs)} | Ambiguous: {len(ambiguous_songs)} | "
                      f"ETA: {remaining/60:.1f} min")
                last_status_time = current_time
            
            # CHECKPOINT every 25 songs
            if current % 25 == 0:
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'processed_count': current,
                        'mapped_songs': mapped_songs,
                        'ambiguous_songs': ambiguous_songs,
                        'last_updated': datetime.now().isoformat()
                    }, f, indent=2, ensure_ascii=False)
                print(f"[CHECKPOINT] Saved at {current}/{len(songs)}")
        
        # FINAL CHECKPOINT
        print(f"\n[FINAL CHECKPOINT] Saving...")
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                'processed_count': len(songs),
                'mapped_songs': mapped_songs,
                'ambiguous_songs': ambiguous_songs,
                'last_updated': datetime.now().isoformat(),
                'status': 'COMPLETE'
            }, f, indent=2, ensure_ascii=False)

        # Statistics
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print(f"Total processed: {len(songs)}")
        print(f"Mapped with confidence: {len(mapped_songs)} ({len(mapped_songs)/len(songs)*100:.1f}%)")
        print(f"Ambiguous/Low confidence: {len(ambiguous_songs)} ({len(ambiguous_songs)/len(songs)*100:.1f}%)")

        # Show example reasoning
        if mapped_songs:
            print("\n" + "="*70)
            print("EXAMPLE CLAUDE REASONING:")
            print("="*70)
            example = mapped_songs[0]
            print(f"Song: {example['artist']} - {example['song']}")
            print(f"Sub-vibe: {example['ananki_subvibe']}")
            print(f"Reasoning: {example['ananki_reasoning']}")
            print(f"Confidence: {example['ananki_confidence']}")

        # Save results
        if output_file is None:
            output_file = Path(songs_file).parent / f"{Path(songs_file).stem}_CLAUDE_MAPPED.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(songs),
                'mapped': len(mapped_songs),
                'ambiguous': len(ambiguous_songs),
                'mapped_songs': mapped_songs,
                'ambiguous_songs': ambiguous_songs
            }, f, indent=2, ensure_ascii=False)

        print(f"\nSaved to: {output_file}")

        # Save ambiguous separately
        if ambiguous_songs:
            ambig_file = Path(songs_file).parent / f"{Path(songs_file).stem}_CLAUDE_AMBIGUOUS.json"
            with open(ambig_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total': len(ambiguous_songs),
                    'note': 'These need human review or are not music recommendations',
                    'songs': ambiguous_songs
                }, f, indent=2, ensure_ascii=False)
            print(f"Ambiguous saved to: {ambig_file}")
        
        # Clean up checkpoint file (success!)
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            print(f"[SUCCESS] Checkpoint cleaned up")

        return mapped_songs, ambiguous_songs


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python true_ananki_claude_api.py <songs_file.json>")
        print("\nExample:")
        print("  python true_ananki_claude_api.py test_results/happy_smart_extraction_500.json")
        return

    songs_file = sys.argv[1]

    # Initialize TRUE Ananki
    ananki = TrueAnankiClaudeAPI()

    # Process songs
    mapped, ambiguous = ananki.map_songs(songs_file)

    print("\n" + "="*70)
    print("READY FOR INJECTION!")
    print(f"Use: python inject_to_tapestry.py {Path(songs_file).stem}_CLAUDE_MAPPED.json")


if __name__ == '__main__':
    main()
