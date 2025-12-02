import { useState, useEffect, useMemo } from 'react';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis,
  ResponsiveContainer 
} from 'recharts';

interface VibeScore {
  vibe: string;
  score: number;
  fullMark: number;
}

interface SoulGemProps {
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

function calculateVibeScores(songs: SoulGemProps['songs']): VibeScore[] {
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
    score: Math.max(((vibeCounts[vibe] || 0) / maxCount) * 100, 8),
    fullMark: 100,
  }));
}

export function SoulGem({ songs, size = 240 }: SoulGemProps) {
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
  
  // Create gradient ID unique to this instance
  const gradientId = useMemo(() => `gemGradient-${Math.random().toString(36).substr(2, 9)}`, []);

  return (
    <div 
      className="relative cursor-pointer flex-shrink-0"
      style={{ width: size, height: size }}
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => hasAnimated && setShowDetails(false)}
    >
      {/* Outer glow */}
      <div 
        className="absolute rounded-full transition-all duration-700"
        style={{ 
          top: '5%',
          left: '5%',
          right: '5%',
          bottom: '5%',
          background: `radial-gradient(circle, ${glowColor} 0%, transparent 60%)`,
          opacity: showDetails ? 0.15 : 0.35,
          filter: 'blur(25px)',
        }}
      />
      
      {/* The radar/gem chart */}
      <div className="relative z-10" style={{ width: size, height: size }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="75%" data={vibeScores}>
            {/* Gradient definition for gem effect */}
            <defs>
              <radialGradient id={gradientId} cx="30%" cy="30%" r="70%">
                <stop offset="0%" stopColor="rgba(255,255,255,0.4)" />
                <stop offset="50%" stopColor={glowColor} stopOpacity="0.6" />
                <stop offset="100%" stopColor={glowColor} stopOpacity="0.3" />
              </radialGradient>
            </defs>
            
            {/* Grid lines - fade out */}
            <PolarGrid 
              stroke="rgba(255,255,255,0.08)"
              strokeDasharray="2 4"
              className="transition-opacity duration-700"
              style={{ opacity: showDetails ? 1 : 0 }}
            />
            
            <PolarRadiusAxis 
              angle={90} 
              domain={[0, 100]} 
              tick={false}
              axisLine={false}
            />
            
            {/* Axis labels - fade out */}
            <PolarAngleAxis 
              dataKey="vibe"
              tick={(props) => {
                const { x, y, payload } = props;
                return (
                  <text
                    x={x}
                    y={y}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill="rgba(255,255,255,0.5)"
                    fontSize={10}
                    className="transition-opacity duration-700"
                    style={{ opacity: showDetails ? 1 : 0 }}
                  >
                    {payload.value}
                  </text>
                );
              }}
            />
            
            {/* The gem shape */}
            <Radar
              name="Soul"
              dataKey="score"
              stroke={glowColor}
              strokeWidth={showDetails ? 2 : 2.5}
              fill={`url(#${gradientId})`}
              fillOpacity={showDetails ? 0.5 : 0.7}
              className="transition-all duration-700"
              style={{
                filter: showDetails ? 'none' : `drop-shadow(0 0 15px ${glowColor}) drop-shadow(0 0 30px ${glowColor})`,
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Inner highlight for 3D gem effect - shows when crystallized */}
      <div 
        className="absolute pointer-events-none transition-opacity duration-700"
        style={{
          top: '25%',
          left: '30%',
          width: '20%',
          height: '15%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.3) 0%, transparent 100%)',
          borderRadius: '50%',
          filter: 'blur(8px)',
          opacity: showDetails ? 0 : 0.6,
        }}
      />
    </div>
  );
}
