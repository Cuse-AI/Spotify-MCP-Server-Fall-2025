"""
Quick test - just 500 songs to get fast results
"""
from step1_spotify_validate_v2 import SpotifyValidatorV2
import json
from pathlib import Path

print("\nQUICK TEST - FIRST 500 HAPPY SONGS")
print("="*70)

# Load test results
test_file = Path('test_results/happy_feel_good_IMPROVED.json')
with open(test_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Take only first 500 for quick test
songs = data['songs'][:500]
print(f"Testing first {len(songs)} songs...")

# Initialize validator
validator = SpotifyValidatorV2()

# Validate
print("\nValidating against Spotify...")
matched_good, matched_questionable, unmatched = validator.validate_batch(
    songs, batch_num=999, total_batches=1, min_confidence=0.6
)

# Results
total = len(songs)
good_rate = len(matched_good) / total * 100

print("\n" + "="*70)
print("QUICK TEST RESULTS")
print("="*70)
print(f"Total: {total}")
print(f"High confidence: {len(matched_good)} ({good_rate:.1f}%)")
print(f"Low confidence: {len(matched_questionable)} ({len(matched_questionable)/total*100:.1f}%)")
print(f"Unmatched: {len(unmatched)} ({len(unmatched)/total*100:.1f}%)")
print(f"\nOLD scraper: 48.6%")
print(f"NEW scraper: {good_rate:.1f}%")
print(f"IMPROVEMENT: {good_rate - 48.6:+.1f} points!")

if good_rate >= 70:
    print("\n🎉 SUCCESS! Fixes work!")
elif good_rate >= 60:
    print("\n✅ Better, but needs more work")
else:
    print("\n⚠️ Still has issues")
