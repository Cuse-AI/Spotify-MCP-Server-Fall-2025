# Tapestry - Conversational Vibe Playlist Generator
## Design Guidelines

### Design Approach
**Reference-Based:** Inspired by ChatGPT's conversational interface with a distinct dark, sleek aesthetic. Creating an intimate, focused experience that guides users through an emotional journey.

### Core Design Principles
1. **Conversational Intimacy**: Single-focus interface that feels like a one-on-one conversation
2. **Progressive Disclosure**: Reveal questions sequentially to maintain flow and focus
3. **Emotional Depth**: Dark, moody palette that reflects the project's exploration of human emotion
4. **Minimal Distraction**: Clean, centered layout with maximum breathing room

---

## Typography

**Primary Font:** Inter or SF Pro Display (Google Fonts CDN)
**Secondary Font:** Inter or system-ui

### Hierarchy
- **Hero Question Text**: 48px, font-weight: 300, letter-spacing: -0.02em
  - "What's Your Vibe?" 
  - "Where are you now?..."
  - "...and where are you going?"
- **Input Text**: 18px, font-weight: 400
- **Placeholder Text**: 16px, font-weight: 300, opacity: 0.4
- **Body/Results**: 16px, font-weight: 400, line-height: 1.6
- **Song Titles**: 18px, font-weight: 500
- **Metadata**: 14px, font-weight: 400, opacity: 0.6

---

## Layout System

**Spacing Units:** Tailwind units of 4, 6, 8, 12, 16, 24

### Main Interface Structure
- **Centered Column**: max-w-2xl, mx-auto
- **Vertical Centering**: min-h-screen flex items-center justify-center
- **Question Spacing**: mb-12 between question and input
- **Input Height**: h-14 for comfortable interaction
- **Padding**: px-6 on mobile, px-8 on desktop

### Progressive States
1. **Initial State**: Question 1 centered with input
2. **Transition**: Smooth fade (300ms) as question text changes
3. **Final State**: Results page with playlist display

---

## Component Library

### Input Field
- **Style**: Minimal border (1px, opacity 0.2), rounded-lg (8px)
- **Focus State**: Border opacity increases to 0.4, subtle glow
- **Placeholder**: Multi-line suggestions rotate or display together:
  - "an imaginary place..."
  - "a feeling or mood..."
  - "a real location..."
  - "where your mind wanders..."
- **Height**: 56px (h-14)
- **Padding**: px-6

### Question Display
- **Animation**: Fade out old question (200ms) → Fade in new question (200ms)
- **Alignment**: text-center
- **Weight**: Ultra-light to maintain ethereal quality

### Progress Indicator (Subtle)
- **Style**: Three small dots below input
- **States**: Unfilled (opacity 0.2), Current (opacity 0.6), Filled (opacity 1.0)
- **Size**: 6px diameter, gap-3 between dots

### Playlist Results Card
- **Container**: Rounded corners (12px), subtle border
- **Song Item**: py-4 with border-bottom (last:border-0)
- **Layout**: Flexbox - album art (48px) | song info | duration
- **Hover**: Subtle background shift (opacity 0.03)

### Action Buttons
- **Primary CTA**: "Create Playlist on Spotify"
  - Rounded-full, px-8, py-3
  - Subtle gradient or solid with hover lift
- **Secondary**: "Start Over"
  - Ghost style, border with hover fill

### Loading State
- **Style**: Animated dots or subtle pulse
- **Message**: "Walking the emotional tapestry..." or "Finding your journey..."

---

## Visual Design Notes

### Aesthetic Direction
- **Not a ChatGPT Clone**: Distinct personality through darker palette, more dramatic spacing, music-focused touches
- **Sleek & Modern**: Glassmorphism effects sparingly (input field background blur)
- **Emotional Weight**: Interface feels contemplative, not clinical

### Key Differentiators from ChatGPT
1. Darker overall palette (deep grays/blacks vs. white)
2. More vertical spacing for breathing room
3. Softer, lighter typography weights
4. Music-inspired visual language (subtle waveform or spectrum touches)

---

## User Flow Screens

### 1. Landing/Question 1
- Full viewport height
- Centered: "What's Your Vibe?"
- Single input field
- Subtle progress dots (1 of 3)

### 2. Question 2
- Same layout
- Text transitions to: "Where are you now?..."
- Progress dots (2 of 3)

### 3. Question 3
- Same layout
- Text transitions to: "...and where are you going?"
- Progress dots (3 of 3)

### 4. Processing
- Question fades out
- Loading state appears: "Claude is walking the Tapestry..."
- Brief animation (2-3 seconds)

### 5. Results
- Transition to results layout
- Header: "Your Emotional Journey"
- Explanation paragraph of the arc (Claude's reasoning)
- Playlist display (scrollable list)
- CTA: Create on Spotify
- Secondary: Start Over

---

## Images

**Hero Image**: None - This interface is conversational and text-focused. The power comes from simplicity and the questions themselves.

**Playlist Results**: 
- Album artwork thumbnails (48x48px) for each song
- Spotify logo integration in "Create Playlist" button

**Optional Visual Accent**:
- Subtle abstract gradient or mesh background (very low opacity, 0.03-0.05) that shifts between emotional states
- Placed as fixed background, doesn't interfere with readability

---

## Interaction Notes

- **Enter Key**: Advances to next question (no submit button needed)
- **Smooth Transitions**: All state changes use 200-300ms ease-out
- **Auto-focus**: Input automatically focused on each question
- **Escape Key**: Clears current input
- **Tab Navigation**: Not applicable (single input focus)

---

## Responsive Considerations

**Mobile (< 768px)**:
- Question text: 32px
- Input text: 16px
- max-w-full with px-6 padding
- Full-height layout maintained

**Desktop (≥ 768px)**:
- max-w-2xl centered column
- Generous vertical spacing (py-24)
- Question text: 48px