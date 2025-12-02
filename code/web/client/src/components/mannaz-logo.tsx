/**
 * Mannaz Rune Logo - ᛗ
 * Represents humanity and the self - perfect for human-sourced emotional data
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
  return (
    <svg
      width={size}
      height={size * 1.3}
      viewBox="0 0 40 52"
      fill="none"
      className={className}
      aria-label="Midden logo"
    >
      <path
        d="M6 4 L6 48 M6 4 L20 22 L34 4 M34 4 L34 48"
        stroke={color}
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
