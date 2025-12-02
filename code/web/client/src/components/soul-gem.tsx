import { useState, useEffect, useMemo } from 'react';

interface VibeScore {
  vibe: string;
  score: number;
}

interface SoulShardProps {
  songs: Array<{ sub_vibe?: string; meta_vibe?: string; mapped_subvibe?: string }>;
  size?: number;
}

// Meta-vibe colors
const VIBE_COLORS: Record<string, string> = {
  Happy:    'hsl(48, 70%, 55%)',
  Party:    'hsl(320, 65%, 55%)',
  Chill:    'hsl(168, 55%, 50%)',
  Energy:   'hsl(20, 65%, 55%)',
  Romantic: 'hsl(340, 60%, 60%)',
  Sad:      'hsl(210, 55%, 55%)',
  Drive:    'hsl(25, 65%, 52%)',
  Dark:     'hsl(262, 55%, 55%)',
  Night:    'hsl(240, 40%, 45%)',
};

const META_VIBES = ['Happy', 'Party', 'Chill', 'Energy', 'Romantic', 'Sad', 'Drive', 'Dark', 'Night'];

function calculateVibeScores(songs: SoulShardProps['songs']): VibeScore[] {
  const vibeCounts: Record<string, number> = {};
  
  songs.forEach(song => {
    const subvibe = song.sub_vibe || song.meta_vibe || song.mapped_subvibe || '';
    const metaVibe = subvibe.split(' - ')[0];
    if (META_VIBES.includes(metaVibe)) {
      vibeCounts[metaVibe] = (vibeCounts[metaVibe] || 0) + 1;
    }
  });

  const maxCount = Math.max(...Object.values(vibeCounts), 1);

  return META_VIBES.map(vibe => ({
    vibe,
    score: Math.max(((vibeCounts[vibe] || 0) / maxCount) * 100, 12), // min 12 for visibility
  }));
}

export function SoulGem({ songs, size = 260 }: SoulShardProps) {
  const [showDetails, setShowDetails] = useState(true);
  const [hasAnimated, setHasAnimated] = useState(false);

  const vibeScores = useMemo(() => calculateVibeScores(songs), [songs]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowDetails(false);
      setHasAnimated(true);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  const dominantVibe = useMemo(() => {
    return vibeScores.reduce((a, b) => a.score > b.score ? a : b);
  }, [vibeScores]);
  
  const glowColor = VIBE_COLORS[dominantVibe.vibe] || 'hsl(262, 55%, 55%)';
  
  // Calculate polygon points
  const center = size / 2;
  const maxRadius = size * 0.38;
  
  const points = useMemo(() => {
    return vibeScores.map((vibe, i) => {
      const angle = (i * 360 / vibeScores.length - 90) * (Math.PI / 180);
      const radius = (vibe.score / 100) * maxRadius;
      return {
        x: center + radius * Math.cos(angle),
        y: center + radius * Math.sin(angle),
        vibe: vibe.vibe,
        score: vibe.score,
        angle,
      };
    });
  }, [vibeScores, center, maxRadius]);
  
  // Create polygon path
  const pathData = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
    .join(' ') + ' Z';

  // Unique gradient ID
  const gradientId = useMemo(() => `shardGrad-${Math.random().toString(36).substr(2, 9)}`, []);
  const glowId = useMemo(() => `shardGlow-${Math.random().toString(36).substr(2, 9)}`, []);

  return (
    <div 
      className="relative cursor-pointer flex-shrink-0 transition-transform duration-300 hover:scale-105"
      style={{ width: size, height: size }}
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => hasAnimated && setShowDetails(false)}
    >
      {/* Outer ambient glow */}
      <div 
        className="absolute rounded-full transition-all duration-700"
        style={{ 
          top: '10%',
          left: '10%',
          right: '10%',
          bottom: '10%',
          background: `radial-gradient(circle, ${glowColor} 0%, transparent 60%)`,
          opacity: showDetails ? 0.2 : 0.4,
          filter: 'blur(30px)',
        }}
      />
      
      {/* The crystal shard SVG */}
      <svg 
        width={size} 
        height={size} 
        className="relative z-10"
        style={{ overflow: 'visible' }}
      >
        <defs>
          {/* Gradient fill for gem effect */}
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.3)" />
            <stop offset="30%" stopColor={glowColor} stopOpacity="0.6" />
            <stop offset="100%" stopColor={glowColor} stopOpacity="0.25" />
          </linearGradient>
          
          {/* Glow filter */}
          <filter id={glowId} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        
        {/* Main shard shape with sharp miter joins */}
        <path
          d={pathData}
          fill={`url(#${gradientId})`}
          stroke={glowColor}
          strokeWidth={showDetails ? 2 : 2.5}
          strokeLinejoin="miter"
          strokeMiterlimit="10"
          filter={showDetails ? 'none' : `url(#${glowId})`}
          className="transition-all duration-700"
          style={{
            opacity: showDetails ? 0.7 : 0.9,
          }}
        />
        
        {/* Internal facet lines from center to each point */}
        {points.map((p, i) => (
          <line
            key={`facet-${i}`}
            x1={center}
            y1={center}
            x2={p.x}
            y2={p.y}
            stroke="rgba(255,255,255,0.12)"
            strokeWidth="1"
            className="transition-opacity duration-700"
            style={{ opacity: showDetails ? 0.8 : 0.4 }}
          />
        ))}
        
        {/* Secondary facet lines connecting adjacent points through center area */}
        {points.map((p, i) => {
          const next = points[(i + 1) % points.length];
          const midX = (p.x + next.x) / 2;
          const midY = (p.y + next.y) / 2;
          return (
            <line
              key={`facet2-${i}`}
              x1={center}
              y1={center}
              x2={midX}
              y2={midY}
              stroke="rgba(255,255,255,0.06)"
              strokeWidth="0.5"
              className="transition-opacity duration-700"
              style={{ opacity: showDetails ? 0.6 : 0.3 }}
            />
          );
        })}
        
        {/* Glossy highlight / gleam at top */}
        <ellipse
          cx={center - size * 0.05}
          cy={center - size * 0.12}
          rx={size * 0.08}
          ry={size * 0.04}
          fill="rgba(255,255,255,0.25)"
          className="transition-opacity duration-700"
          style={{ 
            opacity: showDetails ? 0.3 : 0.6,
            filter: 'blur(2px)',
          }}
        />
        
        {/* Small secondary gleam */}
        <ellipse
          cx={center + size * 0.08}
          cy={center - size * 0.06}
          rx={size * 0.03}
          ry={size * 0.015}
          fill="rgba(255,255,255,0.2)"
          className="transition-opacity duration-700"
          style={{ 
            opacity: showDetails ? 0.2 : 0.5,
            filter: 'blur(1px)',
          }}
        />
        
        {/* Vibe labels - fade out on crystallization */}
        {points.map((p, i) => {
          // Position labels outside the shape
          const labelRadius = maxRadius + 25;
          const labelX = center + labelRadius * Math.cos(p.angle);
          const labelY = center + labelRadius * Math.sin(p.angle);
          
          return (
            <text
              key={`label-${i}`}
              x={labelX}
              y={labelY}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="rgba(255,255,255,0.5)"
              fontSize="10"
              className="transition-opacity duration-700"
              style={{ opacity: showDetails ? 1 : 0 }}
            >
              {p.vibe}
            </text>
          );
        })}
      </svg>
    </div>
  );
}
