import { useEffect, useState } from "react";

interface QuestionDisplayProps {
  question: string;
  isVisible: boolean;
}

export function QuestionDisplay({ question, isVisible }: QuestionDisplayProps) {
  const [displayQuestion, setDisplayQuestion] = useState(question);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    if (question !== displayQuestion) {
      setFade(false);
      const timeout = setTimeout(() => {
        setDisplayQuestion(question);
        setFade(true);
      }, 200);
      return () => clearTimeout(timeout);
    }
  }, [question, displayQuestion]);

  if (!isVisible) return null;

  return (
    <h1
      className={`text-center text-4xl md:text-6xl font-black tracking-tight transition-opacity duration-300 ${
        fade ? "opacity-100" : "opacity-0"
      }`}
      style={{ 
        letterSpacing: "-0.03em",
        fontFamily: "'Space Grotesk', 'Inter', sans-serif",
        fontWeight: 800
      }}
      data-testid="text-current-question"
    >
      {displayQuestion}
    </h1>
  );
}
