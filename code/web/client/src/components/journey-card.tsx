interface JourneyCardProps {
  playlistTitle?: string;
  explanation?: string;
}

export function JourneyCard({ playlistTitle, explanation }: JourneyCardProps) {
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
      <div className="relative z-10">
        {/* Title */}
        {playlistTitle && (
          <h1 
            className="text-2xl font-semibold text-white/90 mb-4"
            style={{ fontFamily: "'Quicksand', 'Inter', sans-serif" }}
          >
            {playlistTitle}
          </h1>
        )}
        
        {/* AI Explanation blurb */}
        {explanation && (
          <p className="text-sm text-white/60 leading-relaxed">
            {explanation}
          </p>
        )}
      </div>
    </div>
  );
}
