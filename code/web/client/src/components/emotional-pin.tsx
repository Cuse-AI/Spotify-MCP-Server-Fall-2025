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

interface EmotionalPinProps {
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
 * EmotionalPin - SVG-based pin with gradient fill
 */
export function EmotionalPin({ 
  x, 
  y,
  spotifyId,
  size = "md",
  className = ""
}: EmotionalPinProps) {
  
  const gradientId = useMemo(() => `pin-gradient-${Math.random().toString(36).substr(2, 9)}`, []);
  
  const colors = useMemo(() => {
    if (x === undefined || y === undefined) {
      return [
        { color: "#8B5CF6", offset: 0 },
        { color: "#6366F1", offset: 50 },
        { color: "#4A90D9", offset: 100 }
      ];
    }
    
    const vibes = getClosestVibes(x, y);
    let offset = 0;
    return vibes.map((v, i) => {
      const stop = { color: v.color, offset };
      offset += v.weight * 100;
      return stop;
    });
  }, [x, y]);
  
  const spotifyUrl = getSpotifyUrl(spotifyId);
  
  const sizes = {
    sm: { width: 36, height: 44 },
    md: { width: 48, height: 58 },
    lg: { width: 60, height: 72 }
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
        {/* Radial gradient for the fill */}
        <radialGradient id={gradientId} cx="30%" cy="30%" r="70%" fx="30%" fy="30%">
          {colors.map((c, i) => (
            <stop key={i} offset={`${c.offset}%`} stopColor={c.color} />
          ))}
        </radialGradient>
        
        {/* Shine overlay gradient */}
        <linearGradient id={`${gradientId}-shine`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="white" stopOpacity="0.4" />
          <stop offset="40%" stopColor="white" stopOpacity="0" />
          <stop offset="100%" stopColor="black" stopOpacity="0.1" />
        </linearGradient>
      </defs>
      
      {/* Pin shape - teardrop/location marker */}
      <path 
        d="M24 0C10.745 0 0 10.745 0 24C0 37.255 24 58 24 58C24 58 48 37.255 48 24C48 10.745 37.255 0 24 0Z"
        fill={`url(#${gradientId})`}
      />
      
      {/* Shine overlay */}
      <path 
        d="M24 0C10.745 0 0 10.745 0 24C0 37.255 24 58 24 58C24 58 48 37.255 48 24C48 10.745 37.255 0 24 0Z"
        fill={`url(#${gradientId}-shine)`}
      />
      
      {/* Inner circle highlight */}
      <circle cx="24" cy="22" r="10" fill="white" fillOpacity="0.15" />
      <circle cx="24" cy="22" r="6" fill="white" fillOpacity="0.1" />
      
      {/* Small highlight dot */}
      <circle cx="16" cy="14" r="4" fill="white" fillOpacity="0.3" />
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
