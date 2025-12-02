import { useMemo } from "react";
import { ExternalLink } from "lucide-react";

// Meta-vibe colors and their positions on the manifold (from redesigned manifold)
const META_VIBES = {
  Happy:    { x: 500, y: 200, color: "#FFD93D" },   // Bright yellow - joy
  Party:    { x: 300, y: 250, color: "#E91E8C" },   // Magenta - celebration
  Chill:    { x: 700, y: 250, color: "#6DD5C3" },   // Teal - calm
  Energy:   { x: 250, y: 450, color: "#FF6B35" },   // Orange-red - intensity
  Romantic: { x: 750, y: 450, color: "#FF85A2" },   // Pink - love
  Sad:      { x: 500, y: 600, color: "#4A90D9" },   // Blue - melancholy
  Drive:    { x: 200, y: 650, color: "#F97316" },   // Electric orange - motion
  Dark:     { x: 350, y: 800, color: "#8B5CF6" },   // Purple - mysterious
  Night:    { x: 550, y: 850, color: "#2D3047" },   // Deep indigo - nocturnal
};

// Fallback gradient
const FALLBACK_GRADIENT = "linear-gradient(135deg, #8B5CF6 0%, #6366F1 50%, #4A90D9 100%)";

interface EmotionalPinProps {
  x?: number;
  y?: number;
  spotifyId?: string;  // Can be URI or just the ID
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
 * Calculate color weights based on proximity to meta-vibes
 */
function calculateColorWeights(x: number, y: number): Array<{ color: string; weight: number }> {
  const weights: Array<{ name: string; color: string; weight: number }> = [];
  
  for (const [name, vibe] of Object.entries(META_VIBES)) {
    const dist = distance(x, y, vibe.x, vibe.y);
    const weight = 1 / (dist + 1);
    weights.push({ name, color: vibe.color, weight });
  }
  
  const totalWeight = weights.reduce((sum, w) => sum + w.weight, 0);
  weights.forEach(w => w.weight = w.weight / totalWeight);
  weights.sort((a, b) => b.weight - a.weight);
  
  return weights.slice(0, 3);
}

/**
 * Convert Spotify URI/ID to web URL
 */
function getSpotifyUrl(spotifyId?: string): string | null {
  if (!spotifyId) return null;
  
  // Extract ID from URI if needed (spotify:track:XXX -> XXX)
  const id = spotifyId.replace('spotify:track:', '');
  return `https://open.spotify.com/track/${id}`;
}

/**
 * EmotionalPin - A visual representation of a song's position on the emotional manifold
 * 
 * Creates a gradient based on the song's x,y coordinates.
 * Clickable to open the track on Spotify.
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
      return FALLBACK_GRADIENT;
    }
    
    const colorWeights = calculateColorWeights(x, y);
    
    if (colorWeights.length === 0) {
      return FALLBACK_GRADIENT;
    }
    
    if (colorWeights.length === 1) {
      const c = colorWeights[0];
      return `linear-gradient(135deg, ${c.color} 0%, ${adjustColor(c.color, -30)} 100%)`;
    }
    
    const topColors = colorWeights.slice(0, 3);
    const topTotal = topColors.reduce((sum, c) => sum + c.weight, 0);
    
    const stops: string[] = [];
    let position = 0;
    
    topColors.forEach((c, i) => {
      const normalizedWeight = c.weight / topTotal;
      const startPos = position;
      position += normalizedWeight * 100;
      
      if (i === 0) {
        stops.push(`${c.color} ${startPos}%`);
      }
      stops.push(`${c.color} ${Math.min(position, 100)}%`);
    });
    
    return `linear-gradient(135deg, ${stops.join(", ")})`;
  }, [x, y]);
  
  const spotifyUrl = getSpotifyUrl(spotifyId);
  
  // Size classes
  const sizeClasses = {
    sm: "w-10 h-10",
    md: "w-16 h-16", 
    lg: "w-20 h-20"
  };
  
  const pinContent = (
    <>
      {/* Subtle shine effect */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          background: "linear-gradient(135deg, rgba(255,255,255,0.4) 0%, transparent 50%, rgba(0,0,0,0.1) 100%)"
        }}
      />
      
      {/* Inner glow */}
      <div 
        className="absolute inset-1 rounded opacity-20"
        style={{
          background: "radial-gradient(circle at 30% 30%, rgba(255,255,255,0.8) 0%, transparent 60%)"
        }}
      />
      
      {/* Spotify link icon on hover */}
      {spotifyUrl && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg">
          <ExternalLink className="w-5 h-5 text-white" />
        </div>
      )}
    </>
  );
  
  // If we have a Spotify URL, wrap in a link
  if (spotifyUrl) {
    return (
      <a
        href={spotifyUrl}
        target="_blank"
        rel="noopener noreferrer"
        className={`${sizeClasses[size]} rounded-lg shadow-lg relative overflow-hidden block group cursor-pointer ${className}`}
        style={{ 
          background: gradient,
          boxShadow: "0 4px 12px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.2)"
        }}
        title="Open in Spotify"
      >
        {pinContent}
      </a>
    );
  }
  
  // No Spotify link, just display
  return (
    <div 
      className={`${sizeClasses[size]} rounded-lg shadow-lg relative overflow-hidden ${className}`}
      style={{ 
        background: gradient,
        boxShadow: "0 4px 12px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.2)"
      }}
    >
      {pinContent}
    </div>
  );
}

/**
 * Adjusts a hex color's brightness
 */
function adjustColor(color: string, amount: number): string {
  const hex = color.replace("#", "");
  const r = Math.max(0, Math.min(255, parseInt(hex.slice(0, 2), 16) + amount));
  const g = Math.max(0, Math.min(255, parseInt(hex.slice(2, 4), 16) + amount));
  const b = Math.max(0, Math.min(255, parseInt(hex.slice(4, 6), 16) + amount));
  return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}

export { META_VIBES };
