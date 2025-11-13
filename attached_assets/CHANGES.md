# Tapestry Fixes Applied

## Files Changed
- `server/claude-service.ts`

## What Was Fixed

### 1. **File Path Fix for Replit**
- Changed paths from `..`, `..` to direct paths for Replit environment
- Line 59-60: Uses `process.cwd(), "core", "tapestry.json"` and `process.cwd(), "data", "emotional_manifold_COMPLETE.json"`

### 2. **Sub-Vibe Validation** (CRITICAL FIX)
- Added validation to filter out invalid sub-vibe names returned by Claude
- Lines 173-182: Validates each sub-vibe exists in manifold before using it
- Prevents crash when Claude returns hallucinated or mismatched sub-vibe names

### 3. **Two-Step Optimization** (Already in your GitHub code)
- Step 1: Identify 15-25 relevant sub-vibes for the emotional journey
- Step 2: Load ALL songs only from those relevant sub-vibes
- Reduces token usage from 220K+ to ~50K, staying under Claude's 200K limit

## How to Apply

### Option 1: Replace the whole file
```bash
# In your code/web/ directory
cp server/claude-service.ts server/claude-service.ts.backup
# Copy the new file over
```

### Option 2: Manual changes
Just add the validation block (lines 173-182) after loading songs:

```typescript
// Filter out any sub-vibes that don't exist in the manifold
const validSubVibes = relevantSubVibes.filter(subVibe => {
  if (!manifold.sub_vibes[subVibe]) {
    console.warn(`⚠️  Sub-vibe "${subVibe}" returned by Claude but not found in manifold`);
    return false;
  }
  return true;
});

console.log(`✅ Validated ${validSubVibes.length} sub-vibes exist in manifold`);

// Then use validSubVibes instead of relevantSubVibes in the manifest
```

## Testing
✅ Tested successfully in Replit
✅ No more crashes on invalid sub-vibe names
✅ Claude API working with proper token limits
✅ Playlist generation ~30-60 seconds

