import { useState, useEffect, useMemo } from 'react';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  ResponsiveContainer 
} from 'recharts';

interface VibeScore {
  vibe: string;
  score: number;
}

interface SoulGemProps {
  songs: Array<{ sub_vibe?: string; meta_vibe?: string; mapped_subvibe?: string }>;
  size?: number;
}

// Meta-vibe colors (muted for dark theme)
const VIBE_COLORS: Record<string, string> = {
  Happy:    'hsl(48, 70%, 55%)',
  Party:    'hsl(320, 65%, 55%)',
  Chill:    'hsl(168, 55%, 50%)',
  Energy:   'hsl(20, 65%, 55%)',
  Romantic: 'hsl(340, 60%, 60%)',
  Sad:      'hsl(210, 55%, 55%)',
  Drive:    'hsl(25, 65%, 52%)',
  Dark:     'hsl(262, 55%, 55%)',
  Night:    'hsl(240, 40%, 35%)',
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
    score: ((vibeCounts[vibe] || 0) / maxCount) * 100,
  }));
}

export function SoulGem({ songs, size = 200 }: SoulGemProps) {
  const [showDetails, setShowDetails] = useState(true);
  const [hasAnimated, setHasAnimated] = useState(false);

  const vibeScores = useMemo(() => calculateVibeScores(songs), [songs]);

  // After 2.5 seconds, fade out the labels (crystallize into gem)
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowDetails(false);
      setHasAnimated(true);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  // Calculate dominant color for the gem glow
  const dominantVibe = useMemo(() => {
    return vibeScores.reduce((a, b) => a.score > b.score ? a : b);
  }, [vibeScores]);
  
  const glowColor = VIBE_COLORS[dominantVibe.vibe] || 'hsl(262, 55%, 55%)';

  return (
    <div 
      className="relative cursor-pointer flex-shrink-0"
      style={{ width: size, height: size }}
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => hasAnimated && setShowDetails(false)}
    >
      {/* Glow effect behind the gem */}
      <div 
        className="absolute inset-0 rounded-full blur-xl transition-opacity duration-500"
        style={{ 
          background: glowColor,
          opacity: showDetails ? 0.15 : 0.3,
        }}
      />
      
      {/* The radar/gem chart */}
      <div className="relative z-10">
        <ResponsiveContainer width={size} height={size}>
          <RadarChart data={vibeScores} cx="50%" cy="50%">
            {/* Grid lines - fade out */}
            <PolarGrid 
              stroke="rgba(255,255,255,0.15)"
              strokeDasharray="3 3"
              style={{
                opacity: showDetails ? 1 : 0,
                transition: 'opacity 0.8s ease-in-out',
              }}
            />
            
            {/* Axis labels - fade out */}
            <PolarAngleAxis 
              dataKey="vibe"
              tick={({ x, y, payload }) => (
                <text
                  x={x}
                  y={y}
                  textAnchor="middle"
                  fill="rgba(255,255,255,0.7)"
                  fontSize={10}
                  style={{
                    opacity: showDetails ? 1 : 0,
                    transition: 'opacity 0.8s ease-in-out',
                  }}
                >
                  {payload.value}
                </text>
              )}
            />
            
            {/* The gem shape - always visible */}
            <Radar
              name="Soul"
              dataKey="score"
              stroke={glowColor}
              strokeWidth={2}
              fill={glowColor}
              fillOpacity={showDetails ? 0.3 : 0.5}
              style={{
                filter: showDetails ? 'none' : `drop-shadow(0 0 8px ${glowColor})`,
                transition: 'all 0.8s ease-in-out',
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* "Your Soul Gem" label - appears after crystallization */}
      <div 
        className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-white/50 whitespace-nowrap"
        style={{
          opacity: showDetails ? 0 : 1,
          transition: 'opacity 0.5s ease-in-out 0.3s',
        }}
      >
        Your Soul Gem
      </div>
    </div>
  );
}
