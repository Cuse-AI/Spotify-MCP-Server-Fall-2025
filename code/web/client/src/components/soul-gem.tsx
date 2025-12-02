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

export function SoulGem({ songs, size = 240 }: SoulShardProps) {
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

  // Calculate polygon points with seeded jitter for uncut/organic edges
  const center = size / 2;
  const maxRadius = size * 0.38;

  // Seeded jitter function for consistent randomness
  const jitter = (val: number, seed: number, amount: number = 4) => {
    const rand = Math.sin(seed * 12345.6789) * 0.5 + 0.5;
    return val + (rand - 0.5) * amount;
  };

  // Front face points (outer)
  const points = useMemo(() => {
    return vibeScores.map((vibe, i) => {
      const angle = (i * 360 / vibeScores.length - 90) * (Math.PI / 180);
      const radius = (vibe.score / 100) * maxRadius;
      return {
        x: jitter(center + radius * Math.cos(angle), i, 4),
        y: jitter(center + radius * Math.sin(angle), i + 100, 4),
        vibe: vibe.vibe,
        score: vibe.score,
        angle,
      };
    });
  }, [vibeScores, center, maxRadius]);

  // Back face points (inner, scaled and offset for 3D depth)
  const innerScale = 0.6;
  const depthOffset = 15;
  const innerPoints = useMemo(() => {
    return points.map(p => ({
      x: center + (p.x - center) * innerScale,
      y: center + (p.y - center) * innerScale + depthOffset,
      vibe: p.vibe,
    }));
  }, [points, center]);

  // Create polygon path for front face with micro-vertices for rougher edges
  const pathData = useMemo(() => {
    let path = `M ${points[0].x.toFixed(1)} ${points[0].y.toFixed(1)} `;
    points.forEach((p, i) => {
      const next = points[(i + 1) % points.length];
      // Add subtle mid-point for organic edge variation
      const midX = (p.x + next.x) / 2 + Math.sin(i * 7) * 2;
      const midY = (p.y + next.y) / 2 + Math.cos(i * 7) * 2;
      path += `L ${midX.toFixed(1)} ${midY.toFixed(1)} L ${next.x.toFixed(1)} ${next.y.toFixed(1)} `;
    });
    return path;
  }, [points]);

  // Back face path
  const innerPathData = useMemo(() => {
    return innerPoints.map((p, i) => {
      if (i === 0) return `M ${p.x.toFixed(1)} ${p.y.toFixed(1)}`;
      return `L ${p.x.toFixed(1)} ${p.y.toFixed(1)}`;
    }).join(' ') + ' Z';
  }, [innerPoints]);

  // Unique gradient ID
  const gradientId = useMemo(() => `shardGrad-${Math.random().toString(36).substr(2, 9)}`, []);
  const glowId = useMemo(() => `shardGlow-${Math.random().toString(36).substr(2, 9)}`, []);

  return (
    <div
      className="relative cursor-pointer flex-shrink-0 gem-breathe"
      style={{ width: size, height: size }}
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => hasAnimated && setShowDetails(false)}
    >
      {/* Outer ambient glow - MORE prominent when crystallized */}
      <div 
        className="absolute rounded-full transition-all duration-700"
        style={{ 
          top: '5%',
          left: '5%',
          right: '5%',
          bottom: '5%',
          background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)`,
          opacity: showDetails ? 0.25 : 0.6,
          filter: 'blur(35px)',
        }}
      />
      
      {/* Secondary inner glow for depth */}
      <div 
        className="absolute rounded-full transition-all duration-700"
        style={{ 
          top: '20%',
          left: '20%',
          right: '20%',
          bottom: '20%',
          background: `radial-gradient(circle, rgba(255,255,255,0.15) 0%, ${glowColor} 40%, transparent 70%)`,
          opacity: showDetails ? 0.1 : 0.35,
          filter: 'blur(20px)',
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
          {/* Radial gradient - LIGHT center fading to DARK edges (like a real gem) */}
          <radialGradient id={gradientId} cx="40%" cy="35%" r="65%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.45)" />
            <stop offset="30%" stopColor={glowColor} stopOpacity="0.4" />
            <stop offset="70%" stopColor="hsl(262, 50%, 30%)" stopOpacity="0.35" />
            <stop offset="100%" stopColor="hsl(262, 50%, 15%)" stopOpacity="0.3" />
          </radialGradient>

          {/* Linear gradient for depth edges - darker for 3D effect */}
          <linearGradient id={`${gradientId}-edge`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={glowColor} stopOpacity="0.9" />
            <stop offset="100%" stopColor="hsl(262, 60%, 25%)" stopOpacity="0.7" />
          </linearGradient>

          {/* Glow filter for crystallized state - stronger */}
          <filter id={glowId} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="10" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          
          {/* Liquid NFT sheen - sweeping highlight for plastic look */}
          <linearGradient id="liquidSheen" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.5)" />
            <stop offset="20%" stopColor="rgba(255,255,255,0.15)" />
            <stop offset="40%" stopColor="rgba(255,255,255,0.02)" />
            <stop offset="60%" stopColor="rgba(255,255,255,0.1)" />
            <stop offset="80%" stopColor="rgba(255,255,255,0.02)" />
            <stop offset="100%" stopColor="rgba(200,180,255,0.15)" />
          </linearGradient>
          
          {/* Inner glow for depth */}
          <radialGradient id="innerGlow" cx="30%" cy="25%" r="60%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.25)" />
            <stop offset="50%" stopColor="rgba(168,85,247,0.1)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0)" />
          </radialGradient>
        </defs>

        {/* === RADAR GRID LINES === */}

        {/* Concentric circles at 25%, 50%, 75%, 100% */}
        {[0.25, 0.5, 0.75, 1].map((scale, i) => (
          <circle
            key={`ring-${i}`}
            cx={center}
            cy={center}
            r={maxRadius * scale}
            fill="none"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth="1"
            className="transition-opacity duration-700"
            style={{ opacity: showDetails ? 0.6 : 0.15 }}
          />
        ))}

        {/* Radial spokes from center to each vibe point */}
        {vibeScores.map((_, i) => {
          const angle = (i * 360 / vibeScores.length - 90) * (Math.PI / 180);
          return (
            <line
              key={`spoke-${i}`}
              x1={center}
              y1={center}
              x2={center + maxRadius * Math.cos(angle)}
              y2={center + maxRadius * Math.sin(angle)}
              stroke="rgba(255,255,255,0.06)"
              strokeWidth="1"
              className="transition-opacity duration-700"
              style={{ opacity: showDetails ? 0.5 : 0.15 }}
            />
          );
        })}

        {/* === BACK FACE (rendered first, more transparent) === */}
        <path
          d={innerPathData}
          fill="hsl(262, 50%, 35%)"
          fillOpacity="0.2"
          stroke="hsl(262, 60%, 50%)"
          strokeWidth="1"
          strokeOpacity="0.4"
          className="transition-all duration-700"
          style={{
            opacity: showDetails ? 0.6 : 0.8,
          }}
        />

        {/* === CONNECTING DEPTH EDGES === */}
        {points.map((p, i) => (
          <line
            key={`depth-edge-${i}`}
            x1={p.x}
            y1={p.y}
            x2={innerPoints[i].x}
            y2={innerPoints[i].y}
            stroke={`url(#${gradientId}-edge)`}
            strokeWidth="1.5"
            strokeOpacity="0.5"
            className="transition-all duration-700"
            style={{
              opacity: showDetails ? 0.5 : 0.7,
            }}
          />
        ))}

        {/* === FRONT FACE (rendered on top, brighter) === */}
        <path
          d={pathData}
          fill={`url(#${gradientId})`}
          stroke={glowColor}
          strokeWidth={showDetails ? 2 : 2.5}
          strokeLinejoin="round"
          strokeLinecap="round"
          filter={showDetails ? 'none' : `url(#${glowId})`}
          className="transition-all duration-700"
          style={{
            opacity: showDetails ? 0.6 : 0.95,
          }}
        />
        
        {/* Inner glow layer - depth effect */}
        <path
          d={pathData}
          fill="url(#innerGlow)"
          stroke="none"
          className="transition-opacity duration-700 pointer-events-none"
          style={{
            opacity: showDetails ? 0 : 0.7,
          }}
        />
        
        {/* Liquid NFT sheen - sweeping highlight when crystallized */}
        <path
          d={pathData}
          fill="url(#liquidSheen)"
          stroke="none"
          className="transition-opacity duration-700 pointer-events-none"
          style={{
            opacity: showDetails ? 0 : 0.6,
          }}
        />
        
        {/* Main glossy highlight / gleam (top-left, bigger & brighter for plastic look) */}
        <ellipse
          cx={center - size * 0.08}
          cy={center - size * 0.12}
          rx={size * 0.09}
          ry={size * 0.045}
          fill="rgba(255,255,255,0.45)"
          className="transition-opacity duration-700"
          style={{
            opacity: showDetails ? 0.5 : 0.85,
            filter: 'blur(4px)',
          }}
        />

        {/* Sharp inner highlight for glassy effect */}
        <ellipse
          cx={center - size * 0.06}
          cy={center - size * 0.10}
          rx={size * 0.04}
          ry={size * 0.02}
          fill="rgba(255,255,255,0.7)"
          className="transition-opacity duration-700"
          style={{
            opacity: showDetails ? 0.3 : 0.6,
            filter: 'blur(1px)',
          }}
        />

        {/* Small secondary gleam (offset from center) */}
        <ellipse
          cx={center + size * 0.08}
          cy={center - size * 0.06}
          rx={size * 0.03}
          ry={size * 0.015}
          fill="rgba(255,255,255,0.35)"
          className="transition-opacity duration-700"
          style={{
            opacity: showDetails ? 0.3 : 0.6,
            filter: 'blur(2px)',
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
              fill="rgba(255,255,255,0.85)"
              fontSize="11"
              fontWeight="500"
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
