# SOUL GEM - PHYSICAL SHARD LOOK
## December 2, 2025

---

## THE PROBLEM

The Soul Gem looks like a PowerPoint chart - too flat, too soft, not physical enough.

---

## THE FIX: Make it look like a real cut gem/shard

### Key Changes:

1. **Light center → Dark edges** (like light passing through a real gem)
2. **Thicker edge strokes** (bold "cut facet" look)
3. **Brighter highlights** (glassy reflections)
4. **Higher opacity when crystallized** (more solid/physical)

---

## CODE CHANGES

### In `soul-gem.tsx`, update the `<defs>` section:

**Replace the gradients with these:**

```tsx
<defs>
  {/* Radial gradient - LIGHT center fading to DARK edges (like a gem) */}
  <radialGradient id={gradientId} cx="40%" cy="35%" r="65%">
    <stop offset="0%" stopColor="rgba(255,255,255,0.35)" />
    <stop offset="40%" stopColor={glowColor} stopOpacity="0.25" />
    <stop offset="100%" stopColor="hsl(262, 50%, 25%)" stopOpacity="0.15" />
  </radialGradient>

  {/* Linear gradient for depth edges - darker for 3D effect */}
  <linearGradient id={`${gradientId}-edge`} x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stopColor={glowColor} stopOpacity="0.8" />
    <stop offset="100%" stopColor="hsl(262, 60%, 30%)" stopOpacity="0.6" />
  </linearGradient>

  {/* Glow filter for crystallized state */}
  <filter id={glowId} x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="8" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>
```

---

### Update the FRONT FACE path stroke width and opacity:

**Change from:**
```tsx
strokeWidth={showDetails ? 2 : 2.5}
style={{ opacity: showDetails ? 0.5 : 0.7 }}
```

**To:**
```tsx
strokeWidth={showDetails ? 2.5 : 4}
style={{ opacity: showDetails ? 0.6 : 0.85 }}
```

---

### Replace the highlight ellipses with these brighter ones:

```tsx
{/* Main glossy highlight / gleam (top-left, bigger & brighter) */}
<ellipse
  cx={center - size * 0.08}
  cy={center - size * 0.12}
  rx={size * 0.09}
  ry={size * 0.045}
  fill="rgba(255,255,255,0.45)"
  className="transition-opacity duration-700"
  style={{
    opacity: showDetails ? 0.5 : 0.85,
    filter: 'blur(4px)',
  }}
/>

{/* Sharp inner highlight for glassy effect */}
<ellipse
  cx={center - size * 0.06}
  cy={center - size * 0.10}
  rx={size * 0.04}
  ry={size * 0.02}
  fill="rgba(255,255,255,0.7)"
  className="transition-opacity duration-700"
  style={{
    opacity: showDetails ? 0.3 : 0.6,
    filter: 'blur(1px)',
  }}
/>

{/* Small secondary gleam (offset from center) */}
<ellipse
  cx={center + size * 0.08}
  cy={center - size * 0.06}
  rx={size * 0.03}
  ry={size * 0.015}
  fill="rgba(255,255,255,0.35)"
  className="transition-opacity duration-700"
  style={{
    opacity: showDetails ? 0.3 : 0.6,
    filter: 'blur(2px)',
  }}
/>
```

---

## VISUAL RESULT

| State | Before | After |
|-------|--------|-------|
| **Hovering** | Flat, uniform purple | Light center, defined edges, visible facets |
| **Crystallized** | Faded, weak | Bold edges (4px), bright highlights, solid opacity |
| **Highlights** | Subtle, small | Large glassy gleam + sharp inner reflection |

---

## WHY THIS WORKS

Real gems have:
- **Light concentration in the center** (light refracts inward)
- **Dark edges where facets meet** (shadows at cut lines)
- **Sharp highlight reflections** (from polished surfaces)
- **Bold facet edges** (the cut lines are visible)

The previous version had uniform color + thin edges = PowerPoint chart.

---

*— Replit*


# LOGO PLACEMENT & TYPING EFFECT
## December 2, 2025

---

## OVERVIEW

Two pages in the app:
1. **Question Page** - Where user answers 3 questions
2. **Playlist Page** - Shows results

---

## 1. LOADING SCREEN

**The logo rotates slowly with a pulsing glow.**

```tsx
function LoadingScreen() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6">
      {/* Rotating + pulsing logo */}
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
      <p className="text-white/60 text-sm animate-pulse">
        {loadingMessage}
      </p>
    </div>
  );
}
```

```css
@keyframes gentle-rotate {
  0%, 100% { transform: rotateY(-20deg); }
  50% { transform: rotateY(20deg); }
}

@keyframes breathe {
  0%, 100% { filter: drop-shadow(0 0 15px rgba(139, 92, 246, 0.3)); }
  50% { filter: drop-shadow(0 0 25px rgba(139, 92, 246, 0.6)); }
}

.animate-gentle-rotate {
  animation: gentle-rotate 10s ease-in-out infinite;
}

.animate-breathe {
  animation: breathe 3s ease-in-out infinite;
}
```

---

## 2. QUESTION PAGE - COMMAND LINE TYPING EFFECT

### The Concept

The Mannaz rune acts as the "prompt" symbol (like `$` or `>` in a terminal).

**Visual:**
```
ᛗ: How are you feeling right now?█
   [user types answer]

ᛗ: Where do you want to go?█
   [user types answer]

ᛗ: How do you want to get there?█
   [user types answer]
```

The `█` is a blinking cursor. Each question types out letter-by-letter.

---

### Full Component

```tsx
import { useState, useEffect } from 'react';

// Mannaz Logo Component
function MannazLogo({ size = 24, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size * 1.3} viewBox="0 0 40 52" fill="none">
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

// Typing effect hook
function useTypewriter(text: string, speed: number = 50, startDelay: number = 0) {
  const [displayed, setDisplayed] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isDone, setIsDone] = useState(false);

  useEffect(() => {
    setDisplayed('');
    setIsDone(false);
    
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

// Blinking cursor
function BlinkingCursor({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <span className="animate-blink text-white/80 font-normal">█</span>
  );
}

// Single question row with typing effect
interface QuestionRowProps {
  question: string;
  answer: string;
  onAnswerChange: (value: string) => void;
  onSubmit: () => void;
  isActive: boolean;
  showQuestion: boolean;
  typingDelay?: number;
}

function QuestionRow({ 
  question, 
  answer, 
  onAnswerChange, 
  onSubmit, 
  isActive,
  showQuestion,
  typingDelay = 0
}: QuestionRowProps) {
  const { displayed, isTyping, isDone } = useTypewriter(
    showQuestion ? question : '', 
    40,  // typing speed (ms per char)
    typingDelay
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && answer.trim()) {
      onSubmit();
    }
  };

  if (!showQuestion && !displayed) return null;

  return (
    <div className="space-y-3">
      {/* Prompt line: Logo + Question */}
      <div className="flex items-start gap-3">
        {/* The Mannaz rune as prompt */}
        <div className="flex items-center gap-2 flex-shrink-0 pt-1">
          <MannazLogo size={24} color="hsl(262, 70%, 65%)" />
          <span className="text-white/50 text-xl">:</span>
        </div>
        
        {/* Typed question */}
        <p className="text-xl text-white/90 font-light">
          {displayed}
          <BlinkingCursor visible={isTyping || (isDone && isActive && !answer)} />
        </p>
      </div>
      
      {/* Answer input - appears after typing is done */}
      {isDone && isActive && (
        <div className="pl-12 animate-fade-in">
          <input
            type="text"
            value={answer}
            onChange={(e) => onAnswerChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="..."
            autoFocus
            className="w-full bg-transparent border-b border-white/20 
                       text-white/80 text-lg py-2 
                       focus:outline-none focus:border-white/40
                       placeholder:text-white/30"
          />
        </div>
      )}
      
      {/* Answered (locked in) */}
      {!isActive && answer && (
        <div className="pl-12">
          <p className="text-lg text-white/60 italic">{answer}</p>
        </div>
      )}
    </div>
  );
}

// Main Question Page
export function QuestionPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState(['', '', '']);
  
  const questions = [
    "How are you feeling right now?",
    "Where do you want to go?",
    "How do you want to get there?"
  ];

  const handleAnswerChange = (index: number, value: string) => {
    const newAnswers = [...answers];
    newAnswers[index] = value;
    setAnswers(newAnswers);
  };

  const handleSubmit = (index: number) => {
    if (answers[index].trim() && index < questions.length - 1) {
      setCurrentStep(index + 1);
    } else if (index === questions.length - 1 && answers[index].trim()) {
      // All done - navigate to results
      handleGeneratePlaylist();
    }
  };

  const handleGeneratePlaylist = () => {
    // Call API and navigate to playlist page
  };

  return (
    <div className="min-h-screen bg-[hsl(262,30%,8%)] flex items-center justify-center p-8">
      <div className="max-w-2xl w-full space-y-8">
        {questions.map((q, i) => (
          <QuestionRow
            key={i}
            question={q}
            answer={answers[i]}
            onAnswerChange={(val) => handleAnswerChange(i, val)}
            onSubmit={() => handleSubmit(i)}
            isActive={currentStep === i}
            showQuestion={i <= currentStep}
            typingDelay={i === 0 ? 500 : 300}  // First question delays a bit
          />
        ))}
      </div>
    </div>
  );
}
```

---

### CSS Animations

```css
/* Blinking cursor */
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.animate-blink {
  animation: blink 1s step-end infinite;
}

/* Fade in for answer input */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
```

---

### Tailwind Config Addition

```ts
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      animation: {
        'blink': 'blink 1s step-end infinite',
        'fade-in': 'fade-in 0.3s ease-out',
        'gentle-rotate': 'gentle-rotate 10s ease-in-out infinite',
        'breathe': 'breathe 3s ease-in-out infinite',
      },
      keyframes: {
        blink: {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' },
        },
        'fade-in': {
          from: { opacity: '0', transform: 'translateY(5px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'gentle-rotate': {
          '0%, 100%': { transform: 'rotateY(-20deg)' },
          '50%': { transform: 'rotateY(20deg)' },
        },
        'breathe': {
          '0%, 100%': { filter: 'drop-shadow(0 0 15px rgba(139, 92, 246, 0.3))' },
          '50%': { filter: 'drop-shadow(0 0 25px rgba(139, 92, 246, 0.6))' },
        },
      },
    },
  },
}
```

---

## 3. PLAYLIST PAGE

**Logo only at the very bottom, centered, as a footer/end mark.**

```tsx
function PlaylistPage() {
  return (
    <div className="min-h-screen">
      {/* ... playlist content ... */}
      
      {/* Footer with logo */}
      <footer className="py-12 flex justify-center">
        <div className="opacity-40 hover:opacity-60 transition-opacity">
          <MannazLogo size={32} color="hsl(262, 60%, 55%)" />
        </div>
      </footer>
    </div>
  );
}
```

Small, subtle, muted - just a signature at the bottom.

---

## SUMMARY

| Location | Logo Behavior |
|----------|---------------|
| **Loading Screen** | Large (72px), slow 3D rotation, pulsing glow |
| **Question Page** | Acts as prompt symbol (24px), static, with blinking cursor after |
| **Playlist Page** | Only at footer, small (32px), muted, centered |

---

## THE FLOW

```
1. Loading Screen
   [Logo rotating + glowing]
   "Excavating emotional artifacts..."

2. Question Page
   ᛗ: How are you feeling right now?█
      [user types, presses enter]
   
   ᛗ: Where do you want to go?█
      [user types, presses enter]
   
   ᛗ: How do you want to get there?█
      [user types, presses enter]

3. Loading Screen again
   [Logo rotating + glowing]
   "Crystallizing your feelings..."

4. Playlist Page
   [Soul Gem + Songs]
   ...
   [Small logo at bottom]
```

---

*The terminal/command-line aesthetic is perfect for Midden - like you're querying an ancient oracle!*

*— Replit*
