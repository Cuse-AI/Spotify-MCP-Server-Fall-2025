import { useEffect, useState } from "react";
import { MannazLogo } from "./mannaz-logo";

const LOADING_MESSAGES = [
  "Excavating emotional artifacts...",
  "Digging through digital strata...",
  "Aligning emotional coordinates...",
  "Mapping uncharted emotional territory...",
  "Collecting fragments of shared experience...",
  "Searching the spaces between feelings...",
  "Asking the algorithm nicely...",
];

export function NodeConnectionAnimation() {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const messageInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
    }, 2500);

    return () => {
      clearInterval(messageInterval);
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6 gap-8">
      {/* Rotating Mannaz Logo with glow */}
      <div style={{ perspective: '300px' }}>
        <div className="animate-gentle-rotate">
          <div className="relative animate-breathe">
            {/* Glow layer */}
            <div className="absolute inset-0 blur-lg opacity-50">
              <MannazLogo size={72} color="hsl(262, 80%, 55%)" />
            </div>
            {/* Sharp layer */}
            <div className="relative">
              <MannazLogo size={72} color="hsl(262, 75%, 70%)" />
            </div>
          </div>
        </div>
      </div>

      {/* Loading text */}
      <div className="h-16 flex items-center justify-center">
        <p
          className="text-xl font-light text-purple-300/90 transition-opacity duration-500"
          data-testid="text-loading-message"
          key={messageIndex}
          style={{
            fontFamily: "'Space Grotesk', 'Inter', sans-serif",
            letterSpacing: '-0.01em'
          }}
        >
          {LOADING_MESSAGES[messageIndex]}
        </p>
      </div>
    </div>
  );
}
