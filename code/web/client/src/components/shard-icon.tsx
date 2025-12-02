import { useMemo } from "react";

// Meta-vibe colors and their positions on the manifold
const META_VIBES = {
  Happy:    { x: 500, y: 200, color: "#FFD93D" },
  Party:    { x: 300, y: 250, color: "#E91E8C" },
  Chill:    { x: 700, y: 250, color: "#6DD5C3" },
  Energy:   { x: 250, y: 450, color: "#FF6B35" },
  Romantic: { x: 750, y: 450, color: "#FF85A2" },
  Sad:      { x: 500, y: 600, color: "#4A90D9" },
  Drive:    { x: 200, y: 650, color: "#F97316" },
  Dark:     { x: 350, y: 800, color: "#8B5CF6" },
  Night:    { x: 550, y: 850, color: "#2D3047" },
};

interface ShardIconProps {
  x?: number;
  y?: number;
  spotifyId?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

function distance(x1: number, y1: number, x2: number, y2: number): number {
  return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

function getClosestVibes(x: number, y: number): Array<{ name: string; color: string; weight: number }> {
  const vibesWithDistance = Object.entries(META_VIBES).map(([name, vibe]) => ({
    name,
    color: vibe.color,
    dist: distance(x, y, vibe.x, vibe.y)
  }));
  
  vibesWithDistance.sort((a, b) => a.dist - b.dist);
  const top3 = vibesWithDistance.slice(0, 3);
  
  // Exponential falloff for more dramatic color separation
  const weights = top3.map(v => ({
    name: v.name,
    color: v.color,
    weight: Math.pow(1 / (v.dist + 50), 2)
  }));
  
  const totalWeight = weights.reduce((sum, w) => sum + w.weight, 0);
  weights.forEach(w => w.weight = w.weight / totalWeight);
  
  return weights;
}

function getSpotifyUrl(spotifyId?: string): string | null {
  if (!spotifyId) return null;
  const id = spotifyId.replace('spotify:track:', '');
  return `https://open.spotify.com/track/${id}`;
}

/**
 * ShardIcon - Pottery shard with gradient fill based on emotional coordinates
 * Represents the archaeological "midden" theme - treasures excavated from human emotion
 */
export function ShardIcon({ 
  x, 
  y,
  spotifyId,
  size = "md",
  className = ""
}: ShardIconProps) {
  
  const gradientId = useMemo(() => `shard-gradient-${Math.random().toString(36).substr(2, 9)}`, []);
  
  const colors = useMemo(() => {
    if (x === undefined || y === undefined) {
      // Default purple gradient for unknown coordinates
      return [
        { color: "#8B5CF6", offset: 0 },
        { color: "#6366F1", offset: 50 },
        { color: "#4A90D9", offset: 100 }
      ];
    }
    
    const vibes = getClosestVibes(x, y);
    let offset = 0;
    return vibes.map((v) => {
      const stop = { color: v.color, offset };
      offset += v.weight * 100;
      return stop;
    });
  }, [x, y]);
  
  const spotifyUrl = getSpotifyUrl(spotifyId);
  
  const sizes = {
    sm: { width: 32, height: 38 },
    md: { width: 48, height: 58 },
    lg: { width: 64, height: 77 }
  };
  
  const { width, height } = sizes[size];
  
  const svgContent = (
    <svg 
      width={width} 
      height={height} 
      viewBox="0 0 48 58" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className="drop-shadow-lg"
    >
      <defs>
        {/* Main gradient fill */}
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
          {colors.map((c, i) => (
            <stop key={i} offset={`${c.offset}%`} stopColor={c.color} />
          ))}
        </linearGradient>
        
        {/* Gloss highlight gradient for "bubble pop" effect */}
        <linearGradient id={`${gradientId}-gloss`} x1="0%" y1="0%" x2="50%" y2="100%">
          <stop offset="0%" stopColor="white" stopOpacity="0.25" />
          <stop offset="40%" stopColor="white" stopOpacity="0.08" />
          <stop offset="100%" stopColor="white" stopOpacity="0" />
        </linearGradient>
      </defs>
      
      {/* Main shard shape - broken pottery fragment */}
      <path 
        d="M8 4 
           L36 2 
           L42 12 
           L40 28 
           L44 36 
           L38 48 
           L24 56 
           L10 52 
           L4 40 
           L6 20 
           Z" 
        fill={`url(#${gradientId})`}
      />
      
      {/* Gloss highlight overlay (top-left area) */}
      <path 
        d="M10 8 L28 5 L24 22 L8 18 Z"
        fill={`url(#${gradientId}-gloss)`}
      />
      
      {/* Subtle inner edge highlight */}
      <path 
        d="M8 4 
           L36 2 
           L42 12 
           L40 28 
           L44 36 
           L38 48 
           L24 56 
           L10 52 
           L4 40 
           L6 20 
           Z" 
        fill="none"
        stroke="white"
        strokeOpacity="0.1"
        strokeWidth="1"
      />
    </svg>
  );
  
  if (spotifyUrl) {
    return (
      <a
        href={spotifyUrl}
        target="_blank"
        rel="noopener noreferrer"
        className={`group inline-block transition-transform hover:scale-110 ${className}`}
        title="Open in Spotify"
      >
        {svgContent}
      </a>
    );
  }
  
  return <div className={className}>{svgContent}</div>;
}

export { META_VIBES };
