"""Quick test of new manifold positions"""
import math

NEW_POSITIONS = {
    "Happy":    {"x": 500, "y": 200},
    "Party":    {"x": 300, "y": 250},
    "Chill":    {"x": 700, "y": 250},
    "Energy":   {"x": 250, "y": 450},
    "Romantic": {"x": 750, "y": 450},
    "Sad":      {"x": 500, "y": 600},
    "Drive":    {"x": 200, "y": 650},
    "Dark":     {"x": 350, "y": 800},
    "Night":    {"x": 550, "y": 850},
}

def dist(v1, v2):
    p1, p2 = NEW_POSITIONS[v1], NEW_POSITIONS[v2]
    return math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)

print("NEW MANIFOLD LAYOUT")
print("=" * 60)
print("""
              Y=0 (TOP - LIGHT/UPLIFTING)
                    |
         Party(300,250) -- Happy(500,200) -- Chill(700,250)
              |                 |                 |
         Energy(250,450) ------+------- Romantic(750,450)
              |                 |                 
         Drive(200,650) --- Sad(500,600) --------+
              |                 |                 
         Dark(350,800) ---- Night(550,850)
                    |
              Y=1000 (BOTTOM - DARK/HEAVY)
              
         X=0 (INTENSE) -------- X=1000 (CALM)
""")

print("NEAREST NEIGHBORS:")
print("=" * 60)
for vibe in NEW_POSITIONS:
    distances = [(other, dist(vibe, other)) for other in NEW_POSITIONS if other != vibe]
    distances.sort(key=lambda x: x[1])
    neighbors = [d[0] for d in distances[:3]]
    print(f"  {vibe:12} -> {neighbors}")

print("\n" + "=" * 60)
print("EMOTIONAL LOGIC VERIFICATION:")
print("=" * 60)

checks = [
    ("Sad", ["Dark", "Night"], "Sadness near darkness"),
    ("Sad", ["Romantic"], "Sadness near lost love"),
    ("Happy", ["Party", "Chill"], "Joy near celebration & calm"),
    ("Dark", ["Night", "Drive"], "Darkness near night & intensity"),
    ("Energy", ["Party", "Drive"], "Energy near party & driving"),
    ("Party", ["Energy", "Happy"], "Party near energy & joy"),
    ("Chill", ["Happy", "Romantic"], "Chill near happy & romantic"),
    ("Romantic", ["Chill", "Sad"], "Romance near tender & longing"),
    ("Night", ["Dark", "Sad"], "Night near dark & melancholy"),
    ("Drive", ["Energy", "Dark"], "Drive near energy & darkness"),
]

all_good = True
for vibe, expected_neighbors, reason in checks:
    distances = [(other, dist(vibe, other)) for other in NEW_POSITIONS if other != vibe]
    distances.sort(key=lambda x: x[1])
    actual = [d[0] for d in distances[:4]]  # Check top 4
    
    found = [e for e in expected_neighbors if e in actual]
    status = "PASS" if len(found) == len(expected_neighbors) else "PARTIAL" if found else "FAIL"
    
    if status != "PASS":
        all_good = False
    
    print(f"  {reason}")
    print(f"    {vibe} should be near {expected_neighbors}")
    print(f"    Actually near: {actual[:3]} [{status}]")
    print()

if all_good:
    print("[SUCCESS] All emotional adjacencies verified!")
else:
    print("[NOTE] Some adjacencies are partial - may need position tweaks")
