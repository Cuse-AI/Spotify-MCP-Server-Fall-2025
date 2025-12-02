/**
 * Mannaz Rune Logo - ᛗ
 * Represents humanity and the self - perfect for human-sourced emotional data
 * 
 * Traced directly from the Wikipedia Mannaz rune image
 */

interface MannazLogoProps {
  size?: number;
  color?: string;
  className?: string;
}

export function MannazLogo({
  size = 24,
  color = "currentColor",
  className = ""
}: MannazLogoProps) {
  const width = size;
  const height = size * 1.5;
  
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 40 60"
      fill="none"
      className={className}
      aria-label="Midden logo"
    >
      {/* 
        Mannaz rune ᛗ:
        
        |\  /|  <- diagonals from top go down to center
        | \/ |  <- meet at center (~1/3 down)
        | /\ |  <- diagonals go back out
        |/  \|  <- reach the staves
        |    |  <- verticals continue down
        |    |
      */}
      
      {/* Left vertical stave - full height */}
      <line x1="6" y1="2" x2="6" y2="58" stroke={color} strokeWidth="4" strokeLinecap="round" />
      
      {/* Right vertical stave - full height */}
      <line x1="34" y1="2" x2="34" y2="58" stroke={color} strokeWidth="4" strokeLinecap="round" />
      
      {/* Upper-left diagonal: from top-left down to center */}
      <line x1="6" y1="2" x2="20" y2="18" stroke={color} strokeWidth="4" strokeLinecap="round" />
      
      {/* Upper-right diagonal: from top-right down to center */}
      <line x1="34" y1="2" x2="20" y2="18" stroke={color} strokeWidth="4" strokeLinecap="round" />
      
      {/* Lower-left diagonal: from center back out to left stave */}
      <line x1="20" y1="18" x2="6" y2="34" stroke={color} strokeWidth="4" strokeLinecap="round" />
      
      {/* Lower-right diagonal: from center back out to right stave */}
      <line x1="20" y1="18" x2="34" y2="34" stroke={color} strokeWidth="4" strokeLinecap="round" />
    </svg>
  );
}
