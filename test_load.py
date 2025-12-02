import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("Loading checkpoint...")
with open('ananki/output/RELEVANCY_CHECKPOINT_20251201_201014.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"Loaded! Processed: {data['processed']} / {data['total']}")
print(f"Passed: {len(data['passed'])}, Failed: {len(data['failed'])}")
print("Checkpoint loads fine!")
