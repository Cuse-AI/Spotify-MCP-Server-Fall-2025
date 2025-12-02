"""
HELPER: COORDINATE ASSIGNMENT
=============================
Uses Haiku to analyze each song's emotional composition and assign
unique x,y coordinates on the Midden manifold.

NO RANDOM DATA - each coordinate is based on AI analysis of:
- The comment's emotional content
- The song's sub-vibe context
- How the specific emotions blend together

The manifold has 9 central vibes with known positions.
Songs get coordinates based on weighted blend of these centers.
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

class CoordinateAssigner:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found!")
        self.client = Anthropic(api_key=api_key)
        
        # Load manifold
        project_root = Path(__file__).parent.parent
        manifold_path = project_root / "data" / "manifold" / "emotional_manifold_COMPLETE.json"
        
        with open(manifold_path, 'r', encoding='utf-8') as f:
            self.manifold = json.load(f)
        
        self.central_positions = self.manifold['central_vibes']['positions']
        self.central_vibes = list(self.central_positions.keys())
        
        print(f"[COORDINATES] Loaded manifold with {len(self.central_vibes)} central vibes:")
        for vibe, pos in self.central_positions.items():
            print(f"  {vibe}: ({pos['x']:.0f}, {pos['y']:.0f})")
    
    def analyze_emotional_blend(self, song_data):
        """
        Analyze the emotional composition of this specific song.
        Returns weights for each central vibe that sum to 1.0.
        """
        
        comment = song_data.get('comment_text', '')
        artist = song_data.get('artist', 'Unknown')
        song_name = song_data.get('song', 'Unknown')
        subvibe = song_data.get('mapped_subvibe', song_data.get('current_vibe', 'Unknown'))
        
        vibes_list = ", ".join(self.central_vibes)
        
        prompt = f"""You are mapping a song's emotional position on a 2D manifold.

SONG: {artist} - {song_name}
SUB-VIBE: {subvibe}
COMMENT: "{comment[:500]}"

THE 9 EMOTIONAL CENTERS: {vibes_list}

TASK: Determine this song's emotional composition as a blend of the 9 centers.

Based on the comment and sub-vibe, what percentage does this song pull toward each center?

RULES:
- Weights MUST sum to exactly 1.0
- Use 0.0 for vibes with no presence
- Primary vibe (from sub-vibe name) usually gets 0.4-0.7
- Secondary emotions from comment get 0.1-0.3 each
- Be specific to THIS song's comment, not generic

Example for a "Sad - Heartbreak" song with an angry comment:
{{"Sad": 0.45, "Dark": 0.25, "Romantic": 0.15, "Energy": 0.15}}

Example for a "Party - Club" song with euphoric comment:
{{"Party": 0.5, "Energy": 0.3, "Happy": 0.2}}

Respond ONLY with JSON - the emotional weights object:
{{"Sad": 0.0, "Happy": 0.0, "Chill": 0.0, "Energy": 0.0, "Dark": 0.0, "Romantic": 0.0, "Night": 0.0, "Drive": 0.0, "Party": 0.0}}

Fill in the actual weights. Must sum to 1.0."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            
            if json_match:
                weights = json.loads(json_match.group())
                
                # Validate and normalize
                total = sum(weights.values())
                if total > 0:
                    weights = {k: v/total for k, v in weights.items()}
                
                return weights
            else:
                # Fallback: use sub-vibe's meta as primary
                return self._fallback_weights(subvibe)
                
        except Exception as e:
            print(f"  [ERROR] {str(e)[:50]}")
            return self._fallback_weights(subvibe)
    
    def _fallback_weights(self, subvibe):
        """Fallback weights based on sub-vibe name"""
        meta = subvibe.split(' - ')[0] if ' - ' in subvibe else subvibe
        weights = {v: 0.0 for v in self.central_vibes}
        if meta in weights:
            weights[meta] = 0.8
            # Add small amounts to related vibes
            weights['Chill'] = 0.1
            weights['Night'] = 0.1
        else:
            # Even distribution as last resort
            for v in weights:
                weights[v] = 1.0 / len(weights)
        return weights
    
    def calculate_coordinates(self, weights):
        """
        Calculate x,y from emotional weights using weighted average of central positions.
        """
        total_x = 0
        total_y = 0
        total_weight = 0
        
        for vibe, weight in weights.items():
            if vibe in self.central_positions and weight > 0:
                pos = self.central_positions[vibe]
                total_x += pos['x'] * weight
                total_y += pos['y'] * weight
                total_weight += weight
        
        if total_weight > 0:
            return {
                'x': round(total_x / total_weight, 2),
                'y': round(total_y / total_weight, 2)
            }
        else:
            return {'x': 500.0, 'y': 500.0}
    
    def assign_coordinates(self, song_data):
        """
        Full coordinate assignment for a song.
        Returns song data with coordinates and emotional_composition added.
        """
        weights = self.analyze_emotional_blend(song_data)
        coordinates = self.calculate_coordinates(weights)
        
        return {
            **song_data,
            'coordinates': coordinates,
            'emotional_composition': weights
        }


def run_coordinate_assignment(input_source='tapestry', output_file=None, checkpoint_file=None):
    """
    Assign coordinates to all songs.
    
    Args:
        input_source: 'tapestry' or path to JSON file
        output_file: Where to save (default: creates new file)
        checkpoint_file: Resume from checkpoint
    """
    
    assigner = CoordinateAssigner()
    project_root = Path(__file__).parent.parent
    
    # Load songs
    if input_source == 'tapestry':
        tapestry_path = project_root / "core" / "tapestry.json"
        with open(tapestry_path, 'r', encoding='utf-8') as f:
            tapestry = json.load(f)
        
        all_songs = []
        song_to_vibe = {}  # Track which vibe each song belongs to
        for vibe_name, vibe_data in tapestry['vibes'].items():
            for idx, song in enumerate(vibe_data.get('songs', [])):
                song_id = f"{vibe_name}_{idx}"
                song['_vibe_key'] = vibe_name
                song['_song_idx'] = idx
                all_songs.append(song)
        
        is_tapestry = True
    else:
        with open(input_source, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_songs = data.get('songs', [])
        is_tapestry = False
    
    print(f"\n[COORDINATES] Processing {len(all_songs)} songs")
    
    # Output setup
    output_dir = project_root / "ananki" / "output"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_path = output_dir / f"COORDS_CHECKPOINT_{timestamp}.json"
    
    processed_songs = []
    start_index = 0
    
    # Resume from checkpoint
    if checkpoint_file and Path(checkpoint_file).exists():
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        processed_songs = checkpoint.get('processed', [])
        start_index = checkpoint.get('index', 0)
        print(f"[RESUME] Starting from song {start_index}")
    
    # Process each song
    for i in range(start_index, len(all_songs)):
        song = all_songs[i]
        
        result = assigner.assign_coordinates(song)
        processed_songs.append(result)
        
        coords = result['coordinates']
        print(f"[{i+1}/{len(all_songs)}] {song.get('artist', '?')[:15]} - {song.get('song', '?')[:20]} -> ({coords['x']:.0f}, {coords['y']:.0f})")
        
        # Checkpoint every 50
        if (i + 1) % 50 == 0:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump({'processed': processed_songs, 'index': i + 1}, f, ensure_ascii=False)
            print(f"  [CHECKPOINT] Saved at {i+1}/{len(all_songs)}")
    
    # Save results
    if is_tapestry:
        # Update tapestry in place
        for song in processed_songs:
            vibe_key = song.pop('_vibe_key', None)
            song_idx = song.pop('_song_idx', None)
            if vibe_key and song_idx is not None:
                tapestry['vibes'][vibe_key]['songs'][song_idx] = song
        
        with open(tapestry_path, 'w', encoding='utf-8') as f:
            json.dump(tapestry, f, indent=2, ensure_ascii=False)
        print(f"\n[SAVED] Updated tapestry with coordinates")
    else:
        out_path = output_file or (output_dir / f"WITH_COORDINATES_{timestamp}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'songs': processed_songs, 'count': len(processed_songs)}, f, indent=2, ensure_ascii=False)
        print(f"\n[SAVED] {out_path}")
    
    print(f"[COMPLETE] Assigned coordinates to {len(processed_songs)} songs")
    return processed_songs


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", default="tapestry", help="'tapestry' or path to JSON")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--resume", "-r", help="Resume from checkpoint")
    args = parser.parse_args()
    
    run_coordinate_assignment(args.input, args.output, args.resume)
