interface JourneyHeaderProps {
  playlistTitle?: string;
  explanation?: string;
}

export function JourneyHeader({ playlistTitle, explanation }: JourneyHeaderProps) {
  return (
    <div className="text-center py-6">
      {/* Title */}
      {playlistTitle && (
        <h1
          className="text-3xl md:text-4xl font-semibold text-white/90 mb-4 tracking-tight"
          style={{
            fontFamily: "'Space Grotesk', 'Inter', sans-serif",
            fontWeight: 600,
            letterSpacing: '-0.02em'
          }}
        >
          {playlistTitle}
        </h1>
      )}
      
      {/* Thin divider */}
      <div className="w-20 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent mx-auto mb-5" />
      
      {/* AI Explanation - elegant italic */}
      {explanation && (
        <p className="text-base md:text-lg text-white/60 italic font-light leading-relaxed max-w-2xl mx-auto">
          {explanation}
        </p>
      )}
      
      {/* Thin divider */}
      <div className="w-20 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent mx-auto mt-5" />
    </div>
  );
}
