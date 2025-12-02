interface JourneyHeaderProps {
  playlistTitle?: string;
  explanation?: string;
}

export function JourneyHeader({ playlistTitle, explanation }: JourneyHeaderProps) {
  return (
    <div className="text-center py-6">
      {/* Title - white with purple underglow */}
      {playlistTitle && (
        <h1
          className="text-3xl md:text-4xl font-semibold mb-4 tracking-tight"
          style={{
            fontFamily: "'Space Grotesk', 'Inter', sans-serif",
            fontWeight: 600,
            letterSpacing: '-0.02em',
            color: 'rgba(255, 255, 255, 0.95)',
            textShadow: '0 0 30px rgba(168, 85, 247, 0.4), 0 0 60px rgba(139, 92, 246, 0.2)',
          }}
        >
          {playlistTitle}
        </h1>
      )}
      
      {/* Thin divider */}
      <div className="w-20 h-px bg-gradient-to-r from-transparent via-purple-400/30 to-transparent mx-auto mb-5" />
      
      {/* AI Explanation - elegant italic with subtle purple tinge */}
      {explanation && (
        <p 
          className="text-base md:text-lg italic font-light leading-relaxed max-w-2xl mx-auto"
          style={{
            color: 'rgba(230, 220, 255, 0.75)',
            textShadow: '0 0 20px rgba(168, 85, 247, 0.15)',
          }}
        >
          {explanation}
        </p>
      )}
      
      {/* Thin divider */}
      <div className="w-20 h-px bg-gradient-to-r from-transparent via-purple-400/30 to-transparent mx-auto mt-5" />
    </div>
  );
}
