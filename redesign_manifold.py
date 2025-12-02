"""
MANIFOLD REDESIGN
=================
Repositioning the 9 meta-vibes so emotional adjacencies make sense.

Design principles:
- Y axis: Top = Light/Uplifting, Bottom = Dark/Heavy
- X axis: Left = Intense/Active, Right = Calm/Passive

Emotional adjacency goals:
- Sad <-> Dark <-> Night (the melancholy cluster)
- Happy <-> Party <-> Energy (the upbeat cluster)  
- Chill <-> Romantic (the tender cluster)
- Drive <-> Energy <-> Dark (the intensity bridge)

Layout concept (1000x1000 grid):

         LIGHT/UPLIFTING
              |
    PARTY --- HAPPY --- CHILL
      |         |         |
    ENERGY ----+---- ROMANTIC
      |         |         |
    DRIVE ---- SAD ----- 
      |         |        
    DARK ----- NIGHT
              |
         DARK/HEAVY

    INTENSE <----+----> CALM
"""

import json
from pathlib import Path
from datetime import datetime

# New meta-vibe positions designed for emotional logic
NEW_POSITIONS = {
    # Top row - bright emotions
    "Happy":    {"x": 500, "y": 200},   # Center-top, the brightest
    "Party":    {"x": 300, "y": 250},   # Left of Happy, more energetic
    "Chill":    {"x": 700, "y": 250},   # Right of Happy, more relaxed
    
    # Middle row - transitional emotions  
    "Energy":   {"x": 250, "y": 450},   # Left-center, high intensity
    "Romantic": {"x": 750, "y": 450},   # Right-center, tender/soft
    
    # Lower-middle - the bridge emotions
    "Sad":      {"x": 500, "y": 600},   # Center, connects to many
    "Drive":    {"x": 200, "y": 650},   # Left, intense but darker
    
    # Bottom row - dark emotions
    "Dark":     {"x": 350, "y": 800},   # Left-bottom, heavy
    "Night":    {"x": 550, "y": 850},   # Center-bottom, mysterious
}

def calculate_distances():
    """Show what's near what with new positions"""
    import math
    
    def dist(v1, v2):
        p1, p2 = NEW_POSITIONS[v1], NEW_POSITIONS[v2]
        return math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)
    
    print("NEW MANIFOLD - NEAREST NEIGHBORS:")
    print("=" * 50)
    
    for vibe in NEW_POSITIONS:
        distances = [(other, dist(vibe, other)) for other in NEW_POSITIONS if other != vibe]
        distances.sort(key=lambda x: x[1])
        neighbors = [f"{d[0]}({d[1]:.0f})" for d in distances[:3]]
        print(f"  {vibe:12} -> {', '.join(neighbors)}")

def check_emotional_logic():
    """Verify emotional adjacencies make sense"""
    import math
    
    def dist(v1, v2):
        p1, p2 = NEW_POSITIONS[v1], NEW_POSITIONS[v2]
        return math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)
    
    checks = [
        ("Sad", ["Dark", "Night", "Romantic"], "Sadness connects to darkness and lost love"),
        ("Happy", ["Party", "Chill"], "Joy connects celebration and relaxation"),
        ("Dark", ["Night", "Sad", "Drive"], "Darkness connects night, sorrow, intensity"),
        ("Energy", ["Party", "Drive"], "Energy connects dancing and driving"),
        ("Chill", ["Happy", "Romantic"], "Calm connects contentment and tenderness"),
        ("Night", ["Dark", "Sad"], "Night connects darkness and melancholy"),
        ("Party", ["Energy", "Happy"], "Party connects excitement and joy"),
        ("Drive", ["Energy", "Dark"], "Driving connects intensity and moodiness"),
        ("Romantic", ["Sad", "Chill"], "Romance connects longing and tenderness"),
    ]
    
    print("\n" + "=" * 50)
    print("EMOTIONAL LOGIC CHECK:")
    print("=" * 50)
    
    all_pass = True
    for vibe, expected, reason in checks:
        distances = [(other, dist(vibe, other)) for other in NEW_POSITIONS if other != vibe]
        distances.sort(key=lambda x: x[1])
        actual_neighbors = [d[0] for d in distances[:3]]
        
        matches = [e for e in expected if e in actual_neighbors]
        status = "PASS" if len(matches) >= 2 else "WARN"
        if status == "WARN":
            all_pass = False
        
        print(f"  {vibe:12}: Want {expected}")
        print(f"               Got  {actual_neighbors} [{status}]")
    
    return all_pass

def create_new_manifold():
    """Create new manifold with repositioned meta-vibes"""
    
    project_root = Path(__file__).parent
    old_manifold_path = project_root / "data" / "manifold" / "emotional_manifold_COMPLETE.json"
    
    with open(old_manifold_path, 'r', encoding='utf-8') as f:
        manifold = json.load(f)
    
    # Update central vibe positions
    manifold['central_vibes']['positions'] = NEW_POSITIONS
    
    # Recalculate ALL sub-vibe coordinates based on their emotional compositions
    print("\n" + "=" * 50)
    print("RECALCULATING SUB-VIBE COORDINATES:")
    print("=" * 50)
    
    for sv_name, sv_data in manifold['sub_vibes'].items():
        composition = sv_data.get('emotional_composition', {})
        
        if composition:
            # Weighted average of meta-vibe positions
            total_x = 0
            total_y = 0
            total_weight = 0
            
            for meta_vibe, weight in composition.items():
                if meta_vibe in NEW_POSITIONS:
                    pos = NEW_POSITIONS[meta_vibe]
                    total_x += pos['x'] * weight
                    total_y += pos['y'] * weight
                    total_weight += weight
            
            if total_weight > 0:
                new_x = round(total_x / total_weight, 2)
                new_y = round(total_y / total_weight, 2)
                
                old_coords = sv_data.get('coordinates', {})
                sv_data['coordinates'] = {'x': new_x, 'y': new_y}
                
                print(f"  {sv_name[:30]:30} -> ({new_x:.0f}, {new_y:.0f})")
    
    # Update metadata
    manifold['metadata']['last_updated'] = datetime.now().isoformat()
    manifold['metadata']['manifold_version'] = "2.0"
    manifold['metadata']['redesign_note'] = "Repositioned meta-vibes for emotional logic adjacency"
    
    return manifold

def save_new_manifold(manifold):
    """Save new manifold, backing up old one"""
    
    project_root = Path(__file__).parent
    manifold_dir = project_root / "data" / "manifold"
    
    old_path = manifold_dir / "emotional_manifold_COMPLETE.json"
    backup_path = manifold_dir / f"emotional_manifold_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Backup old manifold
    if old_path.exists():
        import shutil
        shutil.copy2(old_path, backup_path)
        print(f"\n[BACKUP] Old manifold saved to: {backup_path.name}")
    
    # Save new manifold
    with open(old_path, 'w', encoding='utf-8') as f:
        json.dump(manifold, f, indent=2, ensure_ascii=False)
    
    print(f"[SAVED] New manifold saved to: {old_path.name}")

if __name__ == "__main__":
    print("MANIFOLD REDESIGN")
    print("=" * 50)
    
    # Show new layout
    calculate_distances()
    
    # Check emotional logic
    if check_emotional_logic():
        print("\n[OK] All emotional adjacencies look good!")
    else:
        print("\n[WARN] Some adjacencies may need tweaking")
    
    # Ask for confirmation
    print("\n" + "=" * 50)
    response = input("Create and save new manifold? (yes/no): ")
    
    if response.lower() == 'yes':
        new_manifold = create_new_manifold()
        save_new_manifold(new_manifold)
        print("\n[COMPLETE] Manifold redesigned!")
    else:
        print("\n[CANCELLED] No changes made.")
