/**
 * Mannaz Rune Logo - ᛗ
 * Represents humanity and the self - perfect for human-sourced emotional data
 * 
 * The authentic Mannaz rune structure:
 * - Two vertical staves (left and right)
 * - Two diagonal lines forming an X in the center, connecting the staves
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
  // Calculate dimensions - the rune is taller than wide
  const width = size;
  const height = size * 1.4;
  
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 40 56"
      fill="none"
      className={className}
      aria-label="Midden logo"
    >
      {/* 
        Mannaz rune ᛗ:
        |  /\  |
        | /  \ |
        | \  / |
        |  \/  |
        
        Two vertical staves with an X connecting them in the middle
      */}
      
      {/* Left vertical stave */}
      <line x1="6" y1="4" x2="6" y2="52" stroke={color} strokeWidth="4" strokeLinecap="round" />
      
      {/* Right vertical stave */}
      <line x1="34" y1="4" x2="34" y2="52" stroke={color} strokeWidth="4" strokeLinecap="round" />
      
      {/* Upper diagonal: left-middle to center-top */}
      <line x1="6" y1="28" x2="20" y2="14" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      
      {/* Upper diagonal: center-top to right-middle */}
      <line x1="20" y1="14" x2="34" y2="28" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      
      {/* Lower diagonal: left-middle to center-bottom */}
      <line x1="6" y1="28" x2="20" y2="42" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      
      {/* Lower diagonal: center-bottom to right-middle */}
      <line x1="20" y1="42" x2="34" y2="28" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
