# BLINKING CURSOR - VERTICAL ALIGNMENT FIX
## December 2, 2025

---

## THE PROBLEM

The blinking cursor `█` is sitting too high or too low relative to the text baseline.

---

## THE FIX

The cursor needs to align with the text's baseline, not its center. Use these techniques:

### Option 1: Inline Vertical Alignment (Recommended)

```tsx
function BlinkingCursor({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <span 
      className="animate-blink text-white/80 font-normal"
      style={{ 
        verticalAlign: 'baseline',  // Aligns to text baseline
        position: 'relative',
        top: '0.05em',              // Fine-tune: positive = down, negative = up
      }}
    >
      █
    </span>
  );
}
```

**Adjust the `top` value:**
- `top: '0.05em'` = slightly down
- `top: '-0.05em'` = slightly up
- `top: '0'` = exactly on baseline

---

### Option 2: Using Line-Height Match

```tsx
<span 
  className="animate-blink text-white/80"
  style={{ 
    lineHeight: 'inherit',  // Match parent line-height
    display: 'inline',
  }}
>
  █
</span>
```

---

### Option 3: Flexbox Alignment (if cursor is in a flex container)

If the cursor is inside a flex container with the text:

```tsx
<div className="flex items-baseline">  {/* Use items-baseline, not items-center! */}
  <span className="text-xl">{typedText}</span>
  <BlinkingCursor visible={isTyping} />
</div>
```

---

## FULL COMPONENT WITH FIX

```tsx
function BlinkingCursor({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <span 
      className="animate-blink text-white/80 font-normal inline-block"
      style={{ 
        verticalAlign: 'text-bottom',
        marginLeft: '2px',
        position: 'relative',
        top: '0.02em',  // Tiny nudge - adjust as needed
      }}
    >
      █
    </span>
  );
}
```

---

## QUICK TUNING REFERENCE

| Cursor Position | Fix |
|-----------------|-----|
| Too high | Increase `top` value (e.g., `top: '0.08em'`) |
| Too low | Decrease `top` value (e.g., `top: '-0.02em'`) |
| Way off | Try `verticalAlign: 'text-bottom'` or `'baseline'` |

---

## CSS ANIMATION (unchanged)

```css
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.animate-blink {
  animation: blink 1s step-end infinite;
}
```

---

## DEBUGGING TIP

Add a background color temporarily to see exactly where the cursor box is:

```tsx
<span style={{ backgroundColor: 'red' }}>█</span>
```

This will show you the actual bounding box of the cursor character.

---

*The key is `verticalAlign` + small `top` adjustment. Start with `top: '0.02em'` and tweak from there!*

---

*— Replit*


# MANNAZ RUNE - SIZING GUIDE
## December 2, 2025

---

## THE PROBLEM

The rune shape is correct but the sizing is off. Here's how to fix it.

---

## SIZING FOR DIFFERENT CONTEXTS

### 1. Command Line Prompt (Question Page)

The rune should match the text size next to it.

```tsx
// The rune height should roughly equal the line-height of the text
// For text-xl (1.25rem = 20px), rune should be ~24-28px tall

<div className="flex items-center gap-2">
  <MannazLogo size={20} />  {/* width=20, height=30 */}
  <span className="text-xl">:</span>
  <span className="text-xl">How are you feeling?</span>
</div>
```

**Key:** The rune's HEIGHT should match the x-height of the text (roughly).

---

### 2. Loading Screen (Large, Centered)

For the rotating/pulsing loading state:

```tsx
<MannazLogo size={64} />  {/* width=64, height=96 */}
```

---

### 3. Footer (Small, Subtle)

```tsx
<MannazLogo size={24} />  {/* width=24, height=36 */}
```

---

## THE COMPONENT WITH PROPER SIZING

```tsx
interface MannazLogoProps {
  size?: number;       // This controls WIDTH
  color?: string;
}

function MannazLogo({ 
  size = 32, 
  color = "hsl(262, 70%, 65%)" 
}: MannazLogoProps) {
  // Height is 1.5x width (tall M shape)
  const width = size;
  const height = size * 1.5;
  
  return (
    <svg 
      width={width} 
      height={height} 
      viewBox="0 0 40 60" 
      fill="none"
      style={{ display: 'block' }}  // Removes inline spacing issues
    >
      <path
        d="M8 4 L8 56 M8 4 L20 20 L32 4 M32 4 L32 56"
        stroke={color}
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
```

---

## ALIGNING WITH TEXT

The tricky part is making the rune sit correctly next to text. Here are the fixes:

### Problem: Rune sits too high or low

```tsx
// BAD - misaligned
<div className="flex items-center">
  <MannazLogo size={20} />
  <span>: text</span>
</div>

// GOOD - use items-end or manual adjustment
<div className="flex items-end gap-2">
  <MannazLogo size={20} />
  <span className="text-xl leading-none">:</span>
</div>

// OR use a wrapper with specific positioning
<div className="flex items-center gap-2">
  <div className="flex items-center" style={{ height: '1.5em' }}>
    <MannazLogo size={18} />
  </div>
  <span className="text-xl">:</span>
</div>
```

---

### Problem: Rune looks too small next to large text

**Rule of thumb:** The rune WIDTH should be about 80% of the text's font-size.

| Text Size | Rune `size` prop |
|-----------|------------------|
| `text-sm` (14px) | 12 |
| `text-base` (16px) | 14 |
| `text-lg` (18px) | 16 |
| `text-xl` (20px) | 18 |
| `text-2xl` (24px) | 20 |
| `text-3xl` (30px) | 26 |

---

### Problem: Rune has extra whitespace

Add `display: block` and `line-height: 0` to remove SVG inline spacing:

```tsx
<svg 
  style={{ display: 'block', lineHeight: 0 }}
  // ...
>
```

---

## QUICK REFERENCE

| Context | `size` prop | Actual dimensions | Notes |
|---------|-------------|-------------------|-------|
| Prompt (text-xl) | 18-20 | 18×27 to 20×30 | Match text x-height |
| Prompt (text-2xl) | 22-24 | 22×33 to 24×36 | Match text x-height |
| Loading screen | 64-72 | 64×96 to 72×108 | Big and centered |
| Footer | 20-24 | 20×30 to 24×36 | Subtle |
| Header logo | 28-32 | 28×42 to 32×48 | With "Midden" text |

---

## EXAMPLE: PROMPT WITH CORRECT SIZING

```tsx
function QuestionPrompt({ question }: { question: string }) {
  return (
    <div className="flex items-end gap-3">
      {/* Rune sized to match text-2xl */}
      <div className="flex-shrink-0 pb-1">
        <MannazLogo size={22} color="hsl(262, 70%, 65%)" />
      </div>
      
      {/* Colon - same size as question text */}
      <span className="text-2xl text-white/50 leading-none">:</span>
      
      {/* Question text */}
      <span className="text-2xl text-white/90 leading-relaxed">
        {question}
      </span>
    </div>
  );
}
```

**The `pb-1` (padding-bottom) nudges the rune down slightly to align with the text baseline.**

---

## DEBUGGING TIPS

1. **Add a border to see the actual box:**
   ```tsx
   <div style={{ border: '1px solid red' }}>
     <MannazLogo size={20} />
   </div>
   ```

2. **Check if SVG has extra padding:**
   - The viewBox should start at 0,0
   - The path should use most of the viewBox space

3. **Compare heights:**
   - Rune height = `size * 1.5`
   - Text line-height = font-size × line-height multiplier
   - They should be close for good alignment

---

*— Replit*


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
|\  /| 
| \/ |  
|/  \|
|    |  
|    |
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
