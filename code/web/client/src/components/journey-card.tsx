import type { UserJourney } from "@shared/schema";

interface JourneyCardProps {
  journey: UserJourney;
  playlistTitle?: string;
}

export function JourneyCard({ journey, playlistTitle }: JourneyCardProps) {
  return (
    <div className="relative p-6 rounded-2xl overflow-hidden flex-1">
      {/* Glass background */}
      <div 
        className="absolute inset-0 bg-white/5 backdrop-blur-xl rounded-2xl"
        style={{
          border: '1px solid rgba(255,255,255,0.1)',
        }}
      />
      
      {/* Gradient border glow */}
      <div 
        className="absolute inset-0 rounded-2xl pointer-events-none"
        style={{
          background: 'linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.05))',
          opacity: 0.5,
        }}
      />
      
      {/* Content */}
      <div className="relative z-10 space-y-4">
        {/* Title */}
        {playlistTitle && (
          <h1 
            className="text-2xl font-semibold text-white/90 mb-4"
            style={{ fontFamily: "'Quicksand', 'Inter', sans-serif" }}
          >
            {playlistTitle}
          </h1>
        )}
        
        {/* Journey questions/answers */}
        <div className="space-y-3">
          {journey.now && (
            <div className="space-y-1">
              <p className="text-[11px] text-white/40 uppercase tracking-wider">
                Where you are
              </p>
              <p className="text-base text-white/85">
                {journey.now}
              </p>
            </div>
          )}
          
          {journey.going && (
            <div className="space-y-1">
              <p className="text-[11px] text-white/40 uppercase tracking-wider">
                Where you're going
              </p>
              <p className="text-base text-white/85">
                {journey.going}
              </p>
            </div>
          )}
          
          {journey.vibe && (
            <div className="space-y-1">
              <p className="text-[11px] text-white/40 uppercase tracking-wider">
                The vibe
              </p>
              <p className="text-base text-white/85">
                {journey.vibe}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
