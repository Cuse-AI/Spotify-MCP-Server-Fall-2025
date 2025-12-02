import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check quality tapestry
quality = json.load(open('core/tapestry_quality.json', encoding='utf-8'))
found_quality = False
for vibe, data in quality['vibes'].items():
    for s in data.get('songs', []):
        if 'watermark' in s.get('song', '').lower() and 'enya' in s.get('artist', '').lower():
            print("FOUND IN QUALITY TAPESTRY:")
            print(f"  Vibe: {vibe}")
            print(f"  Artist: {s.get('artist')}")
            print(f"  Song: {s.get('song')}")
            found_quality = True

if not found_quality:
    print("NOT in quality tapestry (score 3+)")

# Check original tapestry
print("\n--- Checking original tapestry ---")
original = json.load(open('core/tapestry.json', encoding='utf-8'))
found_original = False
for vibe, data in original['vibes'].items():
    for s in data.get('songs', []):
        if 'watermark' in s.get('song', '').lower() and 'enya' in s.get('artist', '').lower():
            print("FOUND IN ORIGINAL TAPESTRY:")
            print(f"  Vibe: {vibe}")
            print(f"  Artist: {s.get('artist')}")
            print(f"  Song: {s.get('song')}")
            print(f"  Comment: {s.get('comment_text', '')[:200]}...")
            found_original = True

if not found_original:
    print("NOT in original tapestry either")

# Check relevancy results to see what score it got
print("\n--- Checking relevancy PASSED (score 2+) ---")
passed = json.load(open('ananki/output/RELEVANCY_PASSED_20251201_222203.json', encoding='utf-8'))
found_passed = False
for s in passed.get('songs', []):
    if 'watermark' in s.get('song', '').lower() and 'enya' in s.get('artist', '').lower():
        print(f"FOUND with relevancy score: {s.get('relevancy_score')}")
        print(f"  Comment: {s.get('comment_text', '')[:200]}...")
        found_passed = True

if not found_passed:
    print("NOT in passed results - must have been score 1 (FAIL)")
