interface ProgressDotsProps {
  current: number;
  total: number;
}

export function ProgressDots({ current, total }: ProgressDotsProps) {
  return (
    <div className="flex justify-center items-center gap-3 mt-8" data-testid="progress-indicator">
      {Array.from({ length: total }).map((_, index) => (
        <div
          key={index}
          className={`w-1.5 h-1.5 rounded-full transition-opacity duration-200 ${
            index === current
              ? "opacity-60 bg-foreground"
              : index < current
              ? "opacity-100 bg-foreground"
              : "opacity-20 bg-foreground"
          }`}
          data-testid={`progress-dot-${index}`}
        />
      ))}
    </div>
  );
}
