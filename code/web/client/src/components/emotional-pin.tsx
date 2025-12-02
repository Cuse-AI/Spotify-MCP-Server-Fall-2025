import { useMemo } from "react";

// Meta-vibe colors and their positions on the manifold
const META_VIBES = {
  Happy:    { x: 500, y: 200, color: "#FFD93D" },   // Bright yellow
  Party:    { x: 300, y: 250, color: "#E91E8C" },   // Magenta
  Chill:    { x: 700, y: 250, color: "#6DD5C3" },   // Teal
  Energy:   { x: 250, y: 450, color: "#FF6B35" },   // Orange-red
  Romantic: { x: 750, y: 450, color: "#FF85A2" },   // Pink
  Sad:      { x: 500, y: 600, color: "#4A90D9" },   // Blue
  Drive:    { x: 200, y: 650, color: "#F97316" },   // Electric orange
  Dark:     { x: 350, y: 800, color: "#8B5CF6" },   // Purple
  Night:    { x: 550, y: 850, color: "#2D3047" },   // Deep indigo
};

interface EmotionalPinProps {
  x?: number;
  y?: number;
  spotifyId?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

/**
 * Calculate distance between two points
 */
function distance(x1: number, y1: number, x2: number, y2: number): number {
  return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

/**
 * Get the top 3 closest vibes with their colors and weights
 */
function getClosestVibes(x: number, y: number): Array<{ name: string; color: string; weight: number }> {
  const vibesWithDistance = Object.entries(META_VIBES).map(([name, vibe]) => ({
    name,
    color: vibe.color,
    dist: distance(x, y, vibe.x, vibe.y)
  }));
  
  // Sort by distance (closest first)
  vibesWithDistance.sort((a, b) => a.dist - b.dist);
  
  // Take top 3
  const top3 = vibesWithDistance.slice(0, 3);
  
  // Convert distances to weights (inverse, closer = higher weight)
  // Use exponential falloff for more dramatic color separation
  const weights = top3.map(v => ({
    name: v.name,
    color: v.color,
    weight: Math.pow(1 / (v.dist + 50), 2) // Exponential falloff
  }));
  
  // Normalize weights
  const totalWeight = weights.reduce((sum, w) => sum + w.weight, 0);
  weights.forEach(w => w.weight = w.weight / totalWeight);
  
  return weights;
}

/**
 * Create a radial gradient from the weighted colors
 */
function createGradient(x: number, y: number): string {
  const vibes = getClosestVibes(x, y);
  
  if (vibes.length === 0) {
    return "linear-gradient(135deg, #8B5CF6, #4A90D9)";
  }
  
  // Primary color (closest vibe) in center, blending outward
  const primary = vibes[0];
  const secondary = vibes[1] || vibes[0];
  const tertiary = vibes[2] || vibes[1] || vibes[0];
  
  // Create a more interesting multi-stop gradient
  // Radial from center with primary, transitioning to secondary/tertiary
  return `radial-gradient(circle at 30% 30%, 
    ${primary.color} 0%, 
    ${blendColors(primary.color, secondary.color, 0.5)} 40%, 
    ${secondary.color} 70%,
    ${blendColors(secondary.color, tertiary.color, 0.5)} 100%)`;
}

/**
 * Blend two hex colors
 */
function blendColors(color1: string, color2: string, ratio: number): string {
  const hex1 = color1.replace("#", "");
  const hex2 = color2.replace("#", "");
  
  const r1 = parseInt(hex1.slice(0, 2), 16);
  const g1 = parseInt(hex1.slice(2, 4), 16);
  const b1 = parseInt(hex1.slice(4, 6), 16);
  
  const r2 = parseInt(hex2.slice(0, 2), 16);
  const g2 = parseInt(hex2.slice(2, 4), 16);
  const b2 = parseInt(hex2.slice(4, 6), 16);
  
  const r = Math.round(r1 * (1 - ratio) + r2 * ratio);
  const g = Math.round(g1 * (1 - ratio) + g2 * ratio);
  const b = Math.round(b1 * (1 - ratio) + b2 * ratio);
  
  return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}

/**
 * Get Spotify URL from ID/URI
 */
function getSpotifyUrl(spotifyId?: string): string | null {
  if (!spotifyId) return null;
  const id = spotifyId.replace('spotify:track:', '');
  return `https://open.spotify.com/track/${id}`;
}

/**
 * EmotionalPin - A pin-shaped visual showing the song's emotional blend
 */
export function EmotionalPin({ 
  x, 
  y,
  spotifyId,
  size = "md",
  className = ""
}: EmotionalPinProps) {
  
  const gradient = useMemo(() => {
    if (x === undefined || y === undefined) {
      return "radial-gradient(circle at 30% 30%, #8B5CF6 0%, #6366F1 50%, #4A90D9 100%)";
    }
    return createGradient(x, y);
  }, [x, y]);
  
  const spotifyUrl = getSpotifyUrl(spotifyId);
  
  // Size configurations
  const sizes = {
    sm: { width: 40, height: 52, pointSize: 8 },
    md: { width: 52, height: 68, pointSize: 10 },
    lg: { width: 64, height: 84, pointSize: 12 }
  };
  
  const { width, height, pointSize } = sizes[size];
  const bodyHeight = height - pointSize;
  
  const pinContent = (
    <div className="relative" style={{ width, height }}>
      {/* Main pin body - rounded top, pointed bottom */}
      <div 
        className="absolute top-0 left-0 right-0 overflow-hidden"
        style={{ 
          height: bodyHeight,
          borderRadius: `${width/2}px ${width/2}px 4px 4px`,
          background: gradient,
          boxShadow: "0 4px 12px rgba(0,0,0,0.3), inset 0 2px 4px rgba(255,255,255,0.2)"
        }}
      >
        {/* Shine effect */}
        <div 
          className="absolute inset-0"
          style={{
            background: "linear-gradient(135deg, rgba(255,255,255,0.4) 0%, transparent 40%, transparent 60%, rgba(0,0,0,0.1) 100%)"
          }}
        />
        
        {/* Inner highlight */}
        <div 
          className="absolute"
          style={{
            top: "15%",
            left: "20%",
            width: "30%",
            height: "30%",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%)"
          }}
        />
      </div>
      
      {/* Pin point (triangle at bottom) */}
      <div 
        className="absolute left-1/2 -translate-x-1/2"
        style={{
          top: bodyHeight - 2,
          width: 0,
          height: 0,
          borderLeft: `${pointSize}px solid transparent`,
          borderRight: `${pointSize}px solid transparent`,
          borderTop: `${pointSize + 4}px solid`,
          borderTopColor: gradient.includes("#") ? "#6366F1" : "#6366F1",
          filter: "drop-shadow(0 2px 2px rgba(0,0,0,0.3))"
        }}
      />
      
      {/* Hover overlay with Spotify icon hint */}
      {spotifyUrl && (
        <div 
          className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
          style={{ 
            height: bodyHeight,
            borderRadius: `${width/2}px ${width/2}px 4px 4px`,
            background: "rgba(0,0,0,0.5)"
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
            <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
          </svg>
        </div>
      )}
    </div>
  );
  
  if (spotifyUrl) {
    return (
      <a
        href={spotifyUrl}
        target="_blank"
        rel="noopener noreferrer"
        className={`group inline-block ${className}`}
        title="Open in Spotify"
      >
        {pinContent}
      </a>
    );
  }
  
  return <div className={className}>{pinContent}</div>;
}

export { META_VIBES };
