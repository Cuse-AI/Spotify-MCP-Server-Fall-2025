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
    score: Math.max(((vibeCounts[vibe] || 0) / maxCount) * 100, 5), // minimum 5 for visibility
    fullMark: 100,
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
      style={{ width: size, height: size + 30 }}
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => hasAnimated && setShowDetails(false)}
    >
      {/* Glow effect behind the gem */}
      <div 
        className="absolute rounded-full transition-all duration-700"
        style={{ 
          top: '10%',
          left: '10%',
          right: '10%',
          bottom: '20%',
          background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)`,
          opacity: showDetails ? 0.2 : 0.4,
          filter: 'blur(20px)',
        }}
      />
      
      {/* The radar/gem chart */}
      <div className="relative z-10" style={{ width: size, height: size }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={vibeScores}>
            {/* Grid lines - fade out */}
            <PolarGrid 
              stroke="rgba(255,255,255,0.1)"
              strokeDasharray="3 3"
              className="transition-opacity duration-700"
              style={{ opacity: showDetails ? 1 : 0 }}
            />
            
            {/* Hidden radius axis for proper scaling */}
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
                    fill="rgba(255,255,255,0.6)"
                    fontSize={9}
                    className="transition-opacity duration-700"
                    style={{ opacity: showDetails ? 1 : 0 }}
                  >
                    {payload.value}
                  </text>
                );
              }}
            />
            
            {/* The gem shape - always visible */}
            <Radar
              name="Soul"
              dataKey="score"
              stroke={glowColor}
              strokeWidth={2}
              fill={glowColor}
              fillOpacity={showDetails ? 0.25 : 0.4}
              className="transition-all duration-700"
              style={{
                filter: showDetails ? 'none' : `drop-shadow(0 0 12px ${glowColor})`,
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* "Your Soul Gem" label - appears after crystallization */}
      <div 
        className="absolute left-1/2 -translate-x-1/2 text-xs text-white/50 whitespace-nowrap transition-opacity duration-500"
        style={{
          bottom: 0,
          opacity: showDetails ? 0 : 1,
          transitionDelay: '0.3s',
        }}
      >
        Your Soul Gem
      </div>
    </div>
  );
}
