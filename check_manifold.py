import json
import math

with open(r'C:\Users\sw13t\Desktop\Coding\CuseAI\SpotifyMSP\Spotify-MCP-Server-Fall-2025\data\manifold\emotional_manifold_COMPLETE.json', 'r', encoding='utf-8') as f:
    m = json.load(f)

positions = m['central_vibes']['positions']

def dist(v1, v2):
    p1, p2 = positions[v1], positions[v2]
    return math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)

print("CURRENT MANIFOLD LAYOUT")
print("=" * 50)
print("""
        LOW Y (Top = Bright/Light)
              |
    Happy(498,383)     
              |
    Party(264,409)          Chill(611,542)
              |        Sad(411,522)
              |
    Romantic(215,631)   Energy(471,685)
              |
              |        Dark(350,841)
    Drive(161,892)
              |        Night(476,1000)
              |
        HIGH Y (Bottom = Dark/Deep)
        
    LOW X -------|------- HIGH X
    (Intense)         (Relaxed)
""")

print("\nNEAREST NEIGHBORS FOR EACH VIBE:")
print("=" * 50)

for vibe in positions:
    distances = [(other, dist(vibe, other)) for other in positions if other != vibe]
    distances.sort(key=lambda x: x[1])
    neighbors = [d[0] for d in distances[:3]]
    print(f"{vibe:12} -> {', '.join(neighbors)}")

print("\n" + "=" * 50)
print("EMOTIONAL LOGIC CHECK:")
print("=" * 50)

checks = [
    ("Sad", ["Dark", "Romantic"], "Lost love connects sadness and romance"),
    ("Happy", ["Party", "Chill"], "Joy connects celebration and relaxation"),
    ("Dark", ["Night", "Sad"], "Darkness connects nighttime and sorrow"),
    ("Energy", ["Party", "Drive"], "High energy connects dancing and driving"),
    ("Chill", ["Happy", "Romantic"], "Calm connects contentment and love"),
    ("Night", ["Dark", "Chill"], "Night connects darkness and calm"),
    ("Party", ["Energy", "Happy"], "Party connects excitement and joy"),
    ("Drive", ["Energy", "Dark"], "Driving connects intensity and moodiness"),
    ("Romantic", ["Sad", "Chill"], "Romance connects longing and tenderness"),
]

issues = []
for vibe, expected, reason in checks:
    distances = [(other, dist(vibe, other)) for other in positions if other != vibe]
    distances.sort(key=lambda x: x[1])
    actual_neighbors = [d[0] for d in distances[:3]]
    
    matches = [e for e in expected if e in actual_neighbors]
    missing = [e for e in expected if e not in actual_neighbors]
    
    status = "OK" if len(matches) >= 1 else "ISSUE"
    if missing:
        issues.append((vibe, missing, actual_neighbors))
    
    print(f"{vibe:12}: Want {expected} -> Got {actual_neighbors[:2]} [{status}]")

if issues:
    print("\n" + "=" * 50)
    print("POTENTIAL ISSUES TO CONSIDER:")
    print("=" * 50)
    for vibe, missing, actual in issues:
        print(f"  {vibe} missing {missing} as neighbor")
        print(f"    -> Currently near: {actual[:2]}")
