"""Quick 500-song validation test"""
from step1_spotify_validate_v2 import SpotifyValidatorV2
import json

# Load and take first 500
data = json.load(open('test_results/happy_feel_good_IMPROVED.json', encoding='utf-8'))
songs = data['songs'][:500]

print(f"\nTesting {len(songs)} songs...")

validator = SpotifyValidatorV2()
matched_good, matched_questionable, unmatched = validator.validate_batch(songs, 999, 1, 0.6)

print(f"\nHigh confidence: {len(matched_good)} ({len(matched_good)/500*100:.1f}%)")
print(f"Low confidence: {len(matched_questionable)} ({len(matched_questionable)/500*100:.1f}%)")
print(f"Unmatched: {len(unmatched)} ({len(unmatched)/500*100:.1f}%)")
print(f"\nOLD scraper: 48.6%")
print(f"NEW scraper: {len(matched_good)/500*100:.1f}%")
print(f"Improvement: {len(matched_good)/500*100 - 48.6:+.1f}%")
