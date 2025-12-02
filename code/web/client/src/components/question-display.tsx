import { useEffect, useState } from "react";
import { MannazLogo } from "./mannaz-logo";

interface QuestionDisplayProps {
  question: string;
  isVisible: boolean;
}

// Typing effect hook
function useTypewriter(text: string, speed: number = 35, startDelay: number = 0) {
  const [displayed, setDisplayed] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isDone, setIsDone] = useState(false);

  useEffect(() => {
    setDisplayed('');
    setIsDone(false);
    setIsTyping(false);
    
    const startTimeout = setTimeout(() => {
      setIsTyping(true);
      let i = 0;
      
      const interval = setInterval(() => {
        if (i < text.length) {
          setDisplayed(text.slice(0, i + 1));
          i++;
        } else {
          clearInterval(interval);
          setIsTyping(false);
          setIsDone(true);
        }
      }, speed);
      
      return () => clearInterval(interval);
    }, startDelay);
    
    return () => clearTimeout(startTimeout);
  }, [text, speed, startDelay]);

  return { displayed, isTyping, isDone };
}

// Blinking cursor component
function BlinkingCursor({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <span className="animate-blink text-purple-400 font-normal ml-0.5">▌</span>
  );
}

export function QuestionDisplay({ question, isVisible }: QuestionDisplayProps) {
  const { displayed, isTyping, isDone } = useTypewriter(
    question, 
    35,  // typing speed (ms per char)
    200  // start delay
  );

  if (!isVisible) return null;

  return (
    <div className="flex items-start gap-4 justify-center">
      {/* Mannaz rune as command prompt */}
      <div className="flex-shrink-0 pt-1 opacity-70">
        <MannazLogo size={32} color="hsl(262, 70%, 65%)" />
      </div>
      
      {/* Question with typing effect */}
      <h1
        className="text-2xl md:text-4xl font-light tracking-tight text-white/90"
        style={{
          letterSpacing: "-0.01em",
          fontFamily: "'Space Grotesk', 'Inter', sans-serif",
        }}
        data-testid="text-current-question"
      >
        {displayed}
        <BlinkingCursor visible={isTyping || (isDone)} />
      </h1>
    </div>
  );
}
