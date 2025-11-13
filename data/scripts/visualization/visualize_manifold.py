import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# Load the complete manifold
with open('ananki_outputs/emotional_manifold_COMPLETE.json', 'r', encoding='utf-8') as f:
    manifold = json.load(f)

central_positions = manifold['central_vibes']['positions']
sub_vibes = manifold['sub_vibes']

# Create figure
fig, ax = plt.subplots(figsize=(20, 20))
ax.set_xlim(-50, 1050)
ax.set_ylim(-50, 1050)
ax.set_aspect('equal')
ax.set_facecolor('#0a0a0a')
fig.patch.set_facecolor('#0a0a0a')

# Color map for central vibes
vibe_colors = {
    'Sad': '#4A5899', 'Happy': '#FFD700', 'Chill': '#87CEEB',
    'Anxious': '#FF6B6B', 'Energy': '#FF4500', 'Dark': '#2F2F4F',
    'Introspective': '#9370DB', 'Romantic': '#FF69B4', 'Nostalgic': '#DDA0DD',
    'Night': '#191970', 'Drive': '#4682B4', 'Party': '#FF1493',
    'Angry': '#DC143C', 'Bitter': '#8B4513', 'Hopeful': '#FFA500',
    'Excited': '#FFD700', 'Jealous': '#228B22', 'Peaceful': '#E0FFE0',
    'Playful': '#FF69B4', 'Chaotic': '#8B0000', 'Bored': '#696969',
    'Grateful': '#DAA520', 'Confident': '#FF8C00'
}

# Draw connections between related central vibes (from our relationship map)
with open('ananki_outputs/central_vibe_relationships.json', 'r', encoding='utf-8') as f:
    relationships = json.load(f)

for vibe, data in relationships['central_vibes'].items():
    x1, y1 = central_positions[vibe]['x'], central_positions[vibe]['y']
    for connected_vibe in data['connects_to']:
        if connected_vibe in central_positions:
            x2, y2 = central_positions[connected_vibe]['x'], central_positions[connected_vibe]['y']
            ax.plot([x1, x2], [y1, y2], color='#333333', linewidth=0.5, alpha=0.3, zorder=1)

# Plot central vibes (larger circles)
for vibe_name, pos in central_positions.items():
    color = vibe_colors.get(vibe_name, '#FFFFFF')
    ax.scatter(pos['x'], pos['y'], s=800, c=color, edgecolors='white', 
               linewidths=2, alpha=0.9, zorder=3)
    ax.text(pos['x'], pos['y'], vibe_name, fontsize=10, weight='bold',
            ha='center', va='center', color='white', zorder=4)

# Plot sub-vibes (smaller circles)
for sub_name, sub_data in sub_vibes.items():
    coords = sub_data['coordinates']
    # Determine color based on dominant emotion
    dominant_vibe = max(sub_data['emotional_composition'].items(), key=lambda x: x[1])[0]
    color = vibe_colors.get(dominant_vibe, '#FFFFFF')
    
    ax.scatter(coords['x'], coords['y'], s=50, c=color, edgecolors='white',
               linewidths=0.5, alpha=0.6, zorder=2)

# Title and labels
ax.set_title('THE TAPESTRY: Emotional Manifold\n114 Sub-Vibes across 23 Central Emotions', 
             fontsize=24, weight='bold', color='white', pad=20)
ax.set_xlabel('Emotional Dimension X', fontsize=14, color='white')
ax.set_ylabel('Emotional Dimension Y', fontsize=14, color='white')

# Remove ticks
ax.set_xticks([])
ax.set_yticks([])

# Create legend
legend_elements = [Line2D([0], [0], marker='o', color='w', label='Central Vibes',
                          markerfacecolor='white', markersize=15, linestyle='None'),
                   Line2D([0], [0], marker='o', color='w', label='Sub-Vibes',
                          markerfacecolor='white', markersize=8, linestyle='None'),
                   Line2D([0], [0], color='#333333', linewidth=2, label='Emotional Connections')]
ax.legend(handles=legend_elements, loc='upper right', fontsize=12, 
          facecolor='#1a1a1a', edgecolor='white', labelcolor='white')

# Grid
ax.grid(True, alpha=0.1, color='white')

plt.tight_layout()
plt.savefig('ananki_outputs/emotional_manifold_visualization.png', 
            dpi=300, facecolor='#0a0a0a', edgecolor='none')
print('\nVisualization saved to: ananki_outputs/emotional_manifold_visualization.png')
print('The Tapestry is now visible!')
