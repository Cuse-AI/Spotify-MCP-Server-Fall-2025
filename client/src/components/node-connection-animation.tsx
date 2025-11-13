import { useEffect, useState } from "react";

const LOADING_MESSAGES = [
  "preparing the crystal ball...",
  "consulting the cosmic entities...",
  "I hope you enjoy your trip:} -sw13tch...",
  "weaving your sonic journey...",
  "channeling the musical vibrations...",
  "aligning the stars...",
  "walking through dimensions...",
  "decoding your emotional frequency...",
  "manifesting the perfect vibes...",
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

  const nodes = [
    { id: 0, x: 50, y: 50, delay: 0 },
    { id: 1, x: 150, y: 40, delay: 200 },
    { id: 2, x: 250, y: 60, delay: 400 },
    { id: 3, x: 350, y: 45, delay: 600 },
    { id: 4, x: 450, y: 55, delay: 800 },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6">
      <div className="text-center max-w-md">
        <div className="mb-12 flex justify-center">
          <svg
            width="500"
            height="100"
            viewBox="0 0 500 100"
            className="max-w-full h-auto"
            style={{ filter: "drop-shadow(0 0 8px rgba(168, 85, 247, 0.3))" }}
          >
            {nodes.map((node, i) => {
              if (i < nodes.length - 1) {
                const nextNode = nodes[i + 1];
                return (
                  <line
                    key={`line-${i}`}
                    x1={node.x}
                    y1={node.y}
                    x2={nextNode.x}
                    y2={nextNode.y}
                    stroke="url(#lineGradient)"
                    strokeWidth="2"
                    strokeLinecap="round"
                    className="animate-pulse"
                    style={{
                      animationDelay: `${node.delay}ms`,
                      animationDuration: "2s",
                    }}
                  />
                );
              }
              return null;
            })}

            {nodes.map((node) => (
              <g key={`node-${node.id}`}>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="12"
                  fill="rgba(168, 85, 247, 0.15)"
                  className="animate-ping"
                  style={{
                    animationDelay: `${node.delay}ms`,
                    animationDuration: "2s",
                  }}
                />
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="6"
                  fill="url(#nodeGradient)"
                  stroke="rgba(217, 160, 255, 0.8)"
                  strokeWidth="1.5"
                  className="animate-pulse"
                  style={{
                    animationDelay: `${node.delay}ms`,
                    animationDuration: "2s",
                  }}
                />
              </g>
            ))}

            <defs>
              <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgba(168, 85, 247, 0.4)" />
                <stop offset="50%" stopColor="rgba(217, 160, 255, 0.8)" />
                <stop offset="100%" stopColor="rgba(168, 85, 247, 0.4)" />
              </linearGradient>
              <radialGradient id="nodeGradient">
                <stop offset="0%" stopColor="rgba(217, 160, 255, 1)" />
                <stop offset="100%" stopColor="rgba(168, 85, 247, 0.9)" />
              </radialGradient>
            </defs>
          </svg>
        </div>

        <div className="h-16 flex items-center justify-center">
          <p
            className="text-xl font-light text-purple-300/90 transition-opacity duration-500"
            data-testid="text-loading-message"
            key={messageIndex}
          >
            {LOADING_MESSAGES[messageIndex]}
          </p>
        </div>
      </div>
    </div>
  );
}
