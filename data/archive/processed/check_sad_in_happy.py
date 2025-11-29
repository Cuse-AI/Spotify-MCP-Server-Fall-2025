import json

data = json.load(open('test_results/happy_smart_extraction_500_MAPPED.json', encoding='utf-8'))
sad_songs = [s for s in data['songs'] if 'Sad' in s.get('mapped_subvibe', '')]

print(f"WHY SAD SONGS IN HAPPY THREADS? ({len(sad_songs)} found)\n")
print("="*70)

for i, s in enumerate(sad_songs[:5], 1):
    print(f"\n{i}. {s['artist']} - {s['song']}")
    print(f"   Sub-vibe: {s['mapped_subvibe']}")
    print(f"   Post: {s.get('post_title', '')[:70]}")
    print(f"   Comment: {s.get('comment_text', '')[:120]}")
