"""
ANANKI V2 - Two-Stage Analysis with Per-Song Coordinates
=========================================================

Stage 1: SANITY CHECK (Haiku - cheap)
- Is this comment actually about this song?
- Does it contain emotional content?
- PASS → Stage 2 | FAIL → Trash

Stage 2: VIBE MAPPING + COORDINATES (Sonnet - expensive)  
- Map to sub-vibe
- Calculate unique coordinates based on emotional composition
- Generate reasoning

The key innovation: Each song gets its OWN coordinates on the manifold,
not just the sub-vibe's center. This allows for emotional gradients
WITHIN sub-vibes.
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

# Load environment
load_dotenv()

class AnankiV2:
    def __init__(self, project_root=None):
        """Initialize Ananki V2 with manifold and sub-vibe data"""
        
        # API setup
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found!")
        self.client = Anthropic(api_key=api_key)
        
        # Find project root
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path(__file__).parent.parent
        
        # Load manifold for coordinate calculation
        manifold_path = self.project_root / "data" / "manifold" / "emotional_manifold_COMPLETE.json"
        with open(manifold_path, 'r', encoding='utf-8') as f:
            self.manifold = json.load(f)
        
        # Load tapestry for available sub-vibes
        tapestry_path = self.project_root / "core" / "tapestry.json"
        with open(tapestry_path, 'r', encoding='utf-8') as f:
            tapestry = json.load(f)
        
        self.available_subvibes = list(tapestry['vibes'].keys())
        self.central_vibes = list(self.manifold['central_vibes']['positions'].keys())
        
        print(f"[ANANKI V2] Loaded {len(self.available_subvibes)} sub-vibes")
        print(f"[ANANKI V2] Loaded {len(self.central_vibes)} central vibes for coordinate calculation")
    
    # =========================================================================
    # STAGE 1: SANITY CHECK (Haiku - cheap)
    # =========================================================================
    
    def sanity_check(self, song_data):
        """
        Quick check using Haiku:
        A) Is this comment about THIS song (not generic/wrong song)?
        B) Does it contain emotional content (feelings, experiences, memories)?
        
        Returns: {pass: bool, reason: str}
        """
        
        prompt = f"""You are a quality filter for a music recommendation system. 

SONG: {song_data.get('artist', 'Unknown')} - {song_data.get('song', 'Unknown')}

COMMENT: "{song_data.get('comment_text', '')}"

POST CONTEXT: {song_data.get('post_title', 'N/A')}

Answer these TWO questions:

1. RELEVANCE: Is this comment actually about this specific song or the emotional experience of listening to it?
   - YES if: describes feelings, memories, experiences, emotional reactions, when/how they listen
   - NO if: just states facts, talks about popularity/virality, is about a different song, is generic praise like "great song!", is about the artist's personal life, is a meme/joke with no emotional substance

2. EMOTIONAL CONTENT: Does the comment reveal WHY someone connects to this song emotionally?
   - YES if: describes feelings, paints a scene, shares a memory, explains emotional impact
   - NO if: "this song is good", "I love this", "classic!", timestamps, facts about release date, comments about audio quality

Respond in JSON:
{{"relevance": true/false, "emotional": true/false, "reason": "brief explanation"}}

Be STRICT. We only want comments that show genuine human emotional connection to the music."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",  # Haiku for cheap filtering
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                passes = result.get('relevance', False) and result.get('emotional', False)
                return {
                    'pass': passes,
                    'relevance': result.get('relevance', False),
                    'emotional': result.get('emotional', False),
                    'reason': result.get('reason', 'No reason provided')
                }
            else:
                return {'pass': False, 'reason': f'Could not parse response: {response_text[:100]}'}
                
        except Exception as e:
            return {'pass': False, 'reason': f'API error: {str(e)}'}
    
    # =========================================================================
    # STAGE 2: VIBE MAPPING + COORDINATE CALCULATION (Sonnet - expensive)
    # =========================================================================
    
    def analyze_and_place(self, song_data):
        """
        Full analysis using Sonnet:
        1. Map to sub-vibe
        2. Determine emotional composition for THIS SPECIFIC SONG
        3. Calculate unique coordinates on the manifold
        
        Returns: {sub_vibe, reasoning, confidence, coordinates: {x, y}, emotional_composition}
        """
        
        # Build sub-vibe list
        subvibes_formatted = "\n".join([f"  - {sv}" for sv in sorted(self.available_subvibes)])
        
        # Build central vibes list for composition
        central_vibes_list = ", ".join(self.central_vibes)
        
        prompt = f"""You are Ananki, a music emotion analyst. Your job is to:
1. Map this song to a sub-vibe
2. Determine its unique emotional composition

SONG: {song_data.get('artist', 'Unknown')} - {song_data.get('song', 'Unknown')}
SPOTIFY ID: {song_data.get('spotify_id', 'N/A')}

HUMAN COMMENT: "{song_data.get('comment_text', '')}"

POST CONTEXT: {song_data.get('post_title', 'N/A')}

AVAILABLE SUB-VIBES (choose exactly one):
{subvibes_formatted}

CENTRAL VIBES FOR COMPOSITION: {central_vibes_list}

YOUR TASK:

1. Choose the ONE sub-vibe that best fits this song's emotional context

2. Create an emotional composition using the central vibes. This should reflect THIS SPECIFIC SONG's emotional blend, which may differ from the sub-vibe's typical composition.

   Example: A song in "Sad - Heartbreak" might be:
   - More angry: {{"Sad": 0.5, "Energy": 0.25, "Dark": 0.15, "Romantic": 0.1}}
   - More tender: {{"Sad": 0.6, "Romantic": 0.3, "Chill": 0.1}}
   
   The weights must sum to 1.0 and use only the central vibes listed above.

3. Explain your reasoning - what in the comment reveals the emotional quality?

Respond in JSON:
{{
  "sub_vibe": "Exact - Sub Vibe Name",
  "emotional_composition": {{"Sad": 0.5, "Dark": 0.3, ...}},
  "reasoning": "Explanation of emotional mapping",
  "confidence": 0.85
}}

RULES:
- Sub-vibe name must EXACTLY match one from the list
- Emotional composition weights must sum to 1.0
- Only use central vibes: {central_vibes_list}
- Confidence: 0.9+ (very clear), 0.7-0.8 (clear), 0.5-0.6 (ambiguous)"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250514",  # Sonnet for deep analysis
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                
                # Calculate coordinates from emotional composition
                coordinates = self._calculate_coordinates(result.get('emotional_composition', {}))
                result['coordinates'] = coordinates
                
                return result
            else:
                return {
                    'sub_vibe': 'AMBIGUOUS',
                    'reasoning': f'Could not parse: {response_text[:200]}',
                    'confidence': 0.0,
                    'coordinates': {'x': 500, 'y': 500}
                }
                
        except Exception as e:
            return {
                'sub_vibe': 'AMBIGUOUS',
                'reasoning': f'API error: {str(e)}',
                'confidence': 0.0,
                'coordinates': {'x': 500, 'y': 500}
            }
    
    def _calculate_coordinates(self, emotional_composition):
        """
        Calculate x,y coordinates from emotional composition weights.
        Uses weighted average of central vibe positions.
        """
        if not emotional_composition:
            return {'x': 500, 'y': 500}  # Center fallback
        
        central_positions = self.manifold['central_vibes']['positions']
        
        total_x = 0
        total_y = 0
        total_weight = 0
        
        for vibe, weight in emotional_composition.items():
            if vibe in central_positions:
                pos = central_positions[vibe]
                total_x += pos['x'] * weight
                total_y += pos['y'] * weight
                total_weight += weight
        
        if total_weight > 0:
            return {
                'x': round(total_x / total_weight, 2),
                'y': round(total_y / total_weight, 2)
            }
        else:
            return {'x': 500, 'y': 500}
    
    # =========================================================================
    # FULL PIPELINE: Sanity Check → Analysis
    # =========================================================================
    
    def process_song(self, song_data):
        """
        Full two-stage processing:
        1. Sanity check (Haiku)
        2. If passes → Full analysis (Sonnet)
        
        Returns: {status, data} where status is 'pass', 'fail', or 'error'
        """
        
        # Stage 1: Sanity Check
        sanity = self.sanity_check(song_data)
        
        if not sanity.get('pass', False):
            return {
                'status': 'fail',
                'stage': 'sanity_check',
                'reason': sanity.get('reason', 'Failed sanity check'),
                'song': f"{song_data.get('artist')} - {song_data.get('song')}"
            }
        
        # Stage 2: Full Analysis
        analysis = self.analyze_and_place(song_data)
        
        if analysis.get('sub_vibe') == 'AMBIGUOUS':
            return {
                'status': 'ambiguous',
                'stage': 'analysis',
                'reason': analysis.get('reasoning', 'Ambiguous result'),
                'song': f"{song_data.get('artist')} - {song_data.get('song')}"
            }
        
        return {
            'status': 'pass',
            'data': {
                **song_data,
                'mapped_subvibe': analysis['sub_vibe'],
                'ananki_reasoning': analysis['reasoning'],
                'mapping_confidence': analysis['confidence'],
                'coordinates': analysis['coordinates'],
                'emotional_composition': analysis.get('emotional_composition', {})
            }
        }


# =============================================================================
# BATCH PROCESSING
# =============================================================================

def process_batch(input_file, output_dir=None, checkpoint_every=10):
    """
    Process a batch of songs through Ananki V2
    
    Args:
        input_file: JSON file with songs to process
        output_dir: Where to save results (default: same as input)
        checkpoint_every: Save checkpoint every N songs
    """
    
    ananki = AnankiV2()
    
    # Load input
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    songs = data.get('songs', data.get('mapped_songs', []))
    print(f"[BATCH] Processing {len(songs)} songs")
    
    # Setup output
    if output_dir is None:
        output_dir = Path(input_file).parent
    else:
        output_dir = Path(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    passed_file = output_dir / f"ANANKI_PASSED_{timestamp}.json"
    failed_file = output_dir / f"ANANKI_FAILED_{timestamp}.json"
    checkpoint_file = output_dir / f"ANANKI_CHECKPOINT_{timestamp}.json"
    
    passed = []
    failed = []
    
    for i, song in enumerate(songs):
        print(f"[{i+1}/{len(songs)}] {song.get('artist', '?')} - {song.get('song', '?')}")
        
        result = ananki.process_song(song)
        
        if result['status'] == 'pass':
            passed.append(result['data'])
            print(f"  [PASS] -> {result['data']['mapped_subvibe']}")
            print(f"         Coords: ({result['data']['coordinates']['x']}, {result['data']['coordinates']['y']})")
        else:
            failed.append({
                'song': song,
                'reason': result.get('reason', 'Unknown'),
                'stage': result.get('stage', 'unknown')
            })
            print(f"  [FAIL] {result.get('reason', 'Unknown')[:50]}")
        
        # Checkpoint
        if (i + 1) % checkpoint_every == 0:
            _save_checkpoint(checkpoint_file, passed, failed, i + 1, len(songs))
    
    # Final save
    with open(passed_file, 'w', encoding='utf-8') as f:
        json.dump({'songs': passed, 'count': len(passed)}, f, indent=2, ensure_ascii=False)
    
    with open(failed_file, 'w', encoding='utf-8') as f:
        json.dump({'songs': failed, 'count': len(failed)}, f, indent=2, ensure_ascii=False)
    
    print(f"\n[DONE] Passed: {len(passed)} | Failed: {len(failed)}")
    print(f"  Passed: {passed_file}")
    print(f"  Failed: {failed_file}")
    
    return passed, failed


def _save_checkpoint(filepath, passed, failed, processed, total):
    """Save progress checkpoint"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'passed': passed,
            'failed': failed,
            'processed': processed,
            'total': total,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    print(f"  [CHECKPOINT] Saved at {processed}/{total}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ananki V2 - Two-stage song analysis")
    parser.add_argument("input", help="Input JSON file with songs")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--checkpoint", "-c", type=int, default=10, help="Checkpoint every N songs")
    
    args = parser.parse_args()
    
    process_batch(args.input, args.output, args.checkpoint)
