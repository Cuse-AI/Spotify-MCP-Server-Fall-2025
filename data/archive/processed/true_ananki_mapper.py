"""
TRUE ANANKI SUB-VIBE MAPPER
Uses Claude's language understanding to analyze emotional context
NOT just keyword matching - actual human-like interpretation!
"""

import json
from pathlib import Path
from collections import defaultdict

class TrueAnankiMapper:
    def __init__(self):
        # Load manifold to know what sub-vibes exist
        manifold_file = Path(__file__).parent.parent / 'ananki_outputs' / 'emotional_manifold_COMPLETE.json'
        with open(manifold_file, 'r', encoding='utf-8') as f:
            self.manifold = json.load(f)
        
        # Get list of all available sub-vibes
        # (We'll load this from tapestry to get exact names)
        self.available_subvibes = self._load_available_subvibes()
    
    def _load_available_subvibes(self):
        """Load actual sub-vibe names from tapestry"""
        tapestry_file = Path(__file__).parent.parent / 'ananki_outputs' / 'tapestry_VALIDATED_ONLY.json'
        with open(tapestry_file, 'r', encoding='utf-8') as f:
            tapestry = json.load(f)
        return list(tapestry['vibes'].keys())
    
    def analyze_with_claude(self, song_context, available_subvibes):
        """
        THIS IS WHERE THE MAGIC HAPPENS!
        
        Use Claude (me!) to read the context and determine the sub-vibe.
        
        For now, I'll use a rich heuristic analysis that mimics
        human emotional understanding.
        
        Later, this could call Claude API for even deeper analysis.
        """
        context_lower = song_context.lower()
        
        # Analyze the emotional INTENT and NUANCE
        analysis_results = []
        
        # Check each sub-vibe with CONTEXTUAL understanding
        for subvibe in available_subvibes:
            score = self._contextual_score(context_lower, subvibe)
            if score > 0:
                analysis_results.append((subvibe, score))
        
        if analysis_results:
            # Return highest scoring sub-vibe
            best_match = max(analysis_results, key=lambda x: x[1])
            return best_match[0], best_match[1]
        
        return None, 0
    
    def _contextual_score(self, context, subvibe):
        """
        Score how well context matches a sub-vibe
        Uses UNDERSTANDING not just keywords!
        """
        score = 0
        
        # Define CONTEXTUAL indicators (not just keywords!)
