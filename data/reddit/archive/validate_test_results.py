"""
Validate the test Happy songs to see if improved scraper works!
Target: 70%+ high confidence (vs 48.6% with old scraper)
"""

from step1_spotify_validate_v2 import SpotifyValidatorV2
import json
from pathlib import Path

print("\nVALIDATING IMPROVED HAPPY SCRAPER RESULTS")
print("="*70)

# Load test results
test_file = Path('test_results/happy_feel_good_IMPROVED.json')
with open(test_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

songs = data['songs']
print(f"\nSongs to validate: {len(songs)}")

# Initialize validator
validator = SpotifyValidatorV2()

# Validate
print("\nValidating against Spotify...")
matched_good, matched_questionable, unmatched = validator.validate_batch(
    songs, batch_num=999, total_batches=1, min_confidence=0.6
)

# Calculate results
total = len(songs)
good_rate = len(matched_good) / total * 100
questionable_rate = len(matched_questionable) / total * 100
unmatched_rate = len(unmatched) / total * 100

print("\n" + "="*70)
print("VALIDATION RESULTS - IMPROVED SCRAPER TEST")
print("="*70)
print(f"Total songs: {total}")
print(f"High confidence: {len(matched_good)} ({good_rate:.1f}%)")
print(f"Low confidence: {len(matched_questionable)} ({questionable_rate:.1f}%)")
print(f"Unmatched: {len(unmatched)} ({unmatched_rate:.1f}%)")

print("\n" + "="*70)
print("COMPARISON TO OLD SCRAPER:")
print("="*70)
print("OLD Happy scraper: 48.6% high confidence")
print(f"NEW Happy scraper: {good_rate:.1f}% high confidence")
print(f"\nIMPROVEMENT: {good_rate - 48.6:+.1f} percentage points!")

if good_rate >= 70:
    print("\n🎉 SUCCESS! Hit 70%+ target!")
    print("The scraper fixes WORK! Ready to re-scrape all problem vibes.")
elif good_rate >= 60:
    print("\n✅ GOOD! Significant improvement!")
    print("Consider additional tweaks to hit 70%+")
else:
    print("\n⚠️ Still needs work - investigate further")

# Save validation results
output = {
    'test_vibe': 'Happy - Feel Good',
    'total_songs': total,
    'high_confidence': len(matched_good),
    'low_confidence': len(matched_questionable),
    'unmatched': len(unmatched),
    'validation_rate': good_rate,
    'comparison_to_old': {
        'old_rate': 48.6,
        'new_rate': good_rate,
        'improvement': good_rate - 48.6
    },
    'matched_good': matched_good,
    'matched_questionable': matched_questionable,
    'unmatched': unmatched
}

output_file = Path('test_results/happy_validation_results.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nValidation results saved to: {output_file}")
